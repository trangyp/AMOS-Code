"""AMOS Global Laws - In-memory representation of AMOS legal framework."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LawViolation:
    """Represents a detected law violation."""

    law_id: str
    law_name: str
    severity: str
    message: str
    suggestion: str


class GlobalLaws:
    """Enforces AMOS global laws on outputs and decisions."""

    # Keywords that trigger law scrutiny
    PROHIBITED_PATTERNS = {
        "L4": [
            ("I feel", "Avoid claiming feelings"),
            ("truth is", "Use 'evidence indicates'"),
        ],
    }

    def __init__(self):
        self.violations: list[LawViolation] = []

    def check_output(self, text: str) -> list[LawViolation]:
        """Check text output for law violations."""
        violations = []
        text_lower = text.lower()

        for law_id, patterns in self.PROHIBITED_PATTERNS.items():
            for pattern, suggestion in patterns:
                if pattern.lower() in text_lower:
                    violations.append(
                        LawViolation(
                            law_id=law_id,
                            law_name=self._get_law_name(law_id),
                            severity="warning",
                            message=f"Detected: '{pattern}'",
                            suggestion=suggestion,
                        )
                    )

        return violations

    def _get_law_name(self, law_id: str) -> str:
        """Get law name from ID."""
        names = {
            "L1": "Law of Law",
            "L2": "Rule of 2",
            "L3": "Rule of 4",
            "L4": "Absolute Structural Integrity",
        }
        return names.get(law_id, "Unknown Law")

    def validate_decision(
        self,
        decision: str,
        quadrants_checked: list[str] | None = None,
    ) -> list[LawViolation]:
        """Validate a decision follows Rule of 4."""
        violations = []

        expected = ["biological", "technical", "economic", "environmental"]
        checked = [q.lower() for q in (quadrants_checked or [])]

        missing = [q for q in expected if q not in checked]

        if missing:
            violations.append(
                LawViolation(
                    law_id="L3",
                    law_name="Rule of 4",
                    severity="warning",
                    message=f"Missing quadrants: {', '.join(missing)}",
                    suggestion="Consider all four quadrants or justify omissions",
                )
            )

        return violations
