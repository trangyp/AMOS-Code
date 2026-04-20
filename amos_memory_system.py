#!/usr/bin/env python3
"""AMOS Tiered Memory System v1.0.0
===============================

Multi-layer memory architecture for AI agents based on 2024-2025 research:
- Working Memory: Active context, reasoning scratchpad
- Short-term Memory: Conversation history, checkpoints
- Episodic Memory: Session history, past interactions
- Semantic Memory: Knowledge graph, entity relationships
- Procedural Memory: Learned workflows, routines

Integration:
- Neural: Pattern recognition, semantic retrieval
- Symbolic: Structured storage, entity relationships
- Hybrid: Consolidation, conflict resolution

Author: Trang Phan
Version: 1.0.0
"""

import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


@dataclass
class MemoryEntry:
    """Base memory entry with metadata."""

    content: str
    timestamp: float = field(default_factory=time.time)
    memory_type: str = "unknown"  # working, short_term, episodic, semantic, procedural
    importance: float = 0.5  # 0.0-1.0
    tags: list[str] = field(default_factory=list)
    source: str = ""  # agent_id, user, system
    session_id: str = ""
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)

    def score_relevance(self) -> float:
        """Calculate relevance score (recency * importance)."""
        age_hours = (time.time() - self.timestamp) / 3600
        recency = max(0.1, 1.0 - (age_hours / 168))  # Decay over 1 week
        return recency * self.importance * (1 + self.access_count * 0.1)


class WorkingMemory:
    """Fast, limited-capacity active context.

    Stores current conversation context, active goals,
    and reasoning scratchpad. High volatility.
    """

    def __init__(self, capacity: int = 10):
        self.capacity = capacity
        self._entries: list[MemoryEntry] = []
        self._context: dict[str, Any] = {}

    def add(self, content: str, source: str = "") -> None:
        """Add to working memory with LRU eviction."""
        entry = MemoryEntry(content=content, memory_type="working", importance=0.9, source=source)
        self._entries.append(entry)

        # Evict oldest if over capacity
        if len(self._entries) > self.capacity:
            self._entries.pop(0)

    def get_context(self) -> str:
        """Get current working context."""
        return "\n".join([e.content for e in self._entries])

    def set_context_var(self, key: str, value: Any) -> None:
        """Set context variable."""
        self._context[key] = value

    def get_context_var(self, key: str) -> Optional[Any]:
        """Get context variable."""
        return self._context.get(key)

    def clear(self) -> None:
        """Clear working memory."""
        self._entries.clear()
        self._context.clear()


class ShortTermMemory:
    """Conversation history and recent checkpoints.

    Stores recent interactions with automatic summarization
    and checkpointing for conversation recovery.
    """

    def __init__(self, max_entries: int = 100):
        self.max_entries = max_entries
        self._entries: list[MemoryEntry] = []
        self._checkpoints: dict[str, dict] = {}

    def add_interaction(self, user_input: str, agent_response: str, session_id: str = "") -> None:
        """Record conversation turn."""
        entry = MemoryEntry(
            content=f"User: {user_input}\nAgent: {agent_response}",
            memory_type="short_term",
            importance=0.7,
            session_id=session_id,
            tags=["conversation", "interaction"],
        )
        self._entries.append(entry)

        # Trim if needed
        if len(self._entries) > self.max_entries:
            self._entries = self._entries[-self.max_entries :]

    def create_checkpoint(self, name: str) -> str:
        """Save current state as checkpoint."""
        checkpoint_id = hashlib.md5(f"{name}{time.time()}".encode()).hexdigest()[:12]

        self._checkpoints[checkpoint_id] = {
            "name": name,
            "timestamp": time.time(),
            "entries": len(self._entries),
            "snapshot": [e.content for e in self._entries[-10:]],
        }
        return checkpoint_id

    def restore_checkpoint(self, checkpoint_id: str) -> bool:
        """Restore from checkpoint."""
        if checkpoint_id not in self._checkpoints:
            return False
        # In real implementation, would restore full state
        return True

    def get_recent(self, n: int = 10) -> list[MemoryEntry]:
        """Get n most recent entries."""
        return self._entries[-n:]

    def search(self, query: str) -> list[MemoryEntry]:
        """Simple keyword search."""
        query_lower = query.lower()
        results = [e for e in self._entries if query_lower in e.content.lower()]
        return sorted(results, key=lambda e: e.score_relevance(), reverse=True)


