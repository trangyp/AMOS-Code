#!/usr/bin/env python3
from __future__ import annotations
"""
AMOS Unified Equation API & Dashboard Backend
===============================================

Central API layer unifying all equation systems:
- amos_superbrain_equation_bridge (33 domains)
- equation_knowledge_bridge (PL theory, invariants)
- invariant_verification_engine (neural-symbolic verification)

Provides single interface for equation queries, verification, and reasoning.
"""

import sys
from dataclasses import dataclass, field
from pathlib import Path

# Add subsystem paths
sys.path.insert(0, str(Path(__file__).parent / "01_BRAIN"))
sys.path.insert(0, str(Path(__file__).parent / "03_IMMUNE"))
sys.path.insert(0, str(Path(__file__).parent.parent))


class EquationSource(Protocol):
    """Protocol for equation sources."""

    def query(self, domain: str | None, pattern: str | None) -> list[dict]: ...
    def get_status(self) -> dict[str, Any]: ...


@dataclass
class UnifiedEquation:
    """Unified equation representation from any source."""

    id: str
    name: str
    formula: str
    source: str  # 'superbrain' | 'knowledge_bridge' | 'verification'
    domain: str
    description: str
    invariants: list[str] = field(default_factory=list)
    language: str | None = None


class UnifiedEquationAPI:
    """
    Unified API for all AMOS equation systems.

    Aggregates equations from:
    - SuperBrain (33 technology domains)
    - Knowledge Bridge (PL theory, formal semantics)
    - Verification Engine (neural-symbolic checking)
    """

    def __init__(self, organism_root: Path | None = None):
        self.organism_root = organism_root or Path(__file__).parent
        self.sources: dict[str, EquationSource] = {}
        self._initialize_sources()

    def _initialize_sources(self) -> None:
        """Initialize all equation sources."""
        # Try to initialize knowledge bridge
        try:
            from cognitive_equation_layer import CognitiveEquationLayer

            layer = CognitiveEquationLayer(self.organism_root)
            if layer.initialize():
                self.sources["knowledge_bridge"] = layer
        except ImportError:
            pass

        # Try to initialize verification engine
        try:
            from invariant_verification_engine import InvariantVerificationEngine

            engine = InvariantVerificationEngine(self.organism_root)
            self.sources["verification"] = engine
        except ImportError:
            pass

    def query_all(
        self,
        domain: str | None = None,
        language: str | None = None,
        pattern: str | None = None,
    ) -> list[UnifiedEquation]:
        """Query all equation sources."""
        results = []

        for source_name, source in self.sources.items():
            try:
                source_results = source.query(domain, pattern)
                for eq in source_results:
                    unified = UnifiedEquation(
                        id=eq.get("id", "unknown"),
                        name=eq.get("name", "Unknown"),
                        formula=eq.get("formula", eq.get("latex_formula", "")),
                        source=source_name,
                        domain=eq.get("domain", domain or "general"),
                        description=eq.get("description", ""),
                        invariants=eq.get("invariants", []),
                        language=eq.get("language", language),
                    )
                    results.append(unified)
            except Exception:
                continue

        return results

    def verify_code(
        self,
        code: str,
        language: str,
        categories: list[str] | None = None,
    ) -> dict[str, Any]:
        """Verify code using verification engine."""
        if "verification" not in self.sources:
            return {"error": "Verification engine not available"}

        engine = self.sources["verification"]
        return engine.get_verification_report(code, language)

    def get_dashboard_data(self) -> dict[str, Any]:
        """Get aggregated dashboard data."""
        total_equations = 0
        by_source = {}
        by_domain = {}

        for source_name, source in self.sources.items():
            status = source.get_status()
            count = status.get("equations_loaded", 0)
            by_source[source_name] = count
            total_equations += count

        return {
            "total_equations": total_equations,
            "by_source": by_source,
            "sources_active": len(self.sources),
            "coverage": {
                "programming_languages": 9,
                "invariant_categories": 6,
                "verification_status": "operational",
            },
        }

    def suggest_equations(self, context: str, language: str | None = None) -> list[dict]:
        """Suggest relevant equations for code context."""
        if "knowledge_bridge" not in self.sources:
            return []

        layer = self.sources["knowledge_bridge"]
        if hasattr(layer, "suggest_for_code"):
            return layer.suggest_for_code(context, language)
        return []


def main() -> int:
    """Test unified API."""
    print("[UnifiedEquationAPI] Initializing...")

    api = UnifiedEquationAPI()

    print("\n[Dashboard Data]")
    dashboard = api.get_dashboard_data()
    for key, value in dashboard.items():
        print(f"  {key}: {value}")

    # Test code verification
    test_code = """
def risky_function(items=[]):
    items.append(1)
    return items
"""
    print("\n[Code Verification - Python]")
    result = api.verify_code(test_code, "python")
    print(f"  Summary: {result.get('summary', {})}")

    if result.get("details"):
        for detail in result["details"][:3]:
            print(f"    {detail['invariant']}: {detail['status']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
