#!/usr/bin/env python3
"""
AMOS Self-Healing Orchestrator
==============================

Master orchestrator integrating all equation and remediation systems.
Runs as part of the primary cognitive loop, enabling autonomous code repair.

Flow:
1. SENSE: Monitor code changes
2. BRAIN: Analyze with equation knowledge
3. IMMUNE: Verify invariants
4. MUSCLE: Generate and apply fixes
5. METABOLISM: Validate and deploy

Architecture: Closed-Loop Self-Healing System
"""

import sys
from pathlib import Path
from typing import Any, Optional

try:
    from AMOS_ORGANISM_OS.unified_equation_api import UnifiedEquationAPI

    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False

try:
    from AMOS_ORGANISM_OS.MUSCLE.automated_remediation_engine import AutomatedRemediationEngine

    REMEDIATION_AVAILABLE = True
except ImportError:
    REMEDIATION_AVAILABLE = False


class SelfHealingOrchestrator:
    """
    Self-healing orchestrator for AMOS Organism.

    Integrates all subsystems for autonomous code repair.
    """

    def __init__(self, organism_root: Optional[Path] = None):
        self.organism_root = organism_root or Path(__file__).parent
        self.equation_api: Optional[UnifiedEquationAPI] = None
        self.remediation_engine: Optional[AutomatedRemediationEngine] = None

        if API_AVAILABLE:
            self.equation_api = UnifiedEquationAPI(self.organism_root)

        if REMEDIATION_AVAILABLE:
            self.remediation_engine = AutomatedRemediationEngine(self.organism_root)

    def get_system_status(self) -> dict[str, Any]:
        """Get complete system status."""
        status = {
            "equation_api": API_AVAILABLE,
            "remediation_engine": REMEDIATION_AVAILABLE,
            "sources": {},
            "health": "operational" if (API_AVAILABLE and REMEDIATION_AVAILABLE) else "degraded",
        }

        if self.equation_api:
            status["sources"] = self.equation_api.get_dashboard_data()

        if self.remediation_engine:
            status["remediation"] = self.remediation_engine.get_remediation_report()

        return status

    def analyze_and_remediate(
        self,
        code: str,
        language: str,
        auto_fix: bool = False,
    ) -> dict[str, Any]:
        """
        Full analysis and remediation pipeline.

        Args:
            code: Source code to analyze
            language: Programming language
            auto_fix: Whether to auto-apply fixes

        Returns:
            Complete analysis and remediation results
        """
        results = {
            "code_length": len(code),
            "language": language,
            "verification": None,
            "remediation": None,
            "fixes_applied": 0,
        }

        # Step 1: Verify code
        if self.equation_api:
            results["verification"] = self.equation_api.verify_code(code, language)

        # Step 2: Remediate if violations
        if self.remediation_engine:
            record = self.remediation_engine.remediate(code, language, auto_fix)
            results["remediation"] = {
                "id": record.id,
                "status": record.status.name,
                "violations_count": len([v for v in record.violations if v.violations]),
                "fixes_generated": len(record.fixes),
                "fix_applied": record.applied_fix is not None,
            }
            if record.applied_fix:
                results["fixes_applied"] = 1
                results["fix_type"] = record.applied_fix.fix_type.value

        return results


def main() -> int:
    """Test self-healing orchestrator."""
    print("=" * 70)
    print("AMOS SELF-HEALING ORCHESTRATOR")
    print("=" * 70)

    orchestrator = SelfHealingOrchestrator()

    # System status
    print("\n[System Status]")
    status = orchestrator.get_system_status()
    for key, value in status.items():
        if key == "sources":
            print(f"  {key}:")
            for skey, sval in value.items():
                print(f"    {skey}: {sval}")
        else:
            print(f"  {key}: {value}")

    # Test analysis
    test_code = """
def risky_function(items=[]):
    items.append(1)
    return items

def no_type_hints(x, y):
    return x + y
"""

    print("\n[Analysis Test]")
    print(f"Code: {test_code.strip()[:50]}...")

    results = orchestrator.analyze_and_remediate(test_code, "python", auto_fix=False)

    print("\nResults:")
    print(f"  Violations found: {results['remediation']['violations_count']}")
    print(f"  Fixes generated: {results['remediation']['fixes_generated']}")
    print(f"  Health status: {status['health']}")

    print("\n" + "=" * 70)
    print("ORCHESTRATOR OPERATIONAL")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
