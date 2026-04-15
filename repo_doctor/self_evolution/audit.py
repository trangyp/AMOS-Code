"""Evolution Audit & Governance Layer - Immutable Accountability.

Provides:
- Immutable audit trail for all evolution decisions
- Governance approval workflows
- Decision transparency and accountability
- Compliance reporting

Every evolution decision is recorded with:
- Who (actor/system)
- What (action taken)
- Why (justification)
- When (timestamp)
- Result (outcome)

This creates a truth surface for governance.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from .contract import EvolutionContract, EvolutionStatus


class AuditAction(Enum):
    """Types of auditable actions."""

    DETECTED = "hotspot_detected"
    CONTRACTED = "contract_created"
    APPROVED = "evolution_approved"
    REJECTED = "evolution_rejected"
    PATCHED = "patches_applied"
    VERIFIED = "verification_completed"
    ROLLED_BACK = "evolution_rolled_back"
    COMPLETED = "evolution_completed"
    LEARNED = "pattern_learned"


@dataclass
class AuditEntry:
    """Immutable record of an evolution decision."""

    entry_id: str
    timestamp: str
    action: str
    evolution_id: str
    actor: str  # "system" or specific module
    details: dict[str, Any]
    justification: str
    previous_hash: str | None  # For blockchain-style chaining
    hash: str  # Self-verifying


class EvolutionAuditor:
    """Creates immutable audit trail for all evolution activities."""

    def __init__(self, audit_path: str | None = None) -> None:
        """Initialize auditor."""
        if audit_path:
            self.audit_path = Path(audit_path)
        else:
            self.audit_path = Path(".amos_evolution_audit")

        self.audit_path.mkdir(exist_ok=True)
        self.entries: list[AuditEntry] = []
        self._load_chain()

    def _load_chain(self) -> None:
        """Load existing audit chain."""
        audit_file = self.audit_path / "audit_chain.jsonl"
        if audit_file.exists():
            with open(audit_file, "r") as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        self.entries.append(AuditEntry(**data))

    def _compute_hash(self, entry: AuditEntry) -> str:
        """Compute hash for audit entry (blockchain-style)."""
        data = {
            "timestamp": entry.timestamp,
            "action": entry.action,
            "evolution_id": entry.evolution_id,
            "actor": entry.actor,
            "details": entry.details,
            "justification": entry.justification,
            "previous_hash": entry.previous_hash,
        }
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:32]

    def _get_last_hash(self) -> str | None:
        """Get hash of last entry for chaining."""
        if self.entries:
            return self.entries[-1].hash
        return None

    def record(
        self,
        action: AuditAction,
        evolution_id: str,
        details: dict[str, Any],
        justification: str,
        actor: str = "system",
    ) -> AuditEntry:
        """Record an auditable action."""
        timestamp = datetime.now().isoformat()
        previous_hash = self._get_last_hash()

        # Create entry (hash computed after creation)
        entry = AuditEntry(
            entry_id=hashlib.md5(f"{evolution_id}{timestamp}".encode()).hexdigest()[:16],
            timestamp=timestamp,
            action=action.value,
            evolution_id=evolution_id,
            actor=actor,
            details=details,
            justification=justification,
            previous_hash=previous_hash,
            hash="",  # Will be computed
        )

        # Compute hash
        entry.hash = self._compute_hash(entry)

        # Store and save
        self.entries.append(entry)
        self._save_entry(entry)

        return entry

    def _save_entry(self, entry: AuditEntry) -> None:
        """Save single entry to audit log."""
        audit_file = self.audit_path / "audit_chain.jsonl"
        with open(audit_file, "a") as f:
            f.write(json.dumps(asdict(entry)) + "\n")

    def verify_chain(self) -> bool:
        """Verify integrity of audit chain."""
        for i, entry in enumerate(self.entries):
            # Verify hash
            computed = self._compute_hash(entry)
            if computed != entry.hash:
                return False

            # Verify chain linkage (except first entry)
            if i > 0:
                if entry.previous_hash != self.entries[i - 1].hash:
                    return False

        return True

    def get_evolution_history(self, evolution_id: str) -> list[AuditEntry]:
        """Get complete audit trail for an evolution."""
        return [e for e in self.entries if e.evolution_id == evolution_id]

    def get_statistics(self) -> dict[str, Any]:
        """Get audit statistics."""
        total = len(self.entries)
        by_action: dict[str, int] = {}
        for entry in self.entries:
            by_action[entry.action] = by_action.get(entry.action, 0) + 1

        chain_valid = self.verify_chain()

        return {
            "total_entries": total,
            "by_action": by_action,
            "chain_integrity": "valid" if chain_valid else "compromised",
            "first_entry": self.entries[0].timestamp if self.entries else None,
            "last_entry": self.entries[-1].timestamp if self.entries else None,
        }


class GovernanceController:
    """Governance layer for evolution approval."""

    def __init__(self, auditor: EvolutionAuditor) -> None:
        """Initialize governance with auditor."""
        self.auditor = auditor
        self.approval_rules: dict[str, Any] = {
            "max_files_without_approval": 3,
            "critical_patterns_require_approval": [
                "security_violation",
                "api_breaking_change",
            ],
        }

    def evaluate_contract(self, contract: EvolutionContract) -> dict[str, Any]:
        """Evaluate if contract requires governance approval."""
        needs_approval = False
        reasons = []

        # Check file count
        if len(contract.target_files) > self.approval_rules["max_files_without_approval"]:
            needs_approval = True
            reasons.append(f"Exceeds {self.approval_rules['max_files_without_approval']} files")

        # Check critical patterns
        for pattern in self.approval_rules["critical_patterns_require_approval"]:
            if pattern in contract.problem_pattern.lower():
                needs_approval = True
                reasons.append(f"Critical pattern: {pattern}")

        # Record governance check
        self.auditor.record(
            action=AuditAction.APPROVED if not needs_approval else AuditAction.REJECTED,
            evolution_id=contract.evolution_id,
            details={
                "files": len(contract.target_files),
                "pattern": contract.owner,
                "needs_approval": needs_approval,
            },
            justification="Automated governance check: " + ("; ".join(reasons) if reasons else "Within safe bounds"),
        )

        return {
            "approved": not needs_approval,
            "needs_approval": needs_approval,
            "reasons": reasons,
            "can_auto_execute": not needs_approval,
        }

    def generate_compliance_report(self) -> dict[str, Any]:
        """Generate compliance report for governance."""
        audit_stats = self.auditor.get_statistics()

        return {
            "audit_integrity": audit_stats["chain_integrity"],
            "total_decisions": audit_stats["total_entries"],
            "decision_breakdown": audit_stats["by_action"],
            "governance_policy": self.approval_rules,
            "generated_at": datetime.now().isoformat(),
        }
