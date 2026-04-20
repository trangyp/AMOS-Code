#!/usr/bin/env python3
"""AMOS Integration Client - SDK for 5-Repository Architecture
==============================================================

This is the official Python client SDK for the AMOS Platform API.
It provides typed interfaces for all API endpoints and WebSocket events.

Usage:
    from amos_integration_client import AMOSClient

    client = AMOSClient(base_url="https://api.amos.io", api_key="your-key")

    # Chat
    response = await client.chat.send_message(
        message="Hello, AMOS!",
        workspace_id="ws-123"
    )

    # Run agent
    task = await client.agents.run(
        agent_type="repo_scan",
        target_repo="https://github.com/user/repo"
    )

    # WebSocket events
    async for event in client.websocket.connect():
        print(event)

Repositories Supported:
- AMOS-Code (core brain - imported as library)
- AMOS-Consulting (platform hub - this client connects here)
- AMOS-Claws (operator frontend)
- Mailinhconect (product frontend)
- AMOS-Invest (investor dashboard)

Owner: Trang
Version: 1.0.0
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc

UTC = UTC
from typing import Any, TypeVar

import aiohttp
import aiohttp.client_exceptions

T = TypeVar("T")


# =============================================================================
# Data Models
# =============================================================================


@dataclass
class ChatMessage:
    role: str
    content: str
    timestamp: str = None


@dataclass
class ChatRequest:
    message: str
    workspace_id: str
    context: list[ChatMessage] = field(default_factory=list)
    model: str = None
    temperature: float = 0.7
    max_tokens: int = None


@dataclass
class ChatResponse:
    id: str
    message: str
    model: str
    usage: dict[str, int]
    timestamp: str


@dataclass
class AgentRunRequest:
    agent_type: str
    parameters: dict[str, Any] = field(default_factory=dict)
    target_repo: str = None
    priority: str = "normal"
    callback_url: str = None


@dataclass
class AgentRunResult:
    task_id: str
    status: str
    agent_type: str
    result: dict[str, Any] = None
    error: str = None
    started_at: str = None
    completed_at: str = None
    duration_ms: int = None


@dataclass
class RepoScanRequest:
    repo_url: str
    branch: str = "main"
    scan_types: list[str] = field(default_factory=lambda: ["security", "style"])
    depth: str = "standard"


@dataclass
class TaskStatus:
    id: str
    type: str
    status: str
    progress: float = None
    message: str = None
    created_at: str = ""
    updated_at: str = ""
    completed_at: str = None
    error: str = None


@dataclass
class ModelInfo:
    id: str
    name: str
    provider: str
    status: str
    capabilities: list[str] = field(default_factory=list)
    context_window: int = 0
    loaded_at: str = None


# =============================================================================
# HTTP Client
# =============================================================================


class AMOSHTTPClient:
    """HTTP client for AMOS Platform API."""

    def __init__(
        self,
        base_url: str = "https://api.amos.io",
        api_key: str = None,
        jwt_token: str = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.jwt_token = jwt_token
        self._session: aiohttp.Optional[ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["X-API-Key"] = self.api_key
            if self.jwt_token:
                headers["Authorization"] = f"Bearer {self.jwt_token}"

            self._session = aiohttp.ClientSession(headers=headers)
        return self._session

    async def request(
        self,
        method: str,
        path: str,
        json_data: dict[str, Any] = None,
        params: dict[str, Any] = None,
    ) -> dict[str, Any]:
        """Make HTTP request to API."""
        session = await self._get_session()
        url = f"{self.base_url}/v1{path}"

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
                )

            return await response.json()

    async def get(self, path: str, params: dict[str, Any] = None) -> dict[str, Any]:
        """GET request."""
        return await self.request("GET", path, params=params)

    async def post(self, path: str, json_data: dict[str, Any]) -> dict[str, Any]:
        """POST request."""
        return await self.request("POST", path, json_data=json_data)

    async def delete(self, path: str) -> dict[str, Any]:
        """DELETE request."""
        return await self.request("DELETE", path)

    async def close(self) -> None:
        """Close HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()


