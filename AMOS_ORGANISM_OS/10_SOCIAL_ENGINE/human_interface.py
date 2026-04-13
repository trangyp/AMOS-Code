"""
Human Interface — Human-Computer Interaction Layer

Manages interaction between the organism and human users.
Handles input interpretation, response generation, and context management.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class InteractionMode(Enum):
    """Mode of human interaction."""
    COMMAND = "command"  # Direct commands
    CONVERSATION = "conversation"  # Natural dialogue
    COLLABORATION = "collaboration"  # Working together
    SUPERVISION = "supervision"  # Human oversight


class InputType(Enum):
    """Type of human input."""
    TEXT = "text"
    VOICE = "voice"
    GESTURE = "gesture"
    COMMAND = "command"
    FILE = "file"


@dataclass
class HumanInteraction:
    """A record of human interaction."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    user_id: str = ""
    mode: InteractionMode = InteractionMode.CONVERSATION
    input_type: InputType = InputType.TEXT
    input_content: str = ""
    interpretation: Dict[str, Any] = field(default_factory=dict)
    response: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    feedback: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "mode": self.mode.value,
            "input_type": self.input_type.value,
        }


class HumanInterface:
    """
    Manages interaction between organism and human users.

    Handles input interpretation, maintains interaction context,
    and generates appropriate responses.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path(__file__).parent / "data"
        self.data_dir = data_dir
        self.data_dir.mkdir(exist_ok=True)

        self.interactions: Dict[str, HumanInteraction] = {}
        self.user_profiles: Dict[str, Dict[str, Any]] = {}
        self.current_mode: InteractionMode = InteractionMode.CONVERSATION
        self.active_context: Dict[str, Any] = {}

    def process_input(
        self,
        user_id: str,
        content: str,
        input_type: InputType = InputType.TEXT,
        mode: Optional[InteractionMode] = None,
    ) -> HumanInteraction:
        """Process human input and generate interaction record."""
        interaction = HumanInteraction(
            user_id=user_id,
            mode=mode or self.current_mode,
            input_type=input_type,
            input_content=content,
        )

        # Interpret input based on mode
        interpretation = self._interpret_input(content, interaction.mode)
        interaction.interpretation = interpretation

        # Generate response
        interaction.response = self._generate_response(
            content,
            interpretation,
            interaction.mode,
        )

        # Store interaction
        self.interactions[interaction.id] = interaction

        # Update user profile
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                "first_seen": datetime.utcnow().isoformat(),
                "interaction_count": 0,
                "preferences": {},
            }
        self.user_profiles[user_id]["interaction_count"] += 1
        self.user_profiles[user_id]["last_interaction"] = datetime.utcnow().isoformat()

        self._save_interactions()
        return interaction

    def _interpret_input(
        self,
        content: str,
        mode: InteractionMode,
    ) -> Dict[str, Any]:
        """Interpret human input based on interaction mode."""
        interpretation = {
            "intent": "unknown",
            "entities": [],
            "confidence": 0.5,
        }

        if mode == InteractionMode.COMMAND:
            # Parse as command
            if content.startswith("/") or content.startswith("!"):
                parts = content[1:].split()
                interpretation["intent"] = "command"
                interpretation["command"] = parts[0] if parts else ""
                interpretation["args"] = parts[1:] if len(parts) > 1 else []
                interpretation["confidence"] = 0.9

        elif mode == InteractionMode.CONVERSATION:
            # Natural language interpretation
            question_words = ["what", "how", "why", "when", "where", "who"]
            if any(content.lower().startswith(w) for w in question_words):
                interpretation["intent"] = "question"
                interpretation["confidence"] = 0.8
            elif content.lower().startswith(("can you", "please", "could you")):
                interpretation["intent"] = "request"
                interpretation["confidence"] = 0.8
            else:
                interpretation["intent"] = "statement"
                interpretation["confidence"] = 0.7

        elif mode == InteractionMode.COLLABORATION:
            # Collaboration context
            collaboration_keywords = ["help", "work", "together", "collaborate"]
            if any(kw in content.lower() for kw in collaboration_keywords):
                interpretation["intent"] = "collaboration"
                interpretation["confidence"] = 0.8

        return interpretation

    def _generate_response(
        self,
        input_content: str,
        interpretation: Dict[str, Any],
        mode: InteractionMode,
    ) -> str:
        """Generate response based on interpretation."""
        intent = interpretation.get("intent", "unknown")

        if mode == InteractionMode.COMMAND:
            if intent == "command":
                return f"Executing command: {interpretation.get('command', 'unknown')}"
            return "Command not recognized"

        elif mode == InteractionMode.CONVERSATION:
            if intent == "question":
                return "I understand you're asking a question. Let me provide an answer based on my knowledge."
            elif intent == "request":
                return "I'll help you with that request."
            return "I understand. Please tell me more."

        elif mode == InteractionMode.COLLABORATION:
            return "I'm ready to collaborate with you on this task."

        elif mode == InteractionMode.SUPERVISION:
            return "I'll proceed with your oversight and report back on progress."

        return "I understand your input."

    def set_mode(self, mode: InteractionMode) -> None:
        """Set the current interaction mode."""
        self.current_mode = mode

    def get_user_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get interaction history for a user."""
        user_interactions = [
            i.to_dict() for i in self.interactions.values()
            if i.user_id == user_id
        ]
        user_interactions.sort(key=lambda x: x["timestamp"], reverse=True)
        return user_interactions[:limit]

    def add_feedback(self, interaction_id: str, feedback: str) -> bool:
        """Add feedback to an interaction."""
        interaction = self.interactions.get(interaction_id)
        if not interaction:
            return False

        interaction.feedback = feedback
        self._save_interactions()
        return True

    def _save_interactions(self):
        """Save interactions to disk."""
        interactions_file = self.data_dir / "interactions.json"
        data = {
            "interactions": [i.to_dict() for i in self.interactions.values()],
            "user_profiles": self.user_profiles,
            "saved_at": datetime.utcnow().isoformat(),
        }
        interactions_file.write_text(json.dumps(data, indent=2))

    def list_users(self) -> List[Dict[str, Any]]:
        """List all known users."""
        return [
            {"user_id": uid, **profile}
            for uid, profile in self.user_profiles.items()
        ]

    def get_status(self) -> Dict[str, Any]:
        """Get interface status."""
        return {
            "total_interactions": len(self.interactions),
            "total_users": len(self.user_profiles),
            "current_mode": self.current_mode.value,
            "supported_modes": [m.value for m in InteractionMode],
            "supported_input_types": [t.value for t in InputType],
        }


_INTERFACE: Optional[HumanInterface] = None


def get_human_interface(data_dir: Optional[Path] = None) -> HumanInterface:
    """Get or create global human interface."""
    global _INTERFACE
    if _INTERFACE is None:
        _INTERFACE = HumanInterface(data_dir)
    return _INTERFACE
