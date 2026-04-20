"""
Repo Doctor Omega - Hard Invariant System

I = {I_parse, I_import, I_type, I_api, I_entry, I_pack, I_persist,
     I_status, I_tests, I_runtime, I_security, I_history}

RepoValid = ∧ I_n  (Pass/Fail, not "mostly valid")
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .state_vector import StateDimension


class InvariantType(Enum):
    """Types of hard invariants."""

    PARSE = "parse"
    IMPORT = "import"
    TYPE = "type"
    API = "api"
    ENTRYPOINT = "entrypoint"
    PACKAGING = "packaging"
    PERSISTENCE = "persistence"
    STATUS = "status"
    TESTS = "tests"
    RUNTIME = "runtime"
    SECURITY = "security"
    HISTORY = "history"


@dataclass
class InvariantResult:
    """Result of an invariant check."""

    invariant_type: InvariantType
    passed: bool
    severity: str = "error"  # error, warning, info
    details: list[str] = field(default_factory=list)
    files_affected: list[str] = field(default_factory=list)
    remediation: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "invariant": self.invariant_type.value,
            "passed": self.passed,
            "severity": self.severity,
            "details": self.details,
            "files_affected": self.files_affected,
            "remediation": self.remediation,
        }


class Invariant(ABC):
    """Base class for hard invariants."""

    def __init__(self, inv_type: InvariantType):
        self.inv_type = inv_type

    @abstractmethod
    def check(self, repo_path: str, sensor_data: dict[str, Any]) -> InvariantResult:
        """Check if invariant holds. Must return pass/fail."""
        pass

    def dimension(self) -> StateDimension:
        """Map invariant to state dimension."""
        mapping = {
            InvariantType.PARSE: StateDimension.SYNTAX,
            InvariantType.IMPORT: StateDimension.IMPORTS,
            InvariantType.TYPE: StateDimension.TYPES,
            InvariantType.API: StateDimension.API,
            InvariantType.ENTRYPOINT: StateDimension.ENTRYPOINTS,
            InvariantType.PACKAGING: StateDimension.PACKAGING,
            InvariantType.PERSISTENCE: StateDimension.PERSISTENCE,
            InvariantType.STATUS: StateDimension.DOCS_TESTS_DEMOS,
            InvariantType.TESTS: StateDimension.DOCS_TESTS_DEMOS,
            InvariantType.RUNTIME: StateDimension.RUNTIME,
            InvariantType.SECURITY: StateDimension.SECURITY,
            InvariantType.HISTORY: StateDimension.HISTORY,
        }
        return mapping.get(self.inv_type, StateDimension.SYNTAX)


class ParseInvariant(Invariant):
    """I_parse: All source files parse."""

    def __init__(self):
        super().__init__(InvariantType.PARSE)

    def check(self, repo_path: str, sensor_data: dict[str, Any]) -> InvariantResult:
        parse_errors = sensor_data.get("parse_errors", 0)
        error_files = sensor_data.get("parse_error_files", [])

        return InvariantResult(
            invariant_type=self.inv_type,
            passed=parse_errors == 0,
            severity="critical" if parse_errors > 0 else "info",
            details=[f"{parse_errors} files failed to parse"] if parse_errors > 0 else [],
            files_affected=error_files,
            remediation="Fix syntax errors in affected files" if parse_errors > 0 else "",
        )


class ImportInvariant(Invariant):
    """I_import: All public imports resolve."""

    def __init__(self):
        super().__init__(InvariantType.IMPORT)

    def check(self, repo_path: str, sensor_data: dict[str, Any]) -> InvariantResult:
        unresolved = sensor_data.get("unresolved_imports", 0)
        details = sensor_data.get("unresolved_import_details", [])

        return InvariantResult(
            invariant_type=self.inv_type,
            passed=unresolved == 0,
            severity="error" if unresolved > 0 else "info",
            details=[f"{unresolved} unresolved imports"] if unresolved > 0 else [],
            files_affected=[d.split(":")[0] for d in details if ":" in d],
            remediation="Fix or remove unresolved imports" if unresolved > 0 else "",
        )


class APIInvariant(Invariant):
    """I_api: Public contracts commute [A_public, A_runtime] = 0."""

    def __init__(self):
        super().__init__(InvariantType.API)

    def check(self, repo_path: str, sensor_data: dict[str, Any]) -> InvariantResult:
        mismatches = sensor_data.get("signature_mismatches", 0)
        drift_details = sensor_data.get("api_drift_details", [])

        return InvariantResult(
            invariant_type=self.inv_type,
            passed=mismatches == 0,
            severity="critical" if mismatches > 0 else "info",
            details=[f"{mismatches} API contract mismatches"] if mismatches > 0 else [],
            files_affected=[],
            remediation="Align public contracts with runtime surface" if mismatches > 0 else "",
        )


class EntrypointInvariant(Invariant):
    """I_entry: All entrypoints exist and run."""

    def __init__(self):
        super().__init__(InvariantType.ENTRYPOINT)

    def check(self, repo_path: str, sensor_data: dict[str, Any]) -> InvariantResult:
        missing = sensor_data.get("missing_entrypoints", 0)
        names = sensor_data.get("missing_entrypoint_names", [])

        return InvariantResult(
            invariant_type=self.inv_type,
            passed=missing == 0,
            severity="error" if missing > 0 else "info",
            details=[f"{missing} missing entrypoints: {', '.join(names)}"] if missing > 0 else [],
            files_affected=[],
            remediation="Create missing entrypoints or update package metadata"
            if missing > 0
            else "",
        )


class PackagingInvariant(Invariant):
    """I_pack: Package metadata matches shipped surface."""

    def __init__(self):
        super().__init__(InvariantType.PACKAGING)

    def check(self, repo_path: str, sensor_data: dict[str, Any]) -> InvariantResult:
        conflicts = sensor_data.get("packaging_conflicts", 0)
        metadata_issues = sensor_data.get("metadata_issues", [])

        return InvariantResult(
            invariant_type=self.inv_type,
            passed=conflicts == 0,
            severity="error" if conflicts > 0 else "info",
            details=[f"{conflicts} packaging conflicts"] if conflicts > 0 else [],
            files_affected=[],
            remediation="Align pyproject.toml/setup.py with actual module structure"
            if conflicts > 0
            else "",
        )


class TestInvariant(Invariant):
    """I_tests: Critical test set passes."""

    def __init__(self):
        super().__init__(InvariantType.TESTS)

    def check(self, repo_path: str, sensor_data: dict[str, Any]) -> InvariantResult:
        failures = sensor_data.get("test_failures", 0)
        total = sensor_data.get("total_tests", 1)

        return InvariantResult(
            invariant_type=self.inv_type,
            passed=failures == 0,
            severity="error" if failures > 0 else "info",
            details=[f"{failures}/{total} tests failed"] if failures > 0 else [],
            files_affected=[],
            remediation="Fix failing tests" if failures > 0 else "",
        )


class SecurityInvariant(Invariant):
    """I_security: No critical vulnerabilities."""

    def __init__(self):
        super().__init__(InvariantType.SECURITY)

    def check(self, repo_path: str, sensor_data: dict[str, Any]) -> InvariantResult:
        critical = sensor_data.get("critical_findings", 0)
        high = sensor_data.get("high_findings", 0)

        return InvariantResult(
            invariant_type=self.inv_type,
            passed=critical == 0 and high == 0,
            severity="critical" if critical > 0 else ("error" if high > 0 else "info"),
            details=[f"{critical} critical, {high} high severity findings"],
            files_affected=[],
            remediation="Address security findings immediately" if critical > 0 else "",
        )


class InvariantPack:
    """Collection of invariants to check together."""

    def __init__(self):
        self.invariants: list[Invariant] = []

    def add(self, invariant: Invariant) -> None:
        """Add an invariant to the pack."""
        self.invariants.append(invariant)

    def check_all(self, repo_path: str, sensor_data: dict[str, Any]) -> list[InvariantResult]:
        """Run all invariants and return results."""
        return [inv.check(repo_path, sensor_data) for inv in self.invariants]

    @property
    def all_passed(self) -> bool:
        """Check if all invariants passed (requires check_all first)."""
        return all(r.passed for r in self._last_results)


class InvariantChecker:
    """Main invariant checking orchestrator."""

    def __init__(self):
        self.packs: dict[str, InvariantPack] = {}

    def create_default_pack(self) -> InvariantPack:
        """Create the default hard invariant pack."""
        pack = InvariantPack()
        pack.add(ParseInvariant())
        pack.add(ImportInvariant())
        pack.add(APIInvariant())
        pack.add(EntrypointInvariant())
        pack.add(PackagingInvariant())
        pack.add(TestInvariant())
        pack.add(SecurityInvariant())
        return pack

    def check_repo_valid(
        self, repo_path: str, sensor_data: dict[str, Any]
    ) -> tuple[bool, list[InvariantResult]]:
        """
        Check if repository is valid: RepoValid = ∧ I_n

        Returns (is_valid, failed_invariants)
        """
        pack = self.create_default_pack()
        results = pack.check_all(repo_path, sensor_data)

        failed = [r for r in results if not r.passed]
        is_valid = len(failed) == 0

        return is_valid, failed
