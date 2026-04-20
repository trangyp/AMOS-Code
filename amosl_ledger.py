#!/usr/bin/env python3
"""AMOSL Ledger System
===================

Formal ledger for the AMOSL (AMOS Language) runtime.
Implements auditability theorem and state transition tracking.

Core Components:
- LedgerEntry: Immutable record of state transitions
- StateLedger: Append-only log of all system states
- AuditTrail: Complete history for verification
- Transaction: Atomic state change operations

Formal Specification (16-tuple system):
- Σ: State manifold
- L: Ledger (this module)
- T: Transactions
- V: Verification

Owner: Trang
Version: 1.0.0
"""

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime, timezone

UTC = UTC
from enum import Enum
from typing import Any


class EntryType(Enum):
    """Types of ledger entries."""

    STATE_TRANSITION = "state_transition"
    INVARIANT_CHECK = "invariant_check"
    EVOLUTION_STEP = "evolution_step"
    BRIDGE_OPERATION = "bridge_operation"
    VERIFICATION_RESULT = "verification_result"


@dataclass(frozen=True)
class LedgerEntry:
    """Immutable ledger entry recording a system event.

    Attributes:
        index: Sequential position in ledger
        timestamp: timezone.utc ISO format timestamp
        entry_type: Category of entry
        state_hash: Hash of state at this point
        previous_hash: Hash of previous entry (chain)
        data: Entry-specific data
        signature: Verification signature
    """

    index: int
    timestamp: str
    entry_type: EntryType
    state_hash: str
    previous_hash: str
    data: dict[str, Any]
    signature: str

    def to_dict(self) -> dict[str, Any]:
        """Convert entry to dictionary."""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "entry_type": self.entry_type.value,
            "state_hash": self.state_hash,
            "previous_hash": self.previous_hash,
            "data": self.data,
            "signature": self.signature,
        }

    def compute_hash(self) -> str:
        """Compute cryptographic hash of entry."""
        content = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:32]

    @property
    def hash(self) -> str:
        """Get entry hash (alias for compute_hash)."""
        return self.compute_hash()


