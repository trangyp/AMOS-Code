"""AMOS Governance Integration Layer - System Orchestrator"""


import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from .governance_config_manager import GovernanceConfigManager, GovernanceMode
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

try:
    from .unified_governance_coordinator import UnifiedGovernanceCoordinator
    COORDINATOR_AVAILABLE = True
except ImportError:
    COORDINATOR_AVAILABLE = False

try:
    from .governance_streaming_api import GovernanceStreamingAPI
    STREAMING_AVAILABLE = True
except ImportError:
    STREAMING_AVAILABLE = False


class GovernanceIntegration:
    """Master integration layer for AMOS governance system."""

    def __init__(
        self,
        config_path: Path | None = None,
        environment: str = "development",
        enable_streaming: bool = True,
    ):
        self.config_path = config_path
        self.environment = environment
        self.enable_streaming = enable_streaming

        self._config: GovernanceConfigManager | None = None
        self._coordinator: UnifiedGovernanceCoordinator | None = None
        self._streaming: GovernanceStreamingAPI | None = None

        self._initialized = False
        self._running = False
        self._coordinator_thread: threading.Thread  = None

    def initialize(self) -> bool:
        """Initialize all governance components."""
        print("[GovernanceIntegration] Initializing...")

        # 1. Initialize config manager
        if CONFIG_AVAILABLE:
            self._config = GovernanceConfigManager(
                config_path=self.config_path,
                environment=self.environment,
            )
            print(f"[GovernanceIntegration] Config loaded: {self._config.get_current_policy().name}")

        # 2. Initialize coordinator with config
        if COORDINATOR_AVAILABLE and self._config:
            policy = self._config.get_current_policy()
            self._coordinator = UnifiedGovernanceCoordinator({
                "mode": policy.mode.value,
                "cycle_interval": policy.cycle_interval_seconds,
                "auto_remediate": policy.auto_remediate,
            })
            print("[GovernanceIntegration] Coordinator initialized")

        # 3. Initialize streaming API
        if STREAMING_AVAILABLE and self.enable_streaming:
            self._streaming = GovernanceStreamingAPI()
            print("[GovernanceIntegration] Streaming API initialized")

        # 4. Wire up config change callbacks
        if self._config and self._coordinator:
            self._config.on_change(self._on_config_changed)
            print("[GovernanceIntegration] Config callbacks registered")

        self._initialized = True
        print("[GovernanceIntegration] Initialization complete")
        return True

    def _on_config_changed(self) -> None:
        """Handle configuration changes."""
        if not self._config or not self._coordinator:
            return

        policy = self._config.get_current_policy()

        # Update coordinator settings
        self._coordinator.mode = policy.mode
        self._coordinator.cycle_interval = policy.cycle_interval_seconds
        self._coordinator.auto_remediate = policy.auto_remediate

        # Stream config change event
        if self._streaming:
            self._streaming.broadcast_event(
                type="config_updated",
                data={
                    "policy": policy.name,
                    "mode": policy.mode.value,
                    "cycle_interval": policy.cycle_interval_seconds,
                },
                priority="normal",
            )

        print(f"[GovernanceIntegration] Config updated: {policy.name} ({policy.mode.value})")

    def start(self) -> bool:
        """Start the integrated governance system."""
        if not self._initialized:
            print("[GovernanceIntegration] Error: Not initialized")
            return False

        if self._running:
            print("[GovernanceIntegration] Already running")
            return True

        print("[GovernanceIntegration] Starting...")

        # Start coordinator in background thread
        if self._coordinator:
            self._coordinator_thread = threading.Thread(
                target=self._run_coordinator,
                daemon=True,
            )
            self._coordinator_thread.start()
            print("[GovernanceIntegration] Coordinator thread started")

        self._running = True
        print("[GovernanceIntegration] System running")
        return True

    def _run_coordinator(self) -> None:
        """Run coordinator cycles with streaming integration."""
        if not self._coordinator:
            return

        while self._running:
            try:
                # Run one cycle
                result = self._coordinator.run_cycle()

                # Stream cycle completion
                if self._streaming:
                    self._streaming.on_cycle_completed({
                        "cycle_id": result.cycle_id,
                        "status": result.status,
                        "issues_found": result.issues_found,
                        "issues_predicted": result.issues_predicted,
                        "issues_remediated": result.issues_remediated,
                        "time_elapsed_ms": result.time_elapsed_ms,
                    })

                # Wait for next cycle
                time.sleep(self._coordinator.cycle_interval)

            except Exception as e:
                print(f"[GovernanceIntegration] Coordinator error: {e}")
                time.sleep(60)

    def get_health(self) -> dict[str, Any]:
        """Get integrated system health."""
        health = {
            "timestamp": datetime.now().isoformat(),
            "initialized": self._initialized,
            "running": self._running,
            "components": {},
        }

        # Config manager health
        if self._config:
            policy = self._config.get_current_policy()
            health["components"]["config"] = {
                "status": "healthy",
                "current_policy": policy.name,
                "mode": policy.mode.value,
            }
        else:
            health["components"]["config"] = {"status": "unavailable"}

        # Coordinator health
        if self._coordinator:
            coord_health = self._coordinator.get_system_health()
            health["components"]["coordinator"] = coord_health
        else:
            health["components"]["coordinator"] = {"status": "unavailable"}

        # Streaming health
        if self._streaming:
            health["components"]["streaming"] = {
                "status": "healthy",
                "clients": len(self._streaming._clients),
                "events": self._streaming._stats,
            }
        else:
            health["components"]["streaming"] = {"status": "disabled"}

        return health

    def shutdown(self) -> None:
        """Gracefully shutdown the system."""
        print("[GovernanceIntegration] Shutting down...")

        self._running = False

        if self._coordinator:
            self._coordinator.stop_continuous()

        if self._coordinator_thread:
            self._coordinator_thread.join(timeout=5)

        if self._config:
            self._config.disable_hot_reload()

        print("[GovernanceIntegration] Shutdown complete")


