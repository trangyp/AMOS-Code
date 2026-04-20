"""AMOS AI Agent Plugin System.

Provides extensible plugin architecture for AI agents, enabling third-party
tools, integrations, and extensions to plug into the AMOS ecosystem.

Features:
- Plugin discovery and registration
- Tool call interceptors
- Policy provider interfaces
- Third-party integrations
- Plugin lifecycle management
- Hot-swappable plugins

Research Sources:
- Agent Governance Toolkit (Microsoft 2026)
- AI Agent Plugins Guide (Nevo 2026)
- AI Agent Orchestration Frameworks (KDnuggets 2026)

Creator: Trang Phan
Version: 3.0.0
"""

from __future__ import annotations

import asyncio
import importlib.util
import json
import os
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc, timezone
from typing import Any, Optional

UTC = UTC
from abc import ABC, abstractmethod
from enum import Enum

# Plugin configuration
PLUGIN_DIR = os.getenv("AMOS_PLUGIN_DIR", "./plugins")
PLUGIN_ENABLED = os.getenv("PLUGINS_ENABLED", "true").lower() == "true"
MAX_PLUGINS = int(os.getenv("MAX_PLUGINS", "50"))


class PluginType(Enum):
    """Types of plugins."""

    TOOL = "tool"  # Adds new tools
    INTERCEPTOR = "interceptor"  # Intercepts tool calls
    POLICY = "policy"  # Provides governance policies
    INTEGRATION = "integration"  # Third-party integrations
    MONITORING = "monitoring"  # Monitoring extensions
    CUSTOM = "custom"  # Custom extensions


class PluginStatus(Enum):
    """Plugin lifecycle status."""

    REGISTERED = "registered"
    LOADING = "loading"
    ACTIVE = "active"
    ERROR = "error"
    DISABLED = "disabled"
    UNLOADED = "unloaded"


@dataclass
class PluginManifest:
    """Plugin metadata and configuration."""

    name: str
    version: str
    description: str
    author: str
    plugin_type: str
    entry_point: str
    dependencies: list[str] = field(default_factory=list)
    config_schema: dict[str, Any] = field(default_factory=dict)
    permissions: list[str] = field(default_factory=list)
    hooks: list[str] = field(default_factory=list)


@dataclass
class PluginInstance:
    """Represents a loaded plugin instance."""

    plugin_id: str
    manifest: PluginManifest
    instance: Any
    status: str = "registered"
    config: dict[str, Any] = field(default_factory=dict)
    loaded_at: str = None
    error_message: str = None


class BasePlugin(ABC):
    """Base class for all plugins."""

    @abstractmethod
    async def initialize(self, config: dict[str, Any]) -> bool:
        """Initialize the plugin with configuration."""
        pass

    @abstractmethod
    async def shutdown(self) -> bool:
        """Shutdown the plugin."""
        pass

    def get_manifest(self) -> PluginManifest:
        """Get plugin manifest. Override in subclass."""
        return PluginManifest(
            name="base_plugin",
            version="1.0.0",
            description="Base plugin class",
            author="AMOS",
            plugin_type=PluginType.CUSTOM.value,
            entry_point="base_plugin",
        )


class ToolPlugin(BasePlugin):
    """Plugin that provides new tools for agents."""

    @abstractmethod
    async def get_tools(self) -> dict[str, Callable]:
        """Return dictionary of tool name -> function."""
        pass

    @abstractmethod
    async def execute_tool(self, tool_name: str, params: dict[str, Any]) -> Any:
        """Execute a tool by name."""
        pass


