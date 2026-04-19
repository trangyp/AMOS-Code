#!/usr/bin/env python3
"""AMOS A2A Protocol Implementation - Agent2Agent Interoperability.

Phase 22: Google's Agent2Agent Protocol for multi-agent systems.
Allows AMOS to communicate with agents from different frameworks/providers.

A2A Protocol Features:
    - Agent Cards: Discovery and capability advertisement
    - Task Management: Send, receive, and track tasks
    - Messaging: Structured communication between agents
    - Streaming: Real-time updates for long-running tasks
    - User Experience: UI hints for agent collaboration

Reference: https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/

Usage:
    # Start A2A Server
    python amos_a2a_protocol.py --mode server --port 8001

    # Connect as Client
    client = A2AClient("http://localhost:8001")
    task = await client.send_task(
        recipient="math-agent",
        message="Calculate the derivative of x^3 + 2x"
    )

Architecture:
    ┌─────────────┐      A2A Protocol       ┌─────────────┐
    │  AMOS Agent │  ←────────────────────→  │ Other Agent │
    │   (Server)  │    (HTTP/JSON)          │  (Client)   │
    └─────────────┘                         └─────────────┘
         ↓                                         ↓
    ┌─────────────┐                         ┌─────────────┐
    │  Agent Card │                         │  Agent Card │
    │ (Discovery) │                         │ (Discovery) │
    └─────────────┘                         └─────────────┘

Author: AMOS Architecture Team
Version: 22.0.0-A2A-PROTOCOL
"""

import asyncio
import json
import uuid
from collections.abc import AsyncIterator
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

try:
    from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
    from fastapi.responses import JSONResponse, StreamingResponse

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

try:
    import httpx

    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


class TaskState(Enum):
    """A2A Task states."""

    SUBMITTED = "submitted"
    WORKING = "working"
    INPUT_REQUIRED = "input_required"
    COMPLETED = "completed"
    CANCELED = "canceled"
    FAILED = "failed"
    UNKNOWN = "unknown"


class MessageRole(Enum):
    """A2A Message roles."""

    USER = "user"
    AGENT = "agent"


class PartType(Enum):
    """A2A Message part types."""

    TEXT = "text"
    FILE = "file"
    DATA = "data"


@dataclass
class AgentSkill:
    """Agent capability/skill definition."""

    id: str
    name: str
    description: str
    tags: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    input_modes: List[str] = field(default_factory=lambda: ["text"])
    output_modes: List[str] = field(default_factory=lambda: ["text"])


@dataclass
class AgentAuthentication:
    """Agent authentication scheme."""

    schemes: List[str] = field(default_factory=lambda: ["none"])
    credentials: str = None


@dataclass
class AgentCard:
    """A2A Agent Card - Discovery and capability advertisement."""

    name: str
    description: str
    url: str
    version: str = "1.0.0"
    authentication: AgentAuthentication = field(default_factory=AgentAuthentication)
    default_input_modes: List[str] = field(default_factory=lambda: ["text"])
    default_output_modes: List[str] = field(default_factory=lambda: ["text"])
    capabilities: Dict[str, bool] = field(default_factory=dict)
    skills: List[AgentSkill] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "url": self.url,
            "version": self.version,
            "authentication": asdict(self.authentication),
            "defaultInputModes": self.default_input_modes,
            "defaultOutputModes": self.default_output_modes,
            "capabilities": self.capabilities,
            "skills": [asdict(s) for s in self.skills],
        }


@dataclass
class TextPart:
    """Text message part."""

    type: str = "text"
    text: str = ""


@dataclass
class FilePart:
    """File message part."""

    type: str = "file"
    name: str = ""
    mime_type: str = ""
    bytes: str = None  # Base64 encoded
    uri: str = None


@dataclass
class DataPart:
    """Structured data message part."""

    type: str = "data"
    data: Dict[str, Any] = field(default_factory=dict)


Part = TextPart | FilePart | DataPart


@dataclass
class Message:
    """A2A Message."""

    role: str
    parts: List[Part] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Task:
    """A2A Task."""

    id: str
    session_id: str
    state: str
    message: Optional[Message] = None
    artifacts: List[Part] = field(default_factory=list)
    history: List[Message] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class TaskStatusUpdate:
    """Task status update event."""

    state: str
    message: Optional[Message] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class A2AAgent:
    """Base class for A2A-compatible agents."""

    def __init__(self, agent_card: AgentCard) -> None:
        self.agent_card = agent_card
        self.tasks: Dict[str, Task] = {}

    async def handle_task(self, task: Task) -> Task:
        """Handle incoming task. Override in subclass."""
        task.state = TaskState.COMPLETED.value
        task.updated_at = datetime.now().isoformat()
        return task

    def get_agent_card(self) -> Dict[str, Any]:
        """Return agent card for discovery."""
        return self.agent_card.to_dict()


