"""Git bisect runner with invariant oracle.

Automates git bisect using invariant violations as the oracle.

Exit codes (per git bisect run spec):
- 0: Good commit (invariant passes)
- 1-124: Bad commit (invariant fails)
- 125: Skip (untestable)
- 126-127: Abort
"""
from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


@dataclass
class BisectResult:
    """Result of git bisect operation."""
    first_bad_commit: str | None
    log: list[str]
    successful: bool
    message: str = ""
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "first_bad_commit": self.first_bad_commit,
            "log": self.log,
            "successful": self.successful,
            "message": self.message,
        }


class BisectRunner:
    """
    Git bisect runner with invariant oracle.
    
    Automates git bisect to find first commit where an invariant fails.
    Uses the invariant check as the oracle for good/bad determination.
    
    Usage:
        runner = BisectRunner("/path/to/repo")
        
        # Define invariant oracle
        def check_api_invariant():
            # Return 0 for good, 1-124 for bad
            return 0 if api_invariant_holds() else 1
        
        # Run bisect
        result = runner.run_bisect(
            oracle=check_api_invariant,
            good_commit="v1.0.0",
            bad_commit="HEAD",
            invariant_name="I_api",
        )
        
        if result.first_bad_commit:
            print(f"First bad commit: {result.first_bad_commit}")
    """
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()
    
    def run_bisect(
        self,
        oracle: Callable[[], int],
        good_commit: str,
        bad_commit: str,
        invariant_name: str,
    ) -> BisectResult:
        """
        Run git bisect with invariant oracle.
        
        Args:
            oracle: Function returning exit code (0=good, 1-124=bad, 125=skip)
            good_commit: Known good commit
            bad_commit: Known bad commit
            invariant_name: Name for logging
            
        Returns:
            BisectResult with first bad commit
        """
        log: list[str] = []
        
        try:
            # Reset any existing bisect
            self._run_git(["bisect", "reset"])
            
            # Start bisect
            result = self._run_git(["bisect", "start", bad_commit, good_commit])
            if result.returncode != 0:
                return BisectResult(
                    first_bad_commit=None,
                    log=log + ["Failed to start bisect"],
                    successful=False,
                    message="Failed to start bisect",
                )
            
            log.append(f"Started bisect: {good_commit}..{bad_commit}")
            log.append(f"Checking invariant: {invariant_name}")
            
            # Run bisect with oracle
            # We need to run the oracle at each step
            while True:
                # Get current commit
                commit_result = self._run_git(["rev-parse", "HEAD"])
                current_commit = commit_result.stdout.strip()
                
                # Run oracle
                oracle_code = oracle()
                
                if oracle_code == 0:
                    # Good - mark as good
                    self._run_git(["bisect", "good"])
                    log.append(f"{current_commit[:8]}: good")
                elif oracle_code == 125:
                    # Skip
                    self._run_git(["bisect", "skip"])
                    log.append(f"{current_commit[:8]}: skip")
                elif 1 <= oracle_code <= 124:
                    # Bad - mark as bad
                    self._run_git(["bisect", "bad"])
                    log.append(f"{current_commit[:8]}: bad")
                else:
                    # Abort on unexpected codes
                    self._run_git(["bisect", "reset"])
                    return BisectResult(
                        first_bad_commit=None,
                        log=log,
                        successful=False,
                        message=f"Oracle returned unexpected code: {oracle_code}",
                    )
                
                # Check if bisect is complete
                # (This is a simplified check - real implementation would parse bisect output)
                status = self._run_git(["bisect", "visualize"], check=False)
                if status.returncode != 0:
                    break
                
                # Check for completion (first bad commit found)
                # In real implementation, parse bisect log
                log_output = self._run_git(["bisect", "log"], check=False)
                if "first bad commit" in log_output.stdout.lower():
                    break
        
        except Exception as e:
            self._run_git(["bisect", "reset"], check=False)
            return BisectResult(
                first_bad_commit=None,
                log=log,
                successful=False,
                message=str(e),
            )
        
        # Parse result
        first_bad = self._parse_first_bad(log)
        
        # Reset bisect
        self._run_git(["bisect", "reset"], check=False)
        
        return BisectResult(
            first_bad_commit=first_bad,
            log=log,
            successful=first_bad is not None,
            message="Bisect complete" if first_bad else "No bad commit found",
        )
    
    def run_bisect_simple(
        self,
        invariant_checker: Callable[[str], bool],
        good_commit: str,
        bad_commit: str,
        invariant_name: str,
    ) -> BisectResult:
        """
        Simplified bisect using invariant checker.
        
        Args:
            invariant_checker: Function(commit_hash) -> bool
            good_commit: Known good commit
            bad_commit: Known bad commit
            invariant_name: Name for logging
            
        Returns:
            BisectResult
        """
        log: list[str] = []
        
        try:
            # Get commit range
            result = self._run_git([
                "log", "--format=%H",
                f"{good_commit}..{bad_commit}"
            ])
            
            if result.returncode != 0:
                return BisectResult(
                    first_bad_commit=None,
                    log=log,
                    successful=False,
                    message="Failed to get commit range",
                )
            
            commits = result.stdout.strip().split("\n")
            commits = [c for c in commits if c]
            
            if not commits:
                return BisectResult(
                    first_bad_commit=None,
                    log=log,
                    successful=False,
                    message="No commits in range",
                )
            
            log.append(f"Checking {len(commits)} commits")
            
            # Binary search
            first_bad = self._binary_search(
                commits, invariant_checker, log
            )
            
            return BisectResult(
                first_bad_commit=first_bad,
                log=log,
                successful=first_bad is not None,
            )
        
        except Exception as e:
            return BisectResult(
                first_bad_commit=None,
                log=log,
                successful=False,
                message=str(e),
            )
    
    def _binary_search(
        self,
        commits: list[str],
        checker: Callable[[str], bool],
        log: list[str],
    ) -> str | None:
        """Binary search for first bad commit."""
        if not commits:
            return None
        
        left, right = 0, len(commits) - 1
        first_bad = None
        
        while left <= right:
            mid = (left + right) // 2
            commit = commits[mid]
            
            # Checkout commit
            checkout = self._run_git(["checkout", commit], check=False)
            if checkout.returncode != 0:
                log.append(f"Failed to checkout {commit[:8]}")
                continue
            
            # Check invariant
            is_good = checker(commit)
            
            if is_good:
                log.append(f"{commit[:8]}: good (mid={mid})")
                left = mid + 1
            else:
                log.append(f"{commit[:8]}: bad (mid={mid})")
                first_bad = commit
                right = mid - 1
        
        # Reset to original state
        self._run_git(["checkout", "-"], check=False)
        
        return first_bad
    
    def _run_git(
        self,
        args: list[str],
        check: bool = True,
    ) -> subprocess.CompletedProcess:
        """Run git command."""
        cmd = ["git"] + args
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=self.repo_path,
            check=check,
        )
    
    def _parse_first_bad(self, log: list[str]) -> str | None:
        """Parse first bad commit from bisect log."""
        for line in reversed(log):
            if "bad" in line.lower() and ":" in line:
                # Extract commit hash
                parts = line.split(":")
                if parts:
                    commit = parts[0].strip()
                    if len(commit) >= 8:
                        return commit
        return None
    
    def get_commit_info(self, commit_hash: str) -> dict[str, Any]:
        """Get information about a commit."""
        result = self._run_git([
            "show", "--format=%H|%an|%ae|%ai|%s", "-s", commit_hash
        ])
        
        if result.returncode == 0 and "|" in result.stdout:
            parts = result.stdout.strip().split("|")
            if len(parts) >= 5:
                return {
                    "hash": parts[0],
                    "author": parts[1],
                    "email": parts[2],
                    "date": parts[3],
                    "subject": parts[4],
                }
        
        return {"hash": commit_hash, "error": "Could not get commit info"}
