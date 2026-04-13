"""
11_LEGAL_BRAIN — Legal compliance and governance

The legal subsystem of AMOS. Handles contracts, IP protection,
compliance checking, and regulatory monitoring.

Role: Contracts, IP, compliance, regulatory scanning
Kernel refs: AMOS_Vn_Legal_Engine, CONTRACT_KERNEL

Owner: Trang
Version: 1.0.0
"""

from .legal_engine import (
    LegalEngine, ComplianceRule, ComplianceCheck, RiskAssessment,
)
from .contract_manager import ContractManager, Contract, ContractStatus, get_contract_manager
from .ip_tracker import IPTracker, IPAsset, IPType, get_ip_tracker
from .regulatory_scanner import RegulatoryScanner, Regulation, get_regulatory_scanner

__all__ = [
    # Legal Engine
    "LegalEngine", "ComplianceRule", "ComplianceCheck", "RiskAssessment",
    # Contract Management
    "ContractManager", "Contract", "ContractStatus", "get_contract_manager",
    # IP Tracking
    "IPTracker", "IPAsset", "IPType", "get_ip_tracker",
    # Regulatory
    "RegulatoryScanner", "Regulation", "get_regulatory_scanner",
]
