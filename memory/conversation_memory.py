"""
AMOS Conversation Memory System
Integrates with cognitive chat to provide multi-turn coherence.

Uses sliding window approach (last N exchanges) to maintain context
while staying within token limits.
"""

import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ConversationMessage:
    """Single message in conversation history."""

    role: str  # "user" or "assistant"
    content: str
    timestamp: str
    biological_context: Dict[str, Any] = None
    ui_guidelines: Dict[str, Any] = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "ConversationMessage":
        return cls(**data)


@dataclass
class ConversationSession:
    """Complete conversation session."""

    session_id: str
    title: str
    created_at: str
    updated_at: str
    messages: List[ConversationMessage]
    biological_state_summary: Dict[str, Any] = None

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "title": self.title,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "messages": [m.to_dict() for m in self.messages],
            "biological_state_summary": self.biological_state_summary,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ConversationSession":
        messages = [ConversationMessage.from_dict(m) for m in data.get("messages", [])]
        return cls(
            session_id=data["session_id"],
            title=data["title"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            messages=messages,
            biological_state_summary=data.get("biological_state_summary"),
        )


class ConversationMemoryManager:
    """
    Manages conversation memory with sliding window approach.

    Features:
    - Buffer window (configurable, default 6 exchanges)
    - Session persistence (JSON file storage)
    - Automatic title generation from first message
    - Biological state tracking across conversation
    """

    def __init__(self, storage_dir: str = "amos_conversations"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.buffer_window = 6  # Last 6 exchanges (12 messages)

    def create_session(self, title: str = None) -> ConversationSession:
        """Create new conversation session."""
        session_id = str(uuid.uuid4())[:8]
        now = datetime.now(UTC).isoformat()

        session = ConversationSession(
            session_id=session_id,
            title=title or f"Conversation {session_id}",
            created_at=now,
            updated_at=now,
            messages=[],
        )

        self._save_session(session)
        return session

    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """Retrieve conversation session by ID."""
        session_file = self.storage_dir / f"{session_id}.json"

        if not session_file.exists():
            return None

        try:
            with open(session_file) as f:
                data = json.load(f)
            return ConversationSession.from_dict(data)
        except Exception as e:
            print(f"Error loading session {session_id}: {e}")
            return None

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        biological_context: Dict[str, Any] = None,
        ui_guidelines: Dict[str, Any] = None,
    ) -> Optional[ConversationMessage]:
        """Add message to conversation and update session."""
        session = self.get_session(session_id)
        if not session:
            return None

        # Create message
        message = ConversationMessage(
            role=role,
            content=content,
            timestamp=datetime.now(UTC).isoformat(),
            biological_context=biological_context,
            ui_guidelines=ui_guidelines,
        )

        # Add to session
        session.messages.append(message)
        session.updated_at = datetime.now(UTC).isoformat()

        # Update title if first user message
        if role == "user" and len(session.messages) == 1:
            session.title = self._generate_title(content)

        # Update biological state summary
        if biological_context:
            session.biological_state_summary = self._update_bio_summary(
                session.biological_state_summary, biological_context
            )

        self._save_session(session)
        return message

    def get_context_window(self, session_id: str, window_size: int = None) -> List[dict[str, str]]:
        """
        Get recent conversation context for LLM prompt.

        Returns list of {role, content} dicts for the last N exchanges.
        """
        session = self.get_session(session_id)
        if not session:
            return []

        window = window_size or self.buffer_window * 2  # user + assistant pairs
        recent_messages = session.messages[-window:]

        return [{"role": msg.role, "content": msg.content} for msg in recent_messages]

    def get_all_sessions(self) -> List[ConversationSession]:
        """Get all conversation sessions, sorted by most recent."""
        sessions = []

        for session_file in self.storage_dir.glob("*.json"):
            try:
                with open(session_file) as f:
                    data = json.load(f)
                sessions.append(ConversationSession.from_dict(data))
            except Exception as e:
                print(f"Error loading session file {session_file}: {e}")

        # Sort by updated_at descending
        sessions.sort(key=lambda s: s.updated_at, reverse=True)
        return sessions

    def delete_session(self, session_id: str) -> bool:
        """Delete conversation session."""
        session_file = self.storage_dir / f"{session_id}.json"

        if session_file.exists():
            session_file.unlink()
            return True
        return False

    def _save_session(self, session: ConversationSession):
        """Persist session to disk."""
        session_file = self.storage_dir / f"{session.session_id}.json"

        with open(session_file, "w") as f:
            json.dump(session.to_dict(), f, indent=2)

    def _generate_title(self, first_message: str, max_length: int = 40) -> str:
        """Generate conversation title from first message."""
        # Truncate and clean
        title = first_message.strip()
        if len(title) > max_length:
            title = title[: max_length - 3] + "..."
        return title

    def _update_bio_summary(self, current_summary: Dict[str, Any], new_context: dict) -> dict:
        """Update biological state summary across conversation."""
        if not current_summary:
            return new_context

        # Simple approach: track changes
        summary = current_summary.copy()

        # Update with new values
        for key in ["cognitive_load", "emotional_state", "body_comfort", "environmental_fit"]:
            if key in new_context:
                # Track the most recent state
                summary[f"latest_{key}"] = new_context[key]

        return summary


# Global instance
_conversation_memory = None


def get_conversation_memory() -> ConversationMemoryManager:
    """Get global conversation memory manager."""
    global _conversation_memory
    if _conversation_memory is None:
        _conversation_memory = ConversationMemoryManager()
    return _conversation_memory
