"""Memory Layer — 7-layer memory system for AMOS Brain.

Based on AMOS cognitive architecture:
- sensory_memory: Immediate sensory buffer
- working_memory: Active processing
- short_term: Recent thoughts and context
- episodic: Event sequences, experiences
- semantic: Facts, concepts, knowledge
- procedural: Skills, how-to knowledge
- long_term: Persistent storage, consolidation
"""

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc, timezone
from pathlib import Path
from typing import Any

UTC = UTC


@dataclass
class Memory:
    """A memory entry in the AMOS system."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    layer: str = (
        "short_term"  # sensory, working, short_term, episodic, semantic, procedural, long_term
    )
    content: str = ""
    source: str = "internal"  # Origin subsystem
    importance: float = 0.5  # 0.0 to 1.0
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    access_count: int = 0  # For LRU eviction
    last_accessed: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    tags: list[str] = field(default_factory=list)
    related: list[str] = field(default_factory=list)  # Related memory IDs

    def touch(self):
        """Mark as accessed."""
        self.access_count += 1
        self.last_accessed = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class MemoryLayer:
    """7-layer memory system for the AMOS Brain.

    Layers (highest to lowest frequency access):
    1. sensory: Raw inputs (100ms retention)
    2. working: Active processing (seconds)
    3. short_term: Recent context (minutes-hours)
    4. episodic: Event sequences (days)
    5. semantic: Facts and concepts (persistent)
    6. procedural: Skills and procedures (persistent)
    7. long_term: Consolidated storage (years)
    """

    LAYERS = [
        "sensory",  # Immediate buffer
        "working",  # Active processing
        "short_term",  # Recent context
        "episodic",  # Event sequences
        "semantic",  # Facts/concepts
        "procedural",  # Skills/how-to
        "long_term",  # Persistent storage
    ]

    CAPACITIES = {
        "sensory": 100,
        "working": 50,
        "short_term": 200,
        "episodic": 500,
        "semantic": 1000,
        "procedural": 500,
        "long_term": 10000,
    }

    def __init__(self, storage_dir: Path = None):
        self.storage_dir = storage_dir or Path(__file__).parent / "memory_store"
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # In-memory stores
        self._memories: dict[str, list[Memory]] = {layer: [] for layer in self.LAYERS}
        self._index: dict[str, Memory] = {}  # ID -> Memory lookup

        # Load persistent layers
        self._load_layer("episodic")
        self._load_layer("semantic")
        self._load_layer("procedural")
        self._load_layer("long_term")

    def _layer_file(self, layer: str) -> Path:
        """Get storage file for a layer."""
        return self.storage_dir / f"{layer}.json"

    def _load_layer(self, layer: str):
        """Load a memory layer from disk."""
        filepath = self._layer_file(layer)
        if not filepath.exists():
            return
        try:
            data = json.loads(filepath.read_text())
            for item in data:
                mem = Memory(**item)
                self._memories[layer].append(mem)
                self._index[mem.id] = mem
        except Exception:
            pass  # Corrupted file, start fresh

    def _save_layer(self, layer: str):
        """Save a memory layer to disk."""
        if layer not in ["episodic", "semantic", "procedural", "long_term"]:
            return  # Don't save transient layers
        filepath = self._layer_file(layer)
        data = [m.to_dict() for m in self._memories[layer]]
        filepath.write_text(json.dumps(data, indent=2))

    def store(
        self,
        content: str,
        layer: str = "short_term",
        source: str = "brain",
        importance: float = 0.5,
        tags: list[str] = None,
    ) -> Memory:
        """Store a new memory."""
        if layer not in self.LAYERS:
            layer = "short_term"

        # Check capacity and evict if needed
        if len(self._memories[layer]) >= self.CAPACITIES[layer]:
            self._evict(layer)

        mem = Memory(
            layer=layer,
            content=content,
            source=source,
            importance=importance,
            tags=tags or [],
        )
        self._memories[layer].append(mem)
        self._index[mem.id] = mem

        # Save persistent layers
        if layer in ["episodic", "semantic", "procedural", "long_term"]:
            self._save_layer(layer)

        return mem

    def _evict(self, layer: str):
        """Evict least important/least recently accessed memory."""
        if not self._memories[layer]:
            return

        # Score by importance * recency * access count
        def score(m: Memory):
            recency = datetime.fromisoformat(m.last_accessed).timestamp()
            return m.importance * (recency / 1e9) * (1 + m.access_count * 0.1)

        # Remove lowest score
        to_remove = min(self._memories[layer], key=score)
        self._memories[layer].remove(to_remove)
        if to_remove.id in self._index:
            del self._index[to_remove.id]

    def retrieve(self, memory_id: str) -> Memory:
        """Retrieve a memory by ID."""
        mem = self._index.get(memory_id)
        if mem:
            mem.touch()
        return mem

    def search(self, query: str, layer: str = None, limit: int = 10) -> list[Memory]:
        """Simple text search across memories."""
        query_lower = query.lower()
        results = []

        layers = [layer] if layer else self.LAYERS
        for l in layers:
            for mem in self._memories[l]:
                if query_lower in mem.content.lower():
                    mem.touch()
                    results.append(mem)

        # Sort by importance and recency
        results.sort(key=lambda m: (m.importance, m.access_count), reverse=True)
        return results[:limit]

    def consolidate(self, source_layer: str, target_layer: str, query: str = None):
        """Move important memories from source to target layer."""
        if source_layer == target_layer:
            return

        memories = self._memories[source_layer]
        to_move = []

        for mem in memories:
            if query and query.lower() not in mem.content.lower():
                continue
            if mem.importance >= 0.7:  # High importance threshold
                to_move.append(mem)

        for mem in to_move:
            mem.layer = target_layer
            self._memories[target_layer].append(mem)
            self._memories[source_layer].remove(mem)

        # Save both layers
        self._save_layer(source_layer)
        self._save_layer(target_layer)

    def forget(self, memory_id: str) -> bool:
        """Remove a memory by ID."""
        mem = self._index.get(memory_id)
        if not mem:
            return False

        self._memories[mem.layer].remove(mem)
        del self._index[memory_id]
        self._save_layer(mem.layer)
        return True

    def stats(self) -> dict[str, Any]:
        """Get memory statistics."""
        return {
            "total_memories": sum(len(m) for m in self._memories.values()),
            "by_layer": {layer: len(mems) for layer, mems in self._memories.items()},
            "capacity": self.CAPACITIES,
            "utilization": {
                layer: len(mems) / self.CAPACITIES[layer] for layer, mems in self._memories.items()
            },
        }

    def dump(self, layer: str = None) -> list[dict[str, Any]]:
        """Export memories as dicts."""
        layers = [layer] if layer else self.LAYERS
        result = []
        for l in layers:
            for mem in self._memories[l]:
                result.append(mem.to_dict())
        return result
