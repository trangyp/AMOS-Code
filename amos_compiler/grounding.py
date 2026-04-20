"""
AMOS Compiler: Grounding Engine
Maps human language terms to actual code symbols.

This is the core innovation: translating human concepts to repo concepts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from .intent_ir import ActionType, EditLevel, IntentIR
from .repo_graph import RepoGraph, Symbol


@dataclass
class GroundedConcept:
    """A human term grounded to code symbols."""

    human_term: str
    repo_concepts: list[str]  # e.g., ["Customer", "CustomerService"]
    symbols: list[Symbol] = field(default_factory=list)
    confidence: float = 0.0  # 0.0 to 1.0
    reasoning: str = ""


@dataclass
class EditScope:
    """The scope of files/symbols to be edited."""

    files: list[str] = field(default_factory=list)
    symbols: list[str] = field(default_factory=list)
    entrypoints: list[str] = field(default_factory=list)
    tests: list[str] = field(default_factory=list)
    docs: list[str] = field(default_factory=list)

    def is_empty(self) -> bool:
        return not any([self.files, self.symbols, self.entrypoints, self.tests, self.docs])


@dataclass
class GroundedIntent:
    """
    IntentIR grounded to actual repo symbols.

    This is the output of the Grounding Engine, ready for planning.
    """

    original: IntentIR
    grounded_concepts: list[GroundedConcept] = field(default_factory=list)
    edit_scope: EditScope = field(default_factory=EditScope)
    inferred_symbols: list[str] = field(default_factory=list)
    inferred_files: list[str] = field(default_factory=list)
    confidence: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "original_instruction": self.original.raw_instruction,
            "action": self.original.action.name,
            "grounded_concepts": [
                {
                    "human_term": gc.human_term,
                    "repo_concepts": gc.repo_concepts,
                    "symbol_count": len(gc.symbols),
                    "confidence": gc.confidence,
                    "reasoning": gc.reasoning,
                }
                for gc in self.grounded_concepts
            ],
            "edit_scope": {
                "files": self.edit_scope.files,
                "symbols": self.edit_scope.symbols,
                "entrypoints": self.edit_scope.entrypoints,
                "tests": self.edit_scope.tests,
                "docs": self.edit_scope.docs,
            },
            "confidence": self.confidence,
        }


class GroundingEngine:
    """
    Maps human language to code symbols using the glossary and repo graph.

    This implements the critical "understand in code" capability.
    """

    def __init__(self, repo_graph: RepoGraph):
        self.repo_graph = repo_graph
        self.glossary = repo_graph.glossary_terms

    def ground(self, intent: IntentIR) -> GroundedIntent:
        """
        Ground an IntentIR to actual repo symbols.

        Returns:
            GroundedIntent with resolved symbols and edit scope
        """
        grounded = GroundedIntent(original=intent)

        # Ground target domain
        if intent.target_domain.name != "unknown":
            concepts = self._ground_domain(intent.target_domain)
            grounded.grounded_concepts.extend(concepts)

        # Ground terms mentioned in instruction
        words = intent.raw_instruction.lower().split()
        for word in words:
            if word in self.glossary:
                concept = self._ground_term(word, self.glossary[word])
                if concept:
                    grounded.grounded_concepts.append(concept)

        # Determine edit scope based on grounded concepts
        grounded.edit_scope = self._determine_scope(
            intent.action,
            intent.edit_level,
            grounded.grounded_concepts,
        )

        # Calculate overall confidence
        if grounded.grounded_concepts:
            grounded.confidence = sum(gc.confidence for gc in grounded.grounded_concepts) / len(
                grounded.grounded_concepts
            )

        return grounded

    def _ground_domain(self, domain) -> list[GroundedConcept]:
        """Ground a target domain to symbols."""
        concepts = []

        # Ground glossary terms
        for term in domain.glossary_terms:
            if term in self.glossary:
                concept = self._ground_term(term, self.glossary[term])
                if concept:
                    concepts.append(concept)

        # Ground symbol patterns
        for pattern in domain.symbol_patterns:
            symbols = self.repo_graph.symbols_matching(f"*{pattern}*")
            if symbols:
                concepts.append(
                    GroundedConcept(
                        human_term=pattern,
                        repo_concepts=[s.name for s in symbols[:5]],
                        symbols=symbols,
                        confidence=0.7,
                        reasoning=f"Pattern match: {pattern}",
                    )
                )

        # Ground file patterns
        for pattern in domain.file_patterns:
            matching_files = [
                path for path in self.repo_graph.modules.keys() if pattern in path.lower()
            ]
            if matching_files:
                concepts.append(
                    GroundedConcept(
                        human_term=pattern,
                        repo_concepts=matching_files,
                        confidence=0.6,
                        reasoning=f"File pattern match: {pattern}",
                    )
                )

        return concepts

    def _ground_term(self, human_term: str, repo_concepts: list[str]) -> Optional[GroundedConcept]:
        """Ground a single glossary term to symbols."""
        symbols = []

        for concept in repo_concepts:
            # Try exact match
            symbol = self.repo_graph.get_symbol(concept)
            if symbol:
                symbols.append(symbol)
                continue

            # Try partial match
            matches = self.repo_graph.symbols_matching(f"*{concept}*")
            symbols.extend(matches)

        if not symbols:
            return GroundedConcept(
                human_term=human_term,
                repo_concepts=repo_concepts,
                confidence=0.3,
                reasoning="Term in glossary but no matching symbols found",
            )

        # Deduplicate symbols by full_name
        seen = set()
        unique_symbols = []
        for sym in symbols:
            key = sym.full_name()
            if key not in seen:
                seen.add(key)
                unique_symbols.append(sym)

        return GroundedConcept(
            human_term=human_term,
            repo_concepts=repo_concepts,
            symbols=unique_symbols,
            confidence=0.9,
            reasoning=f"Found {len(unique_symbols)} matching symbols",
        )

    def _determine_scope(
        self,
        action: ActionType,
        edit_level: EditLevel,
        grounded_concepts: list[GroundedConcept],
    ) -> EditScope:
        """Determine the edit scope from grounded concepts."""
        scope = EditScope()

        # Collect all referenced files and symbols
        all_files = set()
        all_symbols = set()

        for concept in grounded_concepts:
            for symbol in concept.symbols:
                all_symbols.add(symbol.full_name())
                all_files.add(symbol.file_path)

        # Add files from concept matches
        for concept in grounded_concepts:
            for repo_concept in concept.repo_concepts:
                if ".py" in repo_concept:
                    all_files.add(repo_concept)

        # For symbol-level edits, include dependent files
        if edit_level in (EditLevel.SYMBOL, EditLevel.SEMANTIC):
            for symbol_name in all_symbols:
                dependents = self.repo_graph.get_dependents(symbol_name)
                for dep in dependents:
                    all_symbols.add(dep)
                    # Find file for this symbol
                    if ":" in dep:
                        file_path = dep.split(":")[0]
                        all_files.add(file_path)

        scope.symbols = list(all_symbols)
        scope.files = list(all_files)

        # Find related tests
        scope.tests = self._find_related_tests(scope.files)

        # Find related docs
        scope.docs = self._find_related_docs(scope.files)

        # Find affected entrypoints
        for file_path in scope.files:
            entrypoints = self.repo_graph.get_entrypoints_for_path(file_path)
            scope.entrypoints.extend([ep.name for ep in entrypoints])

        return scope

    def _find_related_tests(self, files: list[str]) -> list[str]:
        """Find test files related to the given source files."""
        tests = []
        for file_path in files:
            # Look for test file patterns
            module_name = file_path.replace(".py", "").replace("/", ".")

            # Check for test_* pattern
            test_patterns = [
                f"tests/test_{file_path}",
                f"tests/{file_path.replace('.py', '_test.py')}",
            ]

            for pattern in test_patterns:
                if pattern in self.repo_graph.modules:
                    tests.append(pattern)

        return tests

    def _find_related_docs(self, files: list[str]) -> list[str]:
        """Find documentation files related to the given source files."""
        docs = []
        # Look for markdown files in docs/ referencing these files
        # This is a simplified implementation
        return docs


def ground_intent(intent: IntentIR, repo_graph: RepoGraph) -> GroundedIntent:
    """Convenience function to ground an intent."""
    engine = GroundingEngine(repo_graph)
    return engine.ground(intent)
