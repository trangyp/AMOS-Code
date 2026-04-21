#!/usr/bin/env python3
"""AMOS Canon Integration Kernel - 11_CANON_INTEGRATION Subsystem

Responsible for:
- Canon protocol adaptation and translation
- API standardization and interface unification
- Canon service discovery and registration
- External Canon system communication
- Protocol bridge between internal and external systems
"""

import json
import logging
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc

UTC = UTC
from enum import Enum, auto
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("amos.canon")


class ProtocolType(Enum):
    """Types of Canon protocols."""

    REST = auto()
    GRAPHQL = auto()
    GRPC = auto()
    WEBSOCKET = auto()
    MCP = auto()  # Model Context Protocol
    CUSTOM = auto()


class InterfaceStatus(Enum):
    """Status of a Canon interface."""

    DISCONNECTED = auto()
    CONNECTING = auto()
    CONNECTED = auto()
    ERROR = auto()
    DEGRADED = auto()


@dataclass
class CanonService:
    """A discovered Canon service."""

    service_id: str
    name: str
    protocol: ProtocolType
    endpoint: str
    version: str = "1.0"
    status: InterfaceStatus = InterfaceStatus.DISCONNECTED
    capabilities: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    discovered_at: str = ""
    last_ping: str = ""
    health_score: float = 1.0

    def __post_init__(self):
        if not self.discovered_at:
            self.discovered_at = datetime.now(UTC).isoformat()
        if not self.last_ping:
            self.last_ping = self.discovered_at


@dataclass
class ProtocolAdapter:
    """An adapter for a specific Canon protocol."""

    adapter_id: str
    protocol: ProtocolType
    version: str
    translator: Callable = None
    encoder: Callable = None
    decoder: Callable = None
    handlers: dict[str, Callable] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(UTC).isoformat()


@dataclass
class ApiEndpoint:
    """A unified API endpoint."""

    endpoint_id: str
    path: str
    method: str
    handler: Callable = None
    adapters: list[str] = field(default_factory=list)
    rate_limit: int = 100
    auth_required: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(UTC).isoformat()


