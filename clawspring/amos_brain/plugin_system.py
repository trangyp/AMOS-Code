#!/usr/bin/env python3
from __future__ import annotations

"""AMOS Ecosystem v2.1 - Plugin Architecture System.

Enables extending AMOS without modifying core code.
Supports cognitive engines, dashboard widgets, and custom commands.
"""

import importlib
import importlib.util
import json
import sys
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class PluginMetadata:
    """Plugin metadata."""

    name: str
    version: str
    author: str
    description: str
    hooks: list[str]
    dependencies: list[str]


class AMOSPlugin(ABC):
    """Base class for AMOS plugins."""

    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        pass

    @abstractmethod
    def initialize(self, context: dict[str, Any]) -> bool:
        """Initialize plugin with context."""
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Cleanup plugin resources."""
        pass


class CognitiveEnginePlugin(AMOSPlugin):
    """Plugin for adding custom cognitive engines."""

    @abstractmethod
    def execute(self, task: str, context: dict[str, Any]) -> dict[str, Any]:
        """Execute cognitive task."""
        pass


class DashboardWidgetPlugin(AMOSPlugin):
    """Plugin for adding dashboard widgets."""

    @abstractmethod
    def render(self) -> str:
        """Render widget HTML."""
        pass


class CommandPlugin(AMOSPlugin):
    """Plugin for adding custom REPL commands."""

    @abstractmethod
    def get_command(self) -> str:
        """Return command name."""
        pass

    @abstractmethod
    def execute(self, args: str) -> str:
        """Execute command with args."""
        pass


class PluginManager:
    """Manages AMOS plugins."""

    PLUGIN_DIR = Path("amos_plugins")

    def __init__(self):
        self.plugins: dict[str, AMOSPlugin] = {}
        self.hooks: dict[str, list[Callable]] = {}
        self._ensure_plugin_dir()

    def _ensure_plugin_dir(self) -> None:
        """Ensure plugin directory exists."""
        if not self.PLUGIN_DIR.exists():
            self.PLUGIN_DIR.mkdir(parents=True)
            # Create example plugin
            self._create_example_plugin()

    def _create_example_plugin(self) -> None:
        """Create an example plugin."""
        example_dir = self.PLUGIN_DIR / "example_plugin"
        example_dir.mkdir(exist_ok=True)

        plugin_code = '''"""Example AMOS Plugin."""
from amos_brain.plugin_system import CommandPlugin, PluginMetadata
from typing import Callable, List, Any
from typing import Any, Callable, List

class HelloPlugin(CommandPlugin):
    """Example hello world plugin."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="hello",
            version="1.0.0",
            author="AMOS Team",
            description="Example hello plugin",
            hooks=["command"],
            dependencies=[]
        )

    def initialize(self, context: dict) -> bool:
        print("Hello plugin initialized!")
        return True

    def shutdown(self) -> None:
        print("Hello plugin shutdown.")

    def get_command(self) -> str:
        return "/hello"

    def execute(self, args: str) -> str:
        return f"Hello {args or 'World'} from AMOS Plugin!"

# Plugin entry point
def create_plugin():
    return HelloPlugin()
'''
        (example_dir / "__init__.py").write_text(plugin_code)

        manifest = {
            "name": "example_plugin",
            "version": "1.0.0",
            "entry_point": "example_plugin:create_plugin",
        }
        (example_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))

    def discover_plugins(self) -> list[Path]:
        """Discover available plugins."""
        plugins = []
        if self.PLUGIN_DIR.exists():
            for plugin_dir in self.PLUGIN_DIR.iterdir():
                if plugin_dir.is_dir() and (plugin_dir / "manifest.json").exists():
                    plugins.append(plugin_dir)
        return plugins

    def load_plugin(self, plugin_path: Path) -> AMOSPlugin | None:
        """Load a plugin from directory."""
        try:
            manifest_path = plugin_path / "manifest.json"
            with open(manifest_path) as f:
                manifest = json.load(f)

            # Add to path
            sys.path.insert(0, str(plugin_path.parent))

            # Import module
            module_name = manifest["entry_point"].split(":")[0]
            module = importlib.import_module(f"{plugin_path.name}.{module_name}")

            # Create plugin instance
            factory_name = manifest["entry_point"].split(":")[1]
            factory = getattr(module, factory_name)
            plugin = factory()

            return plugin

        except Exception as e:
            print(f"[PluginManager] Failed to load {plugin_path}: {e}")
            return None

    def load_all_plugins(self) -> int:
        """Load all discovered plugins."""
        discovered = self.discover_plugins()
        loaded = 0

        for plugin_path in discovered:
            plugin = self.load_plugin(plugin_path)
            if plugin:
                if plugin.initialize({}):
                    self.plugins[plugin.metadata.name] = plugin
                    self._register_hooks(plugin)
                    loaded += 1
                    print(f"[PluginManager] Loaded: {plugin.metadata.name}")
                else:
                    print(f"[PluginManager] Init failed: {plugin_path.name}")

        return loaded

    def _register_hooks(self, plugin: AMOSPlugin) -> None:
        """Register plugin hooks."""
        for hook in plugin.metadata.hooks:
            if hook not in self.hooks:
                self.hooks[hook] = []
            # Add hook handler
            if hasattr(plugin, "on_" + hook):
                self.hooks[hook].append(getattr(plugin, "on_" + hook))

    def execute_hook(self, hook_name: str, *args, **kwargs) -> list[Any]:
        """Execute all handlers for a hook."""
        results = []
        for handler in self.hooks.get(hook_name, []):
            try:
                result = handler(*args, **kwargs)
                results.append(result)
            except Exception as e:
                print(f"[PluginManager] Hook error: {e}")
        return results

    def get_plugin(self, name: str) -> AMOSPlugin | None:
        """Get a loaded plugin by name."""
        return self.plugins.get(name)

    def list_plugins(self) -> list[PluginMetadata]:
        """List all loaded plugins."""
        return [p.metadata for p in self.plugins.values()]

    def unload_plugin(self, name: str) -> bool:
        """Unload a plugin."""
        if name in self.plugins:
            self.plugins[name].shutdown()
            del self.plugins[name]
            return True
        return False

    def unload_all(self) -> None:
        """Unload all plugins."""
        for plugin in self.plugins.values():
            plugin.shutdown()
        self.plugins.clear()
        self.hooks.clear()


def get_plugin_manager() -> PluginManager:
    """Get or create global plugin manager."""
    if not hasattr(get_plugin_manager, "_instance"):
        get_plugin_manager._instance = PluginManager()
    return get_plugin_manager._instance


def main():
    """Demo plugin system."""
    print("=" * 70)
    print("AMOS ECOSYSTEM v2.1 - PLUGIN SYSTEM DEMO")
    print("=" * 70)

    manager = get_plugin_manager()

    # Load all plugins
    loaded = manager.load_all_plugins()
    print(f"\nLoaded {loaded} plugins")

    # List plugins
    print("\nInstalled Plugins:")
    for meta in manager.list_plugins():
        print(f"  - {meta.name} v{meta.version}: {meta.description}")

    # Execute example command
    hello_plugin = manager.get_plugin("hello")
    if hello_plugin and hasattr(hello_plugin, "execute"):
        result = hello_plugin.execute("AMOS User")
        print(f"\nCommand /hello result: {result}")

    print("\n" + "=" * 70)
    print("Plugin system ready for extension development!")
    print("=" * 70)

    # Cleanup
    manager.unload_all()
    return 0


if __name__ == "__main__":
    sys.exit(main())
