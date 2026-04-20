"""
Git Bisect Integration for First Bad Commit Finding

t*_k = min t such that I_k(t-1)=1 and I_k(t)=0

Uses git bisect with automated run/skip/log/replay.
"""

import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, List


class BisectStatus(Enum):
    """Status of bisect operation."""

    GOOD = "good"
    BAD = "bad"
    SKIP = "skip"
    UNKNOWN = "unknown"


@dataclass
class BisectResult:
    """Result of bisect operation."""

    first_bad_commit: str
    iterations: int
    skipped_commits: List[str]
    status: BisectStatus
    message: str


class BisectRunner:
    """
    Run git bisect with invariant oracle.

    t*_k = min t such that I_k(t-1)=1 and I_k(t)=0
    """

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.skipped: List[str] = []

    def bisect_invariant(
        self,
        invariant_name: str,
        oracle: Callable[[str], BisectStatus],
        good_commit: str,
        bad_commit: str,
    ) -> BisectResult:
        """
        Find first bad commit for given invariant.

        Args:
            invariant_name: Name of invariant to check
            oracle: Function that takes commit hash, returns GOOD/BAD/SKIP
            good_commit: Known good commit
            bad_commit: Known bad commit

        """
        iterations = 0

        try:
            # Start bisect
            subprocess.run(
                ["git", "bisect", "start"],
                cwd=self.repo_path,
                capture_output=True,
                check=True,
            )

            # Mark known good
            subprocess.run(
                ["git", "bisect", "good", good_commit],
                cwd=self.repo_path,
                capture_output=True,
                check=True,
            )

            # Mark known bad
            subprocess.run(
                ["git", "bisect", "bad", bad_commit],
                cwd=self.repo_path,
                capture_output=True,
                check=True,
            )

            # Automated bisect with oracle
            while True:
                result = subprocess.run(
                    ["git", "bisect", "next"],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                )

                if "is the first bad commit" in result.stdout:
                    # Parse first bad commit
                    for line in result.stdout.split("\n"):
                        if "is the first bad commit" in line:
                            commit = line.split()[0]
                            return BisectResult(
                                first_bad_commit=commit,
                                iterations=iterations,
                                skipped_commits=self.skipped.copy(),
                                status=BisectStatus.BAD,
                                message=f"Found first bad commit for {invariant_name}",
                            )
                    break

                # Get current commit
                commit_result = subprocess.run(
                    ["git", "rev-parse", "HEAD"],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    check=True,
                )
                current = commit_result.stdout.strip()

                # Run oracle
                status = oracle(current)
                iterations += 1

                if status == BisectStatus.GOOD:
                    subprocess.run(
                        ["git", "bisect", "good"],
                        cwd=self.repo_path,
                        capture_output=True,
                        check=True,
                    )
                elif status == BisectStatus.BAD:
                    subprocess.run(
                        ["git", "bisect", "bad"],
                        cwd=self.repo_path,
                        capture_output=True,
                        check=True,
                    )
                else:  # SKIP
                    self.skipped.append(current)
                    subprocess.run(
                        ["git", "bisect", "skip"],
                        cwd=self.repo_path,
                        capture_output=True,
                        check=True,
                    )

        except subprocess.CalledProcessError as e:
            return BisectResult(
                first_bad_commit=None,
                iterations=iterations,
                skipped_commits=self.skipped,
                status=BisectStatus.UNKNOWN,
                message=f"Bisect failed: {e}",
            )
        finally:
            # Reset bisect
            subprocess.run(
                ["git", "bisect", "reset"],
                cwd=self.repo_path,
                capture_output=True,
            )

        return BisectResult(
            first_bad_commit=None,
            iterations=iterations,
            skipped_commits=self.skipped,
            status=BisectStatus.UNKNOWN,
            message="Bisect completed without finding first bad commit",
        )

    def get_bisect_log(self) -> list[dict[str, Any]]:
        """Get bisect log for replay/correction."""
        try:
            result = subprocess.run(
                ["git", "bisect", "log"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            # Parse log entries
            entries = []
            for line in result.stdout.split("\n"):
                if line.startswith("#"):
                    continue
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        entries.append(
                            {
                                "command": parts[0],
                                "commit": parts[1] if len(parts) > 1 else None,
                            }
                        )
            return entries
        except subprocess.CalledProcessError:
            return []
