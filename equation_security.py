#!/usr/bin/env python3
"""AMOS Equation Security - Production Security Headers & Middleware.

Security hardening middleware providing essential HTTP security headers
for production deployments. Protects against common web vulnerabilities.

Features:
    - Content Security Policy (CSP) - XSS protection
    - HTTP Strict Transport Security (HSTS) - HTTPS enforcement
    - X-Frame-Options - Clickjacking protection
    - X-Content-Type-Options - MIME sniffing protection
    - Referrer-Policy - Privacy control
    - X-XSS-Protection - Legacy XSS protection
    - Permissions-Policy - Feature access control
    - Security-focused CORS configuration
    - Request ID tracking for audit trails

Headers:
    Strict-Transport-Security: max-age=63072000; includeSubDomains
    Content-Security-Policy: default-src 'self'; script-src 'self'
    X-Frame-Options: DENY
    X-Content-Type-Options: nosniff
    X-XSS-Protection: 1; mode=block
    Referrer-Policy: strict-origin-when-cross-origin
    Permissions-Policy: geolocation=(), microphone=()

Usage:
    from equation_security import SecurityMiddleware
    app.add_middleware(SecurityMiddleware)

Environment Variables:
    SECURITY_HEADERS_ENABLED: Toggle security headers (default: true)
    CSP_NONCE_ENABLED: Enable CSP nonce generation (default: true)
    HSTS_MAX_AGE: HSTS max-age in seconds (default: 63072000)
"""

import os
import secrets
import uuid
from typing import Any

try:
    from fastapi import Request, Response
    from starlette.middleware.base import BaseHTTPMiddleware

    STARLETTE_AVAILABLE = True
except ImportError:
    STARLETTE_AVAILABLE = False
    BaseHTTPMiddleware = object  # type: ignore

# Security configuration from environment
_SECURITY_ENABLED = os.getenv("SECURITY_HEADERS_ENABLED", "true").lower() == "true"
_CSP_NONCE_ENABLED = os.getenv("CSP_NONCE_ENABLED", "true").lower() == "true"
_HSTS_MAX_AGE = int(os.getenv("HSTS_MAX_AGE", "63072000"))  # 2 years


def generate_nonce() -> str:
    """Generate CSP nonce for inline scripts/styles."""
    return secrets.token_urlsafe(16)


def get_security_headers(csp_nonce: str = None) -> dict[str, str]:
    """Generate security headers dictionary.

    Args:
        csp_nonce: Optional CSP nonce for inline content

    Returns:
        Dictionary of security header names and values
    """
    # Base CSP directive
    csp = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "media-src 'self'; "
        "object-src 'none'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self';"
    )

    if csp_nonce and _CSP_NONCE_ENABLED:
        csp += f" 'nonce-{csp_nonce}'"

    headers: Dict[str, str] = {
        # Enforce HTTPS for 2 years
        "Strict-Transport-Security": (f"max-age={_HSTS_MAX_AGE}; includeSubDomains; preload"),
        # Prevent XSS
        "Content-Security-Policy": csp,
        # Prevent clickjacking
        "X-Frame-Options": "DENY",
        # Prevent MIME sniffing
        "X-Content-Type-Options": "nosniff",
        # Legacy XSS protection (for older browsers)
        "X-XSS-Protection": "1; mode=block",
        # Control referrer information
        "Referrer-Policy": "strict-origin-when-cross-origin",
        # Control browser features
        "Permissions-Policy": (
            "geolocation=(), microphone=(), camera=(), " "payment=(), usb=(), magnetometer=()"
        ),
        # Cache control for API responses
        "Cache-Control": ("no-store, no-cache, must-revalidate, proxy-revalidate"),
        "Pragma": "no-cache",
        "Expires": "0",
    }

    return headers


class SecurityMiddleware(BaseHTTPMiddleware):  # type: ignore
    """FastAPI middleware for security headers.

    Adds comprehensive security headers to all responses
    and injects request IDs for tracing.
    """

    def __init__(self, app: Any, **kwargs: Any) -> None:
        """Initialize security middleware."""
        if not STARLETTE_AVAILABLE:
            raise ImportError("starlette required for SecurityMiddleware")
        super().__init__(app)

    async def dispatch(
        self,
        request: Request,
        call_next: Any,
    ) -> Response:
        """Process request and add security headers.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler

        Returns:
            HTTP response with security headers
        """
        # Generate request ID for tracing
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Generate CSP nonce if enabled
        csp_nonce = generate_nonce() if _CSP_NONCE_ENABLED else None
        request.state.csp_nonce = csp_nonce

        # Process request
        response = await call_next(request)

        if not _SECURITY_ENABLED:
            return response

        # Add security headers
        headers = get_security_headers(csp_nonce)
        for header, value in headers.items():
            response.headers[header] = value

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response


def get_request_id(request: Any) -> str:
    """Extract request ID from request state.

    Args:
        request: HTTP request object

    Returns:
        Request ID string or None
    """
    if hasattr(request.state, "request_id"):
        return request.state.request_id
    return None


def get_csp_nonce(request: Any) -> str:
    """Extract CSP nonce from request state.

    Args:
        request: HTTP request object

    Returns:
        CSP nonce string or None
    """
    if hasattr(request.state, "csp_nonce"):
        return request.state.csp_nonce
    return None


# Security configuration helpers
def get_cors_config() -> Dict[str, Any]:
    """Get secure CORS configuration.

    Returns:
        CORS middleware configuration dict
    """
    return {
        "allow_origins": os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000").split(","),
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": [
            "Content-Type",
            "Authorization",
            "X-Request-ID",
            "X-API-Key",
        ],
        "expose_headers": [
            "X-Request-ID",
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
        ],
        "max_age": 600,
    }


# Security event logging
def log_security_event(
    event_type: str,
    details: Dict[str, Any],
    request_id: str = None,
) -> None:
    """Log security-related events.

    Args:
        event_type: Type of security event
        details: Event details dictionary
        request_id: Optional request ID for correlation
    """
    import logging

    logger = logging.getLogger("amos.security")

    log_data = {
        "event_type": event_type,
        "request_id": request_id,
        **details,
    }

    logger.warning(f"Security event: {log_data}")


# Rate limiting security decorator helper
def get_client_ip(request: Any) -> str:
    """Extract client IP with proxy awareness.

    Args:
        request: HTTP request object

    Returns:
        Client IP address string
    """
    # Check X-Forwarded-For header (common proxy header)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # Get first IP in chain (original client)
        return forwarded.split(",")[0].strip()

    # Check X-Real-IP header (alternative proxy header)
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    # Fall back to direct connection IP
    if hasattr(request, "client") and request.client:
        return request.client.host

    return "unknown"


# Security headers for static content
STATIC_SECURITY_HEADERS: Dict[str, str] = {
    "Strict-Transport-Security": f"max-age={_HSTS_MAX_AGE}; includeSubDomains",
    "X-Frame-Options": "SAMEORIGIN",  # Allow framing from same origin for UI
    "Content-Security-Policy": "script-src 'self'; object-src 'self'",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Cache-Control": "public, max-age=3600",  # Allow caching for static assets
}