class StateLedger:
    """Append-only ledger for AMOSL runtime state tracking.

    Implements:
    - Tamper-evident logging (hash chain)
    - Complete audit trail
    - State reconstruction
    - Invariant verification history
    """

    def __init__(self):
        self._entries: list[LedgerEntry] = []
        self._current_hash: str = "0" * 32  # Genesis hash
        self._state_cache: dict[int, dict[str, Any]] = {}

    def append(
        self,
        entry_type: EntryType,
        state_data: dict[str, Any],
        metadata: dict[str, Any] = None,
    ) -> LedgerEntry:
        """Append new entry to ledger.

        Args:
            entry_type: Type of entry
            state_data: State being recorded
            metadata: Additional context

        Returns:
            Created ledger entry
        """
        # Compute state hash
        state_content = json.dumps(state_data, sort_keys=True)
        state_hash = hashlib.sha256(state_content.encode()).hexdigest()[:32]

        # Create entry
        entry = LedgerEntry(
            index=len(self._entries),
            timestamp=datetime.now(timezone.utc).isoformat(),
            entry_type=entry_type,
            state_hash=state_hash,
            previous_hash=self._current_hash,
            data=metadata or {},
            signature=self._sign_entry(state_hash, self._current_hash),
        )

        # Update chain
        self._entries.append(entry)
        self._current_hash = entry.compute_hash()
        self._state_cache[entry.index] = state_data.copy()

        return entry

    def _sign_entry(self, state_hash: str, prev_hash: str) -> str:
        """Create entry signature (simplified)."""
        content = f"{state_hash}:{prev_hash}:{len(self._entries)}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def verify_chain(self) -> bool:
        """Verify integrity of entire ledger chain.

        Returns:
            True if chain is valid, False otherwise
        """
        for i, entry in enumerate(self._entries):
            # Check index continuity
            if entry.index != i:
                return False

            # Check hash chain
            if i == 0:
                expected_prev = "0" * 32
            else:
                expected_prev = self._entries[i - 1].compute_hash()

            if entry.previous_hash != expected_prev:
                return False

        return True

    def get_entry(self, index: int) -> LedgerEntry:
        """Retrieve entry by index."""
        if 0 <= index < len(self._entries):
            return self._entries[index]
        return None

    def get_state_at(self, index: int) -> dict[str, Any]:
        """Get reconstructed state at specific ledger index."""
        return self._state_cache.get(index)

    def get_audit_trail(self, start_index: int = 0, end_index: int = None) -> list[LedgerEntry]:
        """Get audit trail for range of entries.

        Args:
            start_index: Starting position
            end_index: Ending position (default: latest)

        Returns:
            List of entries in range
        """
        end = end_index or len(self._entries)
        return self._entries[start_index:end]

    def get_statistics(self) -> dict[str, Any]:
        """Get ledger statistics."""
        type_counts = {}
        for entry in self._entries:
            et = entry.entry_type.value
            type_counts[et] = type_counts.get(et, 0) + 1

        return {
            "total_entries": len(self._entries),
            "current_hash": self._current_hash,
            "chain_valid": self.verify_chain(),
            "entry_types": type_counts,
            "first_timestamp": self._entries[0].timestamp if self._entries else None,
            "last_timestamp": self._entries[-1].timestamp if self._entries else None,
        }

    def reconstruct_state(self, target_index: int) -> dict[str, Any]:
        """Reconstruct state at specific point in history.

        Args:
            target_index: Index to reconstruct to

        Returns:
            Reconstructed state
        """
        if target_index >= len(self._entries):
            target_index = len(self._entries) - 1

        # Start from cached state if available
        state = {}
        for i in range(target_index + 1):
            cached = self._state_cache.get(i)
            if cached:
                state = cached.copy()

        return state

    def export_to_file(self, filepath: str) -> bool:
        """Export ledger to JSON file."""
        try:
            data = {
                "metadata": {
                    "version": "1.0.0",
                    "export_time": datetime.now(timezone.utc).isoformat(),
                    "total_entries": len(self._entries),
                },
                "entries": [e.to_dict() for e in self._entries],
            }
            with open(filepath, "w") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception:
            return False

    def import_from_file(self, filepath: str) -> bool:
        """Import ledger from JSON file."""
        try:
            with open(filepath) as f:
                data = json.load(f)

            self._entries = []
            for entry_data in data.get("entries", []):
                entry = LedgerEntry(
                    index=entry_data["index"],
                    timestamp=entry_data["timestamp"],
                    entry_type=EntryType(entry_data["entry_type"]),
                    state_hash=entry_data["state_hash"],
                    previous_hash=entry_data["previous_hash"],
                    data=entry_data["data"],
                    signature=entry_data["signature"],
                )
                self._entries.append(entry)

            if self._entries:
                self._current_hash = self._entries[-1].compute_hash()

            return self.verify_chain()
        except Exception:
            return False


