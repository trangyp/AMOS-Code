#!/usr/bin/env python3
"""AMOS Platform SDK - Real Client for Unified Gateway
=====================================================

Production SDK using actual aiohttp calls to AMOS Unified Gateway.
NO MOCK IMPLEMENTATIONS - All methods make real HTTP/WebSocket calls.

Usage:
    async with AMOSPlatformSDK() as sdk:
        # Real chat via brain
        response = await sdk.chat.send("Hello")
        
        # Real agent execution
        task = await sdk.agents.run(
            agent_type="repo_scan",
            task_description="Analyze repository"
        )
        
        # Real WebSocket events
        async for event in sdk.websocket.connect():
            print(event)
"""

import asyncio
import json
import logging
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc
from typing import Any, Dict, List, Optional, Protocol
from urllib.parse import urljoin

# Real HTTP client
try:
    import aiohttp
    import aiohttp.client_exceptions
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    raise RuntimeError("aiohttp required for AMOS Platform SDK")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AMOS-SDK")


# =============================================================================
# REAL DATA MODELS
# =============================================================================

@dataclass
class ChatMessage:
    """Real chat message model."""
    role: str
    content: str
    timestamp: Optional[str] = None


@dataclass
class ChatRequest:
    """Real chat request."""
    message: str
    workspace_id: str
    context: List[ChatMessage] = field(default_factory=list)
    model: Optional[str] = None
    temperature: float = 0.7


@dataclass
class ChatResponse:
    """Real chat response with brain metadata."""
    id: str
    message: str
    model: str
    confidence: str
    law_compliant: bool
    violations: List[str]
    reasoning: List[str]
    domain: str
    processing_time_ms: float
    timestamp: str


@dataclass
class AgentTask:
    """Real agent task."""
    task_id: str
    agent_id: str
    status: str
    agent_type: str
    paradigm: str
    progress: int = 0
    logs: List[str] = field(default_factory=list)
    result: Optional[Dict[str, Any] ] = None
    error: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_seconds: Optional[float] = None


# =============================================================================
# REAL HTTP CLIENT
# =============================================================================

