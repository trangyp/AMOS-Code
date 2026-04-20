#!/usr/bin/env python3
"""AXIOM One Ledger - Governance and Economics Layer

Permissions, approvals, policy checks, audit receipts, spend attribution,
risk scoring, rollout control.
Author: AMOS System
Version: 3.0.0
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone, timezone

UTC = UTC

UTC = timezone.utc
from enum import Enum, auto
from typing import Any


class PolicyLevel(Enum):
    INFO = auto()
    WARNING = auto()
    BLOCKING = auto()


@dataclass
class PolicyRule:
    """Single policy rule."""

    name: str
    description: str
    level: PolicyLevel
    check: str  # Python expression or rule ID


@dataclass
class AuditReceipt:
    """Immutable record of execution."""

    receipt_id: str
    slot_id: str
    timestamp: str
    objective: dict[str, Any]
    actions: list[dict[str, Any]] = field(default_factory=list)
    verification_bundle: dict[str, Any] = field(default_factory=dict)
    risk_score: float = 0.0
    approved_by: list[str] = field(default_factory=list)

    def compute_hash(self) -> str:
        """Compute immutable hash of this receipt."""
        data = json.dumps(
            {
                "slot_id": self.slot_id,
                "timestamp": self.timestamp,
                "actions": self.actions,
            },
            sort_keys=True,
        )
        return hashlib.sha256(data.encode()).hexdigest()


@dataclass
class SpendRecord:
    """Cost attribution record."""

    slot_id: str
    compute_cost_usd: float = 0.0
    token_cost_usd: float = 0.0
    api_cost_usd: float = 0.0
    duration_seconds: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class Ledger:
    """Governance, audit, and economics layer."""

    def __init__(self):
        self._policies: list[PolicyRule] = []
        self._receipts: dict[str, AuditReceipt] = {}
        self._spend_records: list[SpendRecord] = []
        self._approvers: set[str] = set()

    def add_policy(self, policy: PolicyRule) -> None:
        """Add a policy rule."""
        self._policies.append(policy)

    def check_policies(self, slot_data: dict[str, Any]) -> list[PolicyRule]:
        """Check which policies are violated."""
        violations = []
        for policy in self._policies:
            # Simple check - would be more sophisticated
            if policy.name in str(slot_data):
                violations.append(policy)
        return violations

    def create_receipt(
        self, slot_id: str, objective: dict[str, Any], actions: list[dict[str, Any]]
    ) -> AuditReceipt:
        """Create audit receipt for completed slot."""
        receipt = AuditReceipt(
            receipt_id=f"REC-{hashlib.sha256(slot_id.encode()).hexdigest()[:8]}",
            slot_id=slot_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            objective=objective,
            actions=actions,
        )
        self._receipts[receipt.receipt_id] = receipt
        return receipt

    def record_spend(
        self,
        slot_id: str,
        compute: float = 0,
        tokens: float = 0,
        api: float = 0,
        duration: float = 0,
    ) -> None:
        """Record spend for a slot."""
        record = SpendRecord(
            slot_id=slot_id,
            compute_cost_usd=compute,
            token_cost_usd=tokens,
            api_cost_usd=api,
            duration_seconds=duration,
        )
        self._spend_records.append(record)

    def get_total_spend(self, slot_id: str = None) -> dict[str, float]:
        """Get total spend, optionally filtered by slot."""
        records = self._spend_records
        if slot_id:
            records = [r for r in records if r.slot_id == slot_id]

        return {
            "compute": sum(r.compute_cost_usd for r in records),
            "tokens": sum(r.token_cost_usd for r in records),
            "api": sum(r.api_cost_usd for r in records),
            "total": sum(r.compute_cost_usd + r.token_cost_usd + r.api_cost_usd for r in records),
        }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="AXIOM One Ledger")
    parser.add_argument("--add-policy", help="Add policy rule")
    parser.add_argument("--list-receipts", action="store_true")
    parser.add_argument("--spend-report", action="store_true")
    args = parser.parse_args()

    ledger = Ledger()

    if args.add_policy:
        ledger.add_policy(
            PolicyRule(
                name=args.add_policy,
                description=args.add_policy,
                level=PolicyLevel.WARNING,
                check="True",
            )
        )
        print(f"Added policy: {args.add_policy}")
    elif args.spend_report:
        spend = ledger.get_total_spend()
        print(json.dumps(spend, indent=2))
    else:
        print("AXIOM One Ledger - Governance Layer")


if __name__ == "__main__":
    main()
