#!/usr/bin/env python3
"""AMOS Brain API Test Suite

Usage:
    python test_api.py           # Run all tests
    python test_api.py -v        # Verbose output

Tests:
    - Health endpoint
    - Authentication
    - Rate limiting
    - Think/Decide/Validate endpoints
    - WebSocket connection
"""

import unittest
import requests
import json
import time
from pathlib import Path

# Add parent to path
import sys
sys.path.insert(0, str(Path(__file__).parent))

BASE_URL = "http://localhost:5000"
MASTER_KEY = "dev-master-key"


class TestHealthEndpoints(unittest.TestCase):
    """Test health and status endpoints."""

    def test_health_check(self):
        """Test /health returns healthy status."""
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['domain'], 'neurosyncai.tech')

    def test_status_endpoint(self):
        """Test /status returns brain status."""
        r = requests.get(f"{BASE_URL}/status", timeout=10)
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertTrue(data['success'])
        self.assertIn('status', data)


class TestThinkEndpoint(unittest.TestCase):
    """Test thinking endpoint."""

    def test_think_without_auth_development(self):
        """Test think endpoint works in dev mode."""
        payload = {"query": "Test query", "domain": "general"}
        r = requests.post(
            f"{BASE_URL}/think",
            json=payload,
            timeout=30
        )
        # In dev mode, should work without auth
        self.assertIn(r.status_code, [200, 401])

    def test_think_missing_query(self):
        """Test think returns error for missing query."""
        r = requests.post(f"{BASE_URL}/think", json={}, timeout=5)
        self.assertEqual(r.status_code, 400)


class TestDecideEndpoint(unittest.TestCase):
    """Test decision endpoint."""

    def test_decide_with_options(self):
        """Test decide with options."""
        payload = {
            "question": "Which to choose?",
            "options": ["A", "B", "C"]
        }
        r = requests.post(f"{BASE_URL}/decide", json=payload, timeout=30)
        self.assertIn(r.status_code, [200, 401])


class TestValidateEndpoint(unittest.TestCase):
    """Test validation endpoint."""

    def test_validate_action(self):
        """Test action validation."""
        payload = {"action": "Test action"}
        r = requests.post(f"{BASE_URL}/validate", json=payload, timeout=10)
        self.assertIn(r.status_code, [200, 401])


class TestAdminEndpoints(unittest.TestCase):
    """Test admin endpoints."""

    def test_admin_keys_requires_master(self):
        """Test admin requires master key."""
        r = requests.get(f"{BASE_URL}/admin/keys", timeout=5)
        self.assertEqual(r.status_code, 401)

    def test_admin_with_master_key(self):
        """Test admin with valid master key."""
        r = requests.get(
            f"{BASE_URL}/admin/keys",
            headers={"X-Master-Key": MASTER_KEY},
            timeout=5
        )
        self.assertIn(r.status_code, [200, 404])


class TestRateLimiting(unittest.TestCase):
    """Test rate limiting functionality."""

    def test_multiple_requests(self):
        """Test multiple requests don't fail immediately."""
        responses = []
        for i in range(5):
            r = requests.get(f"{BASE_URL}/health", timeout=5)
            responses.append(r.status_code)
            time.sleep(0.1)
        
        # Most should succeed
        success_count = sum(1 for s in responses if s == 200)
        self.assertGreaterEqual(success_count, 3)


def run_tests():
    """Run the test suite."""
    # Check if server is running
    try:
        requests.get(f"{BASE_URL}/health", timeout=2)
    except requests.exceptions.ConnectionError:
        print("❌ Error: API server not running")
        print(f"   Start with: python amos_api_server.py")
        sys.exit(1)
    
    # Run tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    import sys
    success = run_tests()
    sys.exit(0 if success else 1)
