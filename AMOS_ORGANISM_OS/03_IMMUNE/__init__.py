"""
03_IMMUNE — Safety, legal, compliance, anomaly and boundary detection.

The immune system of AMOS. Validates all actions before execution.
Acts as a security gate for the MUSCLE subsystem.
"""

from .immune_system import ImmuneSystem, SafetyPolicy, AuditLog
from .threat_detector import ThreatDetector
from .compliance_engine import ComplianceEngine

__all__ = [
    "ImmuneSystem",
    "SafetyPolicy",
    "AuditLog",
    "ThreatDetector",
    "ComplianceEngine",
]