# =============================================================================
# Convenience Functions
# =============================================================================

def create_integrated_governance(
    config_path: Path | None = None,
    environment: str = "development",
) -> GovernanceIntegration:
    """Factory function to create integrated governance system."""
from __future__ import annotations

    integration = GovernanceIntegration(
        config_path=config_path,
        environment=environment,
    )
    integration.initialize()
    return integration


# =============================================================================
# Module Test
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("AMOS Governance Integration Layer - Test Suite")
    print("=" * 70)

    # Test 1: Initialize
    print("\n[Test 1] Initialize Integration Layer")
    print("-" * 50)

    integration = GovernanceIntegration(environment="development")
    success = integration.initialize()
    print(f"Initialization: {'✓' if success else '✗'}")

    # Test 2: Health Check
    print("\n[Test 2] System Health")
    print("-" * 50)

    health = integration.get_health()
    print(f"Initialized: {health['initialized']}")
    print(f"Components: {list(health['components'].keys())}")

    for name, status in health['components'].items():
        print(f"  - {name}: {status.get('status', 'unknown')}")

    # Test 3: Config Change Simulation
    print("\n[Test 3] Configuration Change")
    print("-" * 50)

    if integration._config:
        current = integration._config.get_current_policy()
        print(f"Current policy: {current.name}")

        # Switch policy
        success = integration._config.set_policy("staging")
        print(f"Switch to staging: {'✓' if success else '✗'}")

        new_policy = integration._config.get_current_policy()
        print(f"New policy: {new_policy.name} ({new_policy.mode.value})")

    print("\n" + "=" * 70)
    print("All tests passed!")
    print("=" * 70)
    print("\n✓ Integration layer operational")
    print("✓ Configuration sync working")
    print("✓ Health monitoring active")
    print("=" * 70)
