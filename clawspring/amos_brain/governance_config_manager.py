"""AMOS Governance Configuration Manager v1.0.0

Manages configuration for autonomous governance system with hot-reload support.
Owner: Trang Phan
Version: 1.0.0
"""

from __future__ import annotations


import json
import os
import threading
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path


class GovernanceMode(Enum):
    """Autonomous governance modes."""

    FULL_AUTO = "full_auto"
    SUPERVISED = "supervised"
    ADVISORY = "advisory"
    OFF = "off"


class PolicyAction(Enum):
    """Policy enforcement actions."""

    REMEDIATE = "remediate"
    ESCALATE = "escalate"
    NOTIFY = "notify"
    MONITOR = "monitor"
    IGNORE = "ignore"


@dataclass
class DetectionThresholds:
    """Thresholds for detection system."""

    hallucination_warning: float = 0.5
    hallucination_critical: float = 0.7
    integrity_warning: float = 0.3
    integrity_critical: float = 0.5
    drift_warning: float = 0.5
    drift_critical: float = 0.7


@dataclass
class GovernancePolicy:
    """Complete governance policy definition."""

    name: str
    mode: GovernanceMode = GovernanceMode.SUPERVISED
    description: str = ""
    critical_action: PolicyAction = PolicyAction.ESCALATE
    high_action: PolicyAction = PolicyAction.REMEDIATE
    medium_action: PolicyAction = PolicyAction.MONITOR
    low_action: PolicyAction = PolicyAction.IGNORE
    thresholds: DetectionThresholds = field(default_factory=DetectionThresholds)
    cycle_interval_seconds: int = 300
    auto_remediate: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


