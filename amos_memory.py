#!/usr/bin/env python3
"""AMOS Memory System - Section 12 of Architecture

Mem_t = (W_t, E_t, S_t, P_t, Self_t)

Where:
- W_t: Working memory (short-term)
- E_t: Episodic memory (experiences/events)
- S_t: Semantic memory (facts/knowledge)
- P_t: Procedural memory (skills/how-to)
- Self_t: Self-memory (identity/self-model)

Retrieval:
Retrieve(q) = argmax_m [Similarity(q,m) · Relevance(m) · Freshness(m)]

Consolidation:
Mem_{t+1}^{long} = Mem_t^{long} + Compress(Mem_t^{short}, relevance, repetition, outcome)
"""

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class MemoryEntry:
    """A single memory entry with metadata."""

    content: Any
    memory_type: str  # working, episodic, semantic, procedural, self
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    entry_id: str = field(
        default_factory=lambda: hashlib.md5(datetime.now(UTC).isoformat().encode()).hexdigest()[:12]
    )

    # Retrieval metrics
    relevance_score: float = 0.5
    access_count: int = 0
    last_accessed: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    # Context
    source: str = "unknown"
    tags: List[str] = field(default_factory=list)
    associations: List[str] = field(default_factory=list)

    # Outcome tracking (for learning)
    outcome: str = None
    success: bool = None


class WorkingMemory:
    """W_t - Short-term conscious workspace
    Limited capacity, fast access
    """

    def __init__(self, capacity: int = 7):
        self.capacity = capacity
        self.entries: List[MemoryEntry] = []
        self.focus: str = None

    def add(self, content: Any, source: str = "workspace") -> MemoryEntry:
        """Add to working memory (forgets oldest if full)."""
        entry = MemoryEntry(content=content, memory_type="working", source=source)

        # If at capacity, move oldest to episodic (consolidation)
        if len(self.entries) >= self.capacity:
            self._consolidate_oldest()

        self.entries.append(entry)
        return entry

    def _consolidate_oldest(self):
        """Move oldest entry to long-term storage."""
        if self.entries:
            oldest = self.entries.pop(0)
            # Mark for consolidation (would be passed to episodic)
            oldest.memory_type = "episodic"
            return oldest
        return None

    def get_focus(self) -> Optional[MemoryEntry]:
        """Get currently focused memory."""
        if self.focus:
            for entry in self.entries:
                if entry.entry_id == self.focus:
                    entry.access_count += 1
                    entry.last_accessed = datetime.now(UTC).isoformat()
                    return entry
        return None

    def set_focus(self, entry_id: str):
        """Set focus to specific memory."""
        self.focus = entry_id

    def clear(self):
        """Clear working memory."""
        self.entries = []
        self.focus = None

    def __len__(self) -> int:
        return len(self.entries)

    def store(self, key: str, value: Any, priority: float = 0.5) -> MemoryEntry:
        """Store an item in working memory (alias for add with key-based access)."""
        entry = MemoryEntry(
            content={"key": key, "value": value},
            memory_type="working",
            source="store",
            relevance_score=priority,
        )

        # If at capacity, move oldest to episodic (consolidation)
        if len(self.entries) >= self.capacity:
            self._consolidate_oldest()

        self.entries.append(entry)
        return entry

    def retrieve(self, key: str) -> Any:
        """Retrieve an item from working memory by key."""
        for entry in reversed(self.entries):  # Most recent first
            if isinstance(entry.content, dict) and entry.content.get("key") == key:
                entry.access_count += 1
                entry.last_accessed = datetime.now(UTC).isoformat()
                return entry.content.get("value")
        return None


