"""Plugin Registry - Extensible plugin system for kernel"""

import importlib
import inspect
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class PluginInfo:
    """Plugin metadata."""

    name: str
    version: str
    description: str
    author: str
    entry_point: str
    hooks: list[str]


class KernelPlugin(ABC):
    """Base class for kernel plugins."""

    @property
    @abstractmethod
    def info(self) -> PluginInfo:
        """Return plugin metadata."""
        pass

    @abstractmethod
    def initialize(self, kernel_context: dict[str, Any]) -> bool:
        """Initialize plugin with kernel context."""
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Cleanup when plugin is unloaded."""
        pass


class PluginRegistry:
    """Registry for kernel plugins."""

    def __init__(self):
        self._plugins: dict[str, KernelPlugin] = {}
        self._hooks: dict[str, list[Callable]] = {}
        self._context: dict[str, Any] = {}

    def set_context(self, context: dict[str, Any]) -> None:
        """Set kernel context for plugins."""
        self._context = context

    def register(self, plugin: KernelPlugin) -> bool:
        """Register a plugin."""
        info = plugin.info

        if info.name in self._plugins:
            return False

        # Initialize plugin
        if not plugin.initialize(self._context):
            return False

        self._plugins[info.name] = plugin

        # Register hooks
        for hook_name in info.hooks:
            if hook_name not in self._hooks:
                self._hooks[hook_name] = []
            # Get hook method from plugin
            hook_method = getattr(plugin, f"on_{hook_name}", None)
            if hook_method and callable(hook_method):
                self._hooks[hook_name].append(hook_method)

        return True

    def unregister(self, name: str) -> bool:
        """Unregister a plugin."""
        if name not in self._plugins:
            return False

        plugin = self._plugins[name]
        info = plugin.info

        # Unregister hooks
        for hook_name in info.hooks:
            if hook_name in self._hooks:
                hook_method = getattr(plugin, f"on_{hook_name}", None)
                if hook_method in self._hooks[hook_name]:
                    self._hooks[hook_name].remove(hook_method)

        # Shutdown plugin
        plugin.shutdown()
        del self._plugins[name]

        return True

    def get_plugin(self, name: str) -> Optional[KernelPlugin]:
        """Get plugin by name."""
        return self._plugins.get(name)

    def list_plugins(self) -> list[PluginInfo]:
        """List all registered plugins."""
        return [p.info for p in self._plugins.values()]

    def execute_hook(self, hook_name: str, *args, **kwargs) -> list[Any]:
        """Execute all handlers for a hook."""
        results = []
        for handler in self._hooks.get(hook_name, []):
            try:
                result = handler(*args, **kwargs)
                results.append(result)
            except Exception:
                results.append(None)
        return results

    def load_from_module(self, module_path: str) -> Optional[KernelPlugin]:
        """Load plugin from module path."""
        try:
            module = importlib.import_module(module_path)
            # Find KernelPlugin subclass
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, KernelPlugin) and obj != KernelPlugin:
                    plugin = obj()
                    self.register(plugin)
                    return plugin
        except Exception as e:
            print(f"Failed to load plugin from {module_path}: {e}")
        return None


# Global registry
_registry: Optional[PluginRegistry] = None


def get_plugin_registry() -> PluginRegistry:
    """Get global plugin registry."""
    global _registry
    if _registry is None:
        _registry = PluginRegistry()
    return _registry


# Example plugin implementation
class MetricsPlugin(KernelPlugin):
    """Example plugin that adds metrics collection."""

    @property
    def info(self) -> PluginInfo:
        return PluginInfo(
            name="metrics",
            version="1.0.0",
            description="Collects kernel execution metrics",
            author="AMOS",
            entry_point="amos_kernel.plugins.metrics",
            hooks=["workflow_start", "workflow_complete"],
        )

    def initialize(self, kernel_context: dict[str, Any]) -> bool:
        self._metrics = {"workflows": 0}
        return True

    def shutdown(self) -> None:
        pass

    def on_workflow_start(self, workflow_id: str) -> None:
        self._metrics["workflows"] += 1

    def on_workflow_complete(self, workflow_id: str, success: bool) -> None:
        pass

    def get_metrics(self) -> dict:
        return self._metrics.copy()
