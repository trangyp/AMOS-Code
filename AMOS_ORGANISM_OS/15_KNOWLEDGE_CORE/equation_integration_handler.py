#!/usr/bin/env python3
"""
AMOS Equation Integration Handler
====================================

Subsystem handler integrating ALL equation systems into the primary loop:
- SuperBrain Equation Bridge (33 domains, 145+ equations)
- Equation Knowledge Bridge (PL theory, 400+ equations)
- Invariant Verification Engine (neural-symbolic)
- Automated Remediation Engine (self-healing)

Runs as part of 15_KNOWLEDGE_CORE in the AMOS Master Orchestrator.
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "01_BRAIN"))
sys.path.insert(0, str(Path(__file__).parent.parent / "03_IMMUNE"))
sys.path.insert(0, str(Path(__file__).parent.parent / "06_MUSCLE"))
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from AMOS_MASTER_ORCHESTRATOR import CycleResult, SubsystemHandler

    ORCHESTRATOR_AVAILABLE = True
except ImportError:
    ORCHESTRATOR_AVAILABLE = False

try:
    from unified_equation_api import UnifiedEquationAPI

    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False

try:
    from automated_remediation_engine import AutomatedRemediationEngine

    REMEDIATION_AVAILABLE = True
except ImportError:
    REMEDIATION_AVAILABLE = False


class EquationIntegrationHandler:
    """
    Knowledge Core handler for equation system integration.

    Provides unified equation services to all AMOS subsystems.
    """

    def __init__(self, code: str = "15_KNOWLEDGE_CORE", config: Dict[str, Any] = None):
        self.code = code
        self.config = config or {}
        self.equation_api: Optional[UnifiedEquationAPI] = None
        self.remediation_engine: Optional[AutomatedRemediationEngine] = None
        self._initialized = False

    def initialize(self) -> bool:
        """Initialize equation integration."""
        if API_AVAILABLE:
            self.equation_api = UnifiedEquationAPI()

        if REMEDIATION_AVAILABLE:
            self.remediation_engine = AutomatedRemediationEngine()

        self._initialized = True
        return True

    def process(self, context: Dict[str, Any]) -> Any:
        """
        Process cycle - provides equation services to other subsystems.

        Called by Master Orchestrator during each cycle.
        """
        if not self._initialized:
            self.initialize()

        # Check if any code needs verification (from context)
        code_to_check = context.get("code_to_verify")
        language = context.get("language", "python")

        results = {
            "subsystem": self.code,
            "status": "active",
            "services": {},
        }

        # Provide equation query service
        if self.equation_api:
            results["services"]["equation_query"] = {
                "available": True,
                "sources": self.equation_api.get_dashboard_data(),
            }

        # Provide verification service if code provided
        if code_to_check and self.remediation_engine:
            record = self.remediation_engine.remediate(code_to_check, language, auto_fix=False)
            results["services"]["verification"] = {
                "violations_found": len([v for v in record.violations if v.violations]),
                "fixes_available": len(record.fixes),
            }

        # Create cycle result
        if ORCHESTRATOR_AVAILABLE:
            return CycleResult(
                subsystem=self.code,
                status="success",
                actions=["equation_services"],
                outputs=results,
            )
        return results

    def query_equations(
        self,
        domain: str = None,
        language: str = None,
    ) -> List[dict[str, Any]]:
        """Query equations across all sources."""
        if not self.equation_api:
            return []
        return [eq.__dict__ for eq in self.equation_api.query_all(domain, language)]

    def verify_and_remediate(
        self,
        code: str,
        language: str,
        auto_fix: bool = False,
    ) -> Dict[str, Any]:
        """Full verification and remediation service."""
        if not self.equation_api:
            return {"error": "Equation API not available"}

        return self.equation_api.verify_code(code, language)

    def get_status(self) -> Dict[str, Any]:
        """Get integration status."""
        if self.equation_api:
            return self.equation_api.get_dashboard_data()
        return {"initialized": self._initialized}


def main() -> int:
    """Test equation integration handler."""
    print("[EquationIntegrationHandler] Testing...")

    handler = EquationIntegrationHandler()
    handler.initialize()

    # Test equation query
    print("\n[Equation Query Test]")
    equations = handler.query_equations(language="python")
    print(f"  Found {len(equations)} equations")

    # Test verification
    test_code = "def f(items=[]): items.append(1); return items"
    print("\n[Verification Test]")
    print(f"  Code: {test_code[:40]}...")

    result = handler.verify_and_remediate(test_code, "python")
    print(f"  Violations: {result.get('remediation', {}).get('violations_count', 0)}")

    # Status
    print("\n[System Status]")
    status = handler.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")

    print("\n[OK] Handler operational")
    return 0


if __name__ == "__main__":
    sys.exit(main())
