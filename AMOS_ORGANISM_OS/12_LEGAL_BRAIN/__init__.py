"""12_LEGAL_BRAIN — Compliance & Governance Engine
===============================================

The legal and governance layer of AMOS.
Handles policy enforcement, compliance auditing, contract management,
and risk governance for safe, legal operation.

Role: Legal compliance, policy enforcement, risk governance
Kernel refs: LEGAL_KERNEL, COMPLIANCE_KERNEL, POLICY_KERNEL

Owner: Trang
Version: 1.0.0
"""

from .compliance_auditor import AuditResult, ComplianceAuditor, ComplianceLevel
from .contract_manager import Contract, ContractManager, IPProtection
from .policy_engine import Policy, PolicyEngine, PolicyRule
from .risk_governor import RiskAssessment, RiskGovernor, RiskLevel

__all__ = [
    # Policy engine
    "PolicyEngine",
    "Policy",
    "PolicyRule",
    # Compliance auditing
    "ComplianceAuditor",
    "AuditResult",
    "ComplianceLevel",
    # Contract management
    "ContractManager",
    "Contract",
    "IPProtection",
    # Risk governance
    "RiskGovernor",
    "RiskAssessment",
    "RiskLevel",
]
