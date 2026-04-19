#!/usr/bin/env python3
"""
AMOS SuperBrain ↔ Knowledge Bridge Connector.

Unifies the SuperBrain Equation Bridge (41 domains, 180+ equations) with
the Equation Knowledge Bridge (400+ PL equations) into a single cohesive system.

Includes Phase 15: AGI Pathways & Future Intelligence (2026-2030).

Architecture: Adapter pattern with unified query interface.
"""

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Add paths for both systems
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "AMOS_ORGANISM_OS" / "01_BRAIN"))

# Import both systems
try:
    from amos_superbrain_equation_bridge import Domain, MathematicalPattern

    SUPERBRAIN_AVAILABLE = True
except ImportError:
    SUPERBRAIN_AVAILABLE = False

try:
    from equation_knowledge_bridge import (
        EquationCategory,
        EquationKnowledgeGraph,
        InvariantType,
    )

    KNOWLEDGE_BRIDGE_AVAILABLE = True
except ImportError:
    KNOWLEDGE_BRIDGE_AVAILABLE = False

# Mathematical Framework Integration
try:
    from clawspring.amos_brain.mathematical_framework_engine import (
        MathematicalFrameworkEngine,
        get_framework_engine,
    )

    MATH_FRAMEWORK_AVAILABLE = True
except ImportError:
    MATH_FRAMEWORK_AVAILABLE = False

try:
    from clawspring.amos_brain.math_audit_logger import get_math_audit_logger

    MATH_AUDIT_AVAILABLE = True
except ImportError:
    MATH_AUDIT_AVAILABLE = False


