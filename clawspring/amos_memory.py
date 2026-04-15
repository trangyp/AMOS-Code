"""AMOS Memory Layer - Persistence for brain state and cognitive artifacts."""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class MemoryEntry:
    """Single memory entry with metadata."""

    id: str
    content: dict
    memory_type: str  # 'reasoning', 'decision', 'code', 'design', 'ubi', 'workflow'
    timestamp: float = field(default_factory=time.time)
    tags: list[str] = field(default_factory=list)
    source: str = ""  # Which component created this
    law_compliance: dict = field(default_factory=dict)
    gap_acknowledged: bool = True


@dataclass
class BrainState:
    """Complete brain state snapshot."""

    timestamp: float
    runtime_config: dict
    workflow_history: list[str]
    cognitive_artifacts: list[dict]
    law_violations: list[dict]
    gap_statements: list[str]
    version: str = "vInfinity"
    creator: str = "Trang Phan"


class AMOSMemoryStore:
    """Persistent memory store for AMOS brain."""

    def __init__(self, storage_path: Path | None = None):
        self.storage_path = storage_path or Path("./amos_memory")
        self.storage_path.mkdir(exist_ok=True)
        self._cache: dict[str, MemoryEntry] = {}

    def store(self, entry: MemoryEntry) -> str:
        """Store a memory entry."""
        # Store in cache
        self._cache[entry.id] = entry

        # Persist to disk
        file_path = self.storage_path / f"{entry.memory_type}_{entry.id}.json"
        with open(file_path, "w") as f:
            json.dump(asdict(entry), f, indent=2, default=str)

        return entry.id

    def retrieve(self, entry_id: str) -> MemoryEntry | None:
        """Retrieve a memory entry by ID."""
        # Check cache first
        if entry_id in self._cache:
            return self._cache[entry_id]

        # Try to load from disk
        for file_path in self.storage_path.glob(f"*_{entry_id}.json"):
            with open(file_path) as f:
                data = json.load(f)
                entry = MemoryEntry(**data)
                self._cache[entry_id] = entry
                return entry

        return None

    def query_by_type(self, memory_type: str) -> list[MemoryEntry]:
        """Query all memories of a specific type."""
        entries = []
        for file_path in self.storage_path.glob(f"{memory_type}_*.json"):
            with open(file_path) as f:
                data = json.load(f)
                entries.append(MemoryEntry(**data))
        return sorted(entries, key=lambda x: x.timestamp, reverse=True)

    def query_by_tag(self, tag: str) -> list[MemoryEntry]:
        """Query all memories with a specific tag."""
        entries = []
        for file_path in self.storage_path.glob("*.json"):
            with open(file_path) as f:
                data = json.load(f)
                if tag in data.get("tags", []):
                    entries.append(MemoryEntry(**data))
        return sorted(entries, key=lambda x: x.timestamp, reverse=True)

    def save_brain_state(self, state: BrainState) -> str:
        """Save complete brain state."""
        state_id = f"state_{int(state.timestamp)}"
        file_path = self.storage_path / f"brain_state_{state_id}.json"

        with open(file_path, "w") as f:
            json.dump(asdict(state), f, indent=2, default=str)

        return state_id

    def load_latest_brain_state(self) -> BrainState | None:
        """Load the most recent brain state."""
        state_files = sorted(
            self.storage_path.glob("brain_state_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        if not state_files:
            return None

        with open(state_files[0]) as f:
            data = json.load(f)
            return BrainState(**data)

    def get_memory_stats(self) -> dict:
        """Get memory store statistics."""
        all_files = list(self.storage_path.glob("*.json"))
        by_type = {}
        for f in all_files:
            mem_type = f.name.split("_")[0]
            by_type[mem_type] = by_type.get(mem_type, 0) + 1

        return {
            "total_memories": len(all_files),
            "by_type": by_type,
            "storage_path": str(self.storage_path),
            "creator": "Trang Phan",
            "amos_version": "vInfinity",
        }


class AMOSMemoryBridge:
    """Bridge between AMOS components and memory store."""

    def __init__(self, store: AMOSMemoryStore | None = None):
        self.store = store or AMOSMemoryStore()

    def remember_reasoning(
        self,
        task: str,
        perspectives: list,
        quadrants: dict,
        recommendation: str,
    ) -> str:
        """Store reasoning result."""
        entry = MemoryEntry(
            id=f"reasoning_{int(time.time())}",
            content={
                "task": task,
                "perspectives": perspectives,
                "quadrants": quadrants,
                "recommendation": recommendation,
            },
            memory_type="reasoning",
            tags=["cognitive", "rule_of_2", "rule_of_4"],
            source="amos_execution",
            law_compliance={"L2": True, "L3": True, "L4": True},
        )
        return self.store.store(entry)

    def remember_code(
        self,
        function_name: str,
        layer: str,
        code: str,
        quality_score: float,
    ) -> str:
        """Store generated code."""
        entry = MemoryEntry(
            id=f"code_{function_name}_{int(time.time())}",
            content={
                "function_name": function_name,
                "layer": layer,
                "code": code,
                "quality_score": quality_score,
            },
            memory_type="code",
            tags=["coding_engine", layer],
            source="amos_coding_engine",
            law_compliance={"L4": quality_score > 0.7, "L5": True, "L6": True},
        )
        return self.store.store(entry)

    def remember_design(
        self,
        component_type: str,
        design_system: dict,
        biological_constraints: list,
    ) -> str:
        """Store design specification."""
        entry = MemoryEntry(
            id=f"design_{component_type}_{int(time.time())}",
            content={
                "component_type": component_type,
                "design_system": design_system,
                "biological_constraints": biological_constraints,
            },
            memory_type="design",
            tags=["design_engine", "ubi_aligned"],
            source="amos_design_engine",
            law_compliance={"L6": True},  # UBI alignment
        )
        return self.store.store(entry)

    def remember_ubi_analysis(
        self,
        description: str,
        domains: dict,
        risk_flags: list,
    ) -> str:
        """Store UBI analysis."""
        entry = MemoryEntry(
            id=f"ubi_{int(time.time())}",
            content={
                "description": description,
                "domains_analyzed": list(domains.keys()),
                "risk_flags": risk_flags,
            },
            memory_type="ubi",
            tags=["ubi_engine", "human_factors", "safety_first"],
            source="amos_ubi_engine",
            law_compliance={"L6": True},  # UBI alignment
        )
        return self.store.store(entry)

    def snapshot_brain_state(
        self,
        runtime_config: dict,
        workflow_history: list,
    ) -> str:
        """Create complete brain state snapshot."""
        state = BrainState(
            timestamp=time.time(),
            runtime_config=runtime_config,
            workflow_history=workflow_history,
            cognitive_artifacts=[],
            law_violations=[],
            gap_statements=[
                "GAP: This is a persisted structural model, not lived experience.",
                "GAP: Memory has no biological substrate, only digital storage.",
            ],
        )
        return self.store.save_brain_state(state)

    def recall_recent(self, memory_type: str | None = None, limit: int = 10) -> list[MemoryEntry]:
        """Recall recent memories."""
        if memory_type:
            entries = self.store.query_by_type(memory_type)
        else:
            entries = []
            for t in ["reasoning", "code", "design", "ubi", "workflow"]:
                entries.extend(self.store.query_by_type(t))
            entries.sort(key=lambda x: x.timestamp, reverse=True)

        return entries[:limit]


# Singleton
_memory_bridge: AMOSMemoryBridge | None = None


def get_memory_bridge() -> AMOSMemoryBridge:
    """Get singleton memory bridge."""
    global _memory_bridge
    if _memory_bridge is None:
        _memory_bridge = AMOSMemoryBridge()
    return _memory_bridge


def remember(task_type: str, data: dict) -> str:
    """Quick memory storage helper."""
    bridge = get_memory_bridge()

    if task_type == "reasoning":
        return bridge.remember_reasoning(
            data.get("task", ""),
            data.get("perspectives", []),
            data.get("quadrants", {}),
            data.get("recommendation", ""),
        )
    elif task_type == "code":
        return bridge.remember_code(
            data.get("function_name", ""),
            data.get("layer", ""),
            data.get("code", ""),
            data.get("quality_score", 0.0),
        )
    elif task_type == "design":
        return bridge.remember_design(
            data.get("component_type", ""),
            data.get("design_system", {}),
            data.get("biological_constraints", []),
        )
    elif task_type == "ubi":
        return bridge.remember_ubi_analysis(
            data.get("description", ""),
            data.get("domains", {}),
            data.get("risk_flags", []),
        )

    return ""


def recall(memory_type: str | None = None, limit: int = 10) -> list[MemoryEntry]:
    """Quick recall helper."""
    return get_memory_bridge().recall_recent(memory_type, limit)


if __name__ == "__main__":
    print("=" * 60)
    print("AMOS MEMORY LAYER TEST")
    print("=" * 60)

    # Test memory bridge
    bridge = get_memory_bridge()

    # Store some memories
    print("\nStoring memories...")

    reasoning_id = bridge.remember_reasoning(
        task="Should we implement feature X?",
        perspectives=[
            {"stance": "technical", "view": "feasible"},
            {"stance": "business", "view": "valuable"},
        ],
        quadrants={"biological": {}, "technical": {}, "economic": {}, "environmental": {}},
        recommendation="Proceed with phased implementation",
    )
    print(f"Stored reasoning: {reasoning_id}")

    code_id = bridge.remember_code(
        function_name="analyze_task",
        layer="backend",
        code="def analyze(): pass",
        quality_score=0.85,
    )
    print(f"Stored code: {code_id}")

    design_id = bridge.remember_design(
        component_type="form",
        design_system={"structure": "hierarchical"},
        biological_constraints=["respect_attention_span"],
    )
    print(f"Stored design: {design_id}")

    # Recall recent
    print("\nRecalling recent memories...")
    recent = recall(limit=5)
    for mem in recent:
        print(
            f"  - {mem.memory_type}: {mem.id[:30]}... ({datetime.fromtimestamp(mem.timestamp).strftime('%H:%M:%S')})"
        )

    # Stats
    stats = bridge.store.get_memory_stats()
    print("\nMemory Stats:")
    print(f"  Total: {stats['total_memories']}")
    print(f"  By type: {stats['by_type']}")

    print("\n" + "=" * 60)
    print("Memory Layer: OPERATIONAL")
    print("=" * 60)
    print("\nGAP: Digital memory is not biological memory.")
    print("No neural substrate. No experience. Structural only.")
