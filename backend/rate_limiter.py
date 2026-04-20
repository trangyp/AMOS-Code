"""AMOS Rate Limiting System

Simple in-memory rate limiting for API protection.
For production with distributed systems, use Redis-backed rate limiting.

Creator: Trang Phan
Version: 3.0.0
"""

import time
from dataclasses import dataclass

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware


@dataclass
class RateLimitConfig:
    """Rate limit configuration."""

    requests_per_minute: int = 60
    burst_size: int = 10
    block_duration_seconds: int = 300  # 5 minutes


class TokenBucket:
    """Token bucket rate limiter."""

    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.tokens = config.burst_size
        self.last_update = time.time()
        self.blocked_until: float = None

    def is_blocked(self) -> bool:
        """Check if the client is currently blocked."""
        if self.blocked_until is None:
            return False

        if time.time() >= self.blocked_until:
            self.blocked_until = None
            return False

        return True

    def block(self):
        """Block the client temporarily."""
        self.blocked_until = time.time() + self.config.block_duration_seconds

    def consume(self) -> bool:
        """Try to consume a token. Returns True if allowed."""
        if self.is_blocked():
            return False

        now = time.time()
        time_passed = now - self.last_update

        # Add tokens based on time passed (rate per minute)
        tokens_to_add = time_passed * (self.config.requests_per_minute / 60)
        self.tokens = min(self.config.burst_size, self.tokens + tokens_to_add)
        self.last_update = now

        if self.tokens >= 1:
            self.tokens -= 1
            return True

        # Rate limit exceeded - block the client
        self.block()
        return False

    def get_remaining(self) -> tuple[float, float]:
        """Get remaining tokens and time until reset."""
        if self.is_blocked():
            return 0.0, self.blocked_until - time.time() if self.blocked_until else 0.0

        return max(0, self.tokens), 60.0  # Reset in 60 seconds


class RateLimiter:
    """In-memory rate limiter."""

    def __init__(self):
        self.buckets: dict[str, TokenBucket] = {}
        self.config = RateLimitConfig()

    def get_bucket(self, key: str) -> TokenBucket:
        """Get or create token bucket for a key."""
        if key not in self.buckets:
            self.buckets[key] = TokenBucket(self.config)
        return self.buckets[key]

    def is_allowed(self, key: str) -> tuple[bool, int, int]:
        """
        Check if request is allowed.
        Returns (allowed, remaining, reset_seconds)
        """
        bucket = self.get_bucket(key)
        allowed = bucket.consume()
        remaining, reset_time = bucket.get_remaining()

        return allowed, int(remaining), int(reset_time)

    def cleanup_old_buckets(self):
        """Remove old/idle buckets to prevent memory leak."""
        now = time.time()
        keys_to_remove = []

        for key, bucket in self.buckets.items():
            # Remove if idle for more than 10 minutes
            if now - bucket.last_update > 600:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del self.buckets[key]


# Global rate limiter instance
rate_limiter = RateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for rate limiting."""

    def __init__(self, app, exclude_paths: list = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/health",
            "/health/live",
            "/health/ready",
            "/health/startup",
            "/health/full",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]

    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        path = request.url.path

        # Skip rate limiting for excluded paths
        if any(path.startswith(excluded) for excluded in self.exclude_paths):
            return await call_next(request)

        # Get client identifier (IP + path for granular limiting)
        client_ip = self._get_client_ip(request)
        key = f"{client_ip}:{path}"

        # Check rate limit
        allowed, remaining, reset_time = rate_limiter.is_allowed(key)

        if not allowed:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later.",
                headers={
                    "X-RateLimit-Limit": str(rate_limiter.config.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_time),
                    "Retry-After": str(reset_time),
                },
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(rate_limiter.config.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_time)

        return response

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request."""
        # Check for forwarded IP (behind proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        # Check for real IP
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fall back to direct connection IP
        if request.client:
            return request.client.host

        return "unknown"
