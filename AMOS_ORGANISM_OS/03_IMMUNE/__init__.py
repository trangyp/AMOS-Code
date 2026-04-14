"""03_IMMUNE — Safety, legal, compliance, anomaly and boundary detection.

The immune system of AMOS. Validates all actions before execution.
Acts as a security gate for the MUSCLE subsystem.
"""

from .compliance_engine import ComplianceEngine
from .immune_system import AuditLog, ImmuneSystem, SafetyPolicy
from .threat_detector import ThreatDetector

__all__ = [
    "ImmuneSystem",
    "SafetyPolicy",
    "AuditLog",
    "ThreatDetector",
    "ComplianceEngine",
]
