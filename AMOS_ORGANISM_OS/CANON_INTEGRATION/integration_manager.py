"""Integration Manager — External System Integration

Manages connections and integrations with external systems,
APIs, services, and data sources.

Owner: Trang
Version: 1.0.0
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class IntegrationStatus(Enum):
    """Status of an external integration."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    DISABLED = "disabled"


class IntegrationType(Enum):
    """Types of external integrations."""

    API = "api"
    DATABASE = "database"
    FILE_SYSTEM = "file_system"
    MESSAGE_QUEUE = "message_queue"
    WEBHOOK = "webhook"


@dataclass
class IntegrationConfig:
    """Configuration for external integration."""

    endpoint: str
    auth_method: str
    credentials: dict[str, str]
    timeout_seconds: int = 30
    retry_attempts: int = 3
    headers: dict[str, str] = field(default_factory=dict)


@dataclass
class ExternalSystem:
    """Definition of an external system."""

    id: str
    name: str
    system_type: IntegrationType
    config: IntegrationConfig
    status: IntegrationStatus = IntegrationStatus.DISCONNECTED
    last_connected: datetime = None
    health_check_interval: int = 300  # seconds


@dataclass
class IntegrationEvent:
    """Event from an integration."""

    system_id: str
    timestamp: datetime
    event_type: str
    data: dict[str, Any]
    processed: bool = False


class IntegrationManager:
    """Manages integrations with external systems.

    Handles connections, health checks, and event processing
    for all external integrations.
    """

    def __init__(self):
        self.systems: dict[str, ExternalSystem] = {}
        self.events: list[IntegrationEvent] = []
        self.connection_pool: dict[str, Any] = {}

    def register_system(self, system: ExternalSystem) -> bool:
        """Register a new external system."""
        if system.id in self.systems:
            return False
        self.systems[system.id] = system
        return True

    def connect(self, system_id: str) -> bool:
        """Connect to an external system."""
        if system_id not in self.systems:
            return False

        system = self.systems[system_id]
        system.status = IntegrationStatus.CONNECTING

        # Simulate connection
        try:
            # In production, this would establish actual connection
            system.status = IntegrationStatus.CONNECTED
            system.last_connected = datetime.now(UTC)
            return True
        except Exception:
            system.status = IntegrationStatus.ERROR
            return False

    def disconnect(self, system_id: str) -> bool:
        """Disconnect from an external system."""
        if system_id not in self.systems:
            return False

        system = self.systems[system_id]
        system.status = IntegrationStatus.DISCONNECTED

        if system_id in self.connection_pool:
            del self.connection_pool[system_id]

        return True

    def health_check(self, system_id: str) -> bool:
        """Check health of an external system."""
        if system_id not in self.systems:
            return False

        system = self.systems[system_id]

        if system.status != IntegrationStatus.CONNECTED:
            return False

        # Simulate health check
        return True

    def send_data(self, system_id: str, data: dict[str, Any]) -> bool:
        """Send data to an external system."""
        if system_id not in self.systems:
            return False

        system = self.systems[system_id]

        if system.status != IntegrationStatus.CONNECTED:
            return False

        # Simulate sending data
        return True

    def receive_data(self, system_id: str) -> dict[str, Any]:
        """Receive data from an external system."""
        if system_id not in self.systems:
            return None

        system = self.systems[system_id]

        if system.status != IntegrationStatus.CONNECTED:
            return None

        # Simulate receiving data
        return {}

    def get_system_status(self, system_id: str) -> IntegrationStatus | None:
        """Get status of an external system."""
        if system_id not in self.systems:
            return None
        return self.systems[system_id].status

    def list_systems(self, status_filter: IntegrationStatus | None = None) -> list[ExternalSystem]:
        """List all registered systems, optionally filtered by status."""
        systems = list(self.systems.values())
        if status_filter:
            systems = [s for s in systems if s.status == status_filter]
        return systems

    def get_connected_systems(self) -> list[ExternalSystem]:
        """Get all currently connected systems."""
        return self.list_systems(IntegrationStatus.CONNECTED)

    def record_event(self, event: IntegrationEvent) -> None:
        """Record an integration event."""
        self.events.append(event)

    def get_events(
        self, system_id: str = None, unprocessed_only: bool = False
    ) -> list[IntegrationEvent]:
        """Get integration events, optionally filtered."""
        events = self.events

        if system_id:
            events = [e for e in events if e.system_id == system_id]

        if unprocessed_only:
            events = [e for e in events if not e.processed]

        return events


if __name__ == "__main__":
    print("Integration Manager Module")
    print("=" * 50)

    manager = IntegrationManager()

    # Example system
    config = IntegrationConfig(
        endpoint="https://api.example.com",
        auth_method="api_key",
        credentials={"api_key": "test_key"},
    )

    system = ExternalSystem(
        id="api_001",
        name="Example API",
        system_type=IntegrationType.API,
        config=config,
    )

    manager.register_system(system)
    print(f"Registered system: {system.name}")
    print(f"Total systems: {len(manager.systems)}")
    print("Integration Manager ready")