class EpisodicMemory:
    """E_t - Event/experience memory
    Temporal sequences, specific episodes
    """

    def __init__(self):
        self.episodes: Dict[str, MemoryEntry] = {}
        self.episode_chains: list[list[str]] = []  # Linked episodes

    def record_episode(self, event: str, context: dict, outcome: str = None) -> MemoryEntry:
        """Record a specific episode/event."""
        entry = MemoryEntry(
            content={
                "event": event,
                "context": context,
                "narrative": self._construct_narrative(event, context),
            },
            memory_type="episodic",
            source="experience",
            outcome=outcome,
        )

        self.episodes[entry.entry_id] = entry
        return entry

    def _construct_narrative(self, event: str, context: dict) -> str:
        """Construct narrative from event and context."""
        time_str = context.get("time", datetime.now(UTC).isoformat())
        return f"At {time_str}: {event}"

    def find_similar_episodes(self, query: str, n: int = 3) -> List[MemoryEntry]:
        """Find episodes similar to query."""
        scored = []
        for entry in self.episodes.values():
            similarity = self._compute_similarity(query, str(entry.content))
            scored.append((entry, similarity))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [e[0] for e in scored[:n]]

    def _compute_similarity(self, query: str, content: str) -> float:
        """Simple similarity metric (can be enhanced with embeddings)."""
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())

        if not query_words:
            return 0.0

        overlap = len(query_words & content_words)
        return overlap / len(query_words)

    def chain_episodes(self, episode_ids: List[str]):
        """Create temporal chain of episodes."""
        self.episode_chains.append(episode_ids)

    def record(self, data: dict) -> MemoryEntry:
        """Record an episode (alias for record_episode with dict input)."""
        event = data.get("event", str(data))
        context = data.get("context", data)
        outcome = data.get("outcome")
        return self.record_episode(event, context, outcome)

    def retrieve_recent(self, n: int = 5) -> List[MemoryEntry]:
        """Retrieve the n most recent episodes."""
        sorted_episodes = sorted(self.episodes.values(), key=lambda e: e.timestamp, reverse=True)
        return sorted_episodes[:n]


class SemanticMemory:
    """S_t - Fact/knowledge memory
    Concepts, relations, general knowledge
    """

    def __init__(self):
        self.concepts: Dict[str, dict] = {}  # Concept graph
        self.relations: List[tuple] = []  # (source, relation, target)

    def add_concept(self, concept: str, properties: dict, category: str = "general"):
        """Add a concept to semantic memory."""
        self.concepts[concept] = {
            "properties": properties,
            "category": category,
            "added": datetime.now(UTC).isoformat(),
            "confidence": properties.get("confidence", 0.8),
        }

    def add_relation(self, source: str, relation: str, target: str):
        """Add relation between concepts."""
        self.relations.append((source, relation, target))

        # Update associations
        if source in self.concepts:
            if "associations" not in self.concepts[source]:
                self.concepts[source]["associations"] = []
            self.concepts[source]["associations"].append((relation, target))

    def query(self, concept: str) -> dict:
        """Query concept from semantic memory."""
        return self.concepts.get(concept)

    def infer(self, concept: str, relation: str) -> List[str]:
        """Infer related concepts via relation."""
        results = []
        for s, r, t in self.relations:
            if s == concept and r == relation:
                results.append(t)
        return results

    def get_related(self, concept: str, depth: int = 1) -> List[str]:
        """Get all related concepts up to depth."""
        if depth == 0 or concept not in self.concepts:
            return []

        direct = [t for s, r, t in self.relations if s == concept]

        if depth > 1:
            for related in direct[:]:
                direct.extend(self.get_related(related, depth - 1))

        return list(set(direct))


class ProceduralMemory:
    """P_t - Skill/how-to memory
    Procedures, algorithms, learned skills
    """

    def __init__(self):
        self.procedures: Dict[str, dict] = {}
        self.skill_levels: Dict[str, float] = {}  # 0.0 to 1.0

    def learn_procedure(self, name: str, steps: List[str], preconditions: List[str] = None):
        """Learn a new procedure."""
        self.procedures[name] = {
            "steps": steps,
            "preconditions": preconditions or [],
            "learned": datetime.now(UTC).isoformat(),
            "execution_count": 0,
            "success_count": 0,
        }
        self.skill_levels[name] = 0.1  # Initial skill level

    def execute_procedure(self, name: str, context: dict) -> dict:
        """Execute a learned procedure."""
        if name not in self.procedures:
            return {"success": False, "error": f"Unknown procedure: {name}"}

        proc = self.procedures[name]
        proc["execution_count"] += 1

        # Check preconditions
        missing = [p for p in proc["preconditions"] if p not in context.get("satisfied", [])]
        if missing:
            return {"success": False, "error": f"Missing preconditions: {missing}"}

        # Simulate execution (simplified)
        success_rate = self.skill_levels[name]
        success = success_rate > 0.5  # Deterministic for demo

        if success:
            proc["success_count"] += 1
            # Improve skill with practice
            self.skill_levels[name] = min(1.0, self.skill_levels[name] + 0.1)

        return {
            "success": success,
            "steps_executed": len(proc["steps"]),
            "skill_level": self.skill_levels[name],
        }

    def get_procedure(self, name: str) -> dict:
        """Get procedure details."""
        return self.procedures.get(name)