class EpisodicMemory:
    """Long-term experience storage.

    Stores complete session histories, outcomes,
    and experience-based learning. Persistent storage.
    """

    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path.home() / ".amos" / "episodic_memory"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._episodes: list[dict] = []
        self._load_episodes()

    def _load_episodes(self) -> None:
        """Load episodes from disk."""
        episodes_file = self.storage_path / "episodes.json"
        if episodes_file.exists():
            with open(episodes_file) as f:
                self._episodes = json.load(f)

    def _save_episodes(self) -> None:
        """Save episodes to disk."""
        episodes_file = self.storage_path / "episodes.json"
        with open(episodes_file, "w") as f:
            json.dump(self._episodes, f, indent=2)

    def record_episode(
        self,
        session_id: str,
        task: str,
        outcome: str,
        agents_used: list[str],
        law_compliance: bool,
        lessons_learned: list[str],
    ) -> None:
        """Record complete session as episode."""
        episode = {
            "episode_id": hashlib.md5(f"{session_id}{time.time()}".encode()).hexdigest()[:12],
            "session_id": session_id,
            "timestamp": time.time(),
            "task": task,
            "outcome": outcome,
            "agents_used": agents_used,
            "law_compliance": law_compliance,
            "lessons_learned": lessons_learned,
        }
        self._episodes.append(episode)
        self._save_episodes()

    def find_similar_episodes(self, task_description: str) -> list[dict]:
        """Find episodes similar to current task."""
        # Simple keyword matching - in production would use embeddings
        keywords = set(task_description.lower().split())
        scored = []

        for episode in self._episodes:
            episode_words = set(episode["task"].lower().split())
            overlap = len(keywords & episode_words)
            score = overlap / max(len(keywords), 1)
            if score > 0.3:  # Threshold
                scored.append((score, episode))

        scored.sort(reverse=True)
        return [ep[1] for ep in scored[:5]]

    def get_lessons_for_task(self, task_type: str) -> list[str]:
        """Extract learned lessons for task type."""
        lessons = []
        for episode in self._episodes:
            if task_type.lower() in episode["task"].lower():
                lessons.extend(episode.get("lessons_learned", []))
        return list(set(lessons))  # Deduplicate


class SemanticMemory:
    """Structured knowledge and entity relationships.

    Stores facts, rules, definitions, and relationships.
    Knowledge graph style storage.
    """

    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path.home() / ".amos" / "semantic_memory"
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Knowledge graph: entities and relationships
        self._entities: dict[str, dict] = {}
        self._facts: list[dict] = []
        self._load_knowledge()

    def _load_knowledge(self) -> None:
        """Load knowledge from disk."""
        kg_file = self.storage_path / "knowledge_graph.json"
        if kg_file.exists():
            with open(kg_file) as f:
                data = json.load(f)
                self._entities = data.get("entities", {})
                self._facts = data.get("facts", [])

    def _save_knowledge(self) -> None:
        """Save knowledge to disk."""
        kg_file = self.storage_path / "knowledge_graph.json"
        with open(kg_file, "w") as f:
            json.dump({"entities": self._entities, "facts": self._facts}, f, indent=2)

    def add_entity(self, entity_id: str, entity_type: str, properties: dict) -> None:
        """Add entity to knowledge graph."""
        self._entities[entity_id] = {
            "type": entity_type,
            "properties": properties,
            "added": time.time(),
        }
        self._save_knowledge()

    def add_fact(self, subject: str, predicate: str, obj: str, confidence: float = 1.0) -> None:
        """Add fact (triplet) to knowledge base."""
        self._facts.append(
            {
                "subject": subject,
                "predicate": predicate,
                "object": obj,
                "confidence": confidence,
                "added": time.time(),
            }
        )
        self._save_knowledge()

    def query_entity(self, entity_id: str) -> dict:
        """Query entity information."""
        return self._entities.get(entity_id)

    def query_facts(self, subject: str = None, predicate: str = None) -> list[dict]:
        """Query facts by subject or predicate."""
        results = self._facts
        if subject:
            results = [f for f in results if f["subject"] == subject]
        if predicate:
            results = [f for f in results if f["predicate"] == predicate]
        return results

    def infer_relationship(self, entity1: str, entity2: str) -> list[str]:
        """Find relationship paths between entities."""
        # Simple 1-hop inference
        direct = [
            f["predicate"]
            for f in self._facts
            if f["subject"] == entity1 and f["object"] == entity2
        ]
        return direct