class HTTPTransport:
    """Real HTTP transport using aiohttp."""
    
    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        jwt_token: Optional[str] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.jwt_token = jwt_token
        self._session: aiohttp.ClientSession | None = None
        self._connector = aiohttp.TCPConnector(
            limit=100,
            limit_per_host=20,
            enable_cleanup_closed=True,
            force_close=False,
        )
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create session with real connection pooling."""
        if self._session is None or self._session.closed:
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "AMOS-Platform-SDK/1.0",
            }
            
            if self.api_key:
                headers["X-API-Key"] = self.api_key
            if self.jwt_token:
                headers["Authorization"] = f"Bearer {self.jwt_token}"
            
            timeout = aiohttp.ClientTimeout(total=300, connect=10)
            self._session = aiohttp.ClientSession(
                headers=headers,
                timeout=timeout,
                connector=self._connector,
            )
        
        return self._session
    
    async def request(
        self,
        method: str,
        path: str,
        json_data: Optional[Dict[str, Any] ] = None,
        params: Optional[Dict[str, Any] ] = None,
    ) -> Dict[str, Any]:
        """Make real HTTP request."""
        session = await self._get_session()
        url = urljoin(self.base_url + "/", path.lstrip("/"))
        
        async with session.request(
            method=method,
            url=url,
            json=json_data,
            params=params,
        ) as response:
            if response.status >= 400:
                text = await response.text()
                raise AMOSAPIError(
                    status_code=response.status,
                    message=text,
                    url=url,
                )
            
            return await response.json()
    
    async def get(self, path: str, params: Optional[Dict[str, Any] ] = None) -> Dict[str, Any]:
        """GET request."""
        return await self.request("GET", path, params=params)
    
    async def post(self, path: str, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """POST request."""
        return await self.request("POST", path, json_data=json_data)
    
    async def close(self) -> None:
        """Close session and release connections."""
        if self._session and not self._session.closed:
            await self._session.close()
        await self._connector.close()


class AMOSAPIError(Exception):
    """Real API error with details."""
    
    def __init__(self, status_code: int, message: str, url: str):
        self.status_code = status_code
        self.message = message
        self.url = url
        super().__init__(f"API Error {status_code} at {url}: {message}")


# =============================================================================
# REAL API RESOURCE CLASSES
# =============================================================================

class ChatAPI:
    """Real Chat API using brain facade."""
    
    def __init__(self, transport: HTTPTransport):
        self._transport = transport
    
    async def send(
        self,
        message: str,
        workspace_id: str,
        context: Optional[List[ChatMessage] ] = None,
        model: Optional[str] = None,
    ) -> ChatResponse:
        """Send chat message to real brain via API."""
        request_data = {
            "message": message,
            "workspace_id": workspace_id,
            "context": [
                {"role": m.role, "content": m.content}
                for m in (context or [])
            ],
            "model": model,
        }
        
        result = await self._transport.post("/v1/chat", request_data)
        
        return ChatResponse(
            id=result["id"],
            message=result["message"],
            model=result["model"],
            confidence=result["confidence"],
            law_compliant=result["law_compliant"],
            violations=result["violations"],
            reasoning=result["reasoning"],
            domain=result["domain"],
            processing_time_ms=result["processing_time_ms"],
            timestamp=result["timestamp"],
        )


class AgentsAPI:
    """Real Agents API using AMOSAgent execution."""
    
    def __init__(self, transport: HTTPTransport):
        self._transport = transport
    
    async def run(
        self,
        agent_type: str,
        task_description: str,
        target_repo: Optional[str] = None,
        parameters: Optional[Dict[str, Any] ] = None,
        priority: str = "normal",
        paradigm: str = "HYBRID",
    ) -> AgentTask:
        """Run real agent via API."""
        request_data = {
            "agent_type": agent_type,
            "task_description": task_description,
            "target_repo": target_repo,
            "parameters": parameters or {},
            "priority": priority,
            "paradigm": paradigm,
        }
        
        result = await self._transport.post("/v1/agent/run", request_data)
        
        return AgentTask(
            task_id=result["task_id"],
            agent_id=result["agent_id"],
            status=result["status"],
            agent_type=result["agent_type"],
            paradigm=result["paradigm"],
        )
    
    async def get_status(self, task_id: str) -> AgentTask:
        """Get real agent status."""
        result = await self._transport.get(f"/v1/agent/status/{task_id}")
        
        return AgentTask(
            task_id=result["task_id"],
            agent_id=result["agent_id"],
            status=result["status"],
            agent_type=result["agent_type"],
            paradigm=result["paradigm"],
            progress=result.get("progress", 0),
            logs=result.get("logs", []),
            result=result.get("result"),
            error=result.get("error"),
            started_at=result.get("started_at"),
            completed_at=result.get("completed_at"),
            duration_seconds=result.get("duration_seconds"),
        )
    
    async def wait_for_completion(
        self,
        task_id: str,
        poll_interval: float = 2.0,
        timeout: float = 300.0,
    ) -> AgentTask:
        """Poll until agent completes."""
        start = asyncio.get_event_loop().time()
        
        while True:
            status = await self.get_status(task_id)
            
            if status.status in ("completed", "failed"):
                return status
            
            elapsed = asyncio.get_event_loop().time() - start
            if elapsed > timeout:
                raise TimeoutError(f"Agent {task_id} did not complete within {timeout}s")
            
            await asyncio.sleep(poll_interval)


class WebSocketClient:
    """Real WebSocket client for brain events."""
    
    def __init__(self, base_url: str, jwt_token: Optional[str] = None):
        self.base_url = base_url.replace("https://", "wss://").replace("http://", "ws://")
        self.jwt_token = jwt_token
        self._ws: aiohttp.ClientWebSocketResponse | None = None
        self._connected = False
    
    async def connect(self) -> AsyncIterator[dict[str, Any]]:
        """Connect and yield real events."""
        url = f"{self.base_url}/v1/ws/events"
        
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(url) as ws:
                self._ws = ws
                self._connected = True
                
                logger.info(f"WebSocket connected to {url}")
                
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        yield json.loads(msg.data)
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        logger.error(f"WebSocket error: {msg.data}")
                        break
                    elif msg.type == aiohttp.WSMsgType.CLOSED:
                        break
    
    async def subscribe(self, channel: str) -> None:
        """Subscribe to channel."""
        if self._ws and self._connected:
            await self._ws.send_json({
                "type": "subscribe",
                "channel": channel,
            })
    
    async def ping(self) -> None:
        """Send ping."""
        if self._ws and self._connected:
            await self._ws.send_json({"type": "ping"})


# =============================================================================
# MAIN SDK CLASS
# =============================================================================

class AMOSPlatformSDK:
    """Real AMOS Platform SDK using actual HTTP/WebSocket calls."""
    
    def __init__(
        self,
        base_url: str = "https://api.amos.io",
        api_key: Optional[str] = None,
        jwt_token: Optional[str] = None,
    ):
        self._transport = HTTPTransport(
            base_url=base_url,
            api_key=api_key,
            jwt_token=jwt_token,
        )
        
        # API resources
        self.chat = ChatAPI(self._transport)
        self.agents = AgentsAPI(self._transport)
        
        # WebSocket
        self.websocket = WebSocketClient(
            base_url=base_url,
            jwt_token=jwt_token,
        )
        
        self._base_url = base_url
    
    @property
    def transport(self) -> HTTPTransport:
        """Access HTTP transport for direct API calls."""
        return self._transport
    
    async def health(self) -> Dict[str, Any]:
        """Check API health."""
        return await self._transport.get("/health")
    
    async def close(self) -> None:
        """Close all connections."""
        await self._transport.close()
    
    async def __aenter__(self) -> AMOSPlatformSDK:
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()


# =============================================================================
# REAL USAGE EXAMPLES (These make actual API calls)
# =============================================================================

async def example_chat():
    """Real chat example - makes actual HTTP call."""
    async with AMOSPlatformSDK(base_url="http://localhost:8000") as sdk:
        # Check health
        health = await sdk.health()
        print(f"API Health: {health}")
        
        # Real chat via brain facade
        response = await sdk.chat.send(
            message="Design a secure API architecture",
            workspace_id="test-ws",
        )
        
        print(f"Response: {response.message}")
        print(f"Confidence: {response.confidence}")
        print(f"Domain: {response.domain}")
        print(f"Law Compliant: {response.law_compliant}")


async def example_agent():
    """Real agent execution example."""
    async with AMOSPlatformSDK(base_url="http://localhost:8000") as sdk:
        # Start real agent
        task = await sdk.agents.run(
            agent_type="code_review",
            task_description="Review authentication module for security issues",
            target_repo="https://github.com/example/repo",
            priority="high",
        )
        
        print(f"Agent started: {task.task_id}")
        
        # Wait for completion with real polling
        final_status = await sdk.agents.wait_for_completion(
            task.task_id,
            poll_interval=2.0,
        )
        
        print(f"Status: {final_status.status}")
        if final_status.result:
            print(f"Result: {final_status.result}")


async def example_websocket():
    """Real WebSocket example."""
    sdk = AMOSPlatformSDK(base_url="http://localhost:8000")
    
    # Connect and receive real events
    async for event in sdk.websocket.connect():
        print(f"Event: {event}")
        
        # Subscribe to specific channel
        if event.get("type") == "connected":
            await sdk.websocket.subscribe("tasks")


if __name__ == "__main__":
    # Run real examples
    print("AMOS Platform SDK - Real HTTP/WebSocket Client")
    print("=" * 50)
    
    # Example: Chat
    print("\n1. Testing Chat API...")
    try:
        asyncio.run(example_chat())
    except Exception as e:
        print(f"Chat error (expected if server not running): {e}")
    
    # Example: Agent
    print("\n2. Testing Agent API...")
    try:
        asyncio.run(example_agent())
    except Exception as e:
        print(f"Agent error (expected if server not running): {e}")
