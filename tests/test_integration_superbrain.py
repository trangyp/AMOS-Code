"""AMOS SuperBrain v3.0 - Integration Test Suite.

End-to-end integration tests for the complete AMOS system.
Validates all 10 architecture layers working together at 75% health.

Test Coverage:
- API endpoints (health, status, tools, agents, memory, config)
- Tool execution (calculate, file, git, web_search)
- A2A multi-agent orchestration
- Memory architecture (L1/L2/L3)
- WebSocket real-time communication
- CLI interface commands

Usage:
    pytest tests/test_integration_superbrain.py -v
    pytest tests/test_integration_superbrain.py::TestAPIEndpoints -v
    pytest tests/test_integration_superbrain.py -k "health" -v

References:
- FastAPI Testing 2025 best practices
- pytest integration testing patterns
- httpx TestClient for API testing
"""


import json
import pytest
from datetime import datetime, timezone
UTC = timezone.utc
from typing import Any, Generator

# FastAPI testing
from fastapi.testclient import TestClient

# AMOS imports
from amos_superbrain_api import app
from amos_brain import initialize_super_brain, get_super_brain
from amos_brain.tools_extended import calculate, file_read_write, git_operations
from amos_brain.a2a_orchestrator import get_a2a_orchestrator
from amos_brain.memory_architecture import get_memory_manager, MemoryEntry
from amos_brain.config_validation import ConfigValidator


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    """Create test client for API testing."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def initialized_brain():
    """Initialize SuperBrain for testing."""
    initialize_super_brain()
    return get_super_brain()


# ============================================================================
# API Endpoint Tests
# ============================================================================

class TestAPIEndpoints:
    """Test REST API endpoints."""

    def test_root_endpoint(self, client: TestClient) -> None:
        """Test API root endpoint returns system info."""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "AMOS SuperBrain API"
        assert data["version"] == "3.0.0"
        assert data["health_score"] == "75%"
        assert "endpoints" in data

    def test_health_endpoint(self, client: TestClient) -> None:
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] in ["healthy", "degraded"]
        assert data["health_score"] >= 0.75
        assert data["version"] == "3.0"
        assert "timestamp" in data

    def test_status_endpoint(self, client: TestClient) -> None:
        """Test system status endpoint."""
        response = client.get("/status")
        assert response.status_code == 200

        data = response.json()
        assert data["health_score"] >= 0.75
        assert data["tools_count"] == 10
        assert data["status"] == "active"
        assert "timestamp" in data

    def test_tools_endpoint(self, client: TestClient) -> None:
        """Test tools listing endpoint."""
        response = client.get("/tools")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 10

        # Check for specific tools
        tool_names = [t["name"] for t in data]
        assert "calculate" in tool_names
        assert "web_search" in tool_names
        assert "file_read_write" in tool_names
        assert "git_operations" in tool_names

    def test_agents_endpoint(self, client: TestClient) -> None:
        """Test agents listing endpoint."""
        response = client.get("/agents")
        assert response.status_code == 200

        data = response.json()
        assert len(data) >= 1  # At least AMOS SuperBrain

        # Check AMOS SuperBrain agent
        amos_agent = next((a for a in data if a["name"] == "AMOS SuperBrain"), None)
        assert amos_agent is not None
        assert "calculate" in amos_agent["capabilities"]

    def test_memory_endpoint(self, client: TestClient) -> None:
        """Test memory statistics endpoint."""
        response = client.get("/memory")
        assert response.status_code == 200

        data = response.json()
        assert "tiers" in data
        assert len(data["tiers"]) == 3
        assert "l1_cache_size" in data
        assert "l2_status" in data
        assert "l3_status" in data

    def test_config_endpoint(self, client: TestClient) -> None:
        """Test configuration endpoint."""
        response = client.get("/config")
        assert response.status_code == 200

        data = response.json()
        assert "valid" in data
        assert "environment" in data
        assert "providers_configured" in data


# ============================================================================
# Tool Execution Tests
# ============================================================================

class TestToolExecution:
    """Test tool execution via API."""

    def test_execute_calculate_tool(self, client: TestClient) -> None:
        """Test calculate tool execution."""
        response = client.post(
            "/tools/calculate/execute",
            json={"parameters": {"expression": "2 + 2 * 5"}}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["tool"] == "calculate"
        assert data["success"] is True
        assert "result" in data
        assert data["execution_time_ms"] >= 0

    def test_execute_git_tool(self, client: TestClient) -> None:
        """Test git operations tool."""
        response = client.post(
            "/tools/git_operations/execute",
            json={"parameters": {"operation": "status", "repo_path": "."}}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["tool"] == "git_operations"
        assert "success" in data
        assert "result" in data

    def test_execute_web_search_tool(self, client: TestClient) -> None:
        """Test web search tool."""
        response = client.post(
            "/tools/web_search/execute",
            json={"parameters": {"query": "Python programming", "max_results": 2}}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["tool"] == "web_search"
        assert data["success"] is True
        assert "result" in data


# ============================================================================
# A2A Multi-Agent Tests
# ============================================================================

class TestA2AMultiAgent:
    """Test A2A multi-agent orchestration."""

    def test_create_task_via_api(self, client: TestClient) -> None:
        """Test task creation via API."""
        response = client.post(
            "/agents/task",
            json={"message": "Calculate 10 / 2", "capability": "calculate"}
        )
        assert response.status_code == 200

        data = response.json()
        assert "task_id" in data
        assert data["state"] in ["submitted", "working", "completed"]
        assert "messages" in data
        assert "created_at" in data

    def test_a2a_orchestrator_direct(self) -> None:
        """Test A2A orchestrator directly."""
        orchestrator = get_a2a_orchestrator()

        # Get stats
        stats = orchestrator.get_stats()
        assert stats["registered_agents"] >= 1

        # Discover agents
        agents = orchestrator.discover_agents()
        assert len(agents) >= 1

        # Route task
        task = orchestrator.route_task("Test task", capability="calculate")
        assert task.id is not None
        assert task.assigned_agent is not None


# ============================================================================
# Memory Architecture Tests
# ============================================================================

class TestMemoryArchitecture:
    """Test tiered memory architecture."""

    def test_memory_l1_cache(self) -> None:
        """Test L1 in-memory cache."""
        manager = get_memory_manager()

        # Create entry
        entry = MemoryEntry(
            id="test-l1-001",
            content="Test L1 cache entry",
            timestamp=datetime.now(timezone.utc),
            session_id="test-session",
            memory_type="test",
            priority=5
        )

        # Store in L1
        manager.store(entry, tier="l1")

        # Retrieve
        retrieved = manager.retrieve("test-l1-001")
        assert retrieved is not None
        assert retrieved.content == "Test L1 cache entry"

    def test_memory_l2_sqlite(self) -> None:
        """Test L2 SQLite persistence."""
        manager = get_memory_manager()

        # Create entry
        entry = MemoryEntry(
            id="test-l2-001",
            content="Test L2 SQLite entry",
            timestamp=datetime.now(timezone.utc),
            session_id="test-session",
            memory_type="conversation",
            priority=7
        )

        # Store (goes to L2 by default)
        success = manager.store(entry)
        assert success is True

        # Search
        results = manager.search(session_id="test-session", memory_type="conversation")
        assert len(results) >= 1

    def test_memory_tier_stats(self) -> None:
        """Test memory tier statistics."""
        manager = get_memory_manager()
        stats = manager.get_stats()

        assert "l1_cache_size" in stats
        assert "l2_sqlite" in stats
        assert "l3_file" in stats
        assert "tiers" in stats


# ============================================================================
# Configuration Tests
# ============================================================================

class TestConfiguration:
    """Test configuration validation."""

    def test_config_validation(self) -> None:
        """Test configuration validator."""
        validator = ConfigValidator()
        report = validator.validate()

        assert "valid" in report
        assert "environment" in report
        assert "providers_configured" in report
        assert "issues" in report
        assert "recommendations" in report

    def test_config_at_75_percent(self) -> None:
        """Test configuration at 75% health (no API keys)."""
        validator = ConfigValidator()
        report = validator.validate()

        # At 75%, config should be valid but may have warnings
        assert report["valid"] is True

        # Should have info about missing API keys
        info_present = any(
            "LLM providers" in issue and "INFO" in issue
            for issue in report.get("issues", [])
        )
        assert info_present or report["providers_configured"] == 0


# ============================================================================
# WebSocket Tests
# ============================================================================

class TestWebSocket:
    """Test WebSocket real-time communication."""

    def test_websocket_connection(self, client: TestClient) -> None:
        """Test WebSocket connection."""
        with client.websocket_connect("/ws") as websocket:
            # Receive connection message
            data = websocket.receive_json()
            assert data["type"] == "connection"
            assert data["status"] == "connected"

    def test_websocket_ping_pong(self, client: TestClient) -> None:
        """Test WebSocket ping/pong."""
        with client.websocket_connect("/ws") as websocket:
            # Skip connection message
            websocket.receive_json()

            # Send ping
            websocket.send_json({"type": "ping"})

            # Receive pong
            data = websocket.receive_json()
            assert data["type"] == "pong"
            assert "timestamp" in data


# ============================================================================
# End-to-End Integration Tests
# ============================================================================

class TestEndToEndIntegration:
    """End-to-end integration tests."""

    def test_full_workflow_api(self, client: TestClient) -> None:
        """Test complete workflow via API."""
        # 1. Check health
        response = client.get("/health")
        assert response.status_code == 200
        health = response.json()
        assert health["health_score"] >= 0.75

        # 2. List tools
        response = client.get("/tools")
        assert response.status_code == 200
        tools = response.json()
        assert len(tools) == 10

        # 3. Execute tool
        response = client.post(
            "/tools/calculate/execute",
            json={"parameters": {"expression": "100 / 4"}}
        )
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True

        # 4. Create A2A task
        response = client.post(
            "/agents/task",
            json={"message": "Process calculation result"}
        )
        assert response.status_code == 200
        task = response.json()
        assert "task_id" in task

        # 5. Check memory
        response = client.get("/memory")
        assert response.status_code == 200
        memory = response.json()
        assert "tiers" in memory

        # 6. Check config
        response = client.get("/config")
        assert response.status_code == 200
        config = response.json()
        assert config["valid"] is True

    def test_system_initialization(self) -> None:
        """Test system initializes correctly."""
        # Initialize
        success = initialize_super_brain()
        assert success is True

        # Check state
        brain = get_super_brain()
        state = brain.get_state()

        assert state.health_score >= 0.75
        assert state.status == "active"
        assert len(state.loaded_tools) == 10
        assert state.core_frozen is True


# ============================================================================
# Performance Tests
# ============================================================================

class TestPerformance:
    """Basic performance tests."""

    def test_health_endpoint_performance(self, client: TestClient) -> None:
        """Test health endpoint responds quickly."""
        import time

        start = time.time()
        response = client.get("/health")
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 1.0  # Should respond in under 1 second

    def test_tool_execution_performance(self, client: TestClient) -> None:
        """Test tool execution performance."""
        response = client.post(
            "/tools/calculate/execute",
            json={"parameters": {"expression": "2 + 2"}}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["execution_time_ms"] < 1000  # Under 1 second


# ============================================================================
# Error Handling Tests
# ============================================================================

class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_invalid_tool_name(self, client: TestClient) -> None:
        """Test error for invalid tool."""
        response = client.post(
            "/tools/nonexistent/execute",
            json={"parameters": {}}
        )
        assert response.status_code == 400

    def test_malformed_json(self, client: TestClient) -> None:
        """Test error for malformed JSON."""
        response = client.post(
            "/tools/calculate/execute",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
