"""
AMOS Backend Tests

Unit and integration tests for FastAPI backend.

Creator: Trang Phan
Version: 3.0.0
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Test health and root endpoints."""

    def test_root(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert data["version"] == "3.0.0"

    def test_health(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestCognitiveAPI:
    """Test cognitive mode API endpoints."""

    def test_get_cognitive_mode(self):
        """Test getting cognitive mode."""
        response = client.get("/api/cognitive/mode")
        assert response.status_code == 200
        data = response.json()
        assert "mode" in data
        assert data["mode"] in ["seed", "growth", "full"]

    def test_set_cognitive_mode(self):
        """Test setting cognitive mode."""
        response = client.post("/api/cognitive/mode", params={"mode": "growth"})
        assert response.status_code == 200
        data = response.json()
        assert data["mode"] == "growth"

    def test_set_invalid_cognitive_mode(self):
        """Test setting invalid cognitive mode."""
        response = client.post("/api/cognitive/mode", params={"mode": "invalid"})
        assert response.status_code == 400


class TestReasoningAPI:
    """Test reasoning levels API endpoints."""

    def test_get_reasoning_levels(self):
        """Test getting all reasoning levels."""
        response = client.get("/api/reasoning/levels")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3

    def test_get_reasoning_level(self):
        """Test getting specific reasoning level."""
        response = client.get("/api/reasoning/level/l1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "l1"
        assert "name" in data

    def test_activate_reasoning_level(self):
        """Test activating reasoning level."""
        response = client.post("/api/reasoning/level/l2/activate")
        assert response.status_code == 200
        data = response.json()
        assert data["active"] is True


class TestMCPAPI:
    """Test MCP servers API endpoints."""

    def test_get_mcp_servers(self):
        """Test getting MCP servers."""
        response = client.get("/api/mcp/servers")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_mcp_server(self):
        """Test getting specific MCP server."""
        response = client.get("/api/mcp/servers/mcp-001")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "mcp-001"

    def test_connect_mcp_server(self):
        """Test connecting MCP server."""
        response = client.post("/api/mcp/servers/mcp-001/connect")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "connected"

    def test_disconnect_mcp_server(self):
        """Test disconnecting MCP server."""
        response = client.post("/api/mcp/servers/mcp-001/disconnect")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "disconnected"


class TestAgentTasksAPI:
    """Test agent tasks API endpoints."""

    def test_get_agent_tasks(self):
        """Test getting agent tasks."""
        response = client.get("/api/agents/tasks")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_cancel_agent_task(self):
        """Test canceling agent task."""
        # First create a task
        response = client.post(
            "/api/agents/tasks",
            json={
                "name": "Test Task",
                "type": "analysis",
                "description": "Test task for cancellation",
            },
        )
        task_id = response.json()["id"]

        # Then cancel it
        response = client.post(f"/api/agents/tasks/{task_id}/cancel")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["cancelled", "completed"]


class TestMemoryAPI:
    """Test memory API endpoints."""

    def test_get_memory_entries(self):
        """Test getting memory entries."""
        response = client.get("/api/memory/entries")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_create_memory_entry(self):
        """Test creating memory entry."""
        response = client.post(
            "/api/memory/entries",
            json={
                "system": "episodic",
                "content": "Test memory entry",
                "priority": "medium",
                "tags": ["test"],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Test memory entry"

    def test_search_memory(self):
        """Test searching memory."""
        response = client.get("/api/memory/search?q=test")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestCheckpointsAPI:
    """Test checkpoints API endpoints."""

    def test_get_checkpoints(self):
        """Test getting checkpoints."""
        response = client.get("/api/checkpoints")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_create_checkpoint(self):
        """Test creating checkpoint."""
        response = client.post("/api/checkpoints", json={"label": "Test checkpoint"})
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["label"] == "Test checkpoint"


class TestOrchestraAPI:
    """Test orchestra API endpoints."""

    def test_get_orchestra_agents(self):
        """Test getting orchestra agents."""
        response = client.get("/api/orchestra/agents")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_orchestra_status(self):
        """Test getting orchestra status."""
        response = client.get("/api/orchestra/status")
        assert response.status_code == 200
        data = response.json()
        assert "activeAgents" in data
        assert "totalTasks" in data


class TestSystemAPI:
    """Test system status API endpoints."""

    def test_get_system_status(self):
        """Test getting system status."""
        response = client.get("/api/system/status")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data

    def test_get_system_metrics(self):
        """Test getting system metrics."""
        response = client.get("/api/system/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "cpu" in data
        assert "memory" in data


class TestAGENTSMDAPI:
    """Test AGENTS.md API endpoints."""

    def test_get_agents_files(self):
        """Test getting AGENTS.md files."""
        response = client.get("/api/agents-md/files")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_agents_file(self):
        """Test getting specific AGENTS.md file."""
        response = client.get("/api/agents-md/files/agents-001")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "agents-001"


class TestWebSocket:
    """Test WebSocket endpoint availability."""

    def test_websocket_endpoint_exists(self):
        """Test that WebSocket endpoint is available."""
        # WebSocket endpoints return 403 on HTTP GET, but should exist
        # Full WebSocket testing requires async websocket client
        response = client.get("/ws")
        # Should either be upgrade required or redirect
        assert response.status_code in [403, 426, 307]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
