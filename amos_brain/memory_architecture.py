"""AMOS Memory Architecture - Tiered storage for AI agent persistence.

Implements L1/L2/L3 tiered memory architecture following 2025 best practices:
- L1 (Hot): Redis - In-memory cache for active conversations
- L2 (Warm): SQLite - Persistent storage for session history
- L3 (Cold): File system - Archival storage for long-term memory

References:
- Redis AI Agent Memory Architecture 2025
- Persistent Memory for AI Agents (PAG vs SQLite)
- Tiered Storage Best Practices
"""

from __future__ import annotations

import json
import sqlite3
import threading
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Protocol


@dataclass
class MemoryEntry:
    """Single memory entry with metadata."""

    id: str
    content: str
    timestamp: datetime
    session_id: str
    memory_type: str  # 'conversation', 'tool_result', 'state', 'knowledge'
    priority: int = 5  # 1-10, higher = more important
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "session_id": self.session_id,
            "memory_type": self.memory_type,
            "priority": self.priority,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MemoryEntry:
        """Create from dictionary."""
        return cls(
            id=data["id"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            session_id=data["session_id"],
            memory_type=data["memory_type"],
            priority=data.get("priority", 5),
            metadata=data.get("metadata", {}),
        )


class MemoryBackend(Protocol):
    """Protocol for memory storage backends."""

    def store(self, entry: MemoryEntry) -> bool:
        """Store a memory entry."""
        ...

    def retrieve(self, entry_id: str) -> Optional[MemoryEntry]:
        """Retrieve a specific entry by ID."""
        ...

    def search(
        self, session_id: Optional[str] = None, memory_type: Optional[str] = None, limit: int = 100
    ) -> list[MemoryEntry]:
        """Search for entries."""
        ...

    def clear(self, session_id: Optional[str] = None) -> bool:
        """Clear entries, optionally for a specific session."""
        ...


class SQLiteMemoryBackend:
    """L2 (Warm) Storage - Persistent SQLite storage."""

    def __init__(self, db_path: str = ":memory:"):
        """Initialize SQLite backend.

        Args:
            db_path: Path to SQLite database, default in-memory
        """
        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    priority INTEGER DEFAULT 5,
                    metadata TEXT
                )
            """)

            # Indexes for efficient querying
            conn.execute("CREATE INDEX IF NOT EXISTS idx_session ON memories(session_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_type ON memories(memory_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp)")
            conn.commit()

    def store(self, entry: MemoryEntry) -> bool:
        """Store entry in SQLite."""
        try:
            with self._lock, sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO memories
                    (id, content, timestamp, session_id, memory_type, priority, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        entry.id,
                        entry.content,
                        entry.timestamp.isoformat(),
                        entry.session_id,
                        entry.memory_type,
                        entry.priority,
                        json.dumps(entry.metadata),
                    ),
                )
                conn.commit()
                return True
        except Exception:
            return False

    def retrieve(self, entry_id: str) -> Optional[MemoryEntry]:
        """Retrieve entry by ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT * FROM memories WHERE id = ?", (entry_id,))
                row = cursor.fetchone()

                if row:
                    return MemoryEntry(
                        id=row[0],
                        content=row[1],
                        timestamp=datetime.fromisoformat(row[2]),
                        session_id=row[3],
                        memory_type=row[4],
                        priority=row[5],
                        metadata=json.loads(row[6]) if row[6] else {},
                    )
                return None
        except Exception:
            return None

    def search(
        self,
        session_id: Optional[str] = None,
        memory_type: Optional[str] = None,
        limit: int = 100,
    ) -> list[MemoryEntry]:
        """Search for entries with filters."""
        try:
            query = "SELECT * FROM memories WHERE 1=1"
            params: list[Any] = []

            if session_id:
                query += " AND session_id = ?"
                params.append(session_id)

            if memory_type:
                query += " AND memory_type = ?"
                params.append(memory_type)

            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()

                return [
                    MemoryEntry(
                        id=row[0],
                        content=row[1],
                        timestamp=datetime.fromisoformat(row[2]),
                        session_id=row[3],
                        memory_type=row[4],
                        priority=row[5],
                        metadata=json.loads(row[6]) if row[6] else {},
                    )
                    for row in rows
                ]
        except Exception:
            return []

    def clear(self, session_id: Optional[str] = None) -> bool:
        """Clear entries."""
        try:
            with self._lock, sqlite3.connect(self.db_path) as conn:
                if session_id:
                    conn.execute("DELETE FROM memories WHERE session_id = ?", (session_id,))
                else:
                    conn.execute("DELETE FROM memories")
                conn.commit()
                return True
        except Exception:
            return False