class InterceptorPlugin(BasePlugin):
    """Plugin that intercepts tool calls."""

    @abstractmethod
    async def before_tool_call(self, tool_name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Intercept before tool execution. Return modified params."""
        return params

    @abstractmethod
    async def after_tool_call(self, tool_name: str, result: Any, error: str = None) -> Any:
        """Intercept after tool execution. Return modified result."""
        return result


class PolicyPlugin(BasePlugin):
    """Plugin that provides governance policies."""

    @abstractmethod
    async def get_policies(self) -> list[dict[str, Any]]:
        """Return list of policy definitions."""
        pass

    @abstractmethod
    async def evaluate(self, action: str, context: dict[str, Any]) -> dict[str, Any]:
        """Evaluate an action against policies."""
        pass


class PluginRegistry:
    """Registry for managing plugins."""

    def __init__(self):
        self.plugins: dict[str, PluginInstance] = {}
        self.tools: dict[str, Callable] = {}
        self.interceptors: list[InterceptorPlugin] = []
        self.policies: list[PolicyPlugin] = []
        self.hooks: dict[str, list[Callable]] = {}
        self._lock = asyncio.Lock()

    async def discover_plugins(self) -> list[str]:
        """Discover available plugins in plugin directory."""
        discovered = []

        if not os.path.exists(PLUGIN_DIR):
            return discovered

        for item in os.listdir(PLUGIN_DIR):
            plugin_path = os.path.join(PLUGIN_DIR, item)

            # Check for plugin manifest
            manifest_path = os.path.join(plugin_path, "manifest.json")
            if os.path.isfile(manifest_path):
                discovered.append(plugin_path)

            # Check for Python module
            init_path = os.path.join(plugin_path, "__init__.py")
            if os.path.isfile(init_path) and not os.path.isfile(manifest_path):
                discovered.append(plugin_path)

        return discovered

    async def load_plugin(
        self, plugin_path: str, config: dict[str, Optional[Any]] = None
    ) -> PluginInstance:
        """Load a plugin from path."""
        async with self._lock:
            if len(self.plugins) >= MAX_PLUGINS:
                print(f"⚠ Maximum plugin limit ({MAX_PLUGINS}) reached")
                return None

            try:
                # Read manifest
                manifest_path = os.path.join(plugin_path, "manifest.json")
                if os.path.isfile(manifest_path):
                    with open(manifest_path) as f:
                        manifest_data = json.load(f)
                    manifest = PluginManifest(**manifest_data)
                else:
                    # Generate default manifest
                    manifest = PluginManifest(
                        name=os.path.basename(plugin_path),
                        version="1.0.0",
                        description="Auto-discovered plugin",
                        author="Unknown",
                        plugin_type=PluginType.CUSTOM.value,
                        entry_point="plugin",
                    )

                # Generate plugin ID
                import hashlib

                plugin_id = hashlib.md5(plugin_path.encode()).hexdigest()[:8]

                if plugin_id in self.plugins:
                    print(f"⚠ Plugin {manifest.name} already loaded")
                    return self.plugins[plugin_id]

                # Load module
                spec = importlib.util.spec_from_file_location(
                    manifest.name, os.path.join(plugin_path, manifest.entry_point + ".py")
                )
                if not spec or not spec.loader:
                    raise ImportError(f"Cannot load plugin from {plugin_path}")

                module = importlib.util.module_from_spec(spec)
                sys.modules[manifest.name] = module
                spec.loader.exec_module(module)

                # Find plugin class
                plugin_class = None
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (
                        isinstance(attr, type)
                        and issubclass(attr, BasePlugin)
                        and attr != BasePlugin
                    ):
                        plugin_class = attr
                        break

                if not plugin_class:
                    raise ImportError(f"No plugin class found in {plugin_path}")

                # Instantiate plugin
                instance = plugin_class()

                # Create plugin instance record
                plugin_record = PluginInstance(
                    plugin_id=plugin_id,
                    manifest=manifest,
                    instance=instance,
                    status=PluginStatus.LOADING.value,
                    config=config or {},
                )

                # Initialize plugin
                success = await instance.initialize(config or {})
                if not success:
                    raise RuntimeError("Plugin initialization failed")

                # Register based on type
                if manifest.plugin_type == PluginType.TOOL.value:
                    await self._register_tool_plugin(plugin_record)
                elif manifest.plugin_type == PluginType.INTERCEPTOR.value:
                    await self._register_interceptor_plugin(plugin_record)
                elif manifest.plugin_type == PluginType.POLICY.value:
                    await self._register_policy_plugin(plugin_record)

                plugin_record.status = PluginStatus.ACTIVE.value
                plugin_record.loaded_at = datetime.now(timezone.utc).isoformat()

                self.plugins[plugin_id] = plugin_record

                print(f"✓ Plugin loaded: {manifest.name} v{manifest.version}")
                return plugin_record

            except Exception as e:
                error_msg = str(e)
                print(f"✗ Failed to load plugin from {plugin_path}: {error_msg}")

                # Create error record
                plugin_record = PluginInstance(
                    plugin_id=plugin_id if "plugin_id" in locals() else "error",
                    manifest=manifest
                    if "manifest" in locals()
                    else PluginManifest(
                        name="unknown",
                        version="0.0.0",
                        description="",
                        author="",
                        plugin_type="",
                        entry_point="",
                    ),
                    instance=None,
                    status=PluginStatus.ERROR.value,
                    error_message=error_msg,
                )
                return plugin_record

    async def _register_tool_plugin(self, plugin_record: PluginInstance):
        """Register a tool plugin."""
        tool_plugin = plugin_record.instance
        if isinstance(tool_plugin, ToolPlugin):
            tools = await tool_plugin.get_tools()
            for tool_name, tool_func in tools.items():
                self.tools[tool_name] = tool_func

    async def _register_interceptor_plugin(self, plugin_record: PluginInstance):
        """Register an interceptor plugin."""
        interceptor = plugin_record.instance
        if isinstance(interceptor, InterceptorPlugin):
            self.interceptors.append(interceptor)

    async def _register_policy_plugin(self, plugin_record: PluginInstance):
        """Register a policy plugin."""
        policy = plugin_record.instance
        if isinstance(policy, PolicyPlugin):
            self.policies.append(policy)

    async def unload_plugin(self, plugin_id: str) -> bool:
        """Unload a plugin."""
        async with self._lock:
            plugin_record = self.plugins.get(plugin_id)
            if not plugin_record:
                return False

            try:
                if plugin_record.instance:
                    await plugin_record.instance.shutdown()

                # Unregister based on type
                manifest = plugin_record.manifest
                if manifest.plugin_type == PluginType.TOOL.value:
                    # Remove tools provided by this plugin
                    tools_to_remove = [
                        name
                        for name, func in self.tools.items()
                        if getattr(func, "_plugin_id", None) == plugin_id
                    ]
                    for tool_name in tools_to_remove:
                        del self.tools[tool_name]

                elif manifest.plugin_type == PluginType.INTERCEPTOR.value:
                    if plugin_record.instance in self.interceptors:
                        self.interceptors.remove(plugin_record.instance)

                elif manifest.plugin_type == PluginType.POLICY.value:
                    if plugin_record.instance in self.policies:
                        self.policies.remove(plugin_record.instance)

                plugin_record.status = PluginStatus.UNLOADED.value
                del self.plugins[plugin_id]

                print(f"✓ Plugin unloaded: {manifest.name}")
                return True

            except Exception as e:
                print(f"✗ Error unloading plugin {plugin_id}: {e}")
                return False

    async def execute_with_interceptors(
        self, tool_name: str, params: dict[str, Any], executor: Callable
    ) -> Any:
        """Execute a tool with interceptor chain."""
        # Before hooks
        modified_params = params
        for interceptor in self.interceptors:
            try:
                modified_params = await interceptor.before_tool_call(tool_name, modified_params)
            except Exception as e:
                print(f"⚠ Interceptor error (before): {e}")

        # Execute
        try:
            result = await executor(modified_params)
            error = None
        except Exception as e:
            result = None
            error = str(e)

        # After hooks
        for interceptor in reversed(self.interceptors):
            try:
                result = await interceptor.after_tool_call(tool_name, result, error)
            except Exception as e:
                print(f"⚠ Interceptor error (after): {e}")

        if error:
            raise Exception(error)

        return result

    def get_plugin(self, plugin_id: str) -> PluginInstance:
        """Get a plugin by ID."""
        return self.plugins.get(plugin_id)

    def list_plugins(self, plugin_type: str = None, status: str = None) -> list[PluginInstance]:
        """List all plugins with optional filtering."""
        plugins = list(self.plugins.values())

        if plugin_type:
            plugins = [p for p in plugins if p.manifest.plugin_type == plugin_type]

        if status:
            plugins = [p for p in plugins if p.status == status]

        return plugins

    def get_available_tools(self) -> dict[str, Callable]:
        """Get all available tools from plugins."""
        return self.tools.copy()

    async def evaluate_policies(self, action: str, context: dict[str, Any]) -> list[dict[str, Any]]:
        """Evaluate all policy plugins."""
        results = []

        for policy_plugin in self.policies:
            try:
                result = await policy_plugin.evaluate(action, context)
                results.append(result)
            except Exception as e:
                print(f"⚠ Policy evaluation error: {e}")

        return results

    def register_hook(self, hook_name: str, callback: Callable):
        """Register a callback for a hook."""
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
        self.hooks[hook_name].append(callback)

    async def trigger_hook(self, hook_name: str, data: dict[str, Any]) -> list[Any]:
        """Trigger all callbacks for a hook."""
        results = []

        callbacks = self.hooks.get(hook_name, [])
        for callback in callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    result = await callback(data)
                else:
                    result = callback(data)
                results.append(result)
            except Exception as e:
                print(f"⚠ Hook error: {e}")

        return results

    def get_stats(self) -> dict[str, Any]:
        """Get plugin registry statistics."""
        by_type = {}
        by_status = {}

        for plugin in self.plugins.values():
            ptype = plugin.manifest.plugin_type
            by_type[ptype] = by_type.get(ptype, 0) + 1

            by_status[plugin.status] = by_status.get(plugin.status, 0) + 1

        return {
            "total_plugins": len(self.plugins),
            "by_type": by_type,
            "by_status": by_status,
            "available_tools": len(self.tools),
            "active_interceptors": len(self.interceptors),
            "active_policies": len(self.policies),
            "registered_hooks": len(self.hooks),
        }


# Global plugin registry
plugin_registry = PluginRegistry()


# Convenience functions
async def load_plugin(plugin_path: str, config: dict[str, Optional[Any]] = None) -> PluginInstance:
    """Load a plugin."""
    return await plugin_registry.load_plugin(plugin_path, config)


async def unload_plugin(plugin_id: str) -> bool:
    """Unload a plugin."""
    return await plugin_registry.unload_plugin(plugin_id)


async def discover_and_load_all():
    """Discover and load all available plugins."""
    discovered = await plugin_registry.discover_plugins()
    loaded = []

    for plugin_path in discovered:
        plugin = await plugin_registry.load_plugin(plugin_path)
        if plugin and plugin.status == PluginStatus.ACTIVE.value:
            loaded.append(plugin.manifest.name)

    return loaded


def get_plugin_tools() -> dict[str, Callable]:
    """Get all plugin-provided tools."""
    return plugin_registry.get_available_tools()


async def execute_tool_with_plugins(tool_name: str, params: dict[str, Any]) -> Any:
    """Execute a tool with plugin interceptors."""
    tool = plugin_registry.tools.get(tool_name)
    if not tool:
        raise ValueError(f"Tool '{tool_name}' not found")

    return await plugin_registry.execute_with_interceptors(tool_name, params, tool)
