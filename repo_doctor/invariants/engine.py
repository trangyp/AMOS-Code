"""
InvariantEngine - runs all invariants and produces state vectors.

A simplified version for the Ω∞ module.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .api import APIInvariant
from .base import InvariantResult
from .entrypoints import EntrypointInvariant
from .history import HistoryInvariant
from .imports import ImportInvariant
from .packaging import PackagingInvariant
from .parse import ParseInvariant
from .persistence import PersistenceInvariant
from .runtime import RuntimeInvariant
from .security import SecurityInvariant
from .status import StatusInvariant
from .tests import TestsInvariant
from .types import TypeInvariant


class InvariantEngine:
    """
    The Invariant Engine runs all 12 hard invariants.

    RepoValid = ∧n I_n for n in 12 dimensions
    """

    INVARIANT_CLASSES = [
        ParseInvariant,
        ImportInvariant,
        TypeInvariant,
        APIInvariant,
        EntrypointInvariant,
        PackagingInvariant,
        RuntimeInvariant,
        PersistenceInvariant,
        StatusInvariant,
        TestsInvariant,
        SecurityInvariant,
        HistoryInvariant,
    ]

    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path).resolve()
        self.invariants = [cls() for cls in self.INVARIANT_CLASSES]

    def run_all(self, context: dict[str, Any] | None = None) -> list[InvariantResult]:
        """Run all invariants and return results."""
        results = []
        for invariant in self.invariants:
            result = invariant.check(str(self.repo_path), context)
            results.append(result)
        return results

    def check_specific(
        self, invariant_name: str, context: dict[str, Any] | None = None
    ) -> InvariantResult:
        """Run a specific invariant by name."""
        for invariant in self.invariants:
            if invariant.name == invariant_name:
                return invariant.check(str(self.repo_path), context)
        raise ValueError(f"Unknown invariant: {invariant_name}")

    def get_failing(self, results: list[InvariantResult]) -> list[str]:
        """Get list of failing invariant names."""
        return [r.name for r in results if not r.passed]
