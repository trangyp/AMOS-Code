#!/usr/bin/env python3
"""AMOS State Manager - Persistence layer for 59+ components."""

import json
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class SystemState:
    """Represents the complete state of the AMOS ecosystem."""

    version: str = "1.0.0"
    timestamp: float = field(default_factory=time.time)
    iso_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    # System metadata
    components_total: int = 59
    components_initialized: int = 0

    # Orchestrator state
    tasks_completed: int = 0
    tasks_failed: int = 0
    tasks_pending: int = 0

    # Organism state
    organism_initialized: bool = False
    subsystems_active: List[str] = field(default_factory=list)

    # Knowledge state
    knowledge_files_loaded: int = 0
    knowledge_cache: Dict[str, Any] = field(default_factory=dict)

    # Configuration state
    active_config: str = "default"
    custom_settings: Dict[str, Any] = field(default_factory=dict)

    # Session data
    session_id: str = field(default_factory=lambda: f"session_{int(time.time())}")
    user_context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StateSnapshot:
    """A point-in-time snapshot of system state."""

    snapshot_id: str
    created_at: float
    description: str
    state: SystemState


class AMOSStateManager:
    """State management and persistence for AMOS ecosystem.

    Provides:
    - State persistence across restarts
    - Snapshot/restore functionality
    - Session management
    - Rollback capabilities
    - JSON and binary serialization

    Used by all 59+ components to maintain state.
    """

    def __init__(self, state_dir: str = "amos_state"):
        """Initialize state manager."""
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(exist_ok=True)

        self.current_state = SystemState()
        self.snapshots: List[StateSnapshot] = []
        self.max_snapshots = 10

        # File paths
        self.state_file = self.state_dir / "system_state.json"
        self.snapshots_file = self.state_dir / "snapshots.json"
        self.session_file = self.state_dir / "session.json"

    def initialize(self) -> SystemState:
        """Initialize state, loading from disk if available."""
        if self.state_file.exists():
            try:
                with open(self.state_file) as f:
                    data = json.load(f)
                    self.current_state = self._dict_to_state(data)
                    print(f"   ✓ State loaded from {self.state_file}")
            except Exception as e:
                print(f"   ⚠ Could not load state: {e}")
                self.current_state = SystemState()

        self.current_state.timestamp = time.time()
        self.current_state.iso_timestamp = datetime.now().isoformat()

        return self.current_state

    def save_state(self) -> bool:
        """Save current state to disk."""
        try:
            self.current_state.timestamp = time.time()
            self.current_state.iso_timestamp = datetime.now().isoformat()

            with open(self.state_file, "w") as f:
                json.dump(self._state_to_dict(self.current_state), f, indent=2)

            return True
        except Exception as e:
            print(f"   ✗ Failed to save state: {e}")
            return False

    def create_snapshot(self, description: str = "") -> StateSnapshot:
        """Create a snapshot of current state."""
        snapshot = StateSnapshot(
            snapshot_id=f"snap_{int(time.time() * 1000)}",
            created_at=time.time(),
            description=description or f"Snapshot at {datetime.now().isoformat()}",
            state=self._clone_state(self.current_state),
        )

        self.snapshots.append(snapshot)

        # Keep only max_snapshots
        if len(self.snapshots) > self.max_snapshots:
            self.snapshots.pop(0)

        self._save_snapshots()
        return snapshot

    def restore_snapshot(self, snapshot_id: str) -> bool:
        """Restore state from a snapshot."""
        for snapshot in self.snapshots:
            if snapshot.snapshot_id == snapshot_id:
                self.current_state = self._clone_state(snapshot.state)
                self.save_state()
                return True
        return False

    def list_snapshots(self) -> List[dict[str, Any]]:
        """List all available snapshots."""
        return [
            {
                "id": s.snapshot_id,
                "created": datetime.fromtimestamp(s.created_at).isoformat(),
                "description": s.description,
            }
            for s in self.snapshots
        ]

    def update_task_stats(self, completed: int = 0, failed: int = 0, pending: int = 0):
        """Update task statistics."""
        self.current_state.tasks_completed += completed
        self.current_state.tasks_failed += failed
        self.current_state.tasks_pending += pending

    def update_component_count(self, initialized: int):
        """Update component initialization count."""
        self.current_state.components_initialized = initialized

    def update_knowledge_stats(self, files_loaded: int):
        """Update knowledge loading statistics."""
        self.current_state.knowledge_files_loaded = files_loaded

    def set_user_context(self, key: str, value: Any):
        """Set user context data."""
        self.current_state.user_context[key] = value

    def get_user_context(self, key: str) -> Optional[Any]:
        """Get user context data."""
        return self.current_state.user_context.get(key)

    def export_state(self, path: str) -> bool:
        """Export state to a file."""
        try:
            with open(path, "w") as f:
                json.dump(self._state_to_dict(self.current_state), f, indent=2)
            return True
        except Exception as e:
            print(f"   ✗ Export failed: {e}")
            return False

    def import_state(self, path: str) -> bool:
        """Import state from a file."""
        try:
            with open(path) as f:
                data = json.load(f)
                self.current_state = self._dict_to_state(data)
                return True
        except Exception as e:
            print(f"   ✗ Import failed: {e}")
            return False

    def get_current_state(self) -> SystemState:
        """Get current system state."""
        return self.current_state

    def get_state_summary(self) -> Dict[str, Any]:
        """Get a summary of current state."""
        return {
            "version": self.current_state.version,
            "timestamp": self.current_state.iso_timestamp,
            "session_id": self.current_state.session_id,
            "components": {
                "total": self.current_state.components_total,
                "initialized": self.current_state.components_initialized,
            },
            "tasks": {
                "completed": self.current_state.tasks_completed,
                "failed": self.current_state.tasks_failed,
                "pending": self.current_state.tasks_pending,
            },
            "organism": {
                "initialized": self.current_state.organism_initialized,
                "active_subsystems": len(self.current_state.subsystems_active),
            },
            "knowledge": {"files_loaded": self.current_state.knowledge_files_loaded},
        }

    def _state_to_dict(self, state: SystemState) -> Dict[str, Any]:
        """Convert state to dictionary."""
        return asdict(state)

    def _dict_to_state(self, data: Dict[str, Any]) -> SystemState:
        """Convert dictionary to state."""
        return SystemState(**data)

    def _clone_state(self, state: SystemState) -> SystemState:
        """Create a deep copy of state."""
        return self._dict_to_state(self._state_to_dict(state))

    def _save_snapshots(self):
        """Save snapshots to disk."""
        try:
            snapshots_data = [
                {
                    "snapshot_id": s.snapshot_id,
                    "created_at": s.created_at,
                    "description": s.description,
                    "state": self._state_to_dict(s.state),
                }
                for s in self.snapshots
            ]
            with open(self.snapshots_file, "w") as f:
                json.dump(snapshots_data, f, indent=2)
        except Exception as e:
            print(f"   ✗ Failed to save snapshots: {e}")