class ProceduralMemory:
    """Stored workflows and learned procedures.

    Remembers how to perform tasks, workflow patterns,
    and learned execution strategies.
    """

    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path.home() / ".amos" / "procedural_memory"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._procedures: dict[str, dict] = {}
        self._load_procedures()

    def _load_procedures(self) -> None:
        """Load procedures from disk."""
        proc_file = self.storage_path / "procedures.json"
        if proc_file.exists():
            with open(proc_file) as f:
                self._procedures = json.load(f)

    def _save_procedures(self) -> None:
        """Save procedures to disk."""
        proc_file = self.storage_path / "procedures.json"
        with open(proc_file, "w") as f:
            json.dump(self._procedures, f, indent=2)

    def learn_procedure(
        self, task_pattern: str, steps: list[str], success_rate: float = 0.0
    ) -> None:
        """Learn or update procedure for task pattern."""
        if task_pattern not in self._procedures:
            self._procedures[task_pattern] = {
                "steps": steps,
                "success_rate": success_rate,
                "uses": 0,
                "learned": time.time(),
            }
        else:
            # Update if success rate improved
            if success_rate > self._procedures[task_pattern]["success_rate"]:
                self._procedures[task_pattern]["steps"] = steps
                self._procedures[task_pattern]["success_rate"] = success_rate

        self._save_procedures()

    def get_procedure(self, task_pattern: str) -> dict:
        """Get learned procedure for task."""
        # Exact match
        if task_pattern in self._procedures:
            self._procedures[task_pattern]["uses"] += 1
            self._save_procedures()
            return self._procedures[task_pattern]

        # Pattern matching - find closest
        for pattern, proc in self._procedures.items():
            if pattern in task_pattern or task_pattern in pattern:
                return proc

        return None

    def update_success_rate(self, task_pattern: str, success: bool) -> None:
        """Update success rate based on execution outcome."""
        if task_pattern in self._procedures:
            proc = self._procedures[task_pattern]
            # Exponential moving average
            alpha = 0.3
            current = proc["success_rate"]
            new_rate = current + alpha * (1.0 if success else 0.0 - current)
            proc["success_rate"] = new_rate
            self._save_procedures()


