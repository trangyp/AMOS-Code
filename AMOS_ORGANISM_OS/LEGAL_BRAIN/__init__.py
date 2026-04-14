"""LEGAL_BRAIN module — Alias for 12_LEGAL_BRAIN"""

import sys
from pathlib import Path

legal_path = Path(__file__).parent.parent / "12_LEGAL_BRAIN"
if str(legal_path) not in sys.path:
    sys.path.insert(0, str(legal_path))

from compliance_auditor import AuditResult, ComplianceAuditor, ComplianceLevel
from contract_manager import Contract, ContractManager, IPProtection
from policy_engine import Policy, PolicyEngine, PolicyRule
from risk_governor import RiskAssessment, RiskGovernor, RiskLevel

__all__ = [
    "PolicyEngine",
    "Policy",
    "PolicyRule",
    "ComplianceAuditor",
    "AuditResult",
    "ComplianceLevel",
    "ContractManager",
    "Contract",
    "IPProtection",
    "RiskGovernor",
    "RiskAssessment",
    "RiskLevel",
]
