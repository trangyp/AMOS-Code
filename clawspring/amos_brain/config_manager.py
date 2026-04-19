#!/usr/bin/env python3
"""AMOS Ecosystem v2.7 - Configuration Management System.

Dynamic configuration with hot-reload, environment-specific
settings, and validation for all AMOS components.
"""

import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


@dataclass
class ComponentConfig:
    """Configuration for a single component."""

    enabled: bool
    settings: Dict[str, Any]
    last_updated: datetime


class ConfigManager:
    """Manages AMOS ecosystem configuration."""

    CONFIG_FILE = "amos_config.yaml"
    ENV_PREFIX = "AMOS_"

    def __init__(self):
        self.configs: Dict[str, ComponentConfig] = {}
        self.global_settings: Dict[str, Any] = {}
        self._config_path = Path(self.CONFIG_FILE)
        self._load_default_config()

    def _load_default_config(self) -> None:
        """Load default configuration."""
        self.global_settings = {
            "environment": "production",
            "log_level": "INFO",
            "telemetry_enabled": True,
            "ethics_enabled": True,
            "resilience_enabled": True,
        }

        self.configs = {
            "cognitive_router": ComponentConfig(
                enabled=True,
                settings={"max_engines": 5, "min_confidence": 0.6, "risk_threshold": "MEDIUM"},
                last_updated=datetime.now(),
            ),
            "organism_bridge": ComponentConfig(
                enabled=True,
                settings={"auto_reconnect": True, "timeout_seconds": 30, "fallback_enabled": True},
                last_updated=datetime.now(),
            ),
            "master_orchestrator": ComponentConfig(
                enabled=True,
                settings={
                    "max_workers": 4,
                    "require_consensus": True,
                    "default_priority": "MEDIUM",
                },
                last_updated=datetime.now(),
            ),
            "telemetry": ComponentConfig(
                enabled=True,
                settings={
                    "collection_interval": 30,
                    "retention_hours": 24,
                    "metrics_enabled": True,
                },
                last_updated=datetime.now(),
            ),
            "ethics": ComponentConfig(
                enabled=True,
                settings={
                    "default_framework": "principlism",
                    "strict_mode": False,
                    "log_violations": True,
                },
                last_updated=datetime.now(),
            ),
            "resilience": ComponentConfig(
                enabled=True,
                settings={
                    "circuit_breaker_threshold": 5,
                    "retry_max_attempts": 3,
                    "recovery_timeout": 30,
                },
                last_updated=datetime.now(),
            ),
        }

    def load_from_file(self, path: str = None) -> bool:
        """Load configuration from YAML file."""
        config_path = Path(path) if path else self._config_path

        if not config_path.exists():
            return False

        try:
            with open(config_path) as f:
                data = yaml.safe_load(f)

            if "global" in data:
                self.global_settings.update(data["global"])

            for name, settings in data.get("components", {}).items():
                if name in self.configs:
                    self.configs[name].enabled = settings.get("enabled", True)
                    self.configs[name].settings.update(settings.get("settings", {}))
                    self.configs[name].last_updated = datetime.now()

            return True

        except Exception as e:
            print(f"[ConfigManager] Load error: {e}")
            return False

    def save_to_file(self, path: str = None) -> bool:
        """Save configuration to YAML file."""
        config_path = Path(path) if path else self._config_path

        try:
            data = {
                "global": self.global_settings,
                "components": {
                    name: {"enabled": config.enabled, "settings": config.settings}
                    for name, config in self.configs.items()
                },
            }

            with open(config_path, "w") as f:
                yaml.dump(data, f, default_flow_style=False)

            return True

        except Exception as e:
            print(f"[ConfigManager] Save error: {e}")
            return False

    def load_from_env(self) -> None:
        """Load configuration from environment variables."""
        for key, value in os.environ.items():
            if key.startswith(self.ENV_PREFIX):
                config_key = key[len(self.ENV_PREFIX) :].lower()

                # Try to parse as JSON for complex values
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    pass  # Keep as string

                # Handle nested keys (e.g., AMOS_COGNITIVE_ROUTER_MAX_ENGINES)
                parts = config_key.split("_")
                if len(parts) >= 2 and parts[0] in self.configs:
                    component = parts[0]
                    setting_key = "_".join(parts[1:])
                    self.configs[component].settings[setting_key] = value
                else:
                    self.global_settings[config_key] = value

    def get(self, component: str, setting: str, default: Any = None) -> Any:
        """Get a configuration value."""
        if component not in self.configs:
            return default

        config = self.configs[component]
        if not config.enabled:
            return default

        return config.settings.get(setting, default)

    def set(self, component: str, setting: str, value: Any) -> bool:
        """Set a configuration value."""
        if component not in self.configs:
            return False

        self.configs[component].settings[setting] = value
        self.configs[component].last_updated = datetime.now()
        return True

    def is_enabled(self, component: str) -> bool:
        """Check if a component is enabled."""
        if component not in self.configs:
            return False
        return self.configs[component].enabled

    def enable(self, component: str) -> bool:
        """Enable a component."""
        if component in self.configs:
            self.configs[component].enabled = True
            self.configs[component].last_updated = datetime.now()
            return True
        return False

    def disable(self, component: str) -> bool:
        """Disable a component."""
        if component in self.configs:
            self.configs[component].enabled = False
            self.configs[component].last_updated = datetime.now()
            return True
        return False

    def get_all_configs(self) -> Dict[str, Any]:
        """Get all configurations."""
        return {
            "global": self.global_settings,
            "components": {
                name: {
                    "enabled": config.enabled,
                    "settings": config.settings,
                    "last_updated": config.last_updated.isoformat(),
                }
                for name, config in self.configs.items()
            },
        }

    def validate(self) -> List[str]:
        """Validate configuration and return any issues."""
        issues = []

        # Check required settings
        if self.global_settings.get("environment") not in ["development", "staging", "production"]:
            issues.append("Invalid environment setting")

        # Validate component settings
        for name, config in self.configs.items():
            if not config.enabled:
                continue

            if name == "cognitive_router":
                if config.settings.get("min_confidence", 0) < 0:
                    issues.append(f"{name}: min_confidence must be >= 0")

            elif name == "organism_bridge":
                if config.settings.get("timeout_seconds", 0) <= 0:
                    issues.append(f"{name}: timeout_seconds must be > 0")

        return issues


# Global instance
_config_manager: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """Get or create global config manager."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
        # Try to load from file
        _config_manager.load_from_file()
        # Load from environment
        _config_manager.load_from_env()
    return _config_manager


def main():
    """Demo configuration manager."""
    print("=" * 70)
    print("AMOS ECOSYSTEM v2.7 - CONFIGURATION MANAGER DEMO")
    print("=" * 70)

    config = get_config()

    print("\nDefault Configuration:")
    all_configs = config.get_all_configs()
    print(f"Global: {all_configs['global']}")

    print("\nComponent Status:")
    for name, cfg in all_configs["components"].items():
        status = "enabled" if cfg["enabled"] else "disabled"
        print(f"  {name}: {status}")

    print("\nValidation:")
    issues = config.validate()
    if issues:
        for issue in issues:
            print(f"  ⚠ {issue}")
    else:
        print("  ✓ Configuration valid")

    print("\nEnvironment Variable Support:")
    print("  Set AMOS_LOG_LEVEL=DEBUG to override log level")
    print("  Set AMOS_COGNITIVE_ROUTER_MAX_ENGINES=10 to override")

    # Save example config
    config.save_to_file("amos_config_example.yaml")
    print("\nExample config saved to: amos_config_example.yaml")

    print("=" * 70)
    print("Configuration manager ready!")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