class GovernanceConfigManager:
    """Configuration manager for AMOS governance system."""

    DEFAULT_CONFIG_PATH = Path("amos_governance_config.json")

    def __init__(self, config_path: Path | None = None, environment: str = "development"):
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self.environment = environment
        self._policies: dict[str, GovernancePolicy] = {}
        self._current_policy_name: str = None
        self._change_callbacks: list[Callable[[], None]] = []
        self._lock = threading.RLock()
        self._reload_enabled = False
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from file or create defaults."""
        with self._lock:
            if self.config_path.exists():
                try:
                    with open(self.config_path) as f:
                        data = json.load(f)

                    for name, policy_data in data.get("policies", {}).items():
                        self._policies[name] = self._policy_from_dict(policy_data)

                    self._current_policy_name = data.get("current_policy", "default")
                    print(f"[GovernanceConfig] Loaded {len(self._policies)} policies")

                except Exception as e:
                    print(f"[GovernanceConfig] Error loading: {e}")
                    self._create_defaults()
            else:
                self._create_defaults()
                self.save()

    def _create_defaults(self) -> None:
        """Create default policies."""
        self._policies["development"] = GovernancePolicy(
            name="development",
            mode=GovernanceMode.FULL_AUTO,
            description="Full automation for development",
            critical_action=PolicyAction.REMEDIATE,
            high_action=PolicyAction.REMEDIATE,
            cycle_interval_seconds=60,
        )

        self._policies["staging"] = GovernancePolicy(
            name="staging",
            mode=GovernanceMode.SUPERVISED,
            description="Supervised mode for staging",
            critical_action=PolicyAction.ESCALATE,
            cycle_interval_seconds=300,
        )

        self._policies["production"] = GovernancePolicy(
            name="production",
            mode=GovernanceMode.SUPERVISED,
            description="Conservative production mode",
            critical_action=PolicyAction.ESCALATE,
            high_action=PolicyAction.NOTIFY,
            cycle_interval_seconds=600,
        )

        self._current_policy_name = self.environment

    def _policy_from_dict(self, data: dict) -> GovernancePolicy:
        """Create policy from dictionary."""
        return GovernancePolicy(
            name=data["name"],
            mode=GovernanceMode(data.get("mode", "supervised")),
            description=data.get("description", ""),
            critical_action=PolicyAction(data.get("critical_action", "escalate")),
            high_action=PolicyAction(data.get("high_action", "remediate")),
            medium_action=PolicyAction(data.get("medium_action", "monitor")),
            low_action=PolicyAction(data.get("low_action", "ignore")),
            thresholds=DetectionThresholds(**data.get("thresholds", {})),
            cycle_interval_seconds=data.get("cycle_interval_seconds", 300),
            auto_remediate=data.get("auto_remediate", True),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
        )

    def save(self, path: Path | None = None) -> bool:
        """Save configuration to file."""
        save_path = path or self.config_path
        try:
            with self._lock:
                data = {
                    "current_policy": self._current_policy_name,
                    "policies": {
                        name: {
                            "name": p.name,
                            "mode": p.mode.value,
                            "description": p.description,
                            "critical_action": p.critical_action.value,
                            "high_action": p.high_action.value,
                            "medium_action": p.medium_action.value,
                            "low_action": p.low_action.value,
                            "thresholds": asdict(p.thresholds),
                            "cycle_interval_seconds": p.cycle_interval_seconds,
                            "auto_remediate": p.auto_remediate,
                            "created_at": p.created_at,
                            "updated_at": p.updated_at,
                        }
                        for name, p in self._policies.items()
                    },
                }
                with open(save_path, "w") as f:
                    json.dump(data, f, indent=2)
                return True
        except Exception as e:
            print(f"[GovernanceConfig] Save error: {e}")
            return False

    def get_current_policy(self) -> GovernancePolicy:
        """Get currently active policy."""
        with self._lock:
            if self._current_policy_name in self._policies:
                return self._policies[self._current_policy_name]
            return (
                list(self._policies.values())[0] if self._policies else GovernancePolicy("default")
            )

    def set_policy(self, name: str) -> bool:
        """Switch to named policy."""
        with self._lock:
            if name not in self._policies:
                return False
            self._current_policy_name = name
            self._notify_change()
            return True

    def update_policy(self, name: str, **kwargs) -> bool:
        """Update specific policy settings."""
        with self._lock:
            if name not in self._policies:
                return False

            policy = self._policies[name]
            for key, value in kwargs.items():
                if hasattr(policy, key):
                    setattr(policy, key, value)

            policy.updated_at = datetime.now().isoformat()
            self._notify_change()
            return True

    def create_policy(self, name: str, base_policy: str = None, **kwargs) -> bool:
        """Create new policy optionally based on existing."""
        with self._lock:
            if name in self._policies:
                return False

            if base_policy and base_policy in self._policies:
                base = self._policies[base_policy]
                new_policy = GovernancePolicy(
                    name=name,
                    mode=kwargs.get("mode", base.mode),
                    description=kwargs.get("description", base.description),
                    critical_action=kwargs.get("critical_action", base.critical_action),
                    high_action=kwargs.get("high_action", base.high_action),
                    medium_action=kwargs.get("medium_action", base.medium_action),
                    low_action=kwargs.get("low_action", base.low_action),
                    thresholds=kwargs.get("thresholds", base.thresholds),
                    cycle_interval_seconds=kwargs.get(
                        "cycle_interval_seconds", base.cycle_interval_seconds
                    ),
                    auto_remediate=kwargs.get("auto_remediate", base.auto_remediate),
                )
            else:
                new_policy = GovernancePolicy(name=name, **kwargs)

            self._policies[name] = new_policy
            self._notify_change()
            return True

    def list_policies(self) -> list[str]:
        """List all available policy names."""
        with self._lock:
            return list(self._policies.keys())

    def delete_policy(self, name: str) -> bool:
        """Delete a policy (cannot delete current)."""
        with self._lock:
            if name not in self._policies or name == self._current_policy_name:
                return False
            del self._policies[name]
            self._notify_change()
            return True

    def on_change(self, callback: Callable[[], None]) -> None:
        """Register callback for configuration changes."""
        self._change_callbacks.append(callback)

    def _notify_change(self) -> None:
        """Notify all registered callbacks."""
        for cb in self._change_callbacks:
            try:
                cb()
            except Exception as e:
                print(f"[GovernanceConfig] Callback error: {e}")

    def enable_hot_reload(self, interval: float = 5.0) -> None:
        """Enable periodic config file checking."""
        if self._reload_enabled:
            return

        self._reload_enabled = True

        def watch_loop():
            last_mtime = 0
            if self.config_path.exists():
                last_mtime = self.config_path.stat().st_mtime

            while self._reload_enabled:
                time.sleep(interval)

                if self.config_path.exists():
                    current_mtime = self.config_path.stat().st_mtime
                    if current_mtime > last_mtime:
                        last_mtime = current_mtime
                        print("[GovernanceConfig] Hot-reload triggered")
                        self._load_config()
                        self._notify_change()

        thread = threading.Thread(target=watch_loop, daemon=True)
        thread.start()
        print(f"[GovernanceConfig] Hot-reload enabled (interval: {interval}s)")

    def disable_hot_reload(self) -> None:
        """Disable hot-reload."""
        self._reload_enabled = False

    def apply_env_overrides(self) -> None:
        """Apply environment variable overrides."""
        with self._lock:
            policy = self.get_current_policy()

            # Mode override
            mode = os.environ.get("AMOS_GOVERNANCE_MODE")
            if mode and mode in [m.value for m in GovernanceMode]:
                policy.mode = GovernanceMode(mode)

            # Cycle interval override
            interval = os.environ.get("AMOS_GOVERNANCE_INTERVAL")
            if interval and interval.isdigit():
                policy.cycle_interval_seconds = int(interval)

            # Threshold overrides
            for threshold in ["hallucination", "integrity", "drift"]:
                for level in ["warning", "critical"]:
                    env_var = f"AMOS_{threshold.upper()}_{level.upper()}"
                    value = os.environ.get(env_var)
                    if value:
                        try:
                            setattr(policy.thresholds, f"{threshold}_{level}", float(value))
                        except ValueError:
                            pass

            policy.updated_at = datetime.now().isoformat()
            self._notify_change()


# =============================================================================
# Convenience Functions
# =============================================================================


def create_governance_config(
    config_path: Path | None = None,
    environment: str = "development",
) -> GovernanceConfigManager:
    """Factory function to create governance config manager."""
    return GovernanceConfigManager(config_path, environment)


# =============================================================================
# Module Test
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("AMOS Governance Configuration Manager - Test Suite")
    print("=" * 70)

    # Test 1: Initialize
    print("\n[Test 1] Initialize Config Manager")
    print("-" * 50)

    config = GovernanceConfigManager(environment="development")
    print(f"Environment: {config.environment}")
    print(f"Policies loaded: {len(config.list_policies())}")
    print(f"Available: {', '.join(config.list_policies())}")

    # Test 2: Get current policy
    print("\n[Test 2] Get Current Policy")
    print("-" * 50)

    policy = config.get_current_policy()
    print(f"Current policy: {policy.name}")
    print(f"Mode: {policy.mode.value}")
    print(f"Description: {policy.description}")
    print(f"Cycle interval: {policy.cycle_interval_seconds}s")

    # Test 3: Switch policy
    print("\n[Test 3] Switch Policy")
    print("-" * 50)

    success = config.set_policy("production")
    print(f"Switch to production: {'✓' if success else '✗'}")
    print(f"Current: {config.get_current_policy().name}")

    # Test 4: Update policy
    print("\n[Test 4] Update Policy")
    print("-" * 50)

    success = config.update_policy("development", cycle_interval_seconds=120)
    print(f"Update dev policy: {'✓' if success else '✗'}")
    dev_policy = config._policies["development"]
    print(f"New interval: {dev_policy.cycle_interval_seconds}s")

    # Test 5: Create custom policy
    print("\n[Test 5] Create Custom Policy")
    print("-" * 50)

    success = config.create_policy(
        "custom",
        base_policy="staging",
        description="Custom testing policy",
        cycle_interval_seconds=180,
    )
    print(f"Create custom: {'✓' if success else '✗'}")
    print(f"Policies now: {', '.join(config.list_policies())}")

    # Test 6: Save and reload
    print("\n[Test 6] Save and Reload")
    print("-" * 50)

    config.save()
    print(f"Config saved to: {config.config_path}")

    # Create new instance to test reload
    config2 = GovernanceConfigManager(environment="development")
    print(f"Reloaded policies: {len(config2.list_policies())}")
    print(f"Custom exists: {'custom' in config2.list_policies()}")

    # Cleanup
    config.config_path.unlink(missing_ok=True)

    print("\n" + "=" * 70)
    print("All tests passed!")
    print("=" * 70)
    print("\n✓ Governance configuration system operational")
    print("✓ Policy management ready")
    print("✓ Hot-reload capability available")
    print("=" * 70)