def demo_state_manager():
    """Demonstrate state manager functionality."""
    print("\n" + "=" * 70)
    print("AMOS STATE MANAGER - COMPONENT #59")
    print("=" * 70)

    # Initialize
    print("\n[1] Initializing state manager...")
    manager = AMOSStateManager()
    state = manager.initialize()
    print("   ✓ State initialized")
    print(f"   → Session ID: {state.session_id}")

    # Update task stats
    print("\n[2] Updating task statistics...")
    manager.update_task_stats(completed=5, pending=2)
    print(f"   → Tasks completed: {manager.current_state.tasks_completed}")
    print(f"   → Tasks pending: {manager.current_state.tasks_pending}")

    # Update component count
    print("\n[3] Updating component stats...")
    manager.update_component_count(initialized=45)
    print(f"   → Components initialized: {manager.current_state.components_initialized}/59")

    # Create snapshot
    print("\n[4] Creating state snapshot...")
    snapshot = manager.create_snapshot("After initial setup")
    print(f"   ✓ Snapshot created: {snapshot.snapshot_id}")
    print(f"   → Description: {snapshot.description}")

    # Set user context
    print("\n[5] Setting user context...")
    manager.set_user_context("user_id", "user_12345")
    manager.set_user_context("preferences", {"theme": "dark", "language": "en"})
    print("   ✓ User context saved")

    # Save state
    print("\n[6] Saving state to disk...")
    success = manager.save_state()
    print(f"   {'✓' if success else '✗'} State saved to {manager.state_file}")

    # Get summary
    print("\n[7] Current state summary...")
    summary = manager.get_state_summary()
    print(f"   Version: {summary['version']}")
    print(f"   Session: {summary['session_id']}")
    print(f"   Components: {summary['components']['initialized']}/{summary['components']['total']}")
    print(
        f"   Tasks: {summary['tasks']['completed']} completed, {summary['tasks']['pending']} pending"
    )

    # List snapshots
    print("\n[8] Available snapshots...")
    snapshots = manager.list_snapshots()
    for snap in snapshots:
        print(f"   → {snap['id'][:20]}... ({snap['created']})")

    print("\n" + "=" * 70)
    print("State Manager Demo Complete")
    print("=" * 70)
    print("\n✓ Persistence layer for 59+ components")
    print("✓ State survives restarts")
    print("✓ Snapshot/restore capability")
    print("✓ Session management")
    print("✓ Task history tracking")
    print("=" * 70)


if __name__ == "__main__":
    demo_state_manager()