class AMOSAPIError(Exception):
    """AMOS API error."""

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"API Error {status_code}: {message}")


# =============================================================================
# API Resource Classes
# =============================================================================


class ChatAPI:
    """Chat API resource."""

    def __init__(self, client: AMOSHTTPClient):
        self._client = client

    async def send_message(
        self,
        message: str,
        workspace_id: str,
        context: list[ChatMessage] = None,
        model: str = None,
        temperature: float = 0.7,
    ) -> ChatResponse:
        """Send chat message and get response."""
        request = ChatRequest(
            message=message,
            workspace_id=workspace_id,
            context=context or [],
            model=model,
            temperature=temperature,
        )

        response = await self._client.post("/chat", request.__dict__)

        return ChatResponse(
            id=response["id"],
            message=response["message"],
            model=response["model"],
            usage=response["usage"],
            timestamp=response["timestamp"],
        )


class AgentsAPI:
    """Agents API resource."""

    def __init__(self, client: AMOSHTTPClient):
        self._client = client

    async def run(
        self,
        agent_type: str,
        target_repo: str = None,
        parameters: dict[str, Any] = None,
        priority: str = "normal",
        callback_url: str = None,
    ) -> AgentRunResult:
        """Run an agent task."""
        request = AgentRunRequest(
            agent_type=agent_type,
            target_repo=target_repo,
            parameters=parameters or {},
            priority=priority,
            callback_url=callback_url,
        )

        response = await self._client.post("/agent/run", request.__dict__)

        return AgentRunResult(
            task_id=response["task_id"],
            status=response["status"],
            agent_type=agent_type,
        )

    async def get_status(self, task_id: str) -> AgentRunResult:
        """Get agent task status."""
        response = await self._client.get(f"/agent/status/{task_id}")

        return AgentRunResult(
            task_id=response["task_id"],
            status=response["status"],
            agent_type=response["agent_type"],
            result=response.get("result"),
            error=response.get("error"),
            started_at=response.get("started_at"),
            completed_at=response.get("completed_at"),
            duration_ms=response.get("duration_ms"),
        )

    async def cancel(self, task_id: str) -> bool:
        """Cancel a running agent task."""
        response = await self._client.post(f"/agent/cancel/{task_id}", {})
        return response.get("success", False)


class RepoAPI:
    """Repository API resource."""

    def __init__(self, client: AMOSHTTPClient):
        self._client = client

    async def scan(
        self,
        repo_url: str,
        branch: str = "main",
        scan_types: list[str] = None,
        depth: str = "standard",
    ) -> str:
        """Start repository scan. Returns scan ID."""
        request = RepoScanRequest(
            repo_url=repo_url,
            branch=branch,
            scan_types=scan_types or ["security", "style"],
            depth=depth,
        )

        response = await self._client.post("/repo/scan", request.__dict__)
        return response["scan_id"]

    async def get_status(self, scan_id: str) -> dict[str, Any]:
        """Get scan status."""
        return await self._client.get(f"/repo/status/{scan_id}")


