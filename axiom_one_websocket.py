"""Axiom One WebSocket Streaming

Real-time WebSocket streaming for repo autopsy progress and agent execution.
Integrates with FastAPI WebSocket endpoints.
"""

from __future__ import annotations

import asyncio
import json
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

UTC = UTC
from enum import Enum
from typing import Any, Optional


class StreamEventType(Enum):
    """Types of stream events."""

    AUTOPSY_START = "autopsy_start"
    AUTOPSY_STEP = "autopsy_step"
    AUTOPSY_ISSUE = "autopsy_issue"
    AUTOPSY_COMPLETE = "autopsy_complete"
    AUTOPSY_ERROR = "autopsy_error"
    AGENT_START = "agent_start"
    AGENT_STEP = "agent_step"
    AGENT_COMPLETE = "agent_complete"
    AGENT_ERROR = "agent_error"
    FIX_GENERATED = "fix_generated"
    FIX_APPLIED = "fix_applied"
    SYSTEM_LOG = "system_log"


@dataclass
class StreamEvent:
    """A streaming event for WebSocket clients."""

    event_id: str
    event_type: str
    timestamp: str
    payload: dict[str, Any]
    session_id: str


class AxiomOneStreamManager:
    """Manages WebSocket connections and event streaming for Axiom One."""

    def __init__(self):
        self._connections: dict[str, Any] = {}
        self._session_subscribers: dict[str, set[str]] = {}
        self._event_history: dict[str, list[StreamEvent]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, websocket: Any, session_id: str) -> str:
        """Register a new WebSocket connection."""
        connection_id = str(uuid.uuid4())
        async with self._lock:
            self._connections[connection_id] = {
                "websocket": websocket,
                "session_id": session_id,
                "connected_at": datetime.now(UTC).isoformat(),
            }
            if session_id not in self._session_subscribers:
                self._session_subscribers[session_id] = set()
            self._session_subscribers[session_id].add(connection_id)
        return connection_id

    async def disconnect(self, connection_id: str) -> None:
        """Remove a WebSocket connection."""
        async with self._lock:
            if connection_id in self._connections:
                session_id = self._connections[connection_id]["session_id"]
                del self._connections[connection_id]
                if session_id in self._session_subscribers:
                    self._session_subscribers[session_id].discard(connection_id)

    async def broadcast_to_session(self, session_id: str, event: StreamEvent) -> int:
        """Broadcast event to all subscribers of a session."""
        sent_count = 0
        async with self._lock:
            subscribers = self._session_subscribers.get(session_id, set()).copy()
            # Store in history
            if session_id not in self._event_history:
                self._event_history[session_id] = []
            self._event_history[session_id].append(event)
            # Keep only last 1000 events
            if len(self._event_history[session_id]) > 1000:
                self._event_history[session_id] = self._event_history[session_id][-1000:]

        for conn_id in subscribers:
            if conn_id in self._connections:
                try:
                    ws = self._connections[conn_id]["websocket"]
                    await ws.send_text(
                        json.dumps(
                            {
                                "event_id": event.event_id,
                                "event_type": event.event_type,
                                "timestamp": event.timestamp,
                                "payload": event.payload,
                            }
                        )
                    )
                    sent_count += 1
                except Exception:
                    pass
        return sent_count

    def create_autopsy_start_event(
        self, session_id: str, repo_path: str, repo_name: str
    ) -> StreamEvent:
        """Create autopsy start event."""
        return StreamEvent(
            event_id=str(uuid.uuid4()),
            event_type=StreamEventType.AUTOPSY_START.value,
            timestamp=datetime.now(UTC).isoformat(),
            payload={
                "repo_path": repo_path,
                "repo_name": repo_name,
                "message": f"Starting autopsy for {repo_name}",
            },
            session_id=session_id,
        )

    def create_autopsy_step_event(
        self,
        session_id: str,
        step: str,
        status: str,
        progress: float,
        details: dict[str, Any] = None,
    ) -> StreamEvent:
        """Create autopsy step progress event."""
        return StreamEvent(
            event_id=str(uuid.uuid4()),
            event_type=StreamEventType.AUTOPSY_STEP.value,
            timestamp=datetime.now(UTC).isoformat(),
            payload={
                "step": step,
                "status": status,
                "progress": progress,
                "details": details or {},
            },
            session_id=session_id,
        )

    def create_autopsy_issue_event(
        self,
        session_id: str,
        issue: dict[str, Any],
        severity: str,
    ) -> StreamEvent:
        """Create autopsy issue found event."""
        return StreamEvent(
            event_id=str(uuid.uuid4()),
            event_type=StreamEventType.AUTOPSY_ISSUE.value,
            timestamp=datetime.now(UTC).isoformat(),
            payload={
                "issue": issue,
                "severity": severity,
            },
            session_id=session_id,
        )

    def create_autopsy_complete_event(
        self,
        session_id: str,
        total_issues: int,
        duration_ms: float,
        summary: dict[str, Any],
    ) -> StreamEvent:
        """Create autopsy complete event."""
        return StreamEvent(
            event_id=str(uuid.uuid4()),
            event_type=StreamEventType.AUTOPSY_COMPLETE.value,
            timestamp=datetime.now(UTC).isoformat(),
            payload={
                "total_issues": total_issues,
                "duration_ms": duration_ms,
                "summary": summary,
            },
            session_id=session_id,
        )

    def create_agent_start_event(self, session_id: str, agent_id: str, goal: str) -> StreamEvent:
        """Create agent execution start event."""
        return StreamEvent(
            event_id=str(uuid.uuid4()),
            event_type=StreamEventType.AGENT_START.value,
            timestamp=datetime.now(UTC).isoformat(),
            payload={
                "agent_id": agent_id,
                "goal": goal,
            },
            session_id=session_id,
        )

    def create_agent_step_event(
        self,
        session_id: str,
        agent_id: str,
        step_number: int,
        total_steps: int,
        action: str,
        status: str,
    ) -> StreamEvent:
        """Create agent step progress event."""
        return StreamEvent(
            event_id=str(uuid.uuid4()),
            event_type=StreamEventType.AGENT_STEP.value,
            timestamp=datetime.now(UTC).isoformat(),
            payload={
                "agent_id": agent_id,
                "step_number": step_number,
                "total_steps": total_steps,
                "action": action,
                "status": status,
                "progress": step_number / total_steps if total_steps > 0 else 0,
            },
            session_id=session_id,
        )

    def create_fix_generated_event(
        self,
        session_id: str,
        issue_id: str,
        fix_type: str,
        description: str,
    ) -> StreamEvent:
        """Create fix generated event."""
        return StreamEvent(
            event_id=str(uuid.uuid4()),
            event_type=StreamEventType.FIX_GENERATED.value,
            timestamp=datetime.now(UTC).isoformat(),
            payload={
                "issue_id": issue_id,
                "fix_type": fix_type,
                "description": description,
            },
            session_id=session_id,
        )

    def get_event_history(self, session_id: str, limit: int = 100) -> list[StreamEvent]:
        """Get recent event history for a session."""
        events = self._event_history.get(session_id, [])
        return events[-limit:] if len(events) > limit else events


# Global stream manager instance
_stream_manager: Optional[AxiomOneStreamManager] = None


def get_stream_manager() -> AxiomOneStreamManager:
    """Get or create global stream manager."""
    global _stream_manager
    if _stream_manager is None:
        _stream_manager = AxiomOneStreamManager()
    return _stream_manager
