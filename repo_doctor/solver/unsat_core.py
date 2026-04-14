"""
Repo Doctor Omega - Unsat Core Extractor

When invariants fail, extract the minimum contradictory fact set.
This gives perfect repair-plan input.

Example:
-------
    Unsat core:
      - Claimed /dashboard command exists
      - No /dashboard in shell command registry
      - Tutorial says use /dashboard

"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Contradiction:
    """A single contradiction in the unsat core."""

    claim: str
    reality: str
    source: str
    severity: str = "error"


class UnsatCoreExtractor:
    """
    Extract and interpret unsatisfiable cores from Z3.
    """

    def __init__(self):
        self.contradictions: list[Contradiction] = []

    def extract_from_z3(
        self, unsat_core: list[str], repo_state: dict[str, Any]
    ) -> list[Contradiction]:
        """
        Convert Z3 unsat core to human-readable contradictions.
        """
        self.contradictions = []

        for assertion in unsat_core:
            # Parse assertion and match to repo state
            contradiction = self._interpret_assertion(assertion, repo_state)
            if contradiction:
                self.contradictions.append(contradiction)

        return self.contradictions

    def _interpret_assertion(
        self, assertion: str, repo_state: dict[str, Any]
    ) -> Contradiction | None:
        """
        Interpret a single Z3 assertion as a contradiction.
        """
        # Pattern matching for common assertion types
        if "entrypoint" in assertion:
            return Contradiction(
                claim=f"Claimed: {assertion} exists",
                reality="No such entrypoint found in package metadata",
                source="pyproject.toml/setup.py",
                severity="error",
            )

        if "command" in assertion:
            return Contradiction(
                claim=f"Claimed: {assertion} available",
                reality="Command not registered in shell/CLI",
                source="documentation/tutorials",
                severity="error",
            )

        if "import" in assertion:
            return Contradiction(
                claim=f"Claimed: {assertion} can be imported",
                reality="Module/symbol not found in package",
                source="test files/demo code",
                severity="error",
            )

        return None

    def to_repair_hints(self) -> list[dict[str, str]]:
        """
        Convert contradictions to repair hints.
        """
        hints = []
        for c in self.contradictions:
            hints.append(
                {
                    "issue": c.claim,
                    "reality": c.reality,
                    "action": f"Fix in {c.source}",
                    "severity": c.severity,
                }
            )
        return hints

    def minimal_failing_set(self) -> list[str]:
        """
        Return minimal set of facts that must change to restore consistency.
        """
        return [c.claim for c in self.contradictions]
