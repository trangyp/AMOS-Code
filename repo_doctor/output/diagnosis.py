"""
Repo Doctor Omega - Diagnosis Generator

Generate doctor-quality output:
- State vector with all 11 dimensions
- Energy calculation
- Hard invariant failures
- Minimal failing cut
- First bad commits
"""

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class DiagnosisReport:
    """Complete diagnosis report."""

    repository: str
    commit_hash: str
    branch: str

    # State vector
    state_vector: Dict[str, float] = field(default_factory=dict)

    # Energy
    energy: float = 0.0
    energy_threshold: float = 2.0
    is_stable: bool = True

    # Invariants
    hard_failures: list[dict[str, Any]] = field(default_factory=list)
    is_valid: bool = True

    # Minimal failing cut
    minimal_cut: List[str] = field(default_factory=list)

    # First bad commits
    first_bad_commits: Dict[str, str] = field(default_factory=dict)

    # Score
    score: int = 100
    is_releaseable: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "repository": self.repository,
            "commit_hash": self.commit_hash,
            "branch": self.branch,
            "state_vector": self.state_vector,
            "energy": {
                "value": self.energy,
                "threshold": self.energy_threshold,
                "is_stable": self.is_stable,
            },
            "invariants": {
                "failed": self.hard_failures,
                "is_valid": self.is_valid,
            },
            "minimal_failing_cut": self.minimal_cut,
            "first_bad_commits": self.first_bad_commits,
            "score": self.score,
            "is_releaseable": self.is_releaseable,
        }

    def to_json(self, indent: int = 2) -> str:
        """Export as JSON."""
        return json.dumps(self.to_dict(), indent=indent)

    def to_markdown(self) -> str:
        """Export as Markdown report."""
        lines = [
            "# Repo Doctor Omega - Diagnosis Report",
            "",
            f"**Repository:** `{self.repository}`",
            f"**Commit:** `{self.commit_hash}`",
            f"**Branch:** `{self.branch}`",
            "",
            "## State Vector",
            "",
        ]

        # State vector table
        lines.append("| Dimension | Amplitude | Status |")
        lines.append("|-----------|-----------|--------|")
        for dim, amp in self.state_vector.items():
            status = "✓" if amp > 0.9 else ("⚠" if amp > 0.7 else "✗")
            lines.append(f"| {dim} | {amp:.2f} | {status} |")

        # Energy
        lines.extend(
            [
                "",
                "## Energy Analysis",
                "",
                f"**Total Energy:** `{self.energy:.4f}`",
                f"**Threshold:** `{self.energy_threshold}`",
                f"**Status:** {'Stable ✓' if self.is_stable else 'Unstable ✗'}",
            ]
        )

        # Invariants
        lines.extend(
            [
                "",
                "## Hard Invariants",
                "",
            ]
        )
        if self.hard_failures:
            lines.append("**Failed Invariants:**")
            for failure in self.hard_failures:
                lines.append(
                    f"- ✗ {failure.get('invariant', 'unknown')}: {failure.get('details', '')}"
                )
        else:
            lines.append("**All invariants passing ✓**")

        # Minimal cut
        if self.minimal_cut:
            lines.extend(
                [
                    "",
                    "## Minimal Failing Cut",
                    "",
                    "The smallest subsystem that must be fixed:",
                ]
            )
            for item in self.minimal_cut:
                lines.append(f"- {item}")

        # First bad commits
        if self.first_bad_commits:
            lines.extend(
                [
                    "",
                    "## First Bad Commits",
                    "",
                ]
            )
            for inv, commit in self.first_bad_commits.items():
                lines.append(f"- {inv}: `{commit}`")

        # Summary
        lines.extend(
            [
                "",
                "## Summary",
                "",
                f"**Score:** {self.score}/100",
                f"**Releaseable:** {'Yes ✓' if self.is_releaseable else 'No ✗'}",
            ]
        )

        return "\n".join(lines)


class DiagnosisGenerator:
    """Generate diagnosis from analysis results."""

    def __init__(self, repo_path: str):
        self.repo_path = repo_path

    def generate(
        self,
        state_vector,
        hamiltonian,
        failed_invariants: List[Any],
        first_bad_commits: Dict[str, str],
        minimal_cut: List[str],
    ) -> DiagnosisReport:
        """Generate complete diagnosis."""
        # Get state vector as dict
        sv_dict = {dim.value: state_vector.get(dim) for dim in state_vector.amplitudes.keys()}

        # Calculate energy
        energy = hamiltonian.apply(state_vector)
        is_stable = energy < 2.0

        # Check releaseability
        is_releaseable, _ = state_vector.is_releaseable()

        return DiagnosisReport(
            repository=self.repo_path,
            commit_hash=state_vector.commit_hash,
            branch=state_vector.branch,
            state_vector=sv_dict,
            energy=energy,
            is_stable=is_stable,
            hard_failures=[r.to_dict() for r in failed_invariants],
            is_valid=len(failed_invariants) == 0,
            minimal_cut=minimal_cut,
            first_bad_commits=first_bad_commits,
            score=state_vector.score(),
            is_releaseable=is_releaseable,
        )
