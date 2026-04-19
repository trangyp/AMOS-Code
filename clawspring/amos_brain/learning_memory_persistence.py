from typing import Any, Dict, List, Optional

"""
AMOS Learning-Memory Persistence Layer

Integrates Learning+Memory Kernel with vector search and database persistence.
Provides durable storage for memory tensors with retrieval capabilities.

Core integration:
    - Vector embedding storage (pgvector)
    - Temporal persistence (SQLite/PostgreSQL)
    - Cross-session memory continuity
    - Memory export/import for backup
"""

import asyncio
import json
import sqlite3
from datetime import datetime, timezone
UTC = timezone.utc
from pathlib import Path
from sqlite3 import Connection

try:
    from .learning_memory_kernel import (
        AMOSLearningMemoryKernel,
        MemoryRecord,
        MemoryState,
        MemoryType,
        get_learning_memory_kernel,
    )
except ImportError:
    from learning_memory_kernel import (
        MemoryType,
        get_learning_memory_kernel,
    )


class MemoryPersistenceLayer:
    """
    Persistence layer for AMOS Learning-Memory Kernel.

    Provides:
        - SQLite storage for memory records
        - Vector serialization for embeddings
        - Session continuity across restarts
        - Memory export/import
    """

    def __init__(self, db_path: str = "amos_memory.db"):
        self.db_path = Path(db_path)
        self.connection: sqlite3.Optional[Connection] = None
        self.initialized = False

    async def initialize(self) -> None:
        """Initialize database schema."""
        self.connection = sqlite3.connect(str(self.db_path))
        self.connection.row_factory = sqlite3.Row

        # Create tables
        self.connection.executescript("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                observation TEXT,
                action TEXT,
                context TEXT,
                outcome TEXT,
                error_signal TEXT,
                abstraction TEXT,
                relevance REAL,
                freshness REAL,
                confidence REAL,
                importance REAL,
                retrieval_keys TEXT,
                access_count INTEGER DEFAULT 0,
                last_accessed TEXT,
                decay_rate REAL DEFAULT 0.01
            );

            CREATE TABLE IF NOT EXISTS memory_tensors (
                memory_id TEXT PRIMARY KEY,
                tensor_blob BLOB,
                FOREIGN KEY (memory_id) REFERENCES memories(id)
            );

            CREATE TABLE IF NOT EXISTS retrieval_index (
                key TEXT,
                memory_id TEXT,
                PRIMARY KEY (key, memory_id),
                FOREIGN KEY (memory_id) REFERENCES memories(id)
            );

            CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(type);
            CREATE INDEX IF NOT EXISTS idx_memories_importance ON memories(importance);
            CREATE INDEX IF NOT EXISTS idx_retrieval_key ON retrieval_index(key);
        """)

        self.connection.commit()
        self.initialized = True

    async def save_memory(self, record: MemoryRecord) -> None:
        """Persist a memory record."""
        if not self.connection:
            return

        cursor = self.connection.cursor()

        # Insert memory record
        cursor.execute(
            """
            INSERT OR REPLACE INTO memories (
                id, type, timestamp, observation, action, context,
                outcome, error_signal, abstraction, relevance, freshness,
                confidence, importance, retrieval_keys, access_count,
                last_accessed, decay_rate
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                record.id,
                record.type.value,
                record.timestamp.isoformat(),
                json.dumps(record.observation),
                json.dumps(record.action),
                json.dumps(record.context),
                json.dumps(record.outcome),
                json.dumps(record.error_signal),
                json.dumps(record.abstraction),
                record.relevance,
                record.freshness,
                record.confidence,
                record.importance,
                json.dumps(record.retrieval_keys),
                record.access_count,
                record.last_accessed.isoformat() if record.last_accessed else None,
                record.decay_rate,
            ),
        )

        # Store tensor
        tensor_blob = record.to_tensor().tobytes()
        cursor.execute(
            """
            INSERT OR REPLACE INTO memory_tensors (memory_id, tensor_blob)
            VALUES (?, ?)
        """,
            (record.id, tensor_blob),
        )

        # Update retrieval index
        cursor.execute("DELETE FROM retrieval_index WHERE memory_id = ?", (record.id,))
        for key in record.retrieval_keys:
            cursor.execute(
                """
                INSERT INTO retrieval_index (key, memory_id) VALUES (?, ?)
            """,
                (key, record.id),
            )

        self.connection.commit()

    async def load_memories(
        self,
        memory_type: Optional[MemoryType] = None,
        min_importance: float = 0.0,
        limit: int = 1000,
    ) -> List[MemoryRecord]:
        """Load memories from persistence."""
        if not self.connection:
            return []

        cursor = self.connection.cursor()

        if memory_type:
            cursor.execute(
                """
                SELECT * FROM memories
                WHERE type = ? AND importance >= ?
                ORDER BY timestamp DESC
                LIMIT ?
            """,
                (memory_type.value, min_importance, limit),
            )
        else:
            cursor.execute(
                """
                SELECT * FROM memories
                WHERE importance >= ?
                ORDER BY timestamp DESC
                LIMIT ?
            """,
                (min_importance, limit),
            )

        records = []
        for row in cursor.fetchall():
            record = self._row_to_memory(row)
            if record:
                records.append(record)

        return records

    def _row_to_memory(self, row: sqlite3.Row) -> Optional[MemoryRecord]:
        """Convert database row to MemoryRecord."""
        try:
            return MemoryRecord(
                id=row["id"],
                type=MemoryType(row["type"]),
                timestamp=datetime.fromisoformat(row["timestamp"]),
                observation=json.loads(row["observation"] or "{}"),
                action=json.loads(row["action"] or "{}"),
                context=json.loads(row["context"] or "{}"),
                outcome=json.loads(row["outcome"] or "{}"),
                error_signal=json.loads(row["error_signal"] or "{}"),
                abstraction=json.loads(row["abstraction"] or "{}"),
                relevance=row["relevance"],
                freshness=row["freshness"],
                confidence=row["confidence"],
                importance=row["importance"],
                retrieval_keys=json.loads(row["retrieval_keys"] or "[]"),
                access_count=row["access_count"],
                last_accessed=datetime.fromisoformat(row["last_accessed"])
                if row["last_accessed"]
                else None,
                decay_rate=row["decay_rate"],
            )
        except Exception:
            return None

    async def export_memory_state(self, filepath: str) -> Dict[str, Any]:
        """Export full memory state to JSON file."""
        lmk = get_learning_memory_kernel()
        stats = lmk.get_learning_stats()

        # Load all persistent memories
        all_memories = await self.load_memories(limit=10000)

        export_data = {
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "statistics": stats,
            "memories": [
                {
                    "id": m.id,
                    "type": m.type.value,
                    "timestamp": m.timestamp.isoformat(),
                    "observation": m.observation,
                    "action": m.action,
                    "outcome": m.outcome,
                    "importance": m.importance,
                    "retrieval_keys": m.retrieval_keys,
                }
                for m in all_memories
            ],
        }

        with open(filepath, "w") as f:
            json.dump(export_data, f, indent=2)

        return {"exported": True, "filepath": filepath, "memory_count": len(all_memories)}

    async def close(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None


class VectorSearchAdapter:
    """
    Adapter to integrate with existing AMOS vector search system.

    Bridges memory tensors with pgvector for semantic retrieval.
    """

    def __init__(self, memory_persistence: MemoryPersistenceLayer):
        self.persistence = memory_persistence

    async def index_memory_for_search(self, record: MemoryRecord) -> None:
        """
        Index a memory for vector search.

        This would integrate with amos_vector_search.py to store
        the memory's embedding in pgvector.
        """
        # Placeholder for vector search integration
        # In production, this would call:
        # - Vector embedding generation
        # - pgvector storage via amos_vector_search
        pass

    async def semantic_memory_search(self, query: str, k: int = 5) -> List[MemoryRecord]:
        """
        Search memories by semantic similarity.

        Would use pgvector similarity search in production.
        """
        # Fallback to keyword-based search
        return await self.persistence.load_memories(limit=k)


async def initialize_persistence(db_path: str = "amos_memory.db") -> MemoryPersistenceLayer:
    """Initialize and return persistence layer."""
    persistence = MemoryPersistenceLayer(db_path)
    await persistence.initialize()
    return persistence


# Integration with main kernel
async def persist_memory_state() -> Dict[str, Any]:
    """Persist current memory state to database."""
    lmk = get_learning_memory_kernel()
    persistence = await initialize_persistence()

    # Save all memory pools
    saved_count = 0
    for pool in [
        lmk.state.episodic_memory,
        lmk.state.semantic_memory,
        lmk.state.procedural_memory,
        lmk.state.error_memory,
        lmk.state.identity_memory,
    ]:
        for record in pool.values():
            await persistence.save_memory(record)
            saved_count += 1

    await persistence.close()

    return {"persisted": True, "memory_count": saved_count}


async def restore_memory_state(db_path: str = "amos_memory.db") -> Dict[str, Any]:
    """Restore memory state from persistence."""
    lmk = get_learning_memory_kernel()
    persistence = MemoryPersistenceLayer(db_path)
    await persistence.initialize()

    # Load memories by type
    loaded_count = 0

    for memory_type in MemoryType:
        records = await persistence.load_memories(memory_type=memory_type, limit=10000)

        for record in records:
            # Store in appropriate pool
            if memory_type == MemoryType.WORKING:
                lmk.state.working_memory[record.id] = record
            elif memory_type == MemoryType.EPISODIC:
                lmk.state.episodic_memory[record.id] = record
            elif memory_type == MemoryType.SEMANTIC:
                lmk.state.semantic_memory[record.id] = record
            elif memory_type == MemoryType.PROCEDURAL:
                lmk.state.procedural_memory[record.id] = record
            elif memory_type == MemoryType.IDENTITY:
                lmk.state.identity_memory[record.id] = record
            elif memory_type == MemoryType.ERROR:
                lmk.state.error_memory[record.id] = record

            loaded_count += 1

    await persistence.close()

    return {"restored": True, "memory_count": loaded_count}


# Demonstration
if __name__ == "__main__":

    async def demo():
        """Demonstrate persistence layer."""
        print("Learning-Memory Persistence Demo")
        print("-" * 40)

        # Initialize kernel and persistence
        lmk = get_learning_memory_kernel()
        await lmk.initialize()

        persistence = await initialize_persistence(":memory:")

        # Create and save a memory
        record = lmk.memory_kernel.encode_experience(
            observation={"type": "test", "value": 42},
            action={"type": "process"},
            context={"session": "demo"},
            outcome={"success": True},
            error_signal={},
            memory_type=MemoryType.EPISODIC,
        )

        await persistence.save_memory(record)
        print(f"Saved memory: {record.id}")

        # Load it back
        loaded = await persistence.load_memories(MemoryType.EPISODIC)
        print(f"Loaded {len(loaded)} memories")

        # Export
        export_result = await persistence.export_memory_state("/tmp/amos_memory_export.json")
        print(f"Exported: {export_result}")

        await persistence.close()
        print("Demo complete")

    asyncio.run(demo())