class FileMemoryBackend:
    """L3 (Cold) Storage - File system archival storage."""

    def __init__(self, base_path: str = "./memory"):
        """Initialize file backend.

        Args:
            base_path: Directory for memory storage
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def _get_file_path(self, entry_id: str) -> Path:
        """Get file path for entry."""
        # Use first 2 chars of ID as subdirectory for distribution
        subdir = self.base_path / entry_id[:2]
        subdir.mkdir(exist_ok=True)
        return subdir / f"{entry_id}.json"

    def store(self, entry: MemoryEntry) -> bool:
        """Store entry as JSON file."""
        try:
            with self._lock:
                file_path = self._get_file_path(entry.id)
                file_path.write_text(json.dumps(entry.to_dict(), indent=2))
                return True
        except Exception:
            return False

    def retrieve(self, entry_id: str) -> Optional[MemoryEntry]:
        """Retrieve entry from file."""
        try:
            file_path = self._get_file_path(entry_id)
            if file_path.exists():
                data = json.loads(file_path.read_text())
                return MemoryEntry.from_dict(data)
            return None
        except Exception:
            return None

    def search(
        self,
        session_id: Optional[str] = None,
        memory_type: Optional[str] = None,
        limit: int = 100,
    ) -> list[MemoryEntry]:
        """Search entries (scans all files - slow but simple)."""
        entries = []
        count = 0

        try:
            for subdir in self.base_path.iterdir():
                if subdir.is_dir() and count < limit:
                    for file_path in subdir.glob("*.json"):
                        if count >= limit:
                            break
                        try:
                            data = json.loads(file_path.read_text())
                            entry = MemoryEntry.from_dict(data)

                            # Apply filters
                            if session_id and entry.session_id != session_id:
                                continue
                            if memory_type and entry.memory_type != memory_type:
                                continue

                            entries.append(entry)
                            count += 1
                        except Exception:
                            continue
        except Exception:
            pass

        return entries

    def clear(self, session_id: Optional[str] = None) -> bool:
        """Clear entries."""
        try:
            with self._lock:
                for subdir in self.base_path.iterdir():
                    if subdir.is_dir():
                        for file_path in subdir.glob("*.json"):
                            try:
                                if session_id:
                                    data = json.loads(file_path.read_text())
                                    if data.get("session_id") == session_id:
                                        file_path.unlink()
                                else:
                                    file_path.unlink()
                            except Exception:
                                continue
            return True
        except Exception:
            return False


class TieredMemoryManager:
    """L1/L2/L3 Tiered memory manager.

    Coordinates between hot (Redis), warm (SQLite), and cold (File) storage.
    Implements automatic tiering based on access patterns.
    """

    def __init__(
        self,
        sqlite_path: str = "./memory/amos_memory.db",
        file_path: str = "./memory/archive",
    ):
        """Initialize tiered memory manager.

        Args:
            sqlite_path: Path for L2 SQLite storage
            file_path: Path for L3 file storage
        """
        # L2: SQLite (warm persistent storage)
        self.l2_sqlite = SQLiteMemoryBackend(sqlite_path)

        # L3: File system (cold archival storage)
        self.l3_file = FileMemoryBackend(file_path)

        # In-memory cache for L1 (will integrate Redis later)
        self._l1_cache: dict[str, MemoryEntry] = {}
        self._cache_lock = threading.Lock()

    def store(self, entry: MemoryEntry, tier: str = "auto") -> bool:
        """Store entry in specified tier.

        Args:
            entry: Memory entry to store
            tier: Target tier ('l1', 'l2', 'l3', 'auto')

        Returns:
            True if successful
        """
        # Always store in L2 (warm) as base persistence
        l2_success = self.l2_sqlite.store(entry)

        if tier in ("l1", "auto"):
            # Cache in L1
            with self._cache_lock:
                self._l1_cache[entry.id] = entry

        if tier in ("l3", "auto") and entry.priority >= 7:
            # Archive high-priority entries to L3
            self.l3_file.store(entry)

        return l2_success

    def retrieve(self, entry_id: str) -> Optional[MemoryEntry]:
        """Retrieve entry, checking L1 → L2 → L3."""
        # Check L1 first (fastest)
        with self._cache_lock:
            if entry_id in self._l1_cache:
                return self._l1_cache[entry_id]

        # Check L2 (persistent)
        entry = self.l2_sqlite.retrieve(entry_id)
        if entry:
            # Promote to L1 for faster access
            with self._cache_lock:
                self._l1_cache[entry_id] = entry
            return entry

        # Check L3 (archival)
        entry = self.l3_file.retrieve(entry_id)
        if entry:
            # Restore to L2 and L1
            self.l2_sqlite.store(entry)
            with self._cache_lock:
                self._l1_cache[entry_id] = entry
            return entry

        return None

    def search(
        self,
        session_id: Optional[str] = None,
        memory_type: Optional[str] = None,
        limit: int = 100,
    ) -> list[MemoryEntry]:
        """Search across all tiers (L2 primary)."""
        # L2 is the source of truth for search
        return self.l2_sqlite.search(session_id, memory_type, limit)

    def get_session_history(self, session_id: str, limit: int = 50) -> list[MemoryEntry]:
        """Get conversation history for a session."""
        return self.search(session_id=session_id, memory_type="conversation", limit=limit)

    def clear_session(self, session_id: str) -> bool:
        """Clear all memory for a session."""
        # Clear from all tiers
        l1_cleared = False
        with self._cache_lock:
            keys_to_remove = [k for k, v in self._l1_cache.items() if v.session_id == session_id]
            for k in keys_to_remove:
                del self._l1_cache[k]
            l1_cleared = True

        l2_cleared = self.l2_sqlite.clear(session_id)
        l3_cleared = self.l3_file.clear(session_id)

        return l1_cleared and l2_cleared and l3_cleared

    def get_stats(self) -> dict[str, Any]:
        """Get memory statistics."""
        return {
            "l1_cache_size": len(self._l1_cache),
            "l2_sqlite": "active",
            "l3_file": "active",
            "tiers": ["L1 (Cache)", "L2 (SQLite)", "L3 (File)"],
        }


# Global instance
_memory_manager: Optional[TieredMemoryManager] = None


def get_memory_manager() -> TieredMemoryManager:
    """Get or create global memory manager instance."""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = TieredMemoryManager()
    return _memory_manager
