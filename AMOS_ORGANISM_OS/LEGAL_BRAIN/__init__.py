"""LEGAL_BRAIN module — Alias for 12_LEGAL_BRAIN"""

import importlib.util
from pathlib import Path

# Load modules from 12_LEGAL_BRAIN using importlib
_12_LEGAL_PATH = Path(__file__).parent.parent / "12_LEGAL_BRAIN"

# compliance_auditor
_spec_ca = importlib.util.spec_from_file_location(
    "_comp_aud", _12_LEGAL_PATH / "compliance_auditor.py"
)
_mod_ca = importlib.util.module_from_spec(_spec_ca)
_spec_ca.loader.exec_module(_mod_ca)
ComplianceAuditor = _mod_ca.ComplianceAuditor
AuditResult = _mod_ca.AuditResult
ComplianceLevel = _mod_ca.ComplianceLevel

# contract_manager
_spec_cm = importlib.util.spec_from_file_location(
    "_cont_mgr", _12_LEGAL_PATH / "contract_manager.py"
)
_mod_cm = importlib.util.module_from_spec(_spec_cm)
_spec_cm.loader.exec_module(_mod_cm)
ContractManager = _mod_cm.ContractManager
Contract = _mod_cm.Contract
IPProtection = _mod_cm.IPProtection

# policy_engine
_spec_pe = importlib.util.spec_from_file_location("_pol_eng", _12_LEGAL_PATH / "policy_engine.py")
_mod_pe = importlib.util.module_from_spec(_spec_pe)
_spec_pe.loader.exec_module(_mod_pe)
PolicyEngine = _mod_pe.PolicyEngine
Policy = _mod_pe.Policy
PolicyRule = _mod_pe.PolicyRule

# risk_governor
_spec_rg = importlib.util.spec_from_file_location("_risk_gov", _12_LEGAL_PATH / "risk_governor.py")
_mod_rg = importlib.util.module_from_spec(_spec_rg)
_spec_rg.loader.exec_module(_mod_rg)
RiskGovernor = _mod_rg.RiskGovernor
RiskAssessment = _mod_rg.RiskAssessment
RiskLevel = _mod_rg.RiskLevel

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
