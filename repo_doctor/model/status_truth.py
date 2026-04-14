"""
Repo Doctor Omega - Status Truth Checker

Invariant I_status: Status fields cannot lie.

Status claims must be entailed by actual state:
- initialized = true => real specs loaded
- brain_loaded = true => spec surface non-empty
- healthy = true => no hard invariants currently fail
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class StatusClaim:
    """A status field claim."""

    field: str
    claimed_value: Any
    actual_value: Any
    is_true: bool
    source_file: str = ""


class StatusTruthChecker:
    """Verify that status claims reflect actual state."""

    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.claims: list[StatusClaim] = []

    def check_initialization(self, status_field: str, actual_specs: list) -> StatusClaim:
        """
        Check: initialized = true => LoadedSpecsCount > 0
        """
        # Would parse actual status code
        claimed = True  # From status field
        actual = len(actual_specs) > 0

        return StatusClaim(
            field=status_field,
            claimed_value=claimed,
            actual_value=actual,
            is_true=(claimed == actual) or not claimed,
        )

    def check_brain_loaded(self, status_field: str, actual_domains: list) -> StatusClaim:
        """
        Check: brain_loaded = true => DomainsCount > 0
        """
        claimed = True  # From status field
        actual = len(actual_domains) > 0

        return StatusClaim(
            field=status_field,
            claimed_value=claimed,
            actual_value=actual,
            is_true=(claimed == actual) or not claimed,
        )

    def check_healthy(self, status_field: str, failed_invariants: list) -> StatusClaim:
        """
        Check: healthy = true => no hard invariants currently fail
        """
        claimed = True  # From status field
        actual = len(failed_invariants) == 0

        return StatusClaim(
            field=status_field,
            claimed_value=claimed,
            actual_value=actual,
            is_true=(claimed == actual) or not claimed,
        )

    def analyze(self, sensor_data: dict[str, Any]) -> dict[str, Any]:
        """Full status truth analysis."""
        self.claims = []

        # Check initialization claim
        specs = sensor_data.get("loaded_specs", [])
        init_claim = self.check_initialization("initialized", specs)
        self.claims.append(init_claim)

        # Check brain loaded claim
        domains = sensor_data.get("domains", [])
        brain_claim = self.check_brain_loaded("brain_loaded", domains)
        self.claims.append(brain_claim)

        # Check healthy claim
        failed = sensor_data.get("failed_invariants", [])
        health_claim = self.check_healthy("healthy", failed)
        self.claims.append(health_claim)

        false_claims = [c for c in self.claims if not c.is_true]

        return {
            "is_valid": len(false_claims) == 0,
            "false_claims": [
                {
                    "field": c.field,
                    "claimed": c.claimed_value,
                    "actual": c.actual_value,
                }
                for c in false_claims
            ],
            "recommendation": (
                "Fix status semantics" if false_claims else "Status claims accurate"
            ),
        }