class CanonIntegrationKernel:
    """The Canon Integration Kernel provides a bridge between the AMOS organism
    and external Canon systems. It handles protocol translation, service
    discovery, and interface standardization.
    """

    def __init__(self, organism_root: Path):
        self.root = organism_root
        self.canon_path = organism_root / "11_CANON_INTEGRATION"
        self.memory_path = self.canon_path / "memory"
        self.adapters_path = self.canon_path / "adapters"
        self.services_path = self.canon_path / "services"

        # Ensure directories
        self.memory_path.mkdir(parents=True, exist_ok=True)
        self.adapters_path.mkdir(parents=True, exist_ok=True)
        self.services_path.mkdir(parents=True, exist_ok=True)

        # Protocol adapters
        self.adapters: dict[str, ProtocolAdapter] = {}

        # Discovered services
        self.services: dict[str, CanonService] = {}

        # Unified API endpoints
        self.endpoints: dict[str, ApiEndpoint] = {}

        # Protocol type registry
        self.protocol_registry: dict[ProtocolType, list[str]] = defaultdict(list)

        # Interface statistics
        self.stats = {
            "adapters_created": 0,
            "services_discovered": 0,
            "endpoints_registered": 0,
            "messages_translated": 0,
            "connections_established": 0,
        }

        # Initialize default adapters
        self._init_default_adapters()

        logger.info(f"CanonIntegrationKernel initialized at {self.canon_path}")

    def _init_default_adapters(self):
        """Initialize default protocol adapters."""
        # REST adapter
        self.create_adapter(
            adapter_id="rest_default",
            protocol=ProtocolType.REST,
            version="1.0",
            encoder=self._rest_encoder,
            decoder=self._rest_decoder,
        )

        # MCP adapter
        self.create_adapter(
            adapter_id="mcp_default",
            protocol=ProtocolType.MCP,
            version="2024-11-05",
            encoder=self._mcp_encoder,
            decoder=self._mcp_decoder,
        )

        logger.info("Default protocol adapters initialized")

    def _rest_encoder(self, data: dict[str, Any]) -> str:
        """Encode data for REST protocol."""
        return json.dumps(data)

    def _rest_decoder(self, data: str) -> dict[str, Any]:
        """Decode data from REST protocol."""
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON", "raw": data}

    def _mcp_encoder(self, data: dict[str, Any]) -> dict[str, Any]:
        """Encode data for MCP protocol."""
        return {
            "jsonrpc": "2.0",
            "id": data.get("id", 1),
            "method": data.get("method", "unknown"),
            "params": data.get("params", {}),
        }

    def _mcp_decoder(self, data: dict[str, Any]) -> dict[str, Any]:
        """Decode data from MCP protocol."""
        if "result" in data:
            return {"success": True, "data": data["result"]}
        elif "error" in data:
            return {"success": False, "error": data["error"]}
        return data

    def create_adapter(
        self,
        adapter_id: str,
        protocol: ProtocolType,
        version: str,
        translator: Callable = None,
        encoder: Callable = None,
        decoder: Callable = None,
        metadata: dict[str, Any] = None,
    ) -> ProtocolAdapter:
        """Create a new protocol adapter."""
        adapter = ProtocolAdapter(
            adapter_id=adapter_id,
            protocol=protocol,
            version=version,
            translator=translator,
            encoder=encoder,
            decoder=decoder,
            metadata=metadata or {},
        )

        self.adapters[adapter_id] = adapter
        self.protocol_registry[protocol].append(adapter_id)
        self.stats["adapters_created"] += 1

        logger.info(f"Created {protocol.name} adapter: {adapter_id}")
        return adapter

    def discover_service(
        self,
        service_id: str,
        name: str,
        protocol: ProtocolType,
        endpoint: str,
        version: str = "1.0",
        capabilities: list[str] = None,
        metadata: dict[str, Any] = None,
    ) -> CanonService:
        """Discover and register a Canon service."""
        service = CanonService(
            service_id=service_id,
            name=name,
            protocol=protocol,
            endpoint=endpoint,
            version=version,
            capabilities=capabilities or [],
            metadata=metadata or {},
        )

        self.services[service_id] = service
        self.stats["services_discovered"] += 1

        logger.info(f"Discovered service: {name} ({service_id}) at {endpoint}")
        return service

    def update_service_status(
        self, service_id: str, status: InterfaceStatus, health_score: float = None
    ) -> bool:
        """Update the status of a service."""
        if service_id not in self.services:
            return False

        service = self.services[service_id]
        service.status = status
        service.last_ping = datetime.now(UTC).isoformat()

        if health_score is not None:
            service.health_score = max(0.0, min(1.0, health_score))

        logger.debug(f"Service {service_id} status: {status.name}")
        return True

    def register_endpoint(
        self,
        endpoint_id: str,
        path: str,
        method: str = "GET",
        handler: Callable = None,
        adapters: list[str] = None,
        rate_limit: int = 100,
        auth_required: bool = True,
        metadata: dict[str, Any] = None,
    ) -> ApiEndpoint:
        """Register a unified API endpoint."""
        endpoint = ApiEndpoint(
            endpoint_id=endpoint_id,
            path=path,
            method=method,
            handler=handler,
            adapters=adapters or [],
            rate_limit=rate_limit,
            auth_required=auth_required,
            metadata=metadata or {},
        )

        self.endpoints[endpoint_id] = endpoint
        self.stats["endpoints_registered"] += 1

        logger.info(f"Registered endpoint: {method} {path} ({endpoint_id})")
        return endpoint

    def translate_message(
        self,
        message: dict[str, Any],
        source_protocol: ProtocolType,
        target_protocol: ProtocolType,
        adapter_id: str = None,
    ) -> dict[str, Any]:
        """Translate a message between protocols."""
        # Find appropriate adapter
        adapter = None
        if adapter_id and adapter_id in self.adapters:
            adapter = self.adapters[adapter_id]
        elif target_protocol in self.protocol_registry:
            # Use first available adapter for target protocol
            adapter_id = self.protocol_registry[target_protocol][0]
            adapter = self.adapters[adapter_id]

        if not adapter:
            return {"error": f"No adapter available for {target_protocol.name}"}

        # Encode then decode to translate
        if adapter.encoder:
            encoded = adapter.encoder(message)
        else:
            encoded = message

        # Apply custom translator if available
        if adapter.translator:
            translated = adapter.translator(encoded)
        else:
            translated = encoded

        self.stats["messages_translated"] += 1

        logger.debug(f"Translated message from {source_protocol.name} to {target_protocol.name}")
        return translated

    def get_compatible_services(self, protocol: ProtocolType) -> list[CanonService]:
        """Get services compatible with a specific protocol."""
        return [
            s
            for s in self.services.values()
            if s.protocol == protocol and s.status != InterfaceStatus.ERROR
        ]

    def get_healthy_services(self, min_health: float = 0.5) -> list[CanonService]:
        """Get services with health score above threshold."""
        return [s for s in self.services.values() if s.health_score >= min_health]

    def establish_connection(self, service_id: str) -> bool:
        """Attempt to establish connection to a service."""
        if service_id not in self.services:
            return False

        service = self.services[service_id]

        # Simulate connection (in real implementation, this would actually connect)
        self.update_service_status(service_id, InterfaceStatus.CONNECTING)

        # Check if adapter exists for this protocol
        if service.protocol not in self.protocol_registry:
            self.update_service_status(service_id, InterfaceStatus.ERROR, health_score=0.0)
            return False

        # Success
        self.update_service_status(service_id, InterfaceStatus.CONNECTED, health_score=1.0)
        self.stats["connections_established"] += 1

        logger.info(f"Established connection to {service.name}")
        return True

    def get_state(self) -> dict[str, Any]:
        """Get current Canon integration state."""
        # Count services by status
        status_counts = defaultdict(int)
        for service in self.services.values():
            status_counts[service.status.name] += 1

        # Count by protocol
        protocol_counts = defaultdict(int)
        for service in self.services.values():
            protocol_counts[service.protocol.name] += 1

        return {
            "adapters_active": len(self.adapters),
            "services_discovered": len(self.services),
            "endpoints_registered": len(self.endpoints),
            "connections_active": status_counts.get("CONNECTED", 0),
            "services_by_status": dict(status_counts),
            "services_by_protocol": dict(protocol_counts),
            "stats": self.stats,
            "timestamp": datetime.now(UTC).isoformat(),
        }


