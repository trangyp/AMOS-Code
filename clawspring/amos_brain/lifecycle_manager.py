#!/usr/bin/env python3
"""AMOS Ecosystem v2.0 - Production Lifecycle Manager.

Handles graceful startup, shutdown, and signal management for
production deployments. Ensures clean resource cleanup and
state persistence during termination.
"""


import atexit
import json
import signal
import sys
import threading
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class LifecycleState:
    """Current lifecycle state."""

    status: str  # "starting", "running", "stopping", "stopped"
    start_time: datetime
    stop_time: datetime = None
    shutdown_reason: str = None
    cleanup_tasks_completed: int = 0
    cleanup_tasks_total: int = 0


class LifecycleManager:
    """Manages application lifecycle for production deployments."""

    def __init__(self, app_name: str = "amos-ecosystem"):
        self.app_name = app_name
        self.state = LifecycleState(status="starting", start_time=datetime.now())
        self._cleanup_handlers: List[Callable[[], None]] = []
        self._shutdown_event = threading.Event()
        self._lock = threading.Lock()
        self._state_file = Path(f".amos_lifecycle_{app_name}.json")

        # Register signal handlers
        self._setup_signal_handlers()

        # Register atexit handler
        atexit.register(self._atexit_cleanup)

    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""
        signals = [
            (signal.SIGTERM, "SIGTERM"),
            (signal.SIGINT, "SIGINT"),
            (signal.SIGHUP, "SIGHUP"),
        ]

        for sig, name in signals:
            try:
                signal.signal(sig, self._signal_handler)
                print(f"[Lifecycle] Registered handler for {name}")
            except ValueError:
                pass

    def _signal_handler(self, signum: int, frame: Any) -> None:
        """Handle shutdown signals."""
        signal_names = {
            signal.SIGTERM: "SIGTERM",
            signal.SIGINT: "SIGINT",
            signal.SIGHUP: "SIGHUP",
        }
        name = signal_names.get(signum, "Signal " + str(signum))
        print(f"\n[Lifecycle] Received {name}, starting shutdown...")
        self.shutdown(f"Received {name}")

    def register_cleanup_handler(self, handler: Callable[[], None]) -> None:
        """Register a cleanup handler to run on shutdown."""
        with self._lock:
            self._cleanup_handlers.append(handler)
            self.state.cleanup_tasks_total = len(self._cleanup_handlers)

    def _run_cleanup_handlers(self) -> None:
        """Execute all registered cleanup handlers."""
        print(f"[Lifecycle] Running {len(self._cleanup_handlers)} cleanup handlers...")

        for i, handler in enumerate(self._cleanup_handlers, 1):
            try:
                handler()
                with self._lock:
                    self.state.cleanup_tasks_completed = i
                total = len(self._cleanup_handlers)
                print(f"  Handler {i}/{total} completed")
            except Exception as e:
                total = len(self._cleanup_handlers)
                print(f"  Handler {i}/{total} failed: {e}")

    def _atexit_cleanup(self) -> None:
        """Cleanup handler for atexit."""
        if self.state.status != "stopped":
            self._run_cleanup_handlers()
            self._save_state()

    def _save_state(self) -> None:
        """Save lifecycle state to file."""
        stop_time = None
        if self.state.stop_time:
            stop_time = self.state.stop_time.isoformat()
        data = {
            "app_name": self.app_name,
            "status": self.state.status,
            "start_time": self.state.start_time.isoformat(),
            "stop_time": stop_time,
            "shutdown_reason": self.state.shutdown_reason,
            "cleanup_completed": self.state.cleanup_tasks_completed,
            "cleanup_total": self.state.cleanup_tasks_total,
        }

        try:
            with open(self._state_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[Lifecycle] Failed to save state: {e}")

    def startup(self) -> bool:
        """Execute startup sequence."""
        print(f"[Lifecycle] {self.app_name} starting up...")

        # Check for previous crash
        if self._state_file.exists():
            try:
                with open(self._state_file) as f:
                    prev_state = json.load(f)
                if prev_state.get("status") == "running":
                    print("[Lifecycle] Warning: Previous session did not shut down cleanly")
            except Exception:
                pass

        with self._lock:
            self.state.status = "running"

        self._save_state()
        print(f"[Lifecycle] {self.app_name} is now running")
        return True

    def shutdown(self, reason: str = "Requested") -> None:
        """Initiate graceful shutdown."""
        with self._lock:
            if self.state.status in ("stopping", "stopped"):
                return
            self.state.status = "stopping"
            self.state.shutdown_reason = reason

        print(f"[Lifecycle] Shutdown: {reason}")

        # Run cleanup handlers
        self._run_cleanup_handlers()

        # Update state
        with self._lock:
            self.state.status = "stopped"
            self.state.stop_time = datetime.now()

        self._save_state()
        self._shutdown_event.set()
        print(f"[Lifecycle] {self.app_name} stopped")

    def wait_for_shutdown(self, timeout: float = None) -> bool:
        """Wait for shutdown signal."""
        return self._shutdown_event.wait(timeout)

    def is_running(self) -> bool:
        """Check if application is running."""
        with self._lock:
            return self.state.status == "running"

    def get_status(self) -> Dict[str, Any]:
        """Get current lifecycle status."""
        with self._lock:
            uptime = None
            if self.state.status == "running":
                uptime = (datetime.now() - self.state.start_time).total_seconds()

            return {
                "app_name": self.app_name,
                "status": self.state.status,
                "start_time": self.state.start_time.isoformat(),
                "uptime_seconds": uptime,
                "shutdown_reason": self.state.shutdown_reason,
                "cleanup_completed": self.state.cleanup_tasks_completed,
                "cleanup_total": self.state.cleanup_tasks_total,
            }

    def print_status(self) -> None:
        """Print lifecycle status."""
        status = self.get_status()
        print("\n" + "=" * 50)
        print("AMOS ECOSYSTEM - LIFECYCLE STATUS")
        print("=" * 50)
        print(f"Application: {status['app_name']}")
        print(f"Status: {status['status']}")
        print(f"Started: {status['start_time']}")
        uptime = status.get("uptime_seconds")
        if uptime:
            hours = int(uptime // 3600)
            mins = int((uptime % 3600) // 60)
            print(f"Uptime: {hours}h {mins}m")
        cleanup_completed = status["cleanup_completed"]
        cleanup_total = status["cleanup_total"]
        print(f"Cleanup: {cleanup_completed}/{cleanup_total}")
        print("=" * 50)


class ResourceManager:
    """Manages resource cleanup for AMOS components."""

    def __init__(self, lifecycle: LifecycleManager):
        self.lifecycle = lifecycle
        self._resources: Dict[str, Any] = {}

        # Register cleanup handler
        lifecycle.register_cleanup_handler(self._cleanup_all)

    def register(self, name: str, resource: Any, cleanup_fn: Callable[[Any], None]) -> None:
        """Register a resource for automatic cleanup."""
        self._resources[name] = {
            "resource": resource,
            "cleanup": cleanup_fn,
        }
        print(f"[ResourceManager] Registered: {name}")

    def _cleanup_all(self) -> None:
        """Cleanup all registered resources."""
        print(f"[ResourceManager] Cleaning up {len(self._resources)} resources...")

        for name, data in self._resources.items():
            try:
                data["cleanup"](data["resource"])
                print(f"  Cleaned up: {name}")
            except Exception as e:
                print(f"  Failed cleanup {name}: {e}")


# Global instance
_lifecycle_manager: Optional[LifecycleManager] = None


def get_lifecycle_manager() -> LifecycleManager:
    """Get or create the global lifecycle manager."""
    global _lifecycle_manager
    if _lifecycle_manager is None:
        _lifecycle_manager = LifecycleManager()
    return _lifecycle_manager


def main():
    """Demo the lifecycle manager."""
    print("=" * 70)
    print("AMOS ECOSYSTEM v2.0 - LIFECYCLE MANAGER DEMO")
    print("=" * 70)

    # Create lifecycle manager
    lifecycle = get_lifecycle_manager()

    # Register some cleanup handlers
    def cleanup_audit():
        print("  Saving audit trail...")

    def cleanup_memory():
        print("  Releasing memory...")

    def cleanup_dashboard():
        print("  Stopping dashboard server...")

    lifecycle.register_cleanup_handler(cleanup_audit)
    lifecycle.register_cleanup_handler(cleanup_memory)
    lifecycle.register_cleanup_handler(cleanup_dashboard)

    # Startup
    lifecycle.startup()

    # Show status
    lifecycle.print_status()

    # Simulate running
    print("\n[Demo] Running (Ctrl+C to trigger shutdown)...")
    try:
        lifecycle.wait_for_shutdown(timeout=3)
    except KeyboardInterrupt:
        pass

    # If still running after timeout, trigger shutdown
    if lifecycle.is_running():
        lifecycle.shutdown("Demo complete")

    # Final status
    lifecycle.print_status()

    print("\n" + "=" * 70)
    print("Lifecycle demo complete!")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
