"""Constraint Engine — Structural constraints for AMOS."""

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List


class ConstraintType(Enum):
    FILE_SIZE = "file_size"
    LINE_COUNT = "line_count"
    EXTENSION = "extension"
    PATH_PATTERN = "path_pattern"
    CONTENT_PATTERN = "content_pattern"
    DEPENDENCY = "dependency"


class ConstraintOp(Enum):
    LT = "lt"  # less than
    GT = "gt"  # greater than
    EQ = "eq"  # equal
    NE = "ne"  # not equal
    LE = "le"  # less or equal
    GE = "ge"  # greater or equal
    MATCH = "match"
    NOT_MATCH = "not_match"


@dataclass
class Constraint:
    """A structural constraint."""

    id: str
    name: str
    constraint_type: ConstraintType
    target: str  # what this constraint applies to
    operator: ConstraintOp
    value: Any
    message: str = ""
    severity: str = "error"  # error, warning, info
    enabled: bool = True
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class ConstraintResult:
    """Result of constraint validation."""

    constraint_id: str
    passed: bool
    target: str
    actual_value: Any
    expected_value: Any
    message: str
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


class ConstraintEngine:
    """Validates structural constraints.

    Responsibilities:
    - Define and manage constraints
    - Validate files/structures against constraints
    - Report violations
    - Enforce structural rules
    """

    def __init__(self):
        self._constraints: Dict[str, Constraint] = {}
        self._history: List[ConstraintResult] = []
        self._setup_default_constraints()

    def _setup_default_constraints(self):
        """Setup default constraints."""
        defaults = [
            Constraint(
                id="max_file_size",
                name="Maximum File Size",
                constraint_type=ConstraintType.FILE_SIZE,
                target="*",
                operator=ConstraintOp.LE,
                value=10 * 1024 * 1024,  # 10MB
                message="File exceeds 10MB limit",
                severity="error",
            ),
            Constraint(
                id="no_pyc_files",
                name="No Compiled Python",
                constraint_type=ConstraintType.EXTENSION,
                target="*",
                operator=ConstraintOp.NOT_MATCH,
                value=r"\.pyc$",
                message="Compiled Python files should not be committed",
                severity="warning",
            ),
            Constraint(
                id="max_line_length",
                name="Max Line Length",
                constraint_type=ConstraintType.CONTENT_PATTERN,
                target="*.py",
                operator=ConstraintOp.MATCH,
                value=r"^.{0,120}$",
                message="Lines should not exceed 120 characters",
                severity="warning",
            ),
        ]
        for c in defaults:
            self._constraints[c.id] = c

    def add_constraint(self, constraint: Constraint) -> str:
        """Add a new constraint."""
        self._constraints[constraint.id] = constraint
        return constraint.id

    def remove_constraint(self, constraint_id: str) -> bool:
        """Remove a constraint."""
        if constraint_id in self._constraints:
            del self._constraints[constraint_id]
            return True
        return False

    def validate_file(self, filepath: str, content: str = None) -> List[ConstraintResult]:
        """Validate a file against all applicable constraints."""
        results = []

        for constraint in self._constraints.values():
            if not constraint.enabled:
                continue

            # Check if constraint applies to this file
            if not self._applies_to(constraint, filepath):
                continue

            result = self._check_constraint(constraint, filepath, content)
            results.append(result)
            self._history.append(result)

        return results

    def _applies_to(self, constraint: Constraint, filepath: str) -> bool:
        """Check if constraint applies to filepath."""
        if constraint.target == "*":
            return True
        if constraint.target.startswith("*."):
            ext = constraint.target[1:]
            return filepath.endswith(ext)
        return filepath == constraint.target or constraint.target in filepath

    def _check_constraint(
        self, constraint: Constraint, filepath: str, content: str = None
    ) -> ConstraintResult:
        """Check a single constraint."""
        try:
            actual = self._get_actual_value(constraint, filepath, content)
            expected = constraint.value
            passed = self._compare(constraint.operator, actual, expected)

            return ConstraintResult(
                constraint_id=constraint.id,
                passed=passed,
                target=filepath,
                actual_value=actual,
                expected_value=expected,
                message=constraint.message if not passed else "",
            )
        except Exception as e:
            return ConstraintResult(
                constraint_id=constraint.id,
                passed=False,
                target=filepath,
                actual_value=None,
                expected_value=constraint.value,
                message=f"Error checking constraint: {e}",
            )

    def _get_actual_value(self, constraint: Constraint, filepath: str, content: str = None) -> Any:
        """Get actual value for comparison."""
        import os

        if constraint.constraint_type == ConstraintType.FILE_SIZE:
            return os.path.getsize(filepath)

        elif constraint.constraint_type == ConstraintType.LINE_COUNT:
            if content:
                return len(content.splitlines())
            with open(filepath, encoding="utf-8", errors="ignore") as f:
                return len(f.readlines())

        elif constraint.constraint_type == ConstraintType.EXTENSION:
            return filepath.split(".")[-1] if "." in filepath else ""

        elif constraint.constraint_type == ConstraintType.PATH_PATTERN:
            return filepath

        elif constraint.constraint_type == ConstraintType.CONTENT_PATTERN:
            if content:
                return content
            with open(filepath, encoding="utf-8", errors="ignore") as f:
                return f.read()

        return None

    def _compare(self, op: ConstraintOp, actual: Any, expected: Any) -> bool:
        """Compare actual vs expected using operator."""
        if op == ConstraintOp.LT:
            return actual < expected
        elif op == ConstraintOp.GT:
            return actual > expected
        elif op == ConstraintOp.EQ:
            return actual == expected
        elif op == ConstraintOp.NE:
            return actual != expected
        elif op == ConstraintOp.LE:
            return actual <= expected
        elif op == ConstraintOp.GE:
            return actual >= expected
        elif op == ConstraintOp.MATCH:
            return bool(re.match(expected, str(actual), re.MULTILINE))
        elif op == ConstraintOp.NOT_MATCH:
            return not bool(re.match(expected, str(actual), re.MULTILINE))
        return False

    def validate_batch(self, filepaths: List[str]) -> dict[str, list[ConstraintResult]]:
        """Validate multiple files."""
        return {fp: self.validate_file(fp) for fp in filepaths}

    def get_violations(self, severity: str = None, limit: int = 100) -> List[ConstraintResult]:
        """Get constraint violations from history."""
        violations = [r for r in self._history if not r.passed]
        if severity:
            # Filter by constraint severity
            filtered = []
            for v in violations:
                c = self._constraints.get(v.constraint_id)
                if c and c.severity == severity:
                    filtered.append(v)
            violations = filtered
        return violations[-limit:]

    def status(self) -> Dict[str, Any]:
        """Get engine status."""
        violations = [r for r in self._history if not r.passed]
        return {
            "total_constraints": len(self._constraints),
            "enabled_constraints": sum(1 for c in self._constraints.values() if c.enabled),
            "total_validations": len(self._history),
            "total_violations": len(violations),
            "by_severity": {
                "error": len(
                    [
                        v
                        for v in violations
                        if self._constraints.get(
                            v.constraint_id, Constraint(severity="error")
                        ).severity
                        == "error"
                    ]
                ),
                "warning": len(
                    [
                        v
                        for v in violations
                        if self._constraints.get(
                            v.constraint_id, Constraint(severity="warning")
                        ).severity
                        == "warning"
                    ]
                ),
            },
        }
