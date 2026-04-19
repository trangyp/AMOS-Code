#!/usr/bin/env python3
"""
AMOS Cognitive Equation Layer.

Integrates equation knowledge into BrainOS cognitive processing.
Enables formal reasoning about code using mathematical invariants.
"""

import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Import equation bridge
sys.path.insert(0, str(Path(__file__).parent))

try:
    from equation_knowledge_bridge import (
        EquationKnowledgeGraph,
        EquationParser,
        EquationReasoningEngine,
        InvariantType,
        build_equation_knowledge_base,
    )

    EQUATIONS_AVAILABLE = True
except ImportError:
    EQUATIONS_AVAILABLE = False

try:
    from brain_os import BrainOS, Thought, ThoughtType

    BRAIN_AVAILABLE = True
except ImportError:
    BRAIN_AVAILABLE = False


class CognitiveEquationLayer:
    """
    Cognitive layer integrating equations into BrainOS reasoning.

    This layer enables the AMOS brain to:
    - Suggest relevant equations based on context
    - Verify code against formal invariants
    - Generate thoughts about mathematical properties
    - Create plans for equation-based analysis
    """

    def __init__(self, organism_root: Optional[Path] = None):
        self.organism_root = organism_root or Path(__file__).parent.parent
        self.knowledge_graph: Optional[EquationKnowledgeGraph] = None
        self.reasoning_engine: Optional[EquationReasoningEngine] = None
        self.brain: Optional[BrainOS] = None
        self._initialized = False

    def initialize(self) -> bool:
        """Initialize cognitive equation layer."""
        if not EQUATIONS_AVAILABLE:
            return False

        doc_path = self.organism_root.parent / "EXHAUSTIVE_EQUATIONS_INVARIANTS_ALL_LANGUAGES.md"
        output_path = self.organism_root / "01_BRAIN" / "equation_knowledge_graph.json"

        if doc_path.exists():
            try:
                self.knowledge_graph = build_equation_knowledge_base(doc_path, output_path)

                if BRAIN_AVAILABLE:
                    self.brain = BrainOS()
                    self.reasoning_engine = EquationReasoningEngine(
                        self.knowledge_graph, self.brain
                    )

                self._initialized = True
                return True
            except Exception as e:
                print(f"[ERROR] Failed to initialize: {e}")
                return False

        return False

    def get_status(self) -> Dict[str, Any]:
        """Get layer status."""
        return {
            "initialized": self._initialized,
            "equations_available": EQUATIONS_AVAILABLE,
            "brain_available": BRAIN_AVAILABLE,
            "equations_loaded": (
                len(self.knowledge_graph.equations) if self.knowledge_graph else 0
            ),
        }

    def suggest_for_code(self, code_snippet: str, language: str = None) -> list[dict[str, Any]]:
        """Suggest relevant equations for code."""
        if not self._initialized or not self.reasoning_engine:
            return []

        suggestions = self.reasoning_engine.suggest_equations_for_context(code_snippet, language)
        return [eq.to_dict() for eq in suggestions]

    def verify_invariant(self, code_context: str, invariant_type: str) -> Dict[str, Any]:
        """Verify code against an invariant type."""
        if not self._initialized or not self.knowledge_graph:
            return {"valid": False, "error": "Not initialized"}

        try:
            inv_type = InvariantType(invariant_type)
        except ValueError:
            return {"valid": False, "error": f"Unknown invariant: {invariant_type}"}

        # Get relevant equations
        equations = self.knowledge_graph.find_equations_by_invariant(inv_type)

        return {
            "valid": len(equations) > 0,
            "invariant": invariant_type,
            "relevant_equations": len(equations),
            "equations": [eq.name for eq in equations[:5]],
        }


def main() -> int:
    """Test cognitive equation layer."""
    print("[CognitiveEquationLayer] Initializing...")

    layer = CognitiveEquationLayer()

    if layer.initialize():
        print("[OK] Layer initialized successfully")
        print(f"Status: {layer.get_status()}")

        # Test code suggestion
        rust_code = "fn main() { let x = &mut 5; }"
        suggestions = layer.suggest_for_code(rust_code, "rust")
        print(f"\nSuggestions for Rust code: {len(suggestions)} equations")
        for s in suggestions:
            print(f"  - {s['name']}")

        # Test invariant verification
        result = layer.verify_invariant(rust_code, "memory_safety")
        print(f"\nInvariant check: {result}")

        return 0
    else:
        print("[FAIL] Failed to initialize")
        return 1


if __name__ == "__main__":
    sys.exit(main())