class SelfMemory:
    """Self_t - Identity/self-model memory
    Self-concept, autobiography, identity drift tracking
    """

    def __init__(self):
        self.identity_core: dict = {
            "name": "AMOS",
            "version": "1.0",
            "created": datetime.now(UTC).isoformat(),
            "purpose": "Self-modeling, future-generating organism",
        }
        self.autobiography: List[MemoryEntry] = []
        self.capabilities: Dict[str, float] = {}
        self.values: List[str] = []
        self.drift_history: List[dict] = []

    def record_self_event(self, event_type: str, description: str, significance: float = 0.5):
        """Record autobiographical event."""
        entry = MemoryEntry(
            content={"type": event_type, "description": description, "significance": significance},
            memory_type="self",
            source="self_reflection",
        )
        self.autobiography.append(entry)

        # High significance events affect self-concept
        if significance > 0.8:
            self._update_self_concept(event_type, description)

    def _update_self_concept(self, event_type: str, description: str):
        """Update self-concept based on significant events."""
        if "learned" in event_type:
            self.capabilities[description] = self.capabilities.get(description, 0.0) + 0.1

    def measure_drift(self, previous_state: dict) -> float:
        """Measure identity drift: Drift(Self_t, Self_{t+1}) ≤ δ
        Returns drift score (lower is better).
        """
        current = self._get_state_hash()
        previous = hashlib.md5(json.dumps(previous_state, sort_keys=True).encode()).hexdigest()

        # Simplified: just check if states differ
        drift = 0.0 if current == previous else 0.5

        self.drift_history.append(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "drift_score": drift,
                "within_bounds": drift <= 0.8,  # δ = 0.8
            }
        )

        return drift

    def _get_state_hash(self) -> str:
        """Get hash of current self-state."""
        state = {
            "core": self.identity_core,
            "capabilities": self.capabilities,
            "values": self.values,
        }
        return hashlib.md5(json.dumps(state, sort_keys=True).encode()).hexdigest()

    def who_am_i(self) -> str:
        """Generate self-description."""
        caps = ", ".join([f"{k}({v:.0%})" for k, v in self.capabilities.items()]) or "none yet"
        return f"I am {self.identity_core['name']}, version {self.identity_core['version']}. Capabilities: {caps}"


class AMOSMemory:
    """Complete AMOS Memory System
    Integrates all memory types with retrieval and consolidation.
    """

    def __init__(self):
        self.working = WorkingMemory(capacity=7)
        self.episodic = EpisodicMemory()
        self.semantic = SemanticMemory()
        self.procedural = ProceduralMemory()
        self.self = SelfMemory()

    def retrieve(self, query: str, memory_type: str = None, n: int = 3) -> List[MemoryEntry]:
        """Retrieve(q) = argmax_m [Similarity(q,m) · Relevance(m) · Freshness(m)]"""
        candidates = []

        # Collect from all memory types
        if memory_type is None or memory_type == "episodic":
            candidates.extend(self.episodic.episodes.values())

        if memory_type is None or memory_type == "working":
            candidates.extend(self.working.entries)

        if memory_type is None or memory_type == "self":
            candidates.extend(self.self.autobiography)

        # Score each candidate
        now = datetime.now(UTC)
        scored = []
        for entry in candidates:
            similarity = self._compute_similarity(query, str(entry.content))
            relevance = entry.relevance_score

            # Freshness decay
            entry_time = datetime.fromisoformat(entry.timestamp)
            age_hours = (now - entry_time).total_seconds() / 3600
            freshness = max(0.1, 1.0 - (age_hours / 168))  # Decay over 1 week

            score = similarity * relevance * freshness
            scored.append((entry, score))

        # Sort and return top n
        scored.sort(key=lambda x: x[1], reverse=True)
        return [e[0] for e in scored[:n]]

    def _compute_similarity(self, query: str, content: str) -> float:
        """Compute text similarity."""
        q_words = set(query.lower().split())
        c_words = set(content.lower().split())
        if not q_words:
            return 0.0
        return len(q_words & c_words) / len(q_words)

    def consolidate(self):
        """Mem_{t+1}^{long} = Mem_t^{long} + Compress(Mem_t^{short}, relevance, repetition, outcome)

        Move important working memories to episodic.
        """
        consolidated = []
        for entry in self.working.entries[:]:
            if entry.access_count >= 2 or entry.relevance_score > 0.7:
                # Move to episodic
                entry.memory_type = "episodic"
                self.episodic.episodes[entry.entry_id] = entry
                self.working.entries.remove(entry)
                consolidated.append(entry.entry_id)

        return consolidated

    def stats(self) -> dict:
        """Get memory statistics."""
        return {
            "working": len(self.working),
            "episodic": len(self.episodic.episodes),
            "semantic_concepts": len(self.semantic.concepts),
            "procedural_skills": len(self.procedural.procedures),
            "self_events": len(self.self.autobiography),
            "identity_drift": self.self.drift_history[-1] if self.self.drift_history else None,
        }


