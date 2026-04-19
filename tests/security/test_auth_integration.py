#!/usr/bin/env python3
"""Security tests for AMOS Authentication Integration."""

import time


class TestAuthentication:
    """Test authentication functionality."""

    def test_auth_initialization(self, auth_integration):
        """Test auth system initializes."""
        status = auth_integration.get_status()
        assert status["initialized"] is True

    def test_successful_login(self, auth_integration, test_user_credentials):
        """Test successful user authentication."""
        creds = test_user_credentials["admin"]
        session = auth_integration.authenticate_user(creds["username"], creds["password"])
        assert session is not None
        assert session.username == "admin"
        assert "admin" in session.roles
        assert session.token is not None

    def test_failed_login_wrong_password(self, auth_integration):
        """Test failed login with wrong password."""
        session = auth_integration.authenticate_user("admin", "wrongpassword")
        assert session is None

    def test_failed_login_unknown_user(self, auth_integration):
        """Test failed login with unknown user."""
        session = auth_integration.authenticate_user("nonexistent", "password")
        assert session is None

    def test_token_validation(self, auth_integration, test_user_credentials):
        """Test token validation."""
        creds = test_user_credentials["admin"]
        session = auth_integration.authenticate_user(creds["username"], creds["password"])
        validated = auth_integration.validate_token(session.token)
        assert validated is not None
        assert validated.username == session.username

    def test_invalid_token_rejection(self, auth_integration):
        """Test that invalid tokens are rejected."""
        validated = auth_integration.validate_token("invalid_token_12345")
        assert validated is None

    def test_token_expiration(self, auth_integration, test_user_credentials):
        """Test token expiration."""
        creds = test_user_credentials["admin"]
        session = auth_integration.authenticate_user(creds["username"], creds["password"])
        # Manually expire the token
        session.expires_at = time.time() - 1
        validated = auth_integration.validate_token(session.token)
        assert validated is None


class TestAuthorization:
    """Test authorization and permissions."""

    def test_admin_has_all_permissions(self, auth_integration, test_user_credentials):
        """Test admin role has wildcard permissions."""
        creds = test_user_credentials["admin"]
        session = auth_integration.authenticate_user(creds["username"], creds["password"])
        assert auth_integration.check_permission(session, "system:admin") is True
        assert auth_integration.check_permission(session, "agents:spawn") is True
        assert auth_integration.check_permission(session, "any:action") is True

    def test_permission_check_no_session(self, auth_integration):
        """Test permission check with no session."""
        assert auth_integration.check_permission(None, "any:permission") is False

    def test_wildcard_permission_matching(self, auth_integration):
        """Test wildcard permission matching."""
        from amos_auth_integration import AuthSession

        session = AuthSession(
            user_id="test", username="test", roles=["tester"], permissions=["agents:*"]
        )
        assert auth_integration.check_permission(session, "agents:spawn") is True
        assert auth_integration.check_permission(session, "agents:monitor") is True
        assert auth_integration.check_permission(session, "memory:read") is False


class TestRateLimiting:
    """Test rate limiting functionality."""

    def test_rate_limit_allows_requests(self, auth_integration):
        """Test that requests are allowed within limit."""
        ip = "127.0.0.1"
        # First request should be allowed
        assert auth_integration.check_rate_limit(ip, max_requests=5) is True

    def test_rate_limit_blocks_excessive_requests(self, auth_integration):
        """Test that excessive requests are blocked."""
        ip = "192.168.1.1"
        max_requests = 3
        # Make max_requests requests
        for _ in range(max_requests):
            auth_integration.check_rate_limit(ip, max_requests=max_requests)
        # Next request should be blocked
        assert auth_integration.check_rate_limit(ip, max_requests=max_requests) is False

    def test_rate_limit_per_ip(self, auth_integration):
        """Test rate limiting is per-IP."""
        ip1 = "10.0.0.1"
        ip2 = "10.0.0.2"
        max_requests = 3
        # Exhaust limit for ip1
        for _ in range(max_requests):
            auth_integration.check_rate_limit(ip1, max_requests=max_requests)
        assert auth_integration.check_rate_limit(ip1, max_requests=max_requests) is False
        # ip2 should still be allowed
        assert auth_integration.check_rate_limit(ip2, max_requests=max_requests) is True


class TestAPIKeys:
    """Test API key functionality."""

    def test_api_key_creation(self, auth_integration):
        """Test API key creation."""
        api_key = auth_integration.create_api_key("user123")
        assert api_key.startswith("amos_")
        assert len(api_key) > 32

    def test_api_key_validation(self, auth_integration):
        """Test API key validation."""
        user_id = "test_user"
        api_key = auth_integration.create_api_key(user_id)
        validated_user = auth_integration.validate_api_key(api_key)
        assert validated_user == user_id

    def test_invalid_api_key(self, auth_integration):
        """Test invalid API key rejection."""
        validated = auth_integration.validate_api_key("invalid_key")
        assert validated is None


class TestLogout:
    """Test logout functionality."""

    def test_logout_invalidates_session(self, auth_integration, test_user_credentials):
        """Test that logout invalidates session."""
        creds = test_user_credentials["admin"]
        session = auth_integration.authenticate_user(creds["username"], creds["password"])
        # Logout
        result = auth_integration.logout(session.token)
        assert result is True
        # Token should no longer be valid
        validated = auth_integration.validate_token(session.token)
        assert validated is None

    def test_logout_invalid_token(self, auth_integration):
        """Test logout with invalid token."""
        result = auth_integration.logout("nonexistent_token")
        assert result is False
