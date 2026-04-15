"""
Evolution Contract System - Bounded Self-Improvement Contracts.

Every self-improvement must have a contract declaring:
- evolution_id: Unique identifier
- owner: Responsible module
- target_files: What will be changed
- problem_pattern: What weakness is being addressed
- expected_improvement: Measurable gain
- mutation_budget: Scope limits
- verification_steps: How to prove it worked
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class EvolutionStatus(Enum):
    """Status of an evolution contract."""

    DETECTED = "detected"
    CONTRACTED = "contracted"
    APPROVED = "approved"
    PATCHING = "patching"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    ROLLED_BACK = "rolled_back"
    REJECTED = "rejected"


@dataclass
class EvolutionContract:
    """
    A bounded self-improvement contract.

    Attributes:
        evolution_id: Unique identifier for this evolution
        owner: Module or component responsible
        target_files: List of files to be modified
        problem_pattern: Description of recurring weakness
        expected_improvement: Measurable expected gain
        mutation_budget: Max files/lines to change
        proof_budget: Max effort for verification
        rollback_condition: When to revert
        verification_steps: List of verification actions
        success_condition: How to know it succeeded
        created_at: Timestamp
        status: Current status
        actual_improvement: Measured gain (filled after)
        patched_files: Actual files changed (filled after)

    """

    evolution_id: str
    owner: str
    target_files: list[str]
    problem_pattern: str
    expected_improvement: str
    mutation_budget: str
    proof_budget: str
    rollback_condition: str
    verification_steps: list[str]
    success_condition: str
    created_at: datetime = field(default_factory=datetime.now)
    status: EvolutionStatus = EvolutionStatus.CONTRACTED
    actual_improvement: str | None = None
    patched_files: list[str] = field(default_factory=list)
    pre_state_hash: str | None = None
    post_state_hash: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert contract to dictionary."""
        return {
            "evolution_id": self.evolution_id,
            "owner": self.owner,
            "target_files": self.target_files,
            "problem_pattern": self.problem_pattern,
            "expected_improvement": self.expected_improvement,
            "mutation_budget": self.mutation_budget,
            "proof_budget": self.proof_budget,
            "rollback_condition": self.rollback_condition,
            "verification_steps": self.verification_steps,
            "success_condition": self.success_condition,
            "created_at": self.created_at.isoformat(),
            "status": self.status.value,
            "actual_improvement": self.actual_improvement,
            "patched_files": self.patched_files,
            "pre_state_hash": self.pre_state_hash,
            "post_state_hash": self.post_state_hash,
        }


class EvolutionRegistry:
    """Registry of all evolution contracts and their outcomes."""

    def __init__(self) -> None:
        """Initialize empty registry."""
        self.contracts: dict[str, EvolutionContract] = {}
        self.completed: list[EvolutionContract] = []
        self.rolled_back: list[EvolutionContract] = []

    def register(self, contract: EvolutionContract) -> None:
        """Register a new evolution contract."""
        self.contracts[contract.evolution_id] = contract

    def complete(self, evolution_id: str, actual_improvement: str) -> None:
        """Mark an evolution as completed."""
        if evolution_id in self.contracts:
            contract = self.contracts[evolution_id]
            contract.status = EvolutionStatus.COMPLETED
            contract.actual_improvement = actual_improvement
            self.completed.append(contract)
            del self.contracts[evolution_id]

    def rollback(self, evolution_id: str, reason: str) -> None:
        """Mark an evolution as rolled back."""
        if evolution_id in self.contracts:
            contract = self.contracts[evolution_id]
            contract.status = EvolutionStatus.ROLLED_BACK
            contract.actual_improvement = f"ROLLED_BACK: {reason}"
            self.rolled_back.append(contract)
            del self.contracts[evolution_id]

    def get_active(self) -> list[EvolutionContract]:
        """Get all active (non-completed) contracts."""
        return list(self.contracts.values())

    def get_success_rate(self) -> float:
        """Calculate success rate of completed evolutions."""
        total = len(self.completed) + len(self.rolled_back)
        if total == 0:
            return 1.0
        return len(self.completed) / total