class TasksAPI:
    """Tasks API resource."""

    def __init__(self, client: AMOSHTTPClient):
        self._client = client

    async def list(
        self,
        status: str = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[TaskStatus]:
        """List tasks."""
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if status:
            params["status"] = status

        response = await self._client.get("/tasks", params)

        return [
            TaskStatus(
                id=t["id"],
                type=t["type"],
                status=t["status"],
                progress=t.get("progress"),
                message=t.get("message"),
                created_at=t["created_at"],
                updated_at=t["updated_at"],
                completed_at=t.get("completed_at"),
                error=t.get("error"),
            )
            for t in response.get("tasks", [])
        ]

    async def get(self, task_id: str) -> TaskStatus:
        """Get task details."""
        response = await self._client.get(f"/tasks/{task_id}")

        return TaskStatus(
            id=response["id"],
            type=response["type"],
            status=response["status"],
            progress=response.get("progress"),
            message=response.get("message"),
            created_at=response["created_at"],
            updated_at=response["updated_at"],
            completed_at=response.get("completed_at"),
            error=response.get("error"),
        )


class ModelsAPI:
    """Models API resource."""

    def __init__(self, client: AMOSHTTPClient):
        self._client = client

    async def list(self) -> list[ModelInfo]:
        """List available models."""
        response = await self._client.get("/models")

        return [
            ModelInfo(
                id=m["id"],
                name=m["name"],
                provider=m["provider"],
                status=m["status"],
                capabilities=m.get("capabilities", []),
                context_window=m.get("context_window", 0),
                loaded_at=m.get("loaded_at"),
            )
            for m in response.get("models", [])
        ]


# =============================================================================
# WebSocket Client
# =============================================================================


class AMOSWebSocketClient:
    """WebSocket client for real-time events."""

    def __init__(self, base_url: str, jwt_token: str = None):
        self.base_url = base_url.replace("https://", "wss://").replace("http://", "ws://")
        self.jwt_token = jwt_token
        self._ws: aiohttp.Optional[ClientWebSocketResponse] = None
        self._subscribed_channels: set[str] = set()

    async def connect(self) -> AsyncIterator[dict[str, Any]]:
        """Connect to WebSocket and yield events."""
        url = f"{self.base_url}/v1/ws/stream"

        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(url) as ws:
                self._ws = ws

                # Authenticate
                if self.jwt_token:
                    await ws.send_json(
                        {
                            "type": "auth",
                            "token": self.jwt_token,
                        }
                    )

                # Resubscribe to channels
                for channel in self._subscribed_channels:
                    await ws.send_json(
                        {
                            "type": "subscribe",
                            "channel": channel,
                        }
                    )

                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        yield json.loads(msg.data)
                    elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                        break

    async def subscribe(self, channel: str) -> None:
        """Subscribe to channel."""
        self._subscribed_channels.add(channel)
        if self._ws:
            await self._ws.send_json(
                {
                    "type": "subscribe",
                    "channel": channel,
                }
            )

    async def unsubscribe(self, channel: str) -> None:
        """Unsubscribe from channel."""
        self._subscribed_channels.discard(channel)
        if self._ws:
            await self._ws.send_json(
                {
                    "type": "unsubscribe",
                    "channel": channel,
                }
            )

    async def ping(self) -> None:
        """Send ping to keep connection alive."""
        if self._ws:
            await self._ws.send_json({"type": "ping"})


# =============================================================================
# Main Client
# =============================================================================


class AMOSClient:
    """Main AMOS Platform API client."""

    def __init__(
        self,
        base_url: str = "https://api.amos.io",
        api_key: str = None,
        jwt_token: str = None,
    ):
        self._http = AMOSHTTPClient(
            base_url=base_url,
            api_key=api_key,
            jwt_token=jwt_token,
        )

        # API resources
        self.chat = ChatAPI(self._http)
        self.agents = AgentsAPI(self._http)
        self.repo = RepoAPI(self._http)
        self.tasks = TasksAPI(self._http)
        self.models = ModelsAPI(self._http)

        # WebSocket client
        self.websocket = AMOSWebSocketClient(
            base_url=base_url,
            jwt_token=jwt_token,
        )

    async def health(self) -> dict[str, Any]:
        """Check API health."""
        return await self._http.get("/health")

    async def status(self) -> dict[str, Any]:
        """Get system status."""
        return await self._http.get("/status")

    async def close(self) -> None:
        """Close all connections."""
        await self._http.close()

    async def __aenter__(self) -> AMOSClient:
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()


# =============================================================================
# TypeScript SDK Generator
# =============================================================================

TYPESCRIPT_CLIENT_TEMPLATE = """
// AMOS Platform API TypeScript Client
// Generated from OpenAPI spec
// Version: 1.0.0

export interface ChatRequest {
  message: string;
  workspace_id: string;
  context?: Message[];
  model?: string;
  temperature?: number;
  max_tokens?: number;
}

export interface Message {
  role: 'system' | 'user' | 'assistant';
  content: string;
  timestamp?: string;
}

export interface ChatResponse {
  id: string;
  message: string;
  model: string;
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
  timestamp: string;
}

export interface AgentRunRequest {
  agent_type: 'code_review' | 'repo_scan' | 'fix_generator' | 'security_audit' | 'performance_check' | 'custom';
  target_repo?: string;
  parameters?: Record<string, any>;
  priority?: 'low' | 'normal' | 'high' | 'urgent';
  callback_url?: string;
}

export interface AgentRunResult {
  task_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  agent_type: string;
  result?: any;
  error?: string;
  started_at?: string;
  completed_at?: string;
  duration_ms?: number;
}

export class AMOSClient {
  private baseUrl: string;
  private apiKey?: string;
  private jwtToken?: string;

  constructor(config: { baseUrl: string; apiKey?: string; jwtToken?: string }) {
    this.baseUrl = config.baseUrl.replace(/\\/$/, '');
    this.apiKey = config.apiKey;
    this.jwtToken = config.jwtToken;
  }

  private async request<T>(method: string, path: string, body?: any): Promise<T> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (this.apiKey) {
      headers['X-API-Key'] = this.apiKey;
    }

    if (this.jwtToken) {
      headers['Authorization'] = `Bearer ${this.jwtToken}`;
    }

    const response = await fetch(`${this.baseUrl}/v1${path}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });

    if (!response.ok) {
      throw new Error(`API Error ${response.status}: ${await response.text()}`);
    }

    return response.json();
  }

  // Chat API
  async chat(request: ChatRequest): Promise<ChatResponse> {
    return this.request<ChatResponse>('POST', '/chat', request);
  }

  // Agent API
  async runAgent(request: AgentRunRequest): Promise<AgentRunResult> {
    return this.request<AgentRunResult>('POST', '/agent/run', request);
  }

  async getAgentStatus(taskId: string): Promise<AgentRunResult> {
    return this.request<AgentRunResult>('GET', `/agent/status/${taskId}`);
  }

  async cancelAgent(taskId: string): Promise<{ success: boolean }> {
    return this.request<{ success: boolean }>('POST', `/agent/cancel/${taskId}`);
  }

  // Repository API
  async scanRepo(repoUrl: string, options?: { branch?: string; scan_types?: string[]; depth?: string }): Promise<{ scan_id: string }> {
    return this.request<{ scan_id: string }>('POST', '/repo/scan', {
      repo_url: repoUrl,
      ...options,
    });
  }

  // Task API
  async listTasks(options?: { status?: string; limit?: number; offset?: number }): Promise<{ tasks: any[]; total: number }> {
    const params = new URLSearchParams();
    if (options?.status) params.set('status', options.status);
    if (options?.limit) params.set('limit', options.limit.toString());
    if (options?.offset) params.set('offset', options.offset.toString());

    return this.request('GET', `/tasks?${params}`);
  }

  // Model API
  async listModels(): Promise<{ models: any[] }> {
    return this.request('{ models: any[] }>('GET', '/models');
  }

  // Health check
  async health(): Promise<{ status: string; version: string }> {
    return this.request<{ status: string; version: string }>('GET', '/health');
  }

  // WebSocket
  connectWebSocket(): WebSocket {
    const wsUrl = this.baseUrl.replace('https://', 'wss://').replace('http://', 'ws://');
    const ws = new WebSocket(`${wsUrl}/v1/ws/stream`);

    ws.onopen = () => {
      if (this.jwtToken) {
        ws.send(JSON.stringify({ type: 'auth', token: this.jwtToken }));
      }
    };

    return ws;
  }
}

export default AMOSClient;
"""


def generate_typescript_sdk() -> str:
    """Generate TypeScript SDK code."""
    return TYPESCRIPT_CLIENT_TEMPLATE


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "generate-ts":
        print(generate_typescript_sdk())
    else:
        print("AMOS Integration Client SDK")
        print("Usage: python amos_integration_client.py generate-ts")
