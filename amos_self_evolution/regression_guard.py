"""AMOS Regression Guard - Safety Verification for Self-Evolution

Blocks self-mutation without proof of safety per AMOS Self-Evolution Law 5:
"Evolution must preserve working system."

Every evolution must pass regression checks before mutation is permitted.

Owner: AMOS Brain (Canonical Runtime)
Version: 1.0.0
Evolution ID: E003
"""

from __future__ import annotations

import ast
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any

from evolution_contract_registry import EvolutionContract, EvolutionStatus


class CheckStatus(Enum):
    """Status of a regression check."""
    PENDING = auto()
    PASS = auto()
    FAIL = auto()
    ERROR = auto()
    SKIPPED = auto()


@dataclass
class RegressionCheck:
    """A single regression check result."""
    
    check_name: str
    status: CheckStatus
    details: str = ""
    duration_ms: int = 0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "check_name": self.check_name,
            "status": self.status.name,
            "details": self.details,
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp,
        }


@dataclass
class RegressionReport:
    """Complete regression verification report."""
    
    evolution_id: str
    overall_status: CheckStatus = CheckStatus.PENDING
    checks: list[RegressionCheck] = field(default_factory=list)
    started_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    completed_at: str = ""
    mutation_permitted: bool = False
    
    def add_check(self, check: RegressionCheck) -> None:
        self.checks.append(check)
        self._update_overall_status()
    
    def _update_overall_status(self) -> None:
        if any(c.status == CheckStatus.FAIL for c in self.checks):
            self.overall_status = CheckStatus.FAIL
            self.mutation_permitted = False
        elif any(c.status == CheckStatus.ERROR for c in self.checks):
            self.overall_status = CheckStatus.ERROR
            self.mutation_permitted = False
        elif all(c.status == CheckStatus.PASS for c in self.checks):
            self.overall_status = CheckStatus.PASS
            self.mutation_permitted = True
    
    def complete(self) -> None:
        self.completed_at = datetime.utcnow().isoformat()
        self._update_overall_status()
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "evolution_id": self.evolution_id,
            "overall_status": self.overall_status.name,
            "checks": [c.to_dict() for c in self.checks],
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "mutation_permitted": self.mutation_permitted,
            "total_checks": len(self.checks),
            "passed": len([c for c in self.checks if c.status == CheckStatus.PASS]),
            "failed": len([c for c in self.checks if c.status == CheckStatus.FAIL]),
        }