def demo_memory_system():
    """Demonstrate AMOS Memory System."""
    print("=" * 70)
    print("🧠 AMOS MEMORY SYSTEM - Section 12")
    print("=" * 70)
    print("\nMem_t = (W_t, E_t, S_t, P_t, Self_t)")
    print("-" * 70)

    # Initialize memory
    memory = AMOSMemory()

    # 1. Working Memory
    print("\n[1] Working Memory (Short-term)")
    wm_entry = memory.working.add("Current task: Build memory system", "cognition")
    print(f"  ✓ Added: {wm_entry.entry_id}")
    print(f"  ✓ Capacity: {memory.working.capacity}, Current: {len(memory.working)}")

    # 2. Episodic Memory
    print("\n[2] Episodic Memory (Experiences)")
    ep1 = memory.episodic.record_episode(
        "Started AMOS memory system",
        {"time": datetime.now(UTC).isoformat(), "location": "build_process"},
        outcome="success",
    )
    ep2 = memory.episodic.record_episode(
        "Learned about memory consolidation",
        {"time": datetime.now(UTC).isoformat(), "context": "architecture_doc"},
        outcome="success",
    )
    print(f"  ✓ Recorded episodes: {ep1.entry_id}, {ep2.entry_id}")

    # 3. Semantic Memory
    print("\n[3] Semantic Memory (Facts/Knowledge)")
    memory.semantic.add_concept(
        "memory_consolidation",
        {"definition": "Process of transferring short-term to long-term memory", "confidence": 0.9},
        category="cognitive_science",
    )
    memory.semantic.add_concept(
        "working_memory", {"capacity": 7, "duration": "short"}, category="cognitive_science"
    )
    memory.semantic.add_relation("working_memory", "part_of", "memory_system")
    memory.semantic.add_relation("memory_consolidation", "transforms", "working_memory")
    print(f"  ✓ Concepts: {len(memory.semantic.concepts)}")
    print(f"  ✓ Relations: {len(memory.semantic.relations)}")

    # Query semantic memory
    concept = memory.semantic.query("memory_consolidation")
    if concept:
        print(f"  ✓ Query result: {concept['properties']['definition'][:50]}...")

    # 4. Procedural Memory
    print("\n[4] Procedural Memory (Skills)")
    memory.procedural.learn_procedure(
        "retrieve_memory",
        ["Formulate query", "Search memory stores", "Rank by relevance", "Return top matches"],
        ["query_formulated", "memory_system_active"],
    )
    result = memory.procedural.execute_procedure(
        "retrieve_memory", {"satisfied": ["query_formulated"]}
    )
    print("  ✓ Learned procedure: retrieve_memory")
    print(f"  ✓ Execution: success={result['success']}, skill={result['skill_level']:.1%}")

    # 5. Self Memory
    print("\n[5] Self Memory (Identity)")
    memory.self.record_self_event("initialization", "Memory system initialized", significance=0.9)
    memory.self.record_self_event(
        "capability_added", "Can now store and retrieve memories", significance=0.85
    )
    print(f"  ✓ Autobiographical events: {len(memory.self.autobiography)}")
    print(f"  ✓ Self-description: {memory.self.who_am_i()}")

    # 6. Retrieval
    print("\n[6] Memory Retrieval")
    print("  Query: 'memory system'")
    results = memory.retrieve("memory system", n=3)
    for i, r in enumerate(results, 1):
        print(f"  {i}. [{r.memory_type}] {str(r.content)[:50]}...")

    # 7. Consolidation
    print("\n[7] Memory Consolidation")
    # Access working memory multiple times
    for _ in range(3):
        _ = memory.working.get_focus()
    # Consolidate
    consolidated = memory.consolidate()
    print(f"  ✓ Consolidated {len(consolidated)} memories to episodic")

    # Stats
    print("\n" + "=" * 70)
    print("MEMORY STATISTICS")
    print("=" * 70)
    stats = memory.stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n" + "=" * 70)
    print("✅ AMOS MEMORY SYSTEM OPERATIONAL")
    print("=" * 70)
    print("\nCapabilities:")
    print("  • Multi-store architecture (5 memory types)")
    print("  • Weighted retrieval (similarity × relevance × freshness)")
    print("  • Automatic consolidation (working → episodic)")
    print("  • Identity drift tracking (Self_t)")
    print("  • Semantic relations and inference")
    print("  • Skill learning and improvement")
    print("=" * 70)

    return memory


if __name__ == "__main__":
    memory = demo_memory_system()
