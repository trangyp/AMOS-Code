"""
Bisect Engine - Temporal Debugger

Uses git bisect run with invariant checks to find:
- First bad commit for each invariant class
- Minimum patch set that restores commutativity
"""

import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass
class BisectResult:
    """Result of a bisect operation."""

    first_bad_commit: str
    first_bad_message: str
    good_commit: str
    bad_commit: str
    invariant_name: str
    steps: int
    success: bool
    error: str = None


class BisectEngine:
    """
    Automated bisect engine for finding regression commits.
    """

    def __init__(self, repo_path: Union[str, Path]):
        self.repo_path = Path(repo_path).resolve()
        self.original_commit: str = None
        self._save_current_commit()

    def _save_current_commit(self):
        """Save the current commit hash."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                self.original_commit = result.stdout.strip()
        except Exception:
            pass

    def bisect_invariant(
        self, invariant_name: str, good_commit: str, bad_commit: str
    ) -> BisectResult:
        """
        Bisect to find the first commit that broke an invariant.
        """
        steps = 0

        try:
            # Initialize bisect
            result = subprocess.run(
                ["git", "bisect", "start"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                return BisectResult(
                    first_bad_commit=None,
                    first_bad_message=None,
                    good_commit=good_commit,
                    bad_commit=bad_commit,
                    invariant_name=invariant_name,
                    steps=0,
                    success=False,
                    error="Failed to start bisect",
                )

            # Mark good commit
            result = subprocess.run(
                ["git", "bisect", "good", good_commit],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                self._reset_bisect()
                return BisectResult(
                    first_bad_commit=None,
                    first_bad_message=None,
                    good_commit=good_commit,
                    bad_commit=bad_commit,
                    invariant_name=invariant_name,
                    steps=0,
                    success=False,
                    error=f"Failed to mark good commit: {result.stderr}",
                )

            # Mark bad commit
            result = subprocess.run(
                ["git", "bisect", "bad", bad_commit],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                self._reset_bisect()
                return BisectResult(
                    first_bad_commit=None,
                    first_bad_message=None,
                    good_commit=good_commit,
                    bad_commit=bad_commit,
                    invariant_name=invariant_name,
                    steps=0,
                    success=False,
                    error=f"Failed to mark bad commit: {result.stderr}",
                )

            # Create bisect script
            script_content = self._create_bisect_script(invariant_name)

            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(script_content)
                script_path = f.name

            # Run bisect
            result = subprocess.run(
                ["git", "bisect", "run", "python", script_path],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=300,
            )

            steps = result.stdout.count("Bisecting:")

            # Parse result
            first_bad = None
            first_bad_msg = None

            for line in result.stdout.split("\n"):
                if "is the first bad commit" in line:
                    parts = line.split()
                    if parts:
                        first_bad = parts[0]
                        # Get commit message
                        msg_result = subprocess.run(
                            ["git", "log", "-1", "--pretty=format:%s", first_bad],
                            cwd=self.repo_path,
                            capture_output=True,
                            text=True,
                        )
                        first_bad_msg = msg_result.stdout.strip()
                    break

            # Cleanup
            self._reset_bisect()
            Path(script_path).unlink()

            return BisectResult(
                first_bad_commit=first_bad,
                first_bad_message=first_bad_msg,
                good_commit=good_commit,
                bad_commit=bad_commit,
                invariant_name=invariant_name,
                steps=steps,
                success=first_bad is not None,
            )

        except Exception as e:
            self._reset_bisect()
            return BisectResult(
                first_bad_commit=None,
                first_bad_message=None,
                good_commit=good_commit,
                bad_commit=bad_commit,
                invariant_name=invariant_name,
                steps=steps,
                success=False,
                error=str(e),
            )

    def _create_bisect_script(self, invariant_name: str) -> str:
        """Create the bisect test script."""
        return f"""#!/usr/bin/env python3
import sys
import os

# Import and run invariant check
try:
    from repo_doctor.invariants import InvariantEngine

    engine = InvariantEngine("{self.repo_path}")
    result = engine.check_specific("{invariant_name}")

    if result.passed:
        print(f"INVARIANT_PASSED: {invariant_name}")
        sys.exit(0)  # Good commit
    else:
        print(f"INVARIANT_FAILED: {invariant_name}")
        print(f"  Error: {{result.message}}")
        sys.exit(1)  # Bad commit

except Exception as e:
    print(f"CHECK_ERROR: {{e}}")
    sys.exit(125)  # Skip this commit
"""

    def _reset_bisect(self):
        """Reset git bisect state."""
        try:
            subprocess.run(
                ["git", "bisect", "reset"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10,
            )
        except Exception:
            pass

        # Restore original commit
        if self.original_commit:
            try:
                subprocess.run(
                    ["git", "checkout", "-f", self.original_commit],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
            except Exception:
                pass

    def quick_check(self, commit: str, invariant_name: str) -> tuple[bool, str]:
        """
        Quick check if a specific commit passes an invariant.
        Returns (passed, message).
        """
        from .invariants_legacy import InvariantEngine

        # Checkout commit
        if not self._checkout_commit(commit):
            return False, "Failed to checkout commit"

        try:
            engine = InvariantEngine(self.repo_path)
            result = engine.check_specific(invariant_name)

            return result.passed, result.message
        except Exception as e:
            return False, f"Check failed: {e}"

    def _checkout_commit(self, commit: str) -> bool:
        """Checkout a specific commit."""
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

    def find_regression_range(
        self, invariant_name: str, lookback_commits: int = 20
    ) -> tuple[str, str]:
        """
        Find the regression range for an invariant.
        Returns (good_commit, bad_commit) or None.
        """
        try:
            # Get recent commits
            result = subprocess.run(
                ["git", "log", f"-{lookback_commits}", "--pretty=format:%H"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                return None

            commits = result.stdout.strip().split("\n")
            if len(commits) < 2:
                return None

            # Find most recent bad commit
            bad_commit = None
            for commit in commits:
                passed, _ = self.quick_check(commit, invariant_name)
                if not passed:
                    bad_commit = commit
                    break

            if not bad_commit:
                return None  # All commits pass

            # Find last good commit before bad
            good_commit = None
            for commit in commits[commits.index(bad_commit) + 1 :]:
                passed, _ = self.quick_check(commit, invariant_name)
                if passed:
                    good_commit = commit
                    break

            return (good_commit, bad_commit) if good_commit else None

        except Exception:
            return None
        finally:
            # Restore original
            if self.original_commit:
                self._checkout_commit(self.original_commit)
