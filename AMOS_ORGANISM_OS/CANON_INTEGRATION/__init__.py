"""11_CANON_INTEGRATION — Canonical Standards & Integration Layer

Ensures AMOS adheres to canonical standards, integrates with external systems,
and maintains compliance with defined protocols and specifications.

Components:
- canon_enforcer: Enforces canonical rules and standards
- canon_bridge: Bridges _00_AMOS_CANON with organism integration
- integration_manager: Manages external system integrations
- protocol_handler: Handles protocol compliance and conversions
- standards_registry: Maintains registry of applicable standards

Owner: Trang
Version: 1.0.0
"""

from .canon_bridge import (
    CanonBridge,
    CanonBridgeStatus,
    get_canon_bridge,
    initialize_canon_integration,
)
from .canon_enforcer import CanonEnforcer, CanonRule, ViolationReport
from .integration_manager import ExternalSystem, IntegrationConfig, IntegrationManager
from .protocol_handler import MessageFormat, Protocol, ProtocolHandler
from .standards_registry import ComplianceStatus, Standard, StandardsRegistry

__all__ = [
    "CanonBridge",
    "CanonBridgeStatus",
    "CanonEnforcer",
    "CanonRule",
    "ComplianceStatus",
    "ExternalSystem",
    "IntegrationConfig",
    "IntegrationManager",
    "MessageFormat",
    "Protocol",
    "ProtocolHandler",
    "Standard",
    "StandardsRegistry",
    "ViolationReport",
    "get_canon_bridge",
    "initialize_canon_integration",
]
