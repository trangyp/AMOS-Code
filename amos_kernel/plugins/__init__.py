"""Plugins - Extensible plugin system for kernel"""

from .registry import (
    KernelPlugin,
    MetricsPlugin,
    PluginInfo,
    PluginRegistry,
    get_plugin_registry,
)

__all__ = [
    "PluginRegistry",
    "KernelPlugin",
    "PluginInfo",
    "get_plugin_registry",
    "MetricsPlugin",
]