if __name__ == "__main__":
    # Test the Canon integration kernel
    root = Path(__file__).parent.parent
    canon = CanonIntegrationKernel(root)

    print("Canon Integration State (initial):")
    print(json.dumps(canon.get_state(), indent=2))

    print("\n=== Test 1: Create Custom Adapter ===")
    custom_adapter = canon.create_adapter(
        adapter_id="custom_v1",
        protocol=ProtocolType.CUSTOM,
        version="1.0",
        metadata={"description": "Custom protocol adapter"},
    )
    print(f"Created adapter: {custom_adapter.adapter_id} ({custom_adapter.protocol.name})")

    print("\n=== Test 2: Discover Services ===")

    # Discover REST service
    rest_service = canon.discover_service(
        service_id="rest_api_1",
        name="External REST API",
        protocol=ProtocolType.REST,
        endpoint="https://api.example.com/v1",
        capabilities=["read", "write", "delete"],
        metadata={"auth_type": "bearer"},
    )
    print(f"Discovered: {rest_service.name} ({rest_service.service_id})")

    # Discover MCP service
    mcp_service = canon.discover_service(
        service_id="mcp_server_1",
        name="MCP Tool Server",
        protocol=ProtocolType.MCP,
        endpoint="stdio",
        capabilities=["tools/list", "tools/call"],
        metadata={"tools": ["search", "read_file", "write_file"]},
    )
    print(f"Discovered: {mcp_service.name} ({mcp_service.service_id})")

    print("\n=== Test 3: Update Service Status ===")
    canon.update_service_status("rest_api_1", InterfaceStatus.CONNECTED, health_score=0.95)
    canon.update_service_status("mcp_server_1", InterfaceStatus.CONNECTED, health_score=0.88)
    print(f"REST service status: {canon.services['rest_api_1'].status.name}")
    print(f"MCP service status: {canon.services['mcp_server_1'].status.name}")

    print("\n=== Test 4: Register Endpoints ===")
    endpoint1 = canon.register_endpoint(
        endpoint_id="query_endpoint",
        path="/api/query",
        method="POST",
        adapters=["rest_default"],
        rate_limit=1000,
    )
    endpoint2 = canon.register_endpoint(
        endpoint_id="tool_endpoint",
        path="/api/tools/call",
        method="POST",
        adapters=["mcp_default"],
        auth_required=True,
    )
    print(f"Registered: {endpoint1.method} {endpoint1.path}")
    print(f"Registered: {endpoint2.method} {endpoint2.path}")

    print("\n=== Test 5: Translate Messages ===")

    # Translate to REST
    internal_msg = {"action": "query", "params": {"q": "test query"}}
    rest_msg = canon.translate_message(internal_msg, ProtocolType.CUSTOM, ProtocolType.REST)
    print(f"Internal -> REST: {rest_msg}")

    # Translate to MCP
    mcp_msg = canon.translate_message(
        internal_msg, ProtocolType.CUSTOM, ProtocolType.MCP, adapter_id="mcp_default"
    )
    print(f"Internal -> MCP: {mcp_msg}")

    print("\n=== Test 6: Get Compatible Services ===")
    rest_services = canon.get_compatible_services(ProtocolType.REST)
    print(f"REST-compatible services: {[s.name for s in rest_services]}")

    healthy = canon.get_healthy_services(min_health=0.9)
    print(f"Healthy services (>=0.9): {[s.name for s in healthy]}")

    print("\n=== Test 7: Establish Connection ===")
    success = canon.establish_connection("rest_api_1")
    print(f"Connection to REST API: {'SUCCESS' if success else 'FAILED'}")

    print("\nFinal State:")
    print(json.dumps(canon.get_state(), indent=2))
