"""
12_ETHICS_VALIDATION — Ethics Validation & Moral Reasoning

Ensures AMOS operates within ethical boundaries, validates decisions
against moral frameworks, and maintains ethical compliance.

Components:
- ethics_engine: Core ethical reasoning and validation
- moral_framework: Moral principles and value systems
- bias_detector: Detection and mitigation of biases
- ethics_auditor: Ethical compliance auditing

Owner: Trang
Version: 1.0.0
"""

from .ethics_engine import EthicsEngine, EthicalDecision, EthicsRule
from .moral_framework import MoralFramework, ValueSystem, MoralPrinciple
from .bias_detector import BiasDetector, BiasReport, BiasType
from .ethics_auditor import EthicsAuditor, AuditReport, EthicsCompliance

__all__ = [
    "EthicsEngine",
    "EthicalDecision",
    "EthicsRule",
    "MoralFramework",
    "ValueSystem",
    "MoralPrinciple",
    "BiasDetector",
    "BiasReport",
    "BiasType",
    "EthicsAuditor",
    "AuditReport",
    "EthicsCompliance",
]