class AMOSA2AAgent(A2AAgent):
    """AMOS-specific A2A agent implementation."""

    def __init__(self, base_url: str = "http://localhost:8000") -> None:
        card = AgentCard(
            name="AMOS Equation Agent",
            description="Advanced equation computation and mathematical analysis",
            url=f"{base_url}/a2a",
            version="22.0.0",
            capabilities={
                "streaming": True,
                "pushNotifications": False,
                "stateTransitionHistory": True,
            },
            skills=[
                AgentSkill(
                    id="equation-solve",
                    name="Equation Solving",
                    description="Solve mathematical equations with variable substitution",
                    tags=["math", "equations", "computation"],
                    examples=[
                        "Solve x^2 + 2x + 1 = 0",
                        "Calculate derivative of sin(x)",
                    ],
                ),
                AgentSkill(
                    id="formula-verify",
                    name="Formula Verification",
                    description="Verify mathematical formulas for correctness",
                    tags=["math", "verification", "validation"],
                    examples=["Verify E=mc^2 dimensional analysis"],
                ),
            ],
        )
        super().__init__(card)
        self.base_url = base_url

    async def handle_task(self, task: Task) -> Task:
        """Process equation-related tasks."""
        task.state = TaskState.WORKING.value
        task.updated_at = datetime.now().isoformat()

        # Extract request from message
        if task.message and task.message.parts:
            text_parts = [p for p in task.message.parts if p.type == "text"]
            if text_parts:
                query = text_parts[0].text

                # Simulate equation processing
                await asyncio.sleep(0.5)

                # Create response
                result_part = TextPart(
                    text=f"AMOS processed: '{query}'\n\n"
                    f"Result: 42.0\n"
                    f"Confidence: 0.95\n"
                    f"Method: equation_registry.solve()"
                )

                task.artifacts.append(result_part)
                task.state = TaskState.COMPLETED.value

        task.updated_at = datetime.now().isoformat()
        return task


if FASTAPI_AVAILABLE:

    def create_a2a_server(agent: A2AAgent) -> FastAPI:
        """Create FastAPI app with A2A endpoints."""
        app = FastAPI(title="A2A Server", version="1.0.0")

        @app.get("/.well-known/agent.json")
        async def agent_card() -> JSONResponse:
            """Agent Card discovery endpoint."""
            return JSONResponse(agent.get_agent_card())

        @app.post("/tasks/send")
        async def send_task(request: Request) -> JSONResponse:
            """Send task to agent (blocking)."""
            body = await request.json()

            task = Task(
                id=str(uuid.uuid4()),
                session_id=body.get("sessionId", str(uuid.uuid4())),
                state=TaskState.SUBMITTED.value,
                message=Message(
                    role=body.get("message", {}).get("role", "user"),
                    parts=[
                        TextPart(text=p.get("text", ""))
                        for p in body.get("message", {}).get("parts", [])
                    ],
                ),
            )

            result = await agent.handle_task(task)
            return JSONResponse(
                {
                    "id": result.id,
                    "sessionId": result.session_id,
                    "state": result.state,
                    "message": asdict(result.message) if result.message else None,
                    "artifacts": [asdict(a) for a in result.artifacts],
                }
            )

        @app.post("/tasks/sendSubscribe")
        async def send_subscribe(request: Request) -> StreamingResponse:
            """Send task with streaming updates."""

            async def event_stream() -> AsyncIterator[str]:
                body = await request.json()

                task = Task(
                    id=str(uuid.uuid4()),
                    session_id=body.get("sessionId", str(uuid.uuid4())),
                    state=TaskState.SUBMITTED.value,
                )

                # Stream status updates
                yield f"data: {json.dumps({'state': TaskState.WORKING.value})}\n\n"
                await asyncio.sleep(0.1)

                result = await agent.handle_task(task)
                yield f"data: {json.dumps({'state': result.state})}\n\n"

            return StreamingResponse(
                event_stream(),
                media_type="text/event-stream",
            )

        @app.get("/tasks/{task_id}")
        async def get_task(task_id: str) -> JSONResponse:
            """Get task status."""
            if task_id in agent.tasks:
                task = agent.tasks[task_id]
                return JSONResponse(
                    {
                        "id": task.id,
                        "state": task.state,
                        "artifacts": [asdict(a) for a in task.artifacts],
                    }
                )
            raise HTTPException(status_code=404, detail="Task not found")

        @app.post("/tasks/{task_id}/cancel")
        async def cancel_task(task_id: str) -> JSONResponse:
            """Cancel running task."""
            if task_id in agent.tasks:
                agent.tasks[task_id].state = TaskState.CANCELED.value
                return JSONResponse({"success": True})
            raise HTTPException(status_code=404, detail="Task not found")

        return app


if HTTPX_AVAILABLE:

    class A2AClient:
        """A2A Protocol client."""

        def __init__(self, agent_url: str) -> None:
            self.agent_url = agent_url
            self.client = httpx.AsyncClient()
            self._agent_card: Dict[str, Any] = None

        async def discover(self) -> Dict[str, Any]:
            """Fetch agent card."""
            response = await self.client.get(f"{self.agent_url}/.well-known/agent.json")
            self._agent_card = response.json()
            return self._agent_card

        async def send_task(
            self,
            message: str,
            session_id: str = None,
        ) -> Dict[str, Any]:
            """Send task to agent."""
            payload: Dict[str, Any] = {
                "message": {
                    "role": "user",
                    "parts": [{"type": "text", "text": message}],
                },
            }
            if session_id:
                payload["sessionId"] = session_id

            response = await self.client.post(
                f"{self.agent_url}/tasks/send",
                json=payload,
            )
            return response.json()

        async def stream_task(
            self,
            message: str,
        ) -> AsyncIterator[dict[str, Any]]:
            """Send task with streaming."""
            payload = {
                "message": {
                    "role": "user",
                    "parts": [{"type": "text", "text": message}],
                },
            }

            async with self.client.stream(
                "POST",
                f"{self.agent_url}/tasks/sendSubscribe",
                json=payload,
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        yield json.loads(line[6:])

        async def close(self) -> None:
            await self.client.aclose()


async def demo() -> None:
    """Demonstrate A2A protocol."""

    import uvicorn

    # Create AMOS agent
    agent = AMOSA2AAgent()

    # Create server
    if FASTAPI_AVAILABLE:
        app = create_a2a_server(agent)

        # Run server
        config = uvicorn.Config(app, host="0.0.0.0", port=8001, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()


if __name__ == "__main__":
    if not FASTAPI_AVAILABLE:
        print("FastAPI required: pip install fastapi uvicorn")
        exit(1)

    asyncio.run(demo())
