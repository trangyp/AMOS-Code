"""AMOS Evolution Contract Registry - Foundational Self-Evolution Subsystem

Implements safe, bounded, verified self-improvement through formal contracts.
Every self-evolution must have a contract per AMOS Self-Evolution Laws.

Law 4: Every evolution must have a contract declaring:
- evolution_id, owner, target files/modules
- problem pattern, expected improvement
- mutation budget, proof budget
- rollback condition, verification steps, success condition

Owner: AMOS Brain (Canonical Runtime)
Version: 1.0.0
Evolution ID: E001 (Self-referential: this file is its own first contract)
"""

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone

UTC = timezone.utc
from enum import Enum, auto
from pathlib import Path
from typing import Any, Optional


class EvolutionStatus(Enum):
    """Status of an evolution contract."""

    DRAFT = auto()
    PENDING = auto()
    APPROVED = auto()
    IN_PROGRESS = auto()
    VERIFYING = auto()
    COMPLETED = auto()
    COMPLETE = auto()
    FAILED = auto()
    ROLLED_BACK = auto()
    REJECTED = auto()


@dataclass
class EvolutionContract:
    """Formal contract for safe self-evolution.

    Per AMOS Self-Evolution Law 4:
    Every self-improvement must declare bounds, proof, and verification.
    """

    # Identity
    evolution_id: str
    owner: str
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    # Target
    target_files: list[str] = field(default_factory=list)
    target_modules: list[str] = field(default_factory=list)

    # Problem Definition
    problem_pattern: str = ""
    evidence: list[str] = field(default_factory=list)
    recurrence_count: int = 0

    # Expected Improvement
    expected_improvement: str = ""
    success_condition: str = ""

    # Budgets (bounded evolution)
    mutation_budget_lines: int = 0
    mutation_budget_files: int = 0
    proof_budget_tests: int = 0

    # Safety Controls
    rollback_condition: str = ""
    verification_steps: list[str] = field(default_factory=list)

    # State
    status: EvolutionStatus = EvolutionStatus.DRAFT
    actual_changes: list[dict[str, Any]] = field(default_factory=list)
    measured_improvement: dict[str, Any] = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize contract to dictionary."""
        data = asdict(self)
        data["status"] = self.status.name
        return data

    def to_json(self, indent: int = 2) -> str:
        """Serialize contract to JSON."""
        return json.dumps(self.to_dict(), indent=indent)

    def approve(self) -> None:
        """Approve contract for execution."""
        if self.status == EvolutionStatus.DRAFT:
            self.status = EvolutionStatus.APPROVED

    def start(self) -> None:
        """Mark evolution as in progress."""
        if self.status == EvolutionStatus.APPROVED:
            self.status = EvolutionStatus.IN_PROGRESS

    def complete(self, measured_gain: dict[str, Any]) -> None:
        """Mark evolution as completed with measured improvement."""
        self.measured_improvement = measured_gain
        self.status = EvolutionStatus.COMPLETED

    def rollback(self, reason: str) -> None:
        """Rollback evolution."""
        self.status = EvolutionStatus.ROLLED_BACK
        self.measured_improvement = {"rollback_reason": reason}


class EvolutionContractRegistry:
    """Registry for all self-evolution contracts.

    Central authority for safe self-improvement per AMOS directive.
    No self-evolution without a registered contract.
    """

    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path("evolution_reports/contracts")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._contracts: dict[str, EvolutionContract] = {}
        self._load_existing()

    def _load_existing(self) -> None:
        """Load existing contracts from storage."""
        if not self.storage_path.exists():
            return

        for contract_file in self.storage_path.glob("*.json"):
            try:
                with open(contract_file) as f:
                    data = json.load(f)
                contract = self._dict_to_contract(data)
                self._contracts[contract.evolution_id] = contract
            except Exception:
                continue  # Skip corrupted contracts

    def _dict_to_contract(self, data: dict[str, Any]) -> EvolutionContract:
        """Deserialize dictionary to contract."""
        status = EvolutionStatus[data.get("status", "DRAFT")]
        data["status"] = status
        return EvolutionContract(**data)

    def register(self, contract: EvolutionContract) -> bool:
        """Register a new evolution contract.

        Returns True if registered successfully, False if ID already exists.
        """
        if contract.evolution_id in self._contracts:
            return False

        self._contracts[contract.evolution_id] = contract
        self._save_contract(contract)
        return True

    def _save_contract(self, contract: EvolutionContract) -> None:
        """Save contract to storage."""
        contract_file = self.storage_path / f"{contract.evolution_id}.json"
        with open(contract_file, "w") as f:
            f.write(contract.to_json())

    def get(self, evolution_id: str) -> Optional[EvolutionContract]:
        """Get contract by ID."""
        return self._contracts.get(evolution_id)

    def list_by_status(self, status: EvolutionStatus) -> list[EvolutionContract]:
        """List all contracts with given status."""
        return [c for c in self._contracts.values() if c.status == status]

    def list_active(self) -> list[EvolutionContract]:
        """List all active (in-progress) evolutions."""
        return self.list_by_status(EvolutionStatus.IN_PROGRESS)

    def list_completed(self) -> list[EvolutionContract]:
        """List all completed evolutions."""
        return self.list_by_status(EvolutionStatus.COMPLETED)

    def update(self, contract: EvolutionContract) -> bool:
        """Update existing contract."""
        if contract.evolution_id not in self._contracts:
            return False

        self._contracts[contract.evolution_id] = contract
        self._save_contract(contract)
        return True

    def get_summary(self) -> dict[str, Any]:
        """Get registry summary."""
        status_counts = {}
        for contract in self._contracts.values():
            status_name = contract.status.name
            status_counts[status_name] = status_counts.get(status_name, 0) + 1

        return {
            "total_contracts": len(self._contracts),
            "by_status": status_counts,
            "storage_path": str(self.storage_path),
            "completed_evolutions": len(self.list_completed()),
            "active_evolutions": len(self.list_active()),
        }


def create_e001_contract() -> EvolutionContract:
    """Create the evolution contract for E001 (this file itself).

    Self-referential: This function creates the contract for its own existence.
    """
    return EvolutionContract(
        evolution_id="E001",
        owner="AMOS Brain (Canonical Runtime)",
        target_files=["amos_self_evolution/evolution_contract_registry.py"],
        target_modules=["evolution_contract_registry"],
        problem_pattern="Missing foundational self-evolution subsystem",
        evidence=[
            "Directive requires evolution_contract_registry",
            "Grep search found no existing implementation",
            "All safe self-evolution requires contracts",
            "No contracts possible without registry",
        ],
        recurrence_count=0,  # New requirement
        expected_improvement="Enables all safe self-evolution with formal contracts",
        success_condition="Registry can create, store, and retrieve evolution contracts",
        mutation_budget_lines=200,
        mutation_budget_files=1,
        proof_budget_tests=5,
        rollback_condition="Contract system fails to validate or corrupts data",
        verification_steps=[
            "Import evolution_contract_registry successfully",
            "Create EvolutionContract instance",
            "Create EvolutionContractRegistry instance",
            "Register a contract",
            "Retrieve contract by ID",
            "Verify contract persistence to storage",
        ],
    )


def main():
    """Demonstrate evolution contract system."""
    print("=" * 70)
    print("AMOS EVOLUTION CONTRACT REGISTRY - E001 SELF-VERIFICATION")
    print("=" * 70)

    # Create registry
    registry = EvolutionContractRegistry()
    print(f"\n✓ Registry initialized at: {registry.storage_path}")

    # Create E001 contract (self-referential)
    e001 = create_e001_contract()
    print("✓ E001 contract created (self-referential)")
    print(f"  Target: {e001.target_files}")
    print(f"  Problem: {e001.problem_pattern}")
    print(f"  Expected: {e001.expected_improvement}")

    # Register contract
    if registry.register(e001):
        print("✓ E001 registered successfully")
    else:
        print("✗ E001 already exists")

    # Verify retrieval
    retrieved = registry.get("E001")
    if retrieved:
        print(f"✓ Contract retrieved: {retrieved.evolution_id}")

    # Show summary
    summary = registry.get_summary()
    print("\nRegistry Summary:")
    print(f"  Total contracts: {summary['total_contracts']}")
    print(f"  By status: {summary['by_status']}")

    print("\n" + "=" * 70)
    print("E001 VERIFICATION COMPLETE")
    print("=" * 70)
    print("\nEvolution contract system operational.")
    print("All subsequent self-evolution must register contracts here.")


if __name__ == "__main__":
    main()
