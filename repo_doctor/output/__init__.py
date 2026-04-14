"""
Repo Doctor Omega - Output Generation

Diagnosis and repair plan output formats:
- JSON for programmatic use
- Markdown for human review
- SARIF for security tool integration
"""

from .diagnosis import DiagnosisGenerator
from .repair_plan import RepairPlanGenerator

__all__ = [
    "DiagnosisGenerator",
    "RepairPlanGenerator",
]
