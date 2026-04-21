"""
Axiom Persistence Layer - SQLite-backed storage for Axiom components

Provides durable storage for:
- Memory entries (short-term, long-term, working)
- Command ledger entries
- State snapshots
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..axiom_state import AxiomState
from ..integration_bus import MemoryEntry
from ..nl_processor import CommandLedger


@dataclass
class AxiomPersistenceConfig:
    """Configuration for Axiom persistence layer."""

    db_path: str = ".amos/axiom.db"
    max_memory_entries: int = 10000
    max_ledger_entries: int = 100000
    auto_vacuum: bool = True


class AxiomPersistence:
    """
    SQLite-backed persistence for Axiom kernel components.

    Provides durable storage for memory, ledger, and state.
    """

    _instance: AxiomPersistence | None = None

    def __new__(cls) -> AxiomPersistence:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, config: AxiomPersistenceConfig | None = None) -> None:
        if self._initialized:
            return

        self.config = config or AxiomPersistenceConfig()
        self._conn: sqlite3.Connection | None = None
        self._initialized = True

    def _get_connection(self) -> sqlite3.Connection:
        """Get or create database connection."""
        if self._conn is None:
            Path(self.config.db_path).parent.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(self.config.db_path, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
            self._setup_tables()
        return self._conn

    def _setup_tables(self) -> None:
        """Create database tables."""
        conn = self._conn
        if conn is None:
            return

        # Memory entries table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memory_entries (
                entry_id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                importance REAL NOT NULL,
                tags TEXT NOT NULL,
                created_at TEXT NOT NULL,
                accessed_at TEXT,
                access_count INTEGER DEFAULT 0
            )
        """)

        # Ledger entries table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ledger_entries (
                ledger_id TEXT PRIMARY KEY,
                intent_id TEXT NOT NULL,
                status TEXT NOT NULL,
                transitions TEXT NOT NULL,
                final_state TEXT,
                created_at TEXT NOT NULL,
                completed_at TEXT
            )
        """)

        # State snapshots table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS state_snapshots (
                snapshot_id TEXT PRIMARY KEY,
                state_hash TEXT NOT NULL,
                state_data TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)

        # Create indexes
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_memory_type
            ON memory_entries(memory_type)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_memory_created
            ON memory_entries(created_at)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_ledger_intent
            ON ledger_entries(intent_id)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_ledger_created
            ON ledger_entries(created_at)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_snapshot_hash
            ON state_snapshots(state_hash)
        """)

        conn.commit()

    # ------------------------------------------------------------------
    # Memory Operations
    # ------------------------------------------------------------------

    def store_memory(self, entry: MemoryEntry) -> bool:
        """Store memory entry to database."""
        try:
            conn = self._get_connection()
            conn.execute(
                """
                INSERT OR REPLACE INTO memory_entries
                (entry_id, content, memory_type, importance,
                 tags, created_at, accessed_at, access_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entry.entry_id,
                    entry.content,
                    entry.memory_type,
                    entry.importance,
                    json.dumps(entry.tags),
                    entry.created_at.isoformat(),
                    entry.accessed_at.isoformat() if entry.accessed_at else None,
                    entry.access_count,
                ),
            )
            conn.commit()
            return True
        except sqlite3.Error:
            return False

    def retrieve_memory(self, entry_id: str) -> MemoryEntry | None:
        """Retrieve memory entry from database."""
        try:
            conn = self._get_connection()
            row = conn.execute(
                "SELECT * FROM memory_entries WHERE entry_id = ?",
                (entry_id,),
            ).fetchone()

            if row is None:
                return None

            return MemoryEntry(
                entry_id=row["entry_id"],
                content=row["content"],
                memory_type=row["memory_type"],
                importance=row["importance"],
                tags=json.loads(row["tags"]),
                created_at=datetime.fromisoformat(row["created_at"]),
                accessed_at=(
                    datetime.fromisoformat(row["accessed_at"]) if row["accessed_at"] else None
                ),
                access_count=row["access_count"],
            )
        except (sqlite3.Error, json.JSONDecodeError):
            return None

    def search_memory(
        self, query: str, memory_type: str | None = None, limit: int = 10
    ) -> list[MemoryEntry]:
        """Search memory entries."""
        try:
            conn = self._get_connection()

            if memory_type:
                rows = conn.execute(
                    """
                    SELECT * FROM memory_entries
                    WHERE content LIKE ? AND memory_type = ?
                    ORDER BY importance DESC, access_count DESC
                    LIMIT ?
                    """,
                    (f"%{query}%", memory_type, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT * FROM memory_entries
                    WHERE content LIKE ?
                    ORDER BY importance DESC, access_count DESC
                    LIMIT ?
                    """,
                    (f"%{query}%", limit),
                ).fetchall()

            return [
                MemoryEntry(
                    entry_id=row["entry_id"],
                    content=row["content"],
                    memory_type=row["memory_type"],
                    importance=row["importance"],
                    tags=json.loads(row["tags"]),
                    created_at=datetime.fromisoformat(row["created_at"]),
                    accessed_at=(
                        datetime.fromisoformat(row["accessed_at"]) if row["accessed_at"] else None
                    ),
                    access_count=row["access_count"],
                )
                for row in rows
            ]
        except (sqlite3.Error, json.JSONDecodeError):
            return []

    def delete_memory(self, entry_id: str) -> bool:
        """Delete memory entry."""
        try:
            conn = self._get_connection()
            conn.execute("DELETE FROM memory_entries WHERE entry_id = ?", (entry_id,))
            conn.commit()
            return True
        except sqlite3.Error:
            return False

    def prune_memory(self, memory_type: str, max_entries: int) -> int:
        """Prune old entries to max count."""
        try:
            conn = self._get_connection()

            # Count entries
            count = conn.execute(
                "SELECT COUNT(*) FROM memory_entries WHERE memory_type = ?",
                (memory_type,),
            ).fetchone()[0]

            if count <= max_entries:
                return 0

            # Delete oldest entries
            to_delete = count - max_entries
            conn.execute(
                """
                DELETE FROM memory_entries
                WHERE entry_id IN (
                    SELECT entry_id FROM memory_entries
                    WHERE memory_type = ?
                    ORDER BY created_at ASC
                    LIMIT ?
                )
                """,
                (memory_type, to_delete),
            )
            conn.commit()
            return to_delete
        except sqlite3.Error:
            return 0

    # ------------------------------------------------------------------
    # Ledger Operations
    # ------------------------------------------------------------------

    def store_ledger(self, ledger: CommandLedger) -> bool:
        """Store ledger entry to database."""
        try:
            conn = self._get_connection()
            conn.execute(
                """
                INSERT OR REPLACE INTO ledger_entries
                (ledger_id, intent_id, status, transitions,
                 final_state, created_at, completed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    ledger.ledger_id,
                    ledger.intent_id,
                    ledger.status.value,
                    json.dumps(ledger.transitions),
                    ledger.final_state,
                    ledger.created_at.isoformat(),
                    ledger.completed_at.isoformat() if ledger.completed_at else None,
                ),
            )
            conn.commit()
            return True
        except sqlite3.Error:
            return False

    def retrieve_ledger(self, intent_id: str) -> CommandLedger | None:
        """Retrieve ledger by intent ID."""
        try:
            conn = self._get_connection()
            row = conn.execute(
                "SELECT * FROM ledger_entries WHERE intent_id = ?",
                (intent_id,),
            ).fetchone()

            if row is None:
                return None

            from ..nl_processor import CommandStatus

            return CommandLedger(
                ledger_id=row["ledger_id"],
                intent_id=row["intent_id"],
                status=CommandStatus(row["status"]),
                transitions=json.loads(row["transitions"]),
                final_state=row["final_state"],
                created_at=datetime.fromisoformat(row["created_at"]),
                completed_at=(
                    datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
                ),
            )
        except (sqlite3.Error, json.JSONDecodeError, ValueError):
            return None

    def list_ledgers(self, limit: int = 100) -> list[CommandLedger]:
        """List recent ledgers."""
        try:
            conn = self._get_connection()
            rows = conn.execute(
                """
                SELECT * FROM ledger_entries
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

            from ..nl_processor import CommandStatus

            return [
                CommandLedger(
                    ledger_id=row["ledger_id"],
                    intent_id=row["intent_id"],
                    status=CommandStatus(row["status"]),
                    transitions=json.loads(row["transitions"]),
                    final_state=row["final_state"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    completed_at=(
                        datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
                    ),
                )
                for row in rows
            ]
        except (sqlite3.Error, json.JSONDecodeError, ValueError):
            return []

    # ------------------------------------------------------------------
    # State Snapshots
    # ------------------------------------------------------------------

    def store_state_snapshot(self, state: AxiomState) -> bool:
        """Store state snapshot."""
        try:
            conn = self._get_connection()
            snapshot_id = f"snap_{datetime.now(UTC).timestamp()}"
            conn.execute(
                """
                INSERT INTO state_snapshots
                (snapshot_id, state_hash, state_data, timestamp)
                VALUES (?, ?, ?, ?)
                """,
                (
                    snapshot_id,
                    state.canonical_hash,
                    json.dumps(state.to_dict()),
                    state.timestamp.isoformat(),
                ),
            )
            conn.commit()
            return True
        except sqlite3.Error:
            return False

    def get_latest_snapshot(self) -> dict[str, Any] | None:
        """Get latest state snapshot."""
        try:
            conn = self._get_connection()
            row = conn.execute(
                """
                SELECT * FROM state_snapshots
                ORDER BY timestamp DESC
                LIMIT 1
                """,
            ).fetchone()

            if row is None:
                return None

            return json.loads(row["state_data"])
        except (sqlite3.Error, json.JSONDecodeError):
            return None

    # ------------------------------------------------------------------
    # Maintenance
    # ------------------------------------------------------------------

    def vacuum(self) -> bool:
        """Vacuum database to reclaim space."""
        try:
            conn = self._get_connection()
            conn.execute("VACUUM")
            return True
        except sqlite3.Error:
            return False

    def get_stats(self) -> dict[str, Any]:
        """Get database statistics."""
        try:
            conn = self._get_connection()

            memory_count = conn.execute("SELECT COUNT(*) FROM memory_entries").fetchone()[0]

            ledger_count = conn.execute("SELECT COUNT(*) FROM ledger_entries").fetchone()[0]

            snapshot_count = conn.execute("SELECT COUNT(*) FROM state_snapshots").fetchone()[0]

            db_size = Path(self.config.db_path).stat().st_size

            return {
                "memory_entries": memory_count,
                "ledger_entries": ledger_count,
                "state_snapshots": snapshot_count,
                "database_size_bytes": db_size,
                "database_path": self.config.db_path,
            }
        except (sqlite3.Error, OSError):
            return {}


def get_axiom_persistence(config: AxiomPersistenceConfig | None = None) -> AxiomPersistence:
    """Get singleton Axiom persistence instance."""
    if config:
        return AxiomPersistence(config)
    return AxiomPersistence()
