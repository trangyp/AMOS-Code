"""Law layer type definitions - Invariant, Severity, ValidationResult"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Severity(str, Enum):
    INFO = "info"
    WARN = "warn"
    ERROR = "error"
    FATAL = "fatal"


@dataclass(frozen=True)
class InvariantResult:
    name: str
    passed: bool
    score: float
    severity: Severity
    message: str


@dataclass(frozen=True)
class QuadrantIntegrity:
    code: float
    build: float
    runtime: float
    environment: float

    @property
    def global_integrity(self) -> float:
        return (self.code + self.build + self.runtime + self.environment) / 4.0


@dataclass(frozen=True)
class ValidationResult:
    passed: bool
    contradiction_score: float
    collapse_risk: float
    quadrants: QuadrantIntegrity
    results: list[InvariantResult] = field(default_factory=list)
    timestamp: str = ""

    @property
    def healthy(self) -> bool:
        return self.passed and self.collapse_risk < 0.5


@dataclass(frozen=True)
class Law:
    """A single law with id, name, description and priority."""

    id: str
    name: str
    description: str
    priority: int


@dataclass(frozen=True)
class LawCheckResult:
    """Result of law compliance check."""

    compliant: bool
    violations: list[str]