class TransactionLog:
    """Transaction-specific logging for AMOSL operations.

    Tracks:
    - Transaction begin/commit/rollback
    - Resource allocation/deallocation
    - Cross-substrate operations
    """

    def __init__(self, ledger: StateLedger):
        self.ledger = ledger
        self._active_transactions: dict[str, dict[str, Any]] = {}

    def begin_transaction(
        self, tx_id: str, operation: str, substrate: str = "local"
    ) -> LedgerEntry:
        """Log transaction start."""
        self._active_transactions[tx_id] = {
            "operation": operation,
            "substrate": substrate,
            "start_time": datetime.now(timezone.utc).isoformat(),
            "status": "active",
        }

        return self.ledger.append(
            EntryType.BRIDGE_OPERATION,
            {"tx_id": tx_id, "operation": operation, "substrate": substrate},
            {"event": "begin", "tx_id": tx_id},
        )

    def commit_transaction(self, tx_id: str) -> LedgerEntry:
        """Log transaction commit."""
        if tx_id not in self._active_transactions:
            return None

        tx = self._active_transactions[tx_id]
        tx["status"] = "committed"
        tx["end_time"] = datetime.now(timezone.utc).isoformat()

        entry = self.ledger.append(
            EntryType.BRIDGE_OPERATION,
            {"tx_id": tx_id, "status": "committed"},
            {"event": "commit", "tx_data": tx},
        )

        del self._active_transactions[tx_id]
        return entry

    def rollback_transaction(self, tx_id: str, reason: str) -> LedgerEntry:
        """Log transaction rollback."""
        if tx_id not in self._active_transactions:
            return None

        tx = self._active_transactions[tx_id]
        tx["status"] = "rolled_back"
        tx["reason"] = reason
        tx["end_time"] = datetime.now(timezone.utc).isoformat()

        entry = self.ledger.append(
            EntryType.BRIDGE_OPERATION,
            {"tx_id": tx_id, "status": "rolled_back"},
            {"event": "rollback", "reason": reason, "tx_data": tx},
        )

        del self._active_transactions[tx_id]
        return entry


def demo_ledger():
    """Demonstrate AMOSL ledger functionality."""
    print("\n" + "=" * 70)
    print("AMOSL LEDGER SYSTEM - DEMONSTRATION")
    print("=" * 70)

    # Create ledger
    ledger = StateLedger()
    tx_log = TransactionLog(ledger)

    print("\n[1] Recording state transitions...")

    # Record state transitions
    entry1 = ledger.append(
        EntryType.STATE_TRANSITION,
        {"Σ_c": {"value": 1.0}, "Σ_q": {"value": 0.5}},
        {"description": "Initial state", "source": "genesis"},
    )
    print(f"  Entry #{entry1.index}: {entry1.entry_type.value}")
    print(f"  Hash: {entry1.state_hash}")
    print(f"  Previous: {entry1.previous_hash}")

    entry2 = ledger.append(
        EntryType.EVOLUTION_STEP,
        {"Σ_c": {"value": 1.5}, "Σ_q": {"value": 0.7}},
        {"description": "Evolution step 1", "operator": "Φ"},
    )
    print(f"  Entry #{entry2.index}: {entry2.entry_type.value}")

    print("\n[2] Recording transaction...")
    tx_entry = tx_log.begin_transaction("tx-001", "cross_substrate_op", "local")
    print("  Transaction started: tx-001")

    # Simulate work
    entry3 = ledger.append(
        EntryType.INVARIANT_CHECK,
        {"valid": True, "constraints": ["C1", "C2", "C3"]},
        {"tx_id": "tx-001", "check_result": "passed"},
    )
    print("  Invariant check passed")

    commit_entry = tx_log.commit_transaction("tx-001")
    print("  Transaction committed")

    print("\n[3] Verifying ledger integrity...")
    is_valid = ledger.verify_chain()
    print(f"  Chain valid: {'✓ YES' if is_valid else '✗ NO'}")

    print("\n[4] Ledger statistics...")
    stats = ledger.get_statistics()
    print(f"  Total entries: {stats['total_entries']}")
    print(f"  Current hash: {stats['current_hash'][:16]}...")
    print(f"  Entry types: {list(stats['entry_types'].keys())}")

    print("\n[5] Reconstructing state...")
    state = ledger.reconstruct_state(2)
    print(f"  State at index 2: {state}")

    print("\n" + "=" * 70)
    print("✓ AMOSL LEDGER OPERATIONAL")
    print("=" * 70)
    print("\nFeatures demonstrated:")
    print("  • Immutable append-only entries")
    print("  • Cryptographic hash chain")
    print("  • Transaction logging")
    print("  • State reconstruction")
    print("  • Audit trail generation")
    print("\nFormal specification: 16-tuple system")
    print("Auditability theorem: ENABLED")
    print("=" * 70)


if __name__ == "__main__":
    demo_ledger()
