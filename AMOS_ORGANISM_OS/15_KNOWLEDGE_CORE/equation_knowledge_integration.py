#!/usr/bin/env python3
"""
AMOS Equation Knowledge Integration
====================================

Integrates exhaustive equation research into AMOS Knowledge Core.
Connects EXHAUSTIVE_EQUATIONS_INVARIANTS_ALL_LANGUAGES.md to the ecosystem.
"""

import json
import sys
from pathlib import Path
from typing import Any

# Add brain module to path
sys.path.insert(0, str(Path(__file__).parent.parent / "01_BRAIN"))

try:
    from equation_knowledge_bridge import (
        EquationKnowledgeGraph,
        EquationParser,
        EquationReasoningEngine,
        build_equation_knowledge_base,
    )

    BRIDGE_AVAILABLE = True
except ImportError as e:
    print(f"[WARN] Equation bridge not available: {e}")
    BRIDGE_AVAILABLE = False


class EquationKnowledgeIntegration:
    """Integration layer for equation knowledge in AMOS ecosystem."""

    def __init__(self, organism_root: Optional[Path] = None):
        self.organism_root = organism_root or Path(__file__).parent.parent
        self.knowledge_graph: Optional[EquationKnowledgeGraph] = None
        self.reasoning_engine: Optional[EquationReasoningEngine] = None
        self._initialized = False

    def initialize(self) -> bool:
        """Initialize equation knowledge from exhaustive document."""
        if not BRIDGE_AVAILABLE:
            return False

        doc_path = self.organism_root.parent / "EXHAUSTIVE_EQUATIONS_INVARIANTS_ALL_LANGUAGES.md"
        output_path = self.organism_root / "15_KNOWLEDGE_CORE" / "equation_knowledge_graph.json"

        if doc_path.exists():
            try:
                self.knowledge_graph = build_equation_knowledge_base(doc_path, output_path)
                self.reasoning_engine = EquationReasoningEngine(self.knowledge_graph)
                self._initialized = True
                return True
            except Exception as e:
                print(f"[ERROR] Failed to initialize equation knowledge: {e}")
                return False
        else:
            print(f"[WARN] Equation document not found: {doc_path}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get integration status."""
        return {
            "initialized": self._initialized,
            "bridge_available": BRIDGE_AVAILABLE,
            "equations_loaded": len(self.knowledge_graph.equations) if self.knowledge_graph else 0,
            "languages_profiled": len(self.knowledge_graph.languages)
            if self.knowledge_graph
            else 0,
        }

    def query_equations(self, category: str = None, language: str = None) -> List[dict]:
        """Query equations by category or language."""
        if not self.knowledge_graph:
            return []

        results = []
        for eq in self.knowledge_graph.equations.values():
            if category and eq.category.value != category:
                continue
            if language and eq.language != language:
                continue
            results.append(eq.to_dict())
        return results


def main():
    """Test equation knowledge integration."""
    integration = EquationKnowledgeIntegration()

    if integration.initialize():
        print("[OK] Equation knowledge integration initialized")
        print(f"Status: {json.dumps(integration.get_status(), indent=2)}")

        # Test query
        rust_eqs = integration.query_equations(language="rust")
        print(f"\nFound {len(rust_eqs)} Rust equations")
    else:
        print("[FAIL] Failed to initialize equation knowledge")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
