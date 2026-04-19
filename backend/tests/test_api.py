"""API Endpoint Tests.

Tests for the main API endpoints.

Creator: Trang Phan
Version: 3.0.0
"""


class TestRootEndpoints:
    """Test root and info endpoints."""

    def test_root_endpoint(self, client):
        """Test root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "AMOS Brain API"
        assert data["version"] == "3.0.0"
        assert "docs" in data
        assert "health" in data


class TestLLMEndpoints:
    """Test LLM-related endpoints."""

    def test_get_providers(self, client):
        """Test getting available LLM providers."""
        response = client.get("/api/v1/llm/providers")
        assert response.status_code == 200
        data = response.json()
        assert "providers" in data
        assert isinstance(data["providers"], list)

    def test_get_models(self, client):
        """Test getting available models."""
        response = client.get("/api/v1/llm/models")
        assert response.status_code == 200
        data = response.json()
        assert "models" in data
        assert isinstance(data["models"], list)

    def test_chat_completion_mock(self, client, chat_request_data):
        """Test chat completion with mock provider."""
        response = client.post("/api/v1/llm/chat", json=chat_request_data)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "usage" in data


class TestAgentEndpoints:
    """Test agent task endpoints."""

    def test_list_tasks(self, client):
        """Test listing agent tasks."""
        response = client.get("/api/v1/agents/tasks")
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert isinstance(data["tasks"], list)

    def test_create_task(self, client, sample_agent_task):
        """Test creating an agent task."""
        response = client.post("/api/v1/agents/tasks", json=sample_agent_task)
        assert response.status_code in [200, 201]
        data = response.json()
        assert "id" in data
        assert data["name"] == sample_agent_task["name"]


class TestSystemEndpoints:
    """Test system endpoints."""

    def test_system_status(self, client):
        """Test getting system status."""
        response = client.get("/api/v1/system/status")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data

    def test_system_metrics(self, client):
        """Test getting system metrics."""
        response = client.get("/api/v1/system/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "metrics" in data

    def test_cognitive_mode(self, client):
        """Test getting cognitive mode."""
        response = client.get("/api/v1/system/cognitive/mode")
        assert response.status_code == 200
        data = response.json()
        assert "mode" in data

    def test_reasoning_levels(self, client):
        """Test getting reasoning levels."""
        response = client.get("/api/v1/system/reasoning/levels")
        assert response.status_code == 200
        data = response.json()
        assert "levels" in data

    def test_mcp_servers(self, client):
        """Test getting MCP servers."""
        response = client.get("/api/v1/system/mcp/servers")
        assert response.status_code == 200
        data = response.json()
        assert "servers" in data

    def test_memory_entries(self, client):
        """Test getting memory entries."""
        response = client.get("/api/v1/system/memory/entries")
        assert response.status_code == 200
        data = response.json()
        assert "entries" in data

    def test_checkpoints(self, client):
        """Test getting checkpoints."""
        response = client.get("/api/v1/system/checkpoints")
        assert response.status_code == 200
        data = response.json()
        assert "checkpoints" in data


class TestRateLimiting:
    """Test rate limiting functionality."""

    def test_rate_limit_headers(self, client):
        """Test that rate limit headers are present."""
        response = client.get("/api/v1/system/status")
        assert response.status_code == 200
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers

    def test_health_excluded_from_rate_limit(self, client):
        """Test that health endpoints are excluded from rate limiting."""
        # Make multiple rapid requests
        for _ in range(70):  # Above the 60/min limit
            response = client.get("/health")
            assert response.status_code == 200
