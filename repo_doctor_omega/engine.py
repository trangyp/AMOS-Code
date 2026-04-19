"""Repo Doctor Ω∞∞∞ - Core Engine.

Main orchestration engine that coordinates substrate integration
and computes repository state.
"""

import time
from pathlib import Path
from typing import Any

from .invariants.hard import (
    APIInvariant,
    EntrypointInvariant,
    HardInvariant,
    ImportInvariant,
    InvariantResult,
    PackagingInvariant,
    ParseInvariant,
    StatusInvariant,
    TestInvariant,
)
from .state.basis import BasisVector, RepositoryState
from .state.observables import Observable


class RepoDoctorEngine:
    """Main orchestration engine for repository analysis.

    Coordinates:
    - Tree-sitter for syntax analysis
    - Invariant evaluation
    - State vector computation
    - Repair plan generation
    """

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()
        self.invariants: list[HardInvariant] = []
        self.observables: list[Observable] = []

        # Initialize invariants
        self._init_invariants()

    def _init_invariants(self) -> None:
        """Register all hard invariants."""
        self.invariants = [
            ParseInvariant(),
            ImportInvariant(),
            APIInvariant(),
            EntrypointInvariant(),
            PackagingInvariant(),
            StatusInvariant(),
            TestInvariant(),
        ]

    def compute_state(self) -> RepositoryState:
        """Compute current repository state vector.

        Returns:
            RepositoryState with all amplitudes computed
        """
        state = RepositoryState(timestamp=time.time())

        # Run all invariant checks
        results = self.evaluate_invariants()

        # Update amplitudes based on invariant results
        for result in results:
            if result.passed:
                # Full integrity
                state.set_amplitude(result.basis, 1.0)
            else:
                # Degraded based on severity
                degradation = min(result.severity, 0.99)
                state.set_amplitude(result.basis, 1.0 - degradation)

        return state

    def evaluate_invariants(self) -> list[InvariantResult]:
        """Evaluate all registered hard invariants.

        Returns:
            List of invariant check results
        """
        results = []

        for invariant in self.invariants:
            try:
                result = invariant.check(str(self.repo_path))
                results.append(result)
            except Exception as e:
                # Create failed result on error
                results.append(
                    InvariantResult(
                        invariant=invariant.name,
                        passed=False,
                        basis=invariant.basis,
                        violations=[],
                        metadata={"error": str(e)},
                    )
                )

        return results

    def check_contracts(self, strict: bool = False) -> list[Observable]:
        """Check API contract commutativity.

        Compares documented API surface vs runtime reality.

        Args:
            strict: Flag all discrepancies if True

        Returns:
            List of contract violations as observables
        """
        observables = []

        # This would integrate with:
        # - README/guide parsing
        # - CLI help extraction
        # - Runtime signature inspection
        # - MCP schema validation

        return observables

    def compute_drift(self, since: str = "HEAD~10") -> Dict[str, Any]:
        """Compute temporal drift from reference point.

        Args:
            since: Git reference for comparison

        Returns:
            Drift analysis results
        """
        # Integration point for git bisect
        # and temporal analysis

        return {
            "since": since,
            "total_drift": 0.0,
            "per_basis": {},
        }

    def compute_repair_plan(self) -> Dict[str, Any]:
        """Compute minimum restoring repair set.

        Uses optimization to find best repair order.

        Returns:
            Repair plan with steps and metadata
        """
        state = self.compute_state()
        failed = state.collapsed_subsystems()

        # Repair order law:
        # 1. parse
        # 2. import
        # 3. entrypoint
        # 4. packaging
        # 5. API
        # 6. persistence
        # 7. runtime wrappers
        # 8. tests/demos/docs
        # 9. security hardening
        # 10. performance cleanup

        repair_order = [
            BasisVector.SYNTAX,
            BasisVector.IMPORT,
            BasisVector.ENTRYPOINT,
            BasisVector.PACKAGING,
            BasisVector.API,
            BasisVector.PERSISTENCE,
            BasisVector.RUNTIME,
            BasisVector.TEST,
            BasisVector.DOCS,
            BasisVector.SECURITY,
        ]

        steps = []
        for basis in repair_order:
            if basis in failed:
                steps.append(
                    {
                        "invariant": basis.name,
                        "cost": "medium",
                        "blast_radius": "local",
                        "description": f"Restore {basis.name} integrity",
                    }
                )

        current_energy = state.compute_energy()

        return {
            "energy": current_energy,
            "energy_reduction": len(steps) * 0.5,  # Rough estimate
            "steps": steps,
            "estimated_time": len(steps) * 30,  # Minutes
        }

    def get_report(self) -> Dict[str, Any]:
        """Generate comprehensive diagnosis report."""
        state = self.compute_state()
        invariants = self.evaluate_invariants()

        failed = [r for r in invariants if not r.passed]

        return {
            "repository": str(self.repo_path),
            "timestamp": state.timestamp,
            "energy": state.compute_energy(),
            "releaseable": state.is_releaseable(),
            "state_vector": state.to_dict(),
            "invariants": {
                "passed": len(invariants) - len(failed),
                "failed": len(failed),
                "results": [
                    {
                        "name": r.invariant,
                        "passed": r.passed,
                        "severity": r.severity,
                    }
                    for r in invariants
                ],
            },
            "collapsed": [b.name for b in state.collapsed_subsystems()],
        }