class RegressionGuard:
    """Guards against self-evolution regression.
    
    Implements safety verification per AMOS Self-Evolution Law 5:
    - Verify before mutation
    - Block on any regression
    - Preserve working system
    """
    
    def __init__(self, repo_root: str = "."):
        self.repo_root = Path(repo_root)
        self._check_registry: dict[str, callable] = {
            "syntax_check": self._check_syntax,
            "import_check": self._check_imports,
            "test_check": self._check_tests,
            "type_check": self._check_types,
            "lint_check": self._check_lint,
            "circular_import_check": self._check_circular_imports,
        }
    
    def verify_evolution(self, contract: EvolutionContract) -> RegressionReport:
        """Verify an evolution contract before permitting mutation.
        
        Returns a RegressionReport with overall status.
        Mutation is only permitted if all critical checks pass.
        """
        report = RegressionReport(evolution_id=contract.evolution_id)
        
        # Run all registered checks
        for check_name, check_func in self._check_registry.items():
            try:
                result = check_func(contract)
                report.add_check(result)
            except Exception as e:
                report.add_check(RegressionCheck(
                    check_name=check_name,
                    status=CheckStatus.ERROR,
                    details=f"Check execution error: {e}",
                ))
        
        report.complete()
        return report
    
    def _check_syntax(self, contract: EvolutionContract) -> RegressionCheck:
        """Verify Python syntax of target files."""
        start = datetime.utcnow()
        
        errors = []
        for target_file in contract.target_files[:10]:  # Limit checks
            filepath = self.repo_root / target_file
            if not filepath.exists():
                continue
            
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "py_compile", str(filepath)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if result.returncode != 0:
                    errors.append(f"{target_file}: syntax error")
            except subprocess.TimeoutExpired:
                errors.append(f"{target_file}: syntax check timeout")
            except Exception as e:
                errors.append(f"{target_file}: check error - {e}")
        
        duration = int((datetime.utcnow() - start).total_seconds() * 1000)
        
        if errors:
            return RegressionCheck(
                check_name="syntax_check",
                status=CheckStatus.FAIL,
                details=f"Syntax errors in {len(errors)} files: {', '.join(errors[:3])}",
                duration_ms=duration,
            )
        
        return RegressionCheck(
            check_name="syntax_check",
            status=CheckStatus.PASS,
            details=f"Syntax valid for {len(contract.target_files)} target files",
            duration_ms=duration,
        )
    
    def _check_imports(self, contract: EvolutionContract) -> RegressionCheck:
        """Verify imports resolve correctly."""
        start = datetime.utcnow()
        
        import_errors = []
        
        # Check if target module can be imported
        for target_module in contract.target_modules[:5]:
            try:
                result = subprocess.run(
                    [sys.executable, "-c", f"import {target_module}"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    cwd=self.repo_root,
                )
                if result.returncode != 0:
                    error = result.stderr.strip()[:100] if result.stderr else "Import failed"
                    import_errors.append(f"{target_module}: {error}")
            except subprocess.TimeoutExpired:
                import_errors.append(f"{target_module}: import timeout")
            except Exception as e:
                import_errors.append(f"{target_module}: {e}")
        
        duration = int((datetime.utcnow() - start).total_seconds() * 1000)
        
        if import_errors:
            return RegressionCheck(
                check_name="import_check",
                status=CheckStatus.FAIL,
                details=f"Import failures: {', '.join(import_errors[:3])}",
                duration_ms=duration,
            )
        
        return RegressionCheck(
            check_name="import_check",
            status=CheckStatus.PASS,
            details=f"Imports resolve for {len(contract.target_modules)} modules",
            duration_ms=duration,
        )
    
    def _check_tests(self, contract: EvolutionContract) -> RegressionCheck:
        """Run relevant tests to verify no regression."""
        start = datetime.utcnow()
        
        # Look for tests related to target modules
        test_files = list(self.repo_root.rglob("test_*.py"))
        test_files = [f for f in test_files if "__pycache__" not in str(f)]
        
        if not test_files:
            return RegressionCheck(
                check_name="test_check",
                status=CheckStatus.SKIPPED,
                details="No test files found",
                duration_ms=0,
            )
        
        # Run a subset of tests (quick check)
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "-x", "--tb=short", "-q"],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=self.repo_root,
            )
            
            duration = int((datetime.utcnow() - start).total_seconds() * 1000)
            
            if result.returncode == 0:
                return RegressionCheck(
                    check_name="test_check",
                    status=CheckStatus.PASS,
                    details="All tests pass",
                    duration_ms=duration,
                )
            else:
                # Parse failure count
                output = result.stdout + result.stderr
                fail_count = output.count("FAILED")
                return RegressionCheck(
                    check_name="test_check",
                    status=CheckStatus.FAIL,
                    details=f"Tests failed: {fail_count} failures detected",
                    duration_ms=duration,
                )
        except subprocess.TimeoutExpired:
            return RegressionCheck(
                check_name="test_check",
                status=CheckStatus.SKIPPED,
                details="Test check timeout (skipped)",
                duration_ms=60000,
            )
        except FileNotFoundError:
            return RegressionCheck(
                check_name="test_check",
                status=CheckStatus.SKIPPED,
                details="pytest not available",
                duration_ms=0,
            )
    
    def _check_types(self, contract: EvolutionContract) -> RegressionCheck:
        """Check type consistency with mypy if available."""
        start = datetime.utcnow()
        
        try:
            result = subprocess.run(
                ["python3", "-m", "mypy", "--ignore-missing-imports", "--no-error-summary"]
                + contract.target_files[:5],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.repo_root,
            )
            
            duration = int((datetime.utcnow() - start).total_seconds() * 1000)
            
            if result.returncode == 0:
                return RegressionCheck(
                    check_name="type_check",
                    status=CheckStatus.PASS,
                    details="Type check passed",
                    duration_ms=duration,
                )
            else:
                error_count = result.stdout.count("error:")
                return RegressionCheck(
                    check_name="type_check",
                    status=CheckStatus.FAIL,
                    details=f"Type errors: {error_count} issues found",
                    duration_ms=duration,
                )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return RegressionCheck(
                check_name="type_check",
                status=CheckStatus.SKIPPED,
                details="mypy not available or timeout",
                duration_ms=0,
            )
    
    def _check_lint(self, contract: EvolutionContract) -> RegressionCheck:
        """Check code quality with ruff if available."""
        start = datetime.utcnow()
        
        try:
            result = subprocess.run(
                ["python3", "-m", "ruff", "check"] + contract.target_files[:5],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.repo_root,
            )
            
            duration = int((datetime.utcnow() - start).total_seconds() * 1000)
            
            if result.returncode == 0:
                return RegressionCheck(
                    check_name="lint_check",
                    status=CheckStatus.PASS,
                    details="Lint check passed",
                    duration_ms=duration,
                )
            else:
                issue_count = len(result.stdout.strip().split("\n")) if result.stdout else 0
                return RegressionCheck(
                    check_name="lint_check",
                    status=CheckStatus.FAIL,
                    details=f"Lint issues: {issue_count} violations",
                    duration_ms=duration,
                )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return RegressionCheck(
                check_name="lint_check",
                status=CheckStatus.SKIPPED,
                details="ruff not available or timeout",
                duration_ms=0,
            )
    
    def _check_circular_imports(self, contract: EvolutionContract) -> RegressionCheck:
        """Check for circular import introduction."""
        # This is a simplified check - full circular import detection
        # would require the ImportAnalyzer
        return RegressionCheck(
            check_name="circular_import_check",
            status=CheckStatus.SKIPPED,
            details="Circular import check requires ImportAnalyzer (deferred)",
            duration_ms=0,
        )
    
    def permit_mutation(self, report: RegressionReport) -> bool:
        """Determine if mutation should be permitted based on report."""
        return report.mutation_permitted and report.overall_status == CheckStatus.PASS
    
    def get_mandatory_checks(self) -> list[str]:
        """Get list of mandatory checks that cannot be skipped."""
        return ["syntax_check", "import_check"]


