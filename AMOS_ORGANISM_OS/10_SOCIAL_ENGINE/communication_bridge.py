"""
Communication Bridge — External Communication Handler

Manages communication with external systems, agents, and services.
Handles message routing, protocol adaptation, and connection management.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class MessageType(Enum):
    """Type of message."""
    REQUEST = "request"
    RESPONSE = "response"
    EVENT = "event"
    COMMAND = "command"
    STATUS = "status"
    ERROR = "error"


class MessagePriority(Enum):
    """Priority level for messages."""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


@dataclass
class Message:
    """A message for external communication."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    msg_type: MessageType = MessageType.REQUEST
    priority: MessagePriority = MessagePriority.NORMAL
    sender: str = ""
    recipient: str = ""
    content: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    replied_to: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "msg_type": self.msg_type.value,
            "priority": self.priority.value,
        }


class CommunicationBridge:
    """
    Manages external communication for the organism.

    Handles message routing, protocol management, and
    connection tracking for multi-agent coordination.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path(__file__).parent / "data"
        self.data_dir = data_dir
        self.data_dir.mkdir(exist_ok=True)

        self.connections: Dict[str, Dict[str, Any]] = {}
        self.message_queue: List[Message] = []
        self.sent_messages: List[Message] = []
        self.received_messages: List[Message] = []
        self.protocols: Dict[str, Dict[str, Any]] = {}

        self._init_default_protocols()

    def _init_default_protocols(self):
        """Initialize default communication protocols."""
        self.protocols = {
            "internal": {
                "description": "Internal AMOS organism communication",
                "format": "json",
                "auth_required": False,
            },
            "http": {
                "description": "HTTP/REST API communication",
                "format": "json",
                "auth_required": True,
            },
            "websocket": {
                "description": "Real-time bidirectional communication",
                "format": "json",
                "auth_required": True,
            },
            "mcp": {
                "description": "Model Context Protocol",
                "format": "jsonrpc",
                "auth_required": True,
            },
        }

    def register_connection(
        self,
        connection_id: str,
        protocol: str,
        endpoint: str,
        credentials: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Register a new external connection."""
        if protocol not in self.protocols:
            return False

        self.connections[connection_id] = {
            "protocol": protocol,
            "endpoint": endpoint,
            "credentials": credentials or {},
            "status": "connected",
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
        }
        return True

    def send_message(
        self,
        recipient: str,
        content: Dict[str, Any],
        msg_type: MessageType = MessageType.REQUEST,
        priority: MessagePriority = MessagePriority.NORMAL,
        reply_to: Optional[str] = None,
    ) -> Message:
        """Send a message to an external recipient."""
        message = Message(
            msg_type=msg_type,
            priority=priority,
            sender="amos_organism",
            recipient=recipient,
            content=content,
            replied_to=reply_to,
        )

        self.sent_messages.append(message)

        # Update connection activity
        if recipient in self.connections:
            self.connections[recipient]["last_activity"] = datetime.utcnow().isoformat()

        self._save_messages()
        return message

    def receive_message(self, sender: str, content: Dict[str, Any]) -> Message:
        """Receive a message from an external sender."""
        message = Message(
            msg_type=MessageType.EVENT,
            sender=sender,
            recipient="amos_organism",
            content=content,
        )

        self.received_messages.append(message)

        # Update connection activity
        if sender in self.connections:
            self.connections[sender]["last_activity"] = datetime.utcnow().isoformat()

        self._save_messages()
        return message

    def broadcast(
        self,
        content: Dict[str, Any],
        msg_type: MessageType = MessageType.EVENT,
    ) -> List[Message]:
        """Broadcast a message to all connected recipients."""
        messages = []
        for connection_id in self.connections.keys():
            msg = self.send_message(connection_id, content, msg_type)
            messages.append(msg)
        return messages

    def get_pending_messages(self) -> List[Dict[str, Any]]:
        """Get messages awaiting processing."""
        # In a real implementation, this would filter unprocessed messages
        return [m.to_dict() for m in self.received_messages[-10:]]

    def get_message_history(
        self,
        recipient: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get message history."""
        messages = self.sent_messages + self.received_messages
        if recipient:
            messages = [m for m in messages if m.recipient == recipient or m.sender == recipient]

        # Sort by timestamp
        messages.sort(key=lambda m: m.timestamp, reverse=True)
        return [m.to_dict() for m in messages[:limit]]

    def _save_messages(self):
        """Save message history to disk."""
        messages_file = self.data_dir / "messages.json"
        data = {
            "sent": [m.to_dict() for m in self.sent_messages[-100:]],
            "received": [m.to_dict() for m in self.received_messages[-100:]],
            "saved_at": datetime.utcnow().isoformat(),
        }
        messages_file.write_text(json.dumps(data, indent=2))

    def get_connection_status(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a connection."""
        return self.connections.get(connection_id)

    def list_connections(self) -> List[Dict[str, Any]]:
        """List all registered connections."""
        return [
            {"id": cid, **info}
            for cid, info in self.connections.items()
        ]

    def get_status(self) -> Dict[str, Any]:
        """Get bridge status."""
        return {
            "active_connections": len(self.connections),
            "total_sent": len(self.sent_messages),
            "total_received": len(self.received_messages),
            "supported_protocols": list(self.protocols.keys()),
            "connection_statuses": {
                cid: info["status"]
                for cid, info in self.connections.items()
            },
        }


_BRIDGE: Optional[CommunicationBridge] = None


def get_communication_bridge(data_dir: Optional[Path] = None) -> CommunicationBridge:
    """Get or create global communication bridge."""
    global _BRIDGE
    if _BRIDGE is None:
        _BRIDGE = CommunicationBridge(data_dir)
    return _BRIDGE
