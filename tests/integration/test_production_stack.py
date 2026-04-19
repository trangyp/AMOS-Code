"""AMOS Production Stack Integration Tests (Phase 12)
======================================================

Integration tests for the full production stack:
- FastAPI Gateway (Phase 10)
- Production Runtime (Phase 8)
- Self-Healing (Phase 7)
- Bootstrap Orchestrator (Phase 6)

Run with: pytest tests/integration/test_production_stack.py -v
"""

# Check if FastAPI is available
try:
    from fastapi.testclient import TestClient
    from httpx import AsyncClient

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("FastAPI/httpx not available, skipping API tests")

# Import production modules
try:
    from amos_fastapi_gateway import app
    from amos_production_runtime import AMOSProductionRuntime

    RUNTIME_AVAILABLE = True
except ImportError as e:
    RUNTIME_AVAILABLE = False
    print(f"Production runtime not available: {e}")


# Mark all tests as integration tests
pytestmark = pytest.mark.integration


class TestProductionRuntime:
    """Test suite for production runtime."""

    @pytest.mark.asyncio
    @pytest.mark.skipif(not RUNTIME_AVAILABLE, reason="Production runtime not available")
    async def test_runtime_creation(self):
        """Test that production runtime can be created."""
        runtime = await AMOSProductionRuntime.create()
        assert runtime is not None
        assert runtime._initialized is True

    @pytest.mark.asyncio
    @pytest.mark.skipif(not RUNTIME_AVAILABLE, reason="Production runtime not available")
    async def test_health_check(self):
        """Test health monitoring integration."""
        runtime = await AMOSProductionRuntime.create()
        health = runtime.get_health()

        assert "status" in health
        assert "health_score" in health
        assert "subsystems" in health
        assert health["health_score"] >= 0.0
        assert health["health_score"] <= 100.0

    @pytest.mark.asyncio
    @pytest.mark.skipif(not RUNTIME_AVAILABLE, reason="Production runtime not available")
    async def test_equation_execution(self):
        """Test equation execution through runtime."""
        runtime = await AMOSProductionRuntime.create()

        result = await runtime.execute_equation("softmax", [1.0, 2.0, 3.0])

        assert result is not None
        assert len(result) == 3

    @pytest.mark.asyncio
    @pytest.mark.skipif(not RUNTIME_AVAILABLE, reason="Production runtime not available")
    async def test_bootstrap_integrity(self):
        """Test bootstrap orchestrator integrity check."""
        runtime = await AMOSProductionRuntime.create()

        integrity = await runtime.check_bootstrap_integrity()

        assert integrity["all_healthy"] is True
        assert integrity["phases_complete"] >= 8

    @pytest.mark.asyncio
    @pytest.mark.skipif(not RUNTIME_AVAILABLE, reason="Production runtime not available")
    async def test_graceful_shutdown(self):
        """Test graceful shutdown of runtime."""
        runtime = await AMOSProductionRuntime.create()

        # Should complete without error
        await runtime.shutdown()

        assert runtime._initialized is False


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
class TestFastAPIGateway:
    """Test suite for FastAPI Gateway."""

    def test_root_endpoint(self):
        """Test root API endpoint."""
        client = TestClient(app)
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "AMOS API Gateway"
        assert data["version"] == "1.0.0"
        assert data["phase"] == 10

    def test_health_endpoint(self):
        """Test health check endpoint."""
        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

    def test_status_endpoint(self):
        """Test system status endpoint."""
        client = TestClient(app)
        response = client.get("/status")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"
        assert "phase" in data

    def test_equations_list(self):
        """Test equations list endpoint."""
        client = TestClient(app)
        response = client.get("/equations")

        assert response.status_code == 200
        data = response.json()
        assert "equations" in data
        assert "total" in data

    def test_equations_search(self):
        """Test equations search endpoint."""
        client = TestClient(app)
        response = client.get("/equations/search?query=softmax")

        assert response.status_code == 200
        data = response.json()
        assert "query" in data
        assert data["query"] == "softmax"

    def test_equation_execute(self):
        """Test equation execution endpoint."""
        client = TestClient(app)
        payload = {"name": "softmax", "args": [[1.0, 2.0, 3.0]], "kwargs": {}}
        response = client.post("/equations/execute", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "result" in data
        assert "execution_time_ms" in data

    def test_selfheal_status(self):
        """Test self-healing status endpoint."""
        client = TestClient(app)
        response = client.get("/selfheal/status")

        assert response.status_code == 200
        data = response.json()
        assert "enabled" in data
        assert "monitoring" in data

    def test_runtime_status(self):
        """Test runtime status endpoint."""
        client = TestClient(app)
        response = client.get("/runtime/status")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
class TestAPIErrorHandling:
    """Test API error handling."""

    def test_invalid_equation_name(self):
        """Test error handling for invalid equation."""
        client = TestClient(app)
        payload = {"name": "nonexistent_equation", "args": [], "kwargs": {}}
        # May return 200 with success=False or 500 depending on implementation
        response = client.post("/equations/execute", json=payload)
        assert response.status_code in [200, 500]

    def test_invalid_endpoint(self):
        """Test 404 for invalid endpoint."""
        client = TestClient(app)
        response = client.get("/invalid-endpoint-that-does-not-exist")
        assert response.status_code == 404


class TestSystemIntegration:
    """Test system-wide integration."""

    @pytest.mark.asyncio
    @pytest.mark.skipif(not RUNTIME_AVAILABLE, reason="Runtime not available")
    async def test_full_workflow(self):
        """Test full workflow: create runtime -> execute equation -> health check."""
        # 1. Create runtime
        runtime = await AMOSProductionRuntime.create()
        assert runtime._initialized is True

        # 2. Execute equation
        result = await runtime.execute_equation("softmax", [1.0, 2.0])
        assert result is not None

        # 3. Check health
        health = runtime.get_health()
        assert health["status"] == "healthy"

        # 4. Cleanup
        await runtime.shutdown()

    @pytest.mark.skipif(not RUNTIME_AVAILABLE, reason="Runtime not available")
    def test_module_imports(self):
        """Test that all required modules can be imported."""
        import amos_fastapi_gateway
        import amos_production_runtime

        assert amos_production_runtime is not None
        assert amos_fastapi_gateway is not None


# Performance tests
@pytest.mark.performance
@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
class TestAPIPerformance:
    """Test API performance."""

    def test_health_response_time(self):
        """Test that health endpoint responds quickly."""
        import time

        client = TestClient(app)

        start = time.time()
        response = client.get("/health")
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 1.0  # Should respond within 1 second

    def test_concurrent_requests(self):
        """Test handling of concurrent requests."""
        import concurrent.futures

        def make_request():
            client = TestClient(app)
            return client.get("/health")

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(20)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        assert all(r.status_code == 200 for r in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
