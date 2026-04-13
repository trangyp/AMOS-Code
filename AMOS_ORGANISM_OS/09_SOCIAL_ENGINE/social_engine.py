#!/usr/bin/env python3
"""
AMOS Social Engine (09_SOCIAL_ENGINE)
======================================

Agent communication, coordination, and collective intelligence.
Enables inter-agent messaging, knowledge sharing, and social graphs.

Owner: Trang
Version: 1.0.0
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


@dataclass
class Message:
    """Message between agents."""
    id: str
    sender: str
    recipient: str
    message_type: str
    content: Any
    timestamp: str
    priority: int = 5
    read: bool = False


@dataclass
class SocialConnection:
    """Connection between two agents."""
    agent_a: str
    agent_b: str
    connection_type: str  # collaborates, reports_to, mentors, etc.
    strength: float  # 0.0 to 1.0
    established: str
    last_interaction: str


@dataclass
class KnowledgeShare:
    """Shared knowledge from one agent to others."""
    id: str
    source_agent: str
    knowledge_type: str
    content: Any
    share_scope: str  # team, all, specific_agents
    timestamp: str
    recipients: List[str] = field(default_factory=list)


class SocialEngine:
    """
    Social subsystem - agent communication and coordination.
    Manages messaging, social graphs, and collective intelligence.
    """

    def __init__(self, organism_root: Path) -> None:
        self.root = organism_root
        self.social_dir = organism_root / "09_SOCIAL_ENGINE"
        self.data_dir = self.social_dir / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.messages: List[Message] = []
        self.connections: List[SocialConnection] = []
        self.knowledge_shares: List[KnowledgeShare] = []
        self.agent_presence: Dict[str, str] = {}  # agent_id -> status

        self._load_state()

    def _load_state(self) -> None:
        """Load social state from disk."""
        state_file = self.data_dir / "social_state.json"
        if state_file.exists():
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Load messages
                for msg_data in data.get("messages", []):
                    self.messages.append(Message(**msg_data))

                # Load connections
                for conn_data in data.get("connections", []):
                    self.connections.append(SocialConnection(**conn_data))

                # Load knowledge shares
                for ks_data in data.get("knowledge_shares", []):
                    self.knowledge_shares.append(KnowledgeShare(**ks_data))

            except Exception as e:
                print(f"[SOCIAL] Error loading state: {e}")

    def _save_state(self) -> None:
        """Save social state to disk."""
        state_file = self.data_dir / "social_state.json"

        data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "message_count": len(self.messages),
            "connection_count": len(self.connections),
            "knowledge_share_count": len(self.knowledge_shares),
            "messages": [
                {
                    "id": m.id,
                    "sender": m.sender,
                    "recipient": m.recipient,
                    "message_type": m.message_type,
                    "content": m.content,
                    "timestamp": m.timestamp,
                    "priority": m.priority,
                    "read": m.read
                }
                for m in self.messages[-100:]  # Keep last 100
            ],
            "connections": [
                {
                    "agent_a": c.agent_a,
                    "agent_b": c.agent_b,
                    "connection_type": c.connection_type,
                    "strength": c.strength,
                    "established": c.established,
                    "last_interaction": c.last_interaction
                }
                for c in self.connections
            ],
            "knowledge_shares": [
                {
                    "id": k.id,
                    "source_agent": k.source_agent,
                    "knowledge_type": k.knowledge_type,
                    "content": k.content,
                    "share_scope": k.share_scope,
                    "timestamp": k.timestamp,
                    "recipients": k.recipients
                }
                for k in self.knowledge_shares[-50:]
            ]
        }

        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def send_message(
        self,
        sender: str,
        recipient: str,
        message_type: str,
        content: Any,
        priority: int = 5
    ) -> Message:
        """Send a message from one agent to another."""
        msg = Message(
            id=str(uuid.uuid4())[:8],
            sender=sender,
            recipient=recipient,
            message_type=message_type,
            content=content,
            timestamp=datetime.utcnow().isoformat() + "Z",
            priority=priority,
            read=False
        )

        self.messages.append(msg)

        # Update connection if exists
        self._update_connection(sender, recipient)

        self._save_state()

        print(f"[SOCIAL] Message from {sender} to {recipient}: {message_type}")
        return msg

    def broadcast(
        self,
        sender: str,
        message_type: str,
        content: Any,
        exclude: Optional[Set[str]] = None
    ) -> List[Message]:
        """Broadcast message to all agents."""
        exclude = exclude or set()
        messages = []

        # Get all known agents from connections
        all_agents = set()
        for conn in self.connections:
            all_agents.add(conn.agent_a)
            all_agents.add(conn.agent_b)

        for agent in all_agents:
            if agent != sender and agent not in exclude:
                msg = self.send_message(sender, agent, message_type, content)
                messages.append(msg)

        return messages

    def get_messages(
        self,
        recipient: str,
        unread_only: bool = False,
        message_type: Optional[str] = None
    ) -> List[Message]:
        """Get messages for an agent."""
        msgs = [m for m in self.messages if m.recipient == recipient]

        if unread_only:
            msgs = [m for m in msgs if not m.read]

        if message_type:
            msgs = [m for m in msgs if m.message_type == message_type]

        # Mark as read
        for m in msgs:
            m.read = True

        self._save_state()
        return msgs

    def create_connection(
        self,
        agent_a: str,
        agent_b: str,
        connection_type: str,
        strength: float = 0.5
    ) -> SocialConnection:
        """Create a social connection between agents."""
        # Check if exists
        for conn in self.connections:
            if ((conn.agent_a == agent_a and conn.agent_b == agent_b) or
                (conn.agent_a == agent_b and conn.agent_b == agent_a)):
                # Update existing
                conn.connection_type = connection_type
                conn.strength = strength
                conn.last_interaction = datetime.utcnow().isoformat() + "Z"
                self._save_state()
                return conn

        # Create new
        conn = SocialConnection(
            agent_a=agent_a,
            agent_b=agent_b,
            connection_type=connection_type,
            strength=strength,
            established=datetime.utcnow().isoformat() + "Z",
            last_interaction=datetime.utcnow().isoformat() + "Z"
        )

        self.connections.append(conn)
        self._save_state()

        print(f"[SOCIAL] Connection: {agent_a} <-> {agent_b}")
        print(f"  Type: {connection_type}")
        return conn

    def _update_connection(self, agent_a: str, agent_b: str) -> None:
        """Update connection with new interaction."""
        for conn in self.connections:
            agent_match = (conn.agent_a == agent_a and conn.agent_b == agent_b)
            reverse_match = (conn.agent_a == agent_b and conn.agent_b == agent_a)
            if agent_match or reverse_match:
                conn.last_interaction = datetime.utcnow().isoformat() + "Z"
                # Strengthen connection slightly
                conn.strength = min(1.0, conn.strength + 0.01)
                return

    def share_knowledge(
        self,
        source_agent: str,
        knowledge_type: str,
        content: Any,
        share_scope: str = "team",
        specific_recipients: Optional[List[str]] = None
    ) -> KnowledgeShare:
        """Share knowledge from one agent to others."""
        ks = KnowledgeShare(
            id=str(uuid.uuid4())[:8],
            source_agent=source_agent,
            knowledge_type=knowledge_type,
            content=content,
            share_scope=share_scope,
            timestamp=datetime.utcnow().isoformat() + "Z",
            recipients=specific_recipients or []
        )

        self.knowledge_shares.append(ks)

        # Notify recipients
        if share_scope == "all":
            self.broadcast(
                source_agent,
                "knowledge_share",
                {"knowledge_id": ks.id, "type": knowledge_type},
                exclude={source_agent}
            )
        elif share_scope == "team" and specific_recipients:
            for recipient in specific_recipients:
                self.send_message(
                    source_agent,
                    recipient,
                    "knowledge_share",
                    {"knowledge_id": ks.id, "type": knowledge_type}
                )

        self._save_state()

        print(f"[SOCIAL] Knowledge shared by {source_agent}: {knowledge_type}")
        return ks

    def get_social_graph(self, agent_id: str) -> Dict[str, Any]:
        """Get social graph for an agent."""
        connections = [
            {
                "agent": c.agent_b if c.agent_a == agent_id else c.agent_a,
                "type": c.connection_type,
                "strength": c.strength
            }
            for c in self.connections
            if c.agent_a == agent_id or c.agent_b == agent_id
        ]

        # Get knowledge shared by this agent
        shared = [k for k in self.knowledge_shares if k.source_agent == agent_id]

        # Get messages
        inbox = [m for m in self.messages if m.recipient == agent_id]
        outbox = [m for m in self.messages if m.sender == agent_id]

        return {
            "agent": agent_id,
            "connections": connections,
            "connection_count": len(connections),
            "knowledge_shared": len(shared),
            "messages_received": len(inbox),
            "messages_sent": len(outbox),
            "unread_messages": len([m for m in inbox if not m.read])
        }

    def coordinate_task(
        self,
        task_id: str,
        coordinator: str,
        participants: List[str],
        task_description: str
    ) -> Dict[str, Any]:
        """Coordinate a multi-agent task."""
        # Send coordination messages
        for participant in participants:
            if participant != coordinator:
                self.send_message(
                    coordinator,
                    participant,
                    "task_assignment",
                    {
                        "task_id": task_id,
                        "description": task_description,
                        "role": "participant"
                    },
                    priority=7
                )

        # Create connections if don't exist
        for participant in participants:
            if participant != coordinator:
                self.create_connection(
                    coordinator,
                    participant,
                    "collaborates",
                    0.6
                )

        return {
            "task_id": task_id,
            "coordinator": coordinator,
            "participants": participants,
            "coordination_messages_sent": len(participants) - 1
        }

    def get_status(self) -> Dict[str, Any]:
        """Get social engine status."""
        # Get unique agents
        agents: Set[str] = set()
        for conn in self.connections:
            agents.add(conn.agent_a)
            agents.add(conn.agent_b)

        return {
            "status": "operational",
            "registered_agents": len(agents),
            "total_messages": len(self.messages),
            "total_connections": len(self.connections),
            "knowledge_shares": len(self.knowledge_shares),
            "unread_messages": len([m for m in self.messages if not m.read])
        }


def main() -> int:
    """CLI for Social Engine."""
    print("=" * 50)
    print("AMOS Social Engine (09_SOCIAL_ENGINE)")
    print("=" * 50)

    organism_root = Path(__file__).parent.parent
    engine = SocialEngine(organism_root)

    # Test agent registration
    print("\nCreating test connections...")
    engine.create_connection(
        "planner_agent", "analyst_agent", "collaborates", 0.8
    )
    engine.create_connection(
        "planner_agent", "code_worker", "delegates_to", 0.7
    )
    engine.create_connection(
        "analyst_agent", "auditor_agent", "reports_to", 0.9
    )

    # Test messaging
    print("\nSending test messages...")
    engine.send_message(
        "planner_agent",
        "code_worker",
        "task_request",
        {"task": "Generate Python module", "priority": "high"}
    )

    engine.send_message(
        "analyst_agent",
        "planner_agent",
        "analysis_result",
        {"finding": "Architecture looks good", "confidence": 0.95}
    )

    # Test knowledge sharing
    print("\nSharing knowledge...")
    engine.share_knowledge(
        "analyst_agent",
        "pattern_recognition",
        {
            "pattern": "modular_architecture",
            "benefits": ["scalability", "maintainability"]
        },
        share_scope="all"
    )

    # Get social graphs
    print("\nSocial Graphs:")
    for agent in ["planner_agent", "analyst_agent", "code_worker"]:
        graph = engine.get_social_graph(agent)
        conn_count = graph['connection_count']
        unread = graph['unread_messages']
        print(f"  {agent}: {conn_count} connections, {unread} unread")

    # Show status
    print("\nSocial Engine Status:")
    status = engine.get_status()
    print(f"  Registered agents: {status['registered_agents']}")
    print(f"  Total messages: {status['total_messages']}")
    print(f"  Total connections: {status['total_connections']}")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
