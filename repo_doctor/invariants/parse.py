"""
I_parse = 1 iff every required source file yields acceptable parse tree

Tree-sitter provides incremental, error-tolerant parsing.
"""

from typing import Any, Dict

from ..constants import MSG_PARSING_SUCCESS
from .base import Invariant, InvariantResult, InvariantSeverity


class ParseInvariant(Invariant):
    """
    Parse integrity invariant.
    All source files must parse without fatal errors.
    """

    def __init__(self):
        super().__init__("I_parse", InvariantSeverity.CRITICAL)

    def check(self, repo_path: str, context: Dict[str, Any] = None) -> InvariantResult:
        """Check parse integrity."""
        context = context or {}
        parse_errors = context.get("parse_fatal", 0)
        recoverable = context.get("parse_recoverable", 0)
        total_files = context.get("total_files", 1)

        # Acceptable if no fatal errors and recoverable below threshold
        if parse_errors == 0 and recoverable / max(total_files, 1) < 0.1:
            return InvariantResult(
                name=self.name,
                passed=True,
                severity=self.severity,
                message=MSG_PARSING_SUCCESS,
            )

        return InvariantResult(
            name=self.name,
            passed=False,
            severity=self.severity,
            message=f"Parse failures: {parse_errors} fatal, {recoverable} recoverable",
            details={"fatal": parse_errors, "recoverable": recoverable},
        )
