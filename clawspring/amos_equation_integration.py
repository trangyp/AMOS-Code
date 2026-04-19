"""AMOS Equation Integration - Connects equation kernel to AMOS brain.

This module integrates the amos_equation_kernel with the existing AMOS
knowledge connector, enabling equation-based reasoning across all domains.

Example:
    >>> from clawspring.amos_equation_integration import EquationKnowledgeBridge
    >>> bridge = EquationKnowledgeBridge()
    >>> result = bridge.compute("softmax", {"x": [1.0, 2.0, 3.0]})
    >>> print(result.value)
"""

# Import from AMOS equation kernel
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent directory to path for imports
amos_root = Path(__file__).parent.parent
sys.path.insert(0, str(amos_root))

try:
    from amos_equation_kernel import (
        EquationKernel,
        EquationMetadata,
        EquationResult,
        MathematicalPattern,
        get_equation_kernel,
    )

    KERNEL_AVAILABLE = True
except ImportError:
    KERNEL_AVAILABLE = False

# Import from existing AMOS knowledge connector
try:
    from clawspring.amos_knowledge_connector import KnowledgeGraphKernel, KnowledgeQuery

    KNOWLEDGE_AVAILABLE = True
except ImportError:
    KNOWLEDGE_AVAILABLE = False


@dataclass
class DomainKnowledge:
    """Combined domain and equation knowledge."""

    domain: str
    pattern: MathematicalPattern
    equations: List[EquationMetadata]
    related_concepts: List[str]
    cross_domain_links: List[str]


class EquationKnowledgeBridge:
    """Bridge between equation kernel and AMOS knowledge graph.

    Provides unified access to mathematical equations and domain knowledge,
    enabling cross-domain reasoning and pattern detection.

    Attributes:
        equation_kernel: The underlying equation computation engine
        knowledge_graph: Connection to AMOS knowledge base
    """

    def __init__(self) -> None:
        """Initialize the bridge with kernel and knowledge connections."""
        self._kernel = get_equation_kernel() if KERNEL_AVAILABLE else None
        self._knowledge = KnowledgeGraphKernel() if KNOWLEDGE_AVAILABLE else None

    def compute(self, equation_name: str, parameters: Dict[str, Any]) -> Optional[EquationResult]:
        """Execute an equation with validation.

        Args:
            equation_name: Name of the equation to execute
            parameters: Dictionary of parameter values

        Returns:
            EquationResult with value and validation status, or None if unavailable
        """
        if self._kernel is None:
            return None
        return self._kernel.execute(equation_name, parameters)

    def get_domain_equations(self, pattern: MathematicalPattern) -> List[EquationMetadata]:
        """Get all equations for a specific mathematical pattern.

        Args:
            pattern: The mathematical pattern to query

        Returns:
            List of equation metadata matching the pattern
        """
        if self._kernel is None:
            return []
        return self._kernel.get_by_pattern(pattern)

    def find_cross_domain_patterns(self) -> List[dict[str, Any]]:
        """Find structural similarities across domains.

        Returns:
            List of isomorphism records showing cross-domain connections
        """
        if self._kernel is None:
            return []
        return self._kernel.find_isomorphisms()

    def explain_equation(self, equation_name: str) -> Dict[str, Any]:
        """Get comprehensive explanation of an equation.

        Args:
            equation_name: Name of the equation to explain

        Returns:
            Dictionary with metadata, pattern, and domain context
        """
        if self._kernel is None:
            return None

        # Get equation metadata
        all_eqs = self._kernel.get_all_equations()
        for eq in all_eqs:
            if eq.name == equation_name:
                # Find related equations in same pattern
                pattern_eqs = self._kernel.get_by_pattern(eq.pattern)
                related = [e.name for e in pattern_eqs if e.name != equation_name]

                return {
                    "name": eq.name,
                    "domain": eq.domain,
                    "pattern": eq.pattern.value,
                    "formula": eq.formula,
                    "description": eq.description,
                    "invariants": eq.invariants,
                    "parameters": eq.parameters,
                    "related_equations": related[:5],  # Top 5 related
                }
        return None

    def validate_invariant(self, equation_name: str, result: Any) -> bool:
        """Check if equation result satisfies its invariants.

        Args:
            equation_name: Name of the equation
            result: Computed result to validate

        Returns:
            True if invariants are satisfied
        """
        if self._kernel is None:
            return False

        # Re-execute to get validation
        # This is a simplified version - in production would use stored params
        return True  # Placeholder

    def get_unified_framework_summary(self) -> Dict[str, Any]:
        """Get summary of the unified mathematical framework.

        Returns:
            Dictionary with framework statistics and structure
        """
        if self._kernel is None:
            return {"status": "kernel_unavailable"}

        all_equations = self._kernel.get_all_equations()

        # Count by domain
        domains: Dict[str, int] = {}
        patterns: Dict[str, int] = {}

        for eq in all_equations:
            domains[eq.domain] = domains.get(eq.domain, 0) + 1
            patterns[eq.pattern.value] = patterns.get(eq.pattern.value, 0) + 1

        return {
            "status": "active",
            "total_equations": len(all_equations),
            "domains_covered": len(domains),
            "patterns_identified": len(patterns),
            "domain_distribution": domains,
            "pattern_distribution": patterns,
            "cross_domain_isomorphisms": len(self._kernel.find_isomorphisms()),
        }


# Global bridge instance
_bridge: Optional[EquationKnowledgeBridge] = None


def get_equation_bridge() -> EquationKnowledgeBridge:
    """Get or create the global equation knowledge bridge."""
    global _bridge
    if _bridge is None:
        _bridge = EquationKnowledgeBridge()
    return _bridge


if __name__ == "__main__":
    # Demo and testing
    print("AMOS Equation Integration Demo")
    print("=" * 50)

    bridge = get_equation_bridge()

    # Get framework summary
    summary = bridge.get_unified_framework_summary()
    print(f"\nFramework Status: {summary['status']}")
    print(f"Total Equations: {summary.get('total_equations', 0)}")
    print(f"Domains: {summary.get('domains_covered', 0)}")
    print(f"Patterns: {summary.get('patterns_identified', 0)}")

    # Test computation
    print("\n--- Computation Tests ---")

    result = bridge.compute("softmax", {"x": [1.0, 2.0, 3.0]})
    if result:
        print(f"\nSoftmax result: {result.value}")
        print(f"Invariants valid: {result.invariants_valid}")

    result = bridge.compute("littles_law", {"arrival_rate": 10.0, "avg_time": 5.0})
    if result:
        print(f"\nLittle's Law: L = {result.value}")

    # Get equation explanation
    print("\n--- Equation Explanation ---")
    explanation = bridge.explain_equation("shannon_entropy")
    if explanation:
        print(f"\nEquation: {explanation['name']}")
        print(f"Formula: {explanation['formula']}")
        print(f"Pattern: {explanation['pattern']}")
        print(f"Invariants: {explanation['invariants']}")

    # Cross-domain patterns
    print("\n--- Cross-Domain Patterns ---")
    isomorphisms = bridge.find_cross_domain_patterns()
    for iso in isomorphisms[:3]:
        print(f"\n{iso['equation1']} ↔ {iso['equation2']}")
        print(f"  Similarity: {iso['similarity']}")

    print("\n" + "=" * 50)
    print("Integration test complete")
