"""Health Check Endpoint Tests.

Creator: Trang Phan
Version: 3.0.0
"""


class TestHealthEndpoints:
    """Test suite for health check endpoints."""

    def test_health_basic(self, client):
        """Test basic health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "2.3.0"

    def test_superbrain_present(self, client):
        """Test SuperBrain is present in health check."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "super_brain" in data
        assert "components" in data
        assert data["components"]["super_brain"] is True
        # SuperBrain health details should be present
        assert "brain_id" in data["super_brain"]
        assert "status" in data["super_brain"]

    def test_liveness_probe(self, client):
        """Test Kubernetes liveness probe."""
        response = client.get("/health/live")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "uptime_seconds" in data
        assert "timestamp" in data

    def test_readiness_probe(self, client):
        """Test Kubernetes readiness probe."""
        response = client.get("/health/ready")
        # May return 200 or 503 depending on system state
        assert response.status_code in [200, 503]
        data = response.json()
        assert "status" in data
        assert "checks" in data

    def test_startup_probe(self, client):
        """Test Kubernetes startup probe."""
        response = client.get("/health/startup")
        # May return 200 or 503 depending on startup state
        assert response.status_code in [200, 503]
        data = response.json()
        assert "status" in data
        assert "startup_duration_seconds" in data

    def test_full_health_check(self, client):
        """Test comprehensive health check."""
        response = client.get("/health/full")
        assert response.status_code == 200
        data = response.json()
        assert data["version"] == "3.0.0"
        assert "timestamp" in data
        assert "liveness" in data
        assert "readiness" in data
        assert "startup" in data
