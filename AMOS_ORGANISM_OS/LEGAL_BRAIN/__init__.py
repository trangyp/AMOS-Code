"""LEGAL_BRAIN module — Alias for 12_LEGAL_BRAIN"""

import sys
from pathlib import Path

legal_path = Path(__file__).parent.parent / "12_LEGAL_BRAIN"
if str(legal_path) not in sys.path:
    sys.path.insert(0, str(legal_path))

from policy_engine import PolicyEngine, Policy, PolicyRule
from compliance_auditor import ComplianceAuditor, AuditResult, ComplianceLevel
from contract_manager import ContractManager, Contract, IPProtection
from risk_governor import RiskGovernor, RiskAssessment, RiskLevel

__all__ = [
    "PolicyEngine", "Policy", "PolicyRule",
    "ComplianceAuditor", "AuditResult", "ComplianceLevel",
    "ContractManager", "Contract", "IPProtection",
    "RiskGovernor", "RiskAssessment", "RiskLevel",
]
