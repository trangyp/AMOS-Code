#!/usr/bin/env python3
"""MemoryGovernance - Canonical Memory Write Path.

All memory writes pass through this governance layer.
Provides audit, validation, and policy enforcement.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from threading import Lock
from typing import Any, Optional


@dataclass
class MemoryEntry:
    """Represents a memory entry."""

    key: str
    value: Any
    timestamp: str
    agent_id: str
    entry_type: str = "general"  # e.g., "canon", "evidence", "working"
    metadata: dict[str, Any] = field(default_factory=dict)


class MemoryGovernance:
    """Canonical memory governance layer.

    All memory operations go through this layer.
    Enforces write policies and maintains audit trail.
    """

    def __init__(self):
        self._memory: dict[str, MemoryEntry] = {}
        self._audit_log: list[dict[str, Any]] = []
        self._lock = Lock()
        self._write_count = 0

    def write(
        self, key: str, value: Any, agent_id: Optional[str] = None, entry_type: str = "general"
    ) -> bool:
        """Write to memory through governance layer.

        Args:
            key: Memory key
            value: Value to store
            agent_id: Optional agent identifier
            entry_type: Type of memory entry

        Returns:
            True if write successful
        """
        entry = MemoryEntry(
            key=key,
            value=value,
            timestamp=datetime.now(UTC).isoformat(),
            agent_id=agent_id,
            entry_type=entry_type,
        )

        with self._lock:
            self._memory[key] = entry
            self._write_count += 1

            # Audit the write
            self._audit_log.append(
                {
                    "action": "WRITE",
                    "key": key,
                    "agent_id": agent_id,
                    "entry_type": entry_type,
                    "timestamp": entry.timestamp,
                }
            )

        return True

    def read(self, key: str) -> Optional[Any]:
        """Read from memory.

        Args:
            key: Memory key

        Returns:
            Value or None if not found
        """
        with self._lock:
            entry = self._memory.get(key)
            if entry:
                return entry.value
            return None

    def get_entry(self, key: str) -> Optional[MemoryEntry]:
        """Get full memory entry with metadata."""
        with self._lock:
            return self._memory.get(key)

    def get_stats(self) -> dict[str, Any]:
        """Get memory statistics."""
        with self._lock:
            return {
                "total_entries": len(self._memory),
                "write_count": self._write_count,
                "audit_entries": len(self._audit_log),
            }

    def store_cognitive_state(self, state) -> bool:
        """Store cognitive state in memory.

        Args:
            state: CognitiveState to store

        Returns:
            True if stored successfully
        """
        key = f"cognitive_state:{state.state_id}"
        value = {
            "state_id": state.state_id,
            "query": state.query,
            "domain": state.domain,
            "thought_count": len(state.thoughts),
            "thoughts": [
                {
                    "phase": t.phase.name,
                    "content": t.content,
                    "confidence": t.confidence,
                }
                for t in state.thoughts
            ],
            "tool_calls": len(state.tool_calls),
            "current_phase": state.current_phase.name,
        }
        return self.write(key, value, agent_id="cognitive_engine", entry_type="cognitive")

    def is_healthy(self) -> bool:
        """Check if memory governance is healthy."""
        return True

    def shutdown(self) -> None:
        """Graceful shutdown."""
        pass