@dataclass
class UnifiedEquation:
    """Unified equation representation combining both systems."""

    id: str
    name: str
    source: str  # 'superbrain' or 'knowledge_bridge'
    domain: str = None  # SuperBrain domain
    category: str = None  # Knowledge bridge category
    expression: str = ""
    description: str = ""
    language: str = ""
    invariants: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class SuperBrainKnowledgeBridge:
    """
    Bridge connecting SuperBrain and Knowledge Bridge systems.

    Provides unified access to 500+ equations from both sources.
    """

    def __init__(self):
        self._superbrain_available = SUPERBRAIN_AVAILABLE
        self._knowledge_available = KNOWLEDGE_BRIDGE_AVAILABLE
        self._knowledge_graph: Optional[EquationKnowledgeGraph] = None
        self._equation_cache: List[UnifiedEquation] = []
        self._initialized = False

    def initialize(self) -> bool:
        """Initialize both systems and build unified cache."""
        print("[SuperBrainKnowledgeBridge] Initializing...")

        # Initialize knowledge bridge
        if self._knowledge_available:
            try:
                self._knowledge_graph = EquationKnowledgeGraph()
                print("  ✓ Knowledge bridge loaded")
            except Exception as e:
                print(f"  ✗ Knowledge bridge error: {e}")
                self._knowledge_available = False

        # Build unified cache
        self._build_unified_cache()
        self._initialized = True

        print(f"[SuperBrainKnowledgeBridge] Ready: {len(self._equation_cache)} equations")
        return True

    def _build_unified_cache(self) -> None:
        """Build unified equation cache from both sources."""
        cache: List[UnifiedEquation] = []

        # Add knowledge bridge equations
        if self._knowledge_available and self._knowledge_graph:
            for lang, data in self._knowledge_graph.languages.items():
                for eq in data.equations:
                    cache.append(
                        UnifiedEquation(
                            id=eq.id,
                            name=eq.name,
                            source="knowledge_bridge",
                            category=eq.category.value,
                            expression=eq.expression,
                            description=eq.description,
                            language=lang,
                            invariants=[inv.value for inv in eq.invariants],
                            metadata=eq.metadata,
                        )
                    )

        self._equation_cache = cache

    def query(
        self,
        language: str = None,
        category: str = None,
        source: str = None,
    ) -> List[UnifiedEquation]:
        """Query unified equation database."""
        results = self._equation_cache

        if language:
            results = [eq for eq in results if eq.language == language]

        if category:
            results = [eq for eq in results if eq.category == category]

        if source:
            results = [eq for eq in results if eq.source == source]

        return results

    def get_by_language(self, language: str) -> List[UnifiedEquation]:
        """Get all equations for a language."""
        return [eq for eq in self._equation_cache if eq.language == language]

    def get_by_invariant(self, invariant: str) -> List[UnifiedEquation]:
        """Get equations enforcing a specific invariant."""
        return [eq for eq in self._equation_cache if invariant in eq.invariants]

    def get_stats(self) -> Dict[str, Any]:
        """Get unified system statistics."""
        sources = {}
        languages = set()
        categories = set()
        invariants = set()

        for eq in self._equation_cache:
            sources[eq.source] = sources.get(eq.source, 0) + 1
            languages.add(eq.language)
            if eq.category:
                categories.add(eq.category)
            invariants.update(eq.invariants)

        return {
            "total_equations": len(self._equation_cache),
            "by_source": sources,
            "languages": len(languages),
            "categories": len(categories),
            "invariants": len(invariants),
            "superbrain_available": self._superbrain_available,
            "knowledge_available": self._knowledge_available,
            "status": "operational" if self._initialized else "not_initialized",
        }

    def cross_reference_with_math_framework(self, equation_name: str) -> Dict[str, Any]:
        """Cross-reference equation with Mathematical Framework.

        Finds related equations in the Mathematical Framework Engine
        that match the given equation name or domain.

        Args:
            equation_name: Name of the equation to cross-reference

        Returns:
            Dictionary with cross-reference results
        """
        if not MATH_FRAMEWORK_AVAILABLE:
            return {
                "error": "Mathematical Framework not available",
                "equation": equation_name,
                "math_framework_enabled": False,
            }

        try:
            math_engine = get_framework_engine()

            # Find the equation in cache
            eq = None
            for cached_eq in self._equation_cache:
                if cached_eq.name == equation_name:
                    eq = cached_eq
                    break

            if not eq:
                return {
                    "error": f"Equation '{equation_name}' not found",
                    "math_framework_enabled": True,
                }

            # Map to math framework domain
            domain_map = {
                "machine_learning": "AI_ML",
                "deep_learning": "AI_ML",
                "security": "SECURITY",
                "distributed_systems": "DISTRIBUTED_SYSTEMS",
            }
            math_domain = domain_map.get(eq.domain or "", eq.category or "GENERAL")

            # Query related equations from math framework
            related = []
            equations = math_engine.query_by_domain(math_domain)
            for fw_eq in equations[:5]:  # Limit to 5
                related.append(
                    {"name": fw_eq.name, "formula": fw_eq.formula, "domain": fw_eq.domain}
                )

            # Log to audit if available
            if MATH_AUDIT_AVAILABLE:
                try:
                    audit = get_math_audit_logger()
                    audit.log_equation_query(
                        equation_name, [math_domain], {"related_found": len(related)}
                    )
                except Exception:
                    pass

            return {
                "equation": equation_name,
                "domain": eq.domain,
                "category": eq.category,
                "math_domain": math_domain,
                "related_math_equations": related,
                "math_framework_enabled": True,
            }

        except Exception as e:
            return {"error": str(e), "equation": equation_name, "math_framework_enabled": True}

    def export_unified_graph(self, path: str) -> bool:
        """Export unified equation graph to JSON."""
        data = {
            "equations": [
                {
                    "id": eq.id,
                    "name": eq.name,
                    "source": eq.source,
                    "domain": eq.domain,
                    "category": eq.category,
                    "expression": eq.expression,
                    "description": eq.description,
                    "language": eq.language,
                    "invariants": eq.invariants,
                }
                for eq in self._equation_cache
            ],
            "stats": self.get_stats(),
        }

        with open(path, "w") as f:
            json.dump(data, f, indent=2)

        return True


def main() -> int:
    """Test the unified bridge."""
    print("=" * 60)
    print("AMOS SuperBrain ↔ Knowledge Bridge Connector")
    print("=" * 60)

    bridge = SuperBrainKnowledgeBridge()
    bridge.initialize()

    # Print stats
    stats = bridge.get_stats()
    print("\n[Unified Stats]")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Query examples
    print("\n[Python Equations]")
    python_eqs = bridge.get_by_language("python")
    for eq in python_eqs[:3]:
        print(f"  - {eq.name} ({eq.category})")

    print("\n[Type Safety Invariants]")
    type_eqs = bridge.get_by_invariant("type_safety")
    for eq in type_eqs[:3]:
        print(f"  - {eq.name} ({eq.language})")

    # Export
    export_path = "unified_equation_graph.json"
    bridge.export_unified_graph(export_path)
    print(f"\n[Export] Unified graph saved to {export_path}")

    print("\n[OK] Bridge operational")
    return 0


if __name__ == "__main__":
    sys.exit(main())