class AMOSMemoryManager:
    """Unified memory manager integrating all tiers.

    Provides seamless integration between memory types
    with automatic consolidation and retrieval.
    """

    def __init__(self, session_id: str = None):
        self.session_id = session_id or self._generate_session_id()

        # Initialize all memory tiers
        self.working = WorkingMemory()
        self.short_term = ShortTermMemory()
        self.episodic = EpisodicMemory()
        self.semantic = SemanticMemory()
        self.procedural = ProceduralMemory()

    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        return (
            f"session_{int(time.time())}_{hashlib.md5(str(time.time()).encode()).hexdigest()[:6]}"
        )

    def record_interaction(self, user_input: str, agent_response: str) -> None:
        """Record conversation interaction across memory tiers."""
        # Working memory - immediate context
        self.working.add(f"User: {user_input}", source="user")
        self.working.add(f"Agent: {agent_response}", source="agent")

        # Short-term memory - conversation history
        self.short_term.add_interaction(user_input, agent_response, self.session_id)

    def get_context_for_llm(self) -> str:
        """Get formatted context for LLM prompt."""
        parts = []

        # Working memory (most important, always included)
        working_ctx = self.working.get_context()
        if working_ctx:
            parts.append("## Current Context\n" + working_ctx)

        # Short-term memory (recent history)
        recent = self.short_term.get_recent(5)
        if recent:
            parts.append("## Recent Conversation\n" + "\n".join([e.content for e in recent]))

        # Episodic memory (similar past experiences)
        # Would need current task to search - placeholder

        return "\n\n".join(parts)

    def checkpoint(self, name: str) -> str:
        """Create session checkpoint."""
        return self.short_term.create_checkpoint(name)

    def record_episode(
        self,
        task: str,
        outcome: str,
        agents_used: list[str],
        law_compliance: bool,
        lessons_learned: list[str],
    ) -> None:
        """Record complete episode to long-term memory."""
        self.episodic.record_episode(
            self.session_id, task, outcome, agents_used, law_compliance, lessons_learned
        )

    def learn_from_episode(self) -> None:
        """Consolidate short-term to long-term memory."""
        # Extract patterns from recent interactions
        recent = self.short_term.get_recent(20)

        # Would use LLM to extract facts and patterns
        # For now, placeholder implementation

        # Add to semantic memory
        for entry in recent:
            if "error" in entry.content.lower():
                self.semantic.add_fact("system", "had_error", "true", confidence=0.9)

    def get_memory_summary(self) -> dict:
        """Get summary of all memory tiers."""
        return {
            "session_id": self.session_id,
            "working": len(self.working._entries),
            "short_term": len(self.short_term._entries),
            "episodic": len(self.episodic._episodes),
            "semantic_entities": len(self.semantic._entities),
            "semantic_facts": len(self.semantic._facts),
            "procedures": len(self.procedural._procedures),
        }


def main():
    """Demo memory system."""
    print("=" * 70)
    print("AMOS TIERED MEMORY SYSTEM v1.0.0")
    print("=" * 70)

    memory = AMOSMemoryManager()

    print(f"\n[Session ID] {memory.session_id}")

    # Simulate interactions
    print("\n[Recording Interactions]")
    interactions = [
        ("Design a secure API", "I'll help you design a secure API with authentication."),
        ("Use JWT tokens", "JWT tokens are a good choice for stateless auth."),
        ("Add rate limiting", "Rate limiting is essential for API security."),
    ]

    for user_input, agent_response in interactions:
        memory.record_interaction(user_input, agent_response)
        print(f"  ✓ Recorded: '{user_input[:30]}...'")

    # Show memory state
    print("\n[Memory Summary]")
    summary = memory.get_memory_summary()
    for key, value in summary.items():
        if key != "session_id":
            print(f"  • {key}: {value} entries")

    # Show context
    print("\n[Working Memory Context]")
    print(memory.working.get_context()[:200] + "...")

    # Create checkpoint
    checkpoint_id = memory.checkpoint("after_api_design")
    print(f"\n[Checkpoint Created] {checkpoint_id}")

    # Record episode
    memory.record_episode(
        task="Design secure API",
        outcome="Success - designed JWT-based API with rate limiting",
        agents_used=["architect", "reviewer"],
        law_compliance=True,
        lessons_learned=["Always include rate limiting", "JWT is preferred for stateless"],
    )
    print("\n[Episode Recorded] to episodic memory")

    # Add semantic knowledge
    memory.semantic.add_entity(
        "API", "system_component", {"requires_auth": True, "needs_rate_limiting": True}
    )
    memory.semantic.add_fact("JWT", "is_type_of", "authentication_token")
    print("[Semantic Knowledge] Added entity and fact")

    # Learn procedure
    memory.procedural.learn_procedure(
        "design_secure_api",
        ["1. Choose auth mechanism", "2. Add rate limiting", "3. Validate inputs"],
        success_rate=0.9,
    )
    print("[Procedural Memory] Learned workflow")

    print("\n" + "=" * 70)
    print("All memory tiers operational.")
    print("=" * 70)


if __name__ == "__main__":
    main()
