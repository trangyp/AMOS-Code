"""Observable definitions for repository measurement.

Typed facts extracted from repository analysis.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class ObservableKind(Enum):
    """Observable fact types."""

    PARSE_FATAL = auto()
    PARSE_RECOVERABLE = auto()
    IMPORT_UNRESOLVED = auto()
    EXPORT_MISSING = auto()
    CALL_ARITY_MISMATCH = auto()
    CALL_KWARG_MISMATCH = auto()
    RETURN_SHAPE_MISMATCH = auto()
    ENTRYPOINT_MISSING = auto()
    ENTRYPOINT_WRONG_TARGET = auto()
    UNCONSUMED_FLAG = auto()
    PACKAGING_CONFLICT = auto()
    BUILD_FAILURE = auto()
    ROUNDTRIP_FAILURE = auto()
    STATUS_FALSE_CLAIM = auto()
    RUNTIME_CONTRACT_VIOLATION = auto()
    TEST_CONTRACT_FAILURE = auto()
    DOC_EXAMPLE_FAILURE = auto()
    SECURITY_FLOW_VIOLATION = auto()
    TEMPORAL_BREAKPOINT = auto()


@dataclass
class CodeLocation:
    """Source code location reference."""

    file: str
    line: int = 0
    column: int = 0
    symbol: str = ""


@dataclass
class Observable:
    """Typed fact from repository measurement.

    Example:
        {
            "kind": "call_kwarg_mismatch",
            "caller": {"file": "demo.py", "symbol": "run"},
            "callee": {"file": "lib.py", "symbol": "run"},
            "unexpected_kwarg": "team",
            "surface": "demo_vs_runtime",
            "severity": 0.95
        }
    """

    kind: ObservableKind
    severity: float  # 0.0 to 1.0

    # Location information
    file: str = ""
    line: int = 0
    symbol: str = ""

    # Detailed context
    message: str = ""
    context: Dict[str, Any] = field(default_factory=dict)

    # Affected basis vectors
    basis_impact: List[str] = field(default_factory=list)

    def __post_init__(self):
        self.severity = max(0.0, min(1.0, self.severity))

        # Auto-populate basis impact from kind
        if not self.basis_impact:
            self.basis_impact = self._default_basis_impact()

    def _default_basis_impact(self) -> List[str]:
        """Map observable kind to affected basis vectors."""
        mapping = {
            ObservableKind.PARSE_FATAL: ["SYNTAX"],
            ObservableKind.PARSE_RECOVERABLE: ["SYNTAX"],
            ObservableKind.IMPORT_UNRESOLVED: ["IMPORT"],
            ObservableKind.EXPORT_MISSING: ["API", "IMPORT"],
            ObservableKind.CALL_ARITY_MISMATCH: ["TYPE", "API"],
            ObservableKind.CALL_KWARG_MISMATCH: ["TYPE", "API"],
            ObservableKind.RETURN_SHAPE_MISMATCH: ["TYPE", "API"],
            ObservableKind.ENTRYPOINT_MISSING: ["ENTRYPOINT", "PACKAGING"],
            ObservableKind.ENTRYPOINT_WRONG_TARGET: ["ENTRYPOINT", "RUNTIME"],
            ObservableKind.UNCONSUMED_FLAG: ["RUNTIME", "STATUS"],
            ObservableKind.PACKAGING_CONFLICT: ["PACKAGING"],
            ObservableKind.BUILD_FAILURE: ["PACKAGING"],
            ObservableKind.ROUNDTRIP_FAILURE: ["PERSISTENCE"],
            ObservableKind.STATUS_FALSE_CLAIM: ["STATUS"],
            ObservableKind.RUNTIME_CONTRACT_VIOLATION: ["RUNTIME", "API"],
            ObservableKind.TEST_CONTRACT_FAILURE: ["TEST", "API"],
            ObservableKind.DOC_EXAMPLE_FAILURE: ["DOCS", "API"],
            ObservableKind.SECURITY_FLOW_VIOLATION: ["SECURITY"],
            ObservableKind.TEMPORAL_BREAKPOINT: ["HISTORY"],
        }
        return mapping.get(self.kind, ["SYNTAX"])

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "kind": self.kind.name,
            "severity": self.severity,
            "file": self.file,
            "line": self.line,
            "symbol": self.symbol,
            "message": self.message,
            "context": self.context,
            "basis_impact": self.basis_impact,
        }
