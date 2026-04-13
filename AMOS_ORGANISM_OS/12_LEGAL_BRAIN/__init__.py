"""
12_LEGAL_BRAIN — Compliance & Governance Engine
===============================================

The legal and governance layer of AMOS.
Handles policy enforcement, compliance auditing, contract management,
and risk governance for safe, legal operation.

Role: Legal compliance, policy enforcement, risk governance
Kernel refs: LEGAL_KERNEL, COMPLIANCE_KERNEL, POLICY_KERNEL

Owner: Trang
Version: 1.0.0
"""

from .policy_engine import PolicyEngine, Policy, PolicyRule
from .compliance_auditor import ComplianceAuditor, AuditResult, ComplianceLevel
from .contract_manager import ContractManager, Contract, IPProtection
from .risk_governor import RiskGovernor, RiskAssessment, RiskLevel

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
