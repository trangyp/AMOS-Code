from __future__ import annotations
"""IO Router — Input/Output routing and dispatch

Routes data between subsystems, external interfaces, and
internal components. Handles message queuing and dispatch.
"""

import json
import uuid
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict


class RouteType(Enum):
    """Type of route."""

    INTERNAL = "internal"  # Between subsystems
    EXTERNAL = "external"  # To/from external systems
    BROADCAST = "broadcast"  # To multiple destinations
    QUEUE = "queue"  # Async queue-based


@dataclass
class RouteConfig:
    """Configuration for a route."""

    priority: int = 5  # 1-10, lower is higher priority
    retry_count: int = 3
    timeout_seconds: int = 30
    async_delivery: bool = False
    persist: bool = True


@dataclass
class Route:
    """A routing definition."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    source: str = ""  # Source subsystem/component
    destination: str = ""  # Target subsystem/component
    route_type: RouteType = RouteType.INTERNAL
    config: RouteConfig = field(default_factory=RouteConfig)
    filter_condition: str = ""  # Optional filter
    active: bool = True
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    message_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "route_type": self.route_type.value,
        }


@dataclass
class RoutedMessage:
    """A message being routed."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    route_id: str = ""
    payload: Any = None
    headers: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    delivered: bool = False
    delivery_time: str = None
    error: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class IORouter:
    """Routes data between components and subsystems.

    Manages routing rules, handles message dispatch,
    and tracks delivery status.
    """

    def __init__(self, data_dir: Path | None = None):
        if data_dir is None:
            data_dir = Path(__file__).parent / "data"
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.routes: Dict[str, Route] = {}
        self.pending_messages: list[RoutedMessage] = []
        self.delivered_messages: list[RoutedMessage] = []
        self.handlers: Dict[str, Callable] = {}

        self._load_routes()

    def _load_routes(self):
        """Load saved routes."""
        routes_file = self.data_dir / "routes.json"
        if routes_file.exists():
            try:
                data = json.loads(routes_file.read_text())
                for r_data in data.get("routes", []):
                    route = Route(
                        id=r_data["id"],
                        name=r_data["name"],
                        source=r_data["source"],
                        destination=r_data["destination"],
                        route_type=RouteType(r_data["route_type"]),
                        config=RouteConfig(**r_data.get("config", {})),
                        filter_condition=r_data.get("filter_condition", ""),
                        active=r_data.get("active", True),
                        created_at=r_data["created_at"],
                        message_count=r_data.get("message_count", 0),
                    )
                    self.routes[route.id] = route
            except Exception as e:
                print(f"[ROUTER] Error loading routes: {e}")

    def save(self):
        """Save routes to disk."""
        routes_file = self.data_dir / "routes.json"
        data = {
            "saved_at": datetime.now(UTC).isoformat(),
            "routes": [r.to_dict() for r in self.routes.values()],
        }
        routes_file.write_text(json.dumps(data, indent=2))

    def register_handler(self, destination: str, handler: Callable):
        """Register a handler for a destination."""
        self.handlers[destination] = handler

    def create_route(
        self,
        name: str,
        source: str,
        destination: str,
        route_type: RouteType = RouteType.INTERNAL,
        config: RouteConfig | None = None,
    ) -> Route:
        """Create a new route."""
        route = Route(
            name=name,
            source=source,
            destination=destination,
            route_type=route_type,
            config=config or RouteConfig(),
        )
        self.routes[route.id] = route
        self.save()
        return route

    def route_message(
        self,
        route_id: str,
        payload: Any,
        headers: dict = None,
    ) -> Dict[str, Any]:
        """Route a message through a specific route."""
        route = self.routes.get(route_id)
        if not route:
            return {"success": False, "error": "Route not found"}

        if not route.active:
            return {"success": False, "error": "Route inactive"}

        message = RoutedMessage(
            route_id=route_id,
            payload=payload,
            headers=headers or {},
        )

        # Update route stats
        route.message_count += 1

        # Check if async
        if route.config.async_delivery:
            self.pending_messages.append(message)
            self.save()
            return {
                "success": True,
                "queued": True,
                "message_id": message.id,
            }

        # Immediate delivery
        return self._deliver(message, route)

    def _deliver(self, message: RoutedMessage, route: Route) -> Dict[str, Any]:
        """Deliver a message to its destination."""
        handler = self.handlers.get(route.destination)

        if not handler:
            message.error = f"No handler for destination: {route.destination}"
            self.pending_messages.append(message)
            return {"success": False, "error": message.error}

        try:
            result = handler(message.payload, message.headers)
            message.delivered = True
            message.delivery_time = datetime.now(UTC).isoformat()
            self.delivered_messages.append(message)
            self.save()
            return {
                "success": True,
                "delivered": True,
                "message_id": message.id,
                "result": result,
            }
        except Exception as e:
            message.error = str(e)
            if len(self.pending_messages) < route.config.retry_count:
                self.pending_messages.append(message)
            self.save()
            return {"success": False, "error": str(e)}

    def process_pending(self) -> Dict[str, Any]:
        """Process all pending messages."""
        processed = 0
        failed = 0

        # Create a copy to avoid modification during iteration
        pending = self.pending_messages[:]
        self.pending_messages = []

        for message in pending:
            route = self.routes.get(message.route_id)
            if route and route.active:
                result = self._deliver(message, route)
                if result["success"]:
                    processed += 1
                else:
                    failed += 1
            else:
                failed += 1
                message.error = "Route unavailable"

        return {
            "processed": processed,
            "failed": failed,
            "remaining": len(self.pending_messages),
        }

    def get_route_stats(self, route_id: str) -> dict[str, Any]:
        """Get statistics for a route."""
        route = self.routes.get(route_id)
        if not route:
            return None

        pending = [m for m in self.pending_messages if m.route_id == route_id]
        delivered = [m for m in self.delivered_messages if m.route_id == route_id]

        return {
            "route": route.to_dict(),
            "pending_count": len(pending),
            "delivered_count": len(delivered),
            "total_messages": route.message_count,
        }

    def list_routes(self, active_only: bool = False) -> list[dict]:
        """List all routes."""
        routes = self.routes.values()
        if active_only:
            routes = [r for r in routes if r.active]

        return [
            {
                "id": r.id,
                "name": r.name,
                "source": r.source,
                "destination": r.destination,
                "type": r.route_type.value,
                "active": r.active,
                "messages": r.message_count,
            }
            for r in routes
        ]


# Global instance
_ROUTER: IORouter | None = None


def get_io_router(data_dir: Path | None = None) -> IORouter:
    """Get or create global IO router."""
    global _ROUTER
    if _ROUTER is None:
        _ROUTER = IORouter(data_dir)
    return _ROUTER


if __name__ == "__main__":
    print("IO Router (07_METABOLISM)")
    print("=" * 40)

    router = get_io_router()

    # Create a route
    route = router.create_route(
        "Brain to Muscle",
        "01_BRAIN",
        "06_MUSCLE",
    )
    print(f"\nCreated route: {route.name}")
    print(f"  From: {route.source} -> To: {route.destination}")

    # Register a handler
    def muscle_handler(payload, headers):
        print(f"  [Handler] Received: {payload}")
        return {"processed": True}

    router.register_handler("06_MUSCLE", muscle_handler)

    # Route a message
    result = router.route_message(route.id, {"action": "execute", "task": "test"})
    print(f"\nRouting result: {result}")

    print("\nActive routes:")
    for r in router.list_routes(active_only=True):
        print(f"  - {r['name']}")
