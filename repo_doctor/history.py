"""
History Analysis Module - Temporal Analysis

Computes:
- DeltaPsi(t) = Psi_repo(t) - Psi_repo(t-1)
- ||DeltaPsi(t)|| = sqrt(Sum (DeltaPsi_k)^2)

Use this to detect:
- silent breakpoints
- packaging drift
- API drift
- test collapse
- entrypoint collapse
"""

import subprocess
from dataclasses import dataclass
from pathlib import Path

from .state_vector import RepoStateVector, StateDimension


@dataclass
class CommitState:
    """Repository state at a specific commit."""

    hash: str
    message: str
    timestamp: str
    author: str
    state: RepoStateVector
    drift_from_parent: float = None
    drift_details: dict = None


class HistoryAnalyzer:
    """
    Analyzes repository history for temporal drift.
    """

    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path).resolve()
        self.commits: List[CommitState] = []
        self.current_commit: str = None

    def get_current_commit(self) -> str:
        """Get the current commit hash."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None

    def get_commit_history(self, n: int = 20) -> list[tuple[str, str, str]]:
        """
        Get recent commit history.
        Returns list of (hash, message, timestamp).
        """
        try:
            result = subprocess.run(
                ["git", "log", f"-{n}", "--pretty=format:%H|%s|%ci|%an"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                return []

            commits = []
            for line in result.stdout.strip().split("\n"):
                parts = line.split("|")
                if len(parts) >= 4:
                    commits.append((parts[0], parts[1], parts[2], parts[3]))

            return commits

        except Exception:
            return []

    def analyze_commit_range(
        self, start_commit: str = None, end_commit: str = None
    ) -> List[CommitState]:
        """
        Analyze state vectors for a range of commits.
        """
        from .invariants_legacy import InvariantEngine

        self.commits = []

        # Get commit history
        history = self.get_commit_history(n=20)

        previous_state: Optional[RepoStateVector] = None

        for hash_val, message, timestamp, author in history:
            # Checkout the commit
            if not self._checkout_commit(hash_val):
                continue

            # Run invariant checks
            engine = InvariantEngine(self.repo_path)
            state, _ = engine.run_all()

            # Compute drift
            drift: float = None
            drift_details: dict = None

            if previous_state:
                drift = state.drift_magnitude(previous_state)
                delta = state.delta(previous_state)
                drift_details = {dim.value: delta[dim] for dim in StateDimension}

            commit_state = CommitState(
                hash=hash_val[:8],
                message=message,
                timestamp=timestamp,
                author=author,
                state=state,
                drift_from_parent=drift,
                drift_details=drift_details,
            )

            self.commits.append(commit_state)
            previous_state = state

        # Restore original commit
        if self.current_commit:
            self._checkout_commit(self.current_commit)
        else:
            self._checkout_commit("HEAD")

        return self.commits

    def _checkout_commit(self, commit: str) -> bool:
        """Checkout a specific commit. Returns success."""
        try:
            result = subprocess.run(
                ["git", "checkout", "-f", commit],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30,
            )
            return result.returncode == 0
        except Exception:
            return False

    def find_first_bad_commit(self, invariant_name: str, good_commit: str, bad_commit: str) -> str:
        """
        Use git bisect to find first commit that broke an invariant.
        """
        try:
            # Initialize bisect
            subprocess.run(["git", "bisect", "start"], cwd=self.repo_path, check=True, timeout=10)

            # Mark good and bad commits
            subprocess.run(
                ["git", "bisect", "good", good_commit], cwd=self.repo_path, check=True, timeout=10
            )

            subprocess.run(
                ["git", "bisect", "bad", bad_commit], cwd=self.repo_path, check=True, timeout=10
            )

            # Create bisect script
            script_path = self.repo_path / ".bisect_script.py"
            script_content = f"""#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path("{self.repo_path}")))

from repo_doctor.invariants import InvariantEngine
from typing import Optional

engine = InvariantEngine("{self.repo_path}")
result = engine.check_specific("{invariant_name}")

if result.passed:
    sys.exit(0)  # Good
else:
    sys.exit(1)  # Bad
"""
            script_path.write_text(script_content)
            script_path.chmod(0o755)

            # Run bisect
            result = subprocess.run(
                ["git", "bisect", "run", "python", str(script_path)],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=300,
            )

            # Reset bisect
            subprocess.run(["git", "bisect", "reset"], cwd=self.repo_path, check=True, timeout=10)

            # Clean up script
            script_path.unlink()

            # Parse result
            if "is the first bad commit" in result.stdout:
                for line in result.stdout.split("\n"):
                    if "is the first bad commit" in line:
                        return line.split()[0]

            return None

        except Exception:
            # Reset bisect on error
            subprocess.run(["git", "bisect", "reset"], cwd=self.repo_path, capture_output=True)
            return None

    def get_drift_report(self) -> str:
        """Generate drift analysis report."""
        if not self.commits:
            return "No commits analyzed"

        lines = [
            "=" * 60,
            "TEMPORAL DRIFT ANALYSIS",
            "=" * 60,
            f"Commits analyzed: {len(self.commits)}",
            "-" * 60,
        ]

        for commit in self.commits:
            lines.append(f"\nCommit: {commit.hash}")
            lines.append(f"Message: {commit.message[:60]}")
            lines.append(f"Author: {commit.author}")
            lines.append(f"Energy: {commit.state.energy():.4f}")
            lines.append(f"Score: {commit.state.score()}/100")

            if commit.drift_from_parent:
                lines.append(f"Drift from parent: {commit.drift_from_parent:.4f}")

                # Show which dimensions changed most
                if commit.drift_details:
                    sorted_dims = sorted(
                        commit.drift_details.items(), key=lambda x: abs(x[1]), reverse=True
                    )[:3]

                    lines.append("Top dimensional changes:")
                    for dim, delta in sorted_dims:
                        sign = "+" if delta > 0 else ""
                        lines.append(f"  {dim}: {sign}{delta:.3f}")

        lines.append("\n" + "=" * 60)

        return "\n".join(lines)

    def get_high_drift_commits(self, threshold: float = 0.5) -> List[CommitState]:
        """Get commits with drift above threshold."""
        return [c for c in self.commits if c.drift_from_parent and c.drift_from_parent >= threshold]