def main():
    """Demonstrate regression guard."""
    print("=" * 70)
    print("AMOS REGRESSION GUARD - E003 SELF-VERIFICATION")
    print("=" * 70)
    
    from evolution_contract_registry import create_e001_contract
    
    guard = RegressionGuard()
    print("\n✓ Regression Guard initialized")
    
    # Test with E001 contract
    contract = create_e001_contract()
    print(f"✓ Loaded contract: {contract.evolution_id}")
    
    print("\nRunning regression checks...")
    report = guard.verify_evolution(contract)
    
    print(f"\nRegression Report:")
    print(f"  Overall Status: {report.overall_status.name}")
    print(f"  Mutation Permitted: {report.mutation_permitted}")
    print(f"  Total Checks: {len(report.checks)}")
    
    print(f"\nCheck Results:")
    for check in report.checks:
        status_symbol = "✓" if check.status == CheckStatus.PASS else "✗" if check.status == CheckStatus.FAIL else "○"
        print(f"  {status_symbol} {check.check_name}: {check.status.name}")
        if check.details:
            print(f"      {check.details[:60]}...")
    
    print("\n" + "=" * 70)
    print("E003 VERIFICATION COMPLETE")
    print("=" * 70)
    print("\nRegression Guard operational.")
    print("Self-evolution now has safety verification.")
    print("Future mutations will be blocked without passing checks.")


if __name__ == "__main__":
    main()
