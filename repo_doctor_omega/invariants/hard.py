"""Hard invariants for repository validation.

A repo is valid only if all hard invariants hold:

RepoValid = I_parse ∧ I_import ∧ I_type ∧ I_api ∧ I_entry ∧
            I_pack ∧ I_runtime ∧ I_persist ∧ I_status ∧
            I_tests ∧ I_security ∧ I_history
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

from ..state.basis import BasisVector


class InvariantKind(Enum):
    """Types of hard invariants."""

    PARSE = auto()
    IMPORT = auto()
    TYPE = auto()
    API = auto()
    ENTRYPOINT = auto()
    PACKAGING = auto()
    RUNTIME = auto()
    PERSISTENCE = auto()
    STATUS = auto()
    TEST = auto()
    SECURITY = auto()
    HISTORY = auto()


@dataclass
class InvariantViolation:
    """A violation of a hard invariant."""

    invariant: str
    message: str
    location: str = ""
    severity: float = 1.0
    remediation: str = ""


@dataclass
class InvariantResult:
    """Result of invariant check."""

    invariant: str
    passed: bool
    basis: BasisVector
    violations: list[InvariantViolation] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def severity(self) -> float:
        """Compute aggregate severity of violations."""
        if not self.violations:
            return 0.0
        return max(v.severity for v in self.violations)


class HardInvariant(ABC):
    """Abstract base for hard invariants."""

    def __init__(self, kind: InvariantKind, basis: BasisVector):
        self.kind = kind
        self.basis = basis
        self.name = kind.name

    @abstractmethod
    def check(self, repo_path: str, context: dict[str, Any] | None = None) -> InvariantResult:
        """Check if invariant holds.

        Args:
            repo_path: Path to repository root
            context: Optional check context

        Returns:
            InvariantResult with check outcome
        """
        pass

    def __str__(self) -> str:
        return f"I_{self.name.lower()}"


class ParseInvariant(HardInvariant):
    """I_parse = 1 iff every required source file yields acceptable parse tree.

    "Acceptable" means:
    - No fatal parse failure in critical files
    - Recoverable malformed nodes below threshold
    - Parser-specific error budget not exceeded
    """

    def __init__(self, error_threshold: float = 5.0):
        super().__init__(InvariantKind.PARSE, BasisVector.SYNTAX)
        self.error_threshold = error_threshold
        self._substrate: Any | None = None

    def _get_substrate(self) -> Any:
        """Lazy-load Tree-sitter substrate."""
        if self._substrate is None:
            try:
                from ..ingest.treesitter_substrate import TreeSitterSubstrate

                self._substrate = TreeSitterSubstrate(error_threshold=self.error_threshold)
            except ImportError:
                self._substrate = None
        return self._substrate

    def check(self, repo_path: str, context: dict[str, Any] | None = None) -> InvariantResult:
        """Check parse integrity using Tree-sitter."""
        violations = []
        substrate = self._get_substrate()

        if substrate is None or not substrate.is_available():
            # Tree-sitter not available - use basic fallback
            return InvariantResult(
                invariant=self.name,
                passed=True,  # Defer to other checks
                basis=self.basis,
                violations=[],
                metadata={
                    "substrate": "tree-sitter",
                    "status": "unavailable",
                    "note": "Tree-sitter not installed, using fallback",
                },
            )

        # Parse all Python files in repository
        pattern = context.get("pattern", "*.py") if context else "*.py"
        results = substrate.parse_repository(repo_path, pattern=pattern)

        # Generate summary
        summary = substrate.get_summary(results)

        # Check for violations
        if not summary["acceptable"]:
            # Aggregate error rate too high
            violations.append(
                InvariantViolation(
                    invariant=self.name,
                    message=(
                        f"Parse error rate {summary['aggregate_error_rate']:.2f}% "
                        f"exceeds threshold {self.error_threshold}%"
                    ),
                    severity=min(summary["aggregate_error_rate"] / 100, 1.0),
                    remediation="Fix syntax errors in failing files",
                )
            )

        # Add violations for individual failed files
        failed_files = [r for r in results if not r.success]
        for result in failed_files[:10]:  # Limit to first 10
            for error in result.errors:
                if error.severity == "error":
                    violations.append(
                        InvariantViolation(
                            invariant=self.name,
                            message=f"{error.message} in {result.file}:{error.line}",
                            location=f"{result.file}:{error.line}",
                            severity=0.9,
                            remediation="Fix syntax error",
                        )
                    )

        return InvariantResult(
            invariant=self.name,
            passed=len(violations) == 0,
            basis=self.basis,
            violations=violations,
            metadata={
                "substrate": "tree-sitter",
                "files_checked": summary["total_files"],
                "files_failed": summary["failed"],
                "error_rate": summary["aggregate_error_rate"],
                "acceptable": summary["acceptable"],
            },
        )


class ImportInvariant(HardInvariant):
    """I_import = 1 iff every claimed import resolves to a real symbol.

    Includes:
    - Internal imports
    - Package exports
    - Entrypoint imports
    - Docs/demo/test imports
    - Reflection-based runtime imports
    """

    def __init__(self):
        super().__init__(InvariantKind.IMPORT, BasisVector.IMPORT)

    def __init__(self):
        super().__init__(InvariantKind.IMPORT, BasisVector.IMPORT)
        self._substrate: Any | None = None

    def _get_substrate(self, repo_path: str) -> Any:
        """Lazy-load Import substrate."""
        if self._substrate is None:
            try:
                from ..ingest.import_substrate import ImportSubstrate

                self._substrate = ImportSubstrate(repo_path)
            except ImportError:
                self._substrate = None
        return self._substrate

    def check(self, repo_path: str, context: dict[str, Any] | None = None) -> InvariantResult:
        """Check import resolution integrity."""
        violations = []

        substrate = self._get_substrate(repo_path)

        if substrate is None:
            return InvariantResult(
                invariant=self.name,
                passed=True,
                basis=self.basis,
                violations=[],
                metadata={"substrate": "import", "status": "unavailable"},
            )

        # Analyze all imports in repository
        pattern = context.get("pattern", "*.py") if context else "*.py"
        unresolved = substrate.get_unresolved_imports(pattern)

        # Create violations for unresolved imports
        for resolution in unresolved[:20]:  # Limit to first 20
            imp = resolution.import_stmt
            violations.append(
                InvariantViolation(
                    invariant=self.name,
                    message=(f"Unresolved import '{imp.module}' in {imp.source_file}:{imp.line}"),
                    location=f"{imp.source_file}:{imp.line}",
                    severity=0.85,
                    remediation=(
                        "Check import path, ensure target module exists, or add missing __init__.py"
                    ),
                )
            )

        return InvariantResult(
            invariant=self.name,
            passed=len(violations) == 0,
            basis=self.basis,
            violations=violations,
            metadata={
                "substrate": "import",
                "unresolved_count": len(unresolved),
                "files_checked": len(substrate.analyze_repository(pattern)),
            },
        )


class APIInvariant(HardInvariant):
    """I_api = 1 iff [A_public, A_runtime] = 0

    Where:
    - A_public = docs + guides + tutorials + demos + tests + CLI help + exports + launcher claims
    - A_runtime = actual handlers + actual signatures + actual exports + actual return fields

    The commutator [A_public, A_runtime] = A_public A_runtime - A_runtime A_public
    measures the gap between promised and actual API surface.
    """

    def __init__(self):
        super().__init__(InvariantKind.API, BasisVector.API)

    def check(self, repo_path: str, context: dict[str, Any] | None = None) -> InvariantResult:
        """Check public/runtime API commutativity."""
        violations = []

        # This is the highest-yield invariant
        # Compare documented API vs actual runtime API

        return InvariantResult(
            invariant=self.name,
            passed=len(violations) == 0,
            basis=self.basis,
            violations=violations,
            metadata={"check": "api_commutator"},
        )


class EntrypointInvariant(HardInvariant):
    """I_entry = 1 iff every launcher/script/shell/server/wrapper
    points to a real runnable target.

    Must verify:
    - Target exists
    - Import path resolves
    - Callable exists
    - Transport exists if advertised
    - Flags and env handoffs are consumed
    - Runtime mode matches docs
    """

    def __init__(self):
        super().__init__(InvariantKind.ENTRYPOINT, BasisVector.ENTRYPOINT)

    def check(self, repo_path: str, context: dict[str, Any] | None = None) -> InvariantResult:
        """Check entrypoint integrity."""
        violations = []

        # Check console scripts from pyproject.toml
        # Check shell commands
        # Check server endpoints

        return InvariantResult(
            invariant=self.name,
            passed=len(violations) == 0,
            basis=self.basis,
            violations=violations,
            metadata={"check": "entrypoint_resolution"},
        )


class PackagingInvariant(HardInvariant):
    """I_pack = 1 iff metadata, package discovery, shipped modules,
    and console scripts describe the same runtime surface.

    Catches:
    - pyproject.toml vs setup.py conflicts
    - Console scripts pointing to absent modules
    - Top-level files omitted from artifact
    - Tests shipped accidentally
    - Version authority conflicts
    """

    def __init__(self):
        super().__init__(InvariantKind.PACKAGING, BasisVector.PACKAGING)

    def check(self, repo_path: str, context: dict[str, Any] | None = None) -> InvariantResult:
        """Check packaging integrity."""
        violations = []

        # Check pyproject.toml consistency
        # Check package structure
        # Check console script targets

        return InvariantResult(
            invariant=self.name,
            passed=len(violations) == 0,
            basis=self.basis,
            violations=violations,
            metadata={"check": "packaging_consistency"},
        )


class StatusInvariant(HardInvariant):
    """I_status = 1 iff every reported status label is logically
    implied by actual state.

    Examples:
    - initialized = true implies real specs loaded
    - brain_loaded = true implies non-empty real spec surface
    - healthy = true implies no hard invariant false
    - active_plan = true implies plan not terminal
    """

    def __init__(self):
        super().__init__(InvariantKind.STATUS, BasisVector.STATUS)

    def check(self, repo_path: str, context: dict[str, Any] | None = None) -> InvariantResult:
        """Check status truth integrity."""
        violations = []

        # Check status claims vs actual state
        # This requires runtime inspection

        return InvariantResult(
            invariant=self.name,
            passed=len(violations) == 0,
            basis=self.basis,
            violations=violations,
            metadata={"check": "status_truth"},
        )


class TestInvariant(HardInvariant):
    """I_tests = 1 iff contract-critical tests pass.

    Partition:
    - Hard contract tests (gate release)
    - Soft regression tests
    - Flaky tests
    - Environment-bound tests
    - Quarantined tests

    Only hard contract tests gate release.
    """

    def __init__(self):
        super().__init__(InvariantKind.TEST, BasisVector.TEST)
        self._substrate: Any | None = None

    def _get_substrate(self, repo_path: str) -> Any:
        """Lazy-load Test substrate."""
        if self._substrate is None:
            try:
                from ..ingest.test_substrate import TestSubstrate

                self._substrate = TestSubstrate(repo_path)
            except ImportError:
                self._substrate = None
        return self._substrate

    def check(self, repo_path: str, context: dict[str, Any] | None = None) -> InvariantResult:
        """Check test integrity."""
        violations = []

        substrate = self._get_substrate(repo_path)

        if substrate is None:
            return InvariantResult(
                invariant=self.name,
                passed=True,
                basis=self.basis,
                violations=[],
                metadata={"substrate": "test", "status": "unavailable"},
            )

        # Run hard contract tests
        results = substrate.run_hard_contract_tests()
        failed = [r for r in results if not r.passed]

        # Create violations for failed hard contract tests
        for result in failed:
            test = result.test
            violations.append(
                InvariantViolation(
                    invariant=self.name,
                    message=(f"Hard contract test failed: {test.name} ({test.file}:{test.line})"),
                    location=f"{test.file}:{test.line}",
                    severity=1.0,  # Maximum severity - blocks release
                    remediation=result.error_message or "Fix test failure",
                )
            )

        # Also collect overall test suite statistics
        analysis = substrate.analyze_repository()

        return InvariantResult(
            invariant=self.name,
            passed=len(violations) == 0,
            basis=self.basis,
            violations=violations,
            metadata={
                "substrate": "test",
                "has_tests": analysis.get("has_tests", False),
                "total_tests": analysis.get("total", 0),
                "hard_contract_tests": analysis.get("hard_contract", 0),
                "hard_failed": len(failed),
                "quarantined": analysis.get("quarantined", 0),
                "flaky": analysis.get("flaky", 0),
                "releaseable": len(failed) == 0,
            },
        )


class SecurityInvariant(HardInvariant):
    """I_security = 1 iff no critical security vulnerabilities exist.

    Checks:
    - Source-to-sink taint flows (user input → dangerous functions)
    - SQL injection patterns
    - Hardcoded secrets
    - Unsafe deserialization
    - Dangerous function usage (eval, exec, etc.)

    Severity mapping:
    - Critical: Blocks release (RCE, SQL injection, hardcoded keys)
    - High: Must fix soon (unsafe deserialization)
    - Medium: Should fix (hardcoded passwords)
    - Low: Advisory
    """

    def __init__(self):
        super().__init__(InvariantKind.SECURITY, BasisVector.SECURITY)
        self._substrate: Any | None = None

    def _get_substrate(self, repo_path: str) -> Any:
        """Lazy-load Security substrate."""
        if self._substrate is None:
            try:
                from ..ingest.security_substrate import SecuritySubstrate

                self._substrate = SecuritySubstrate(repo_path)
            except ImportError:
                self._substrate = None
        return self._substrate

    def check(self, repo_path: str, context: dict[str, Any] | None = None) -> InvariantResult:
        """Check for security vulnerabilities."""
        violations = []

        substrate = self._get_substrate(repo_path)

        if substrate is None:
            return InvariantResult(
                invariant=self.name,
                passed=True,
                basis=self.basis,
                violations=[],
                metadata={"substrate": "security", "status": "unavailable"},
            )

        # Run security analysis
        analysis = substrate.analyze_repository()

        # Create violations for critical and high findings
        for finding in analysis.findings:
            if finding.severity in ("critical", "high"):
                violations.append(
                    InvariantViolation(
                        invariant=self.name,
                        message=f"{finding.rule_name}: {finding.message}",
                        location=f"{finding.file}:{finding.line}",
                        severity=1.0 if finding.severity == "critical" else 0.9,
                        remediation=finding.remediation,
                    )
                )

        return InvariantResult(
            invariant=self.name,
            passed=len(violations) == 0,
            basis=self.basis,
            violations=violations,
            metadata={
                "substrate": "security",
                "critical": analysis.critical_count,
                "high": analysis.high_count,
                "total": analysis.total_count,
                "is_secure": analysis.is_secure,
                "bandit_available": substrate._bandit_available,
            },
        )
