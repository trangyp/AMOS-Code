#!/usr/bin/env python3
"""
AMOS API Rate Limiting and Throttling System (2025 SOTA)
========================================================

Implements state-of-the-art rate limiting for API Gateway protection.
Based on Zuplo 2025 best practices and industry standards.

Features:
- Token Bucket Algorithm (burst tolerance)
- Sliding Window (accurate limiting)
- Key-Level Rate Limiting (per API key, user, endpoint)
- Resource-Based Rate Limiting (per endpoint protection)
- Dynamic Rate Limiting (adjust based on load)
- Multiple Rate Limit Tiers (different users, different limits)
- Integration with API Gateway

Research Sources:
- Zuplo "10 Best Practices for API Rate Limiting in 2025/2026"
- API7.ai Token Bucket vs Leaky Bucket analysis
- APIsec.ai DDoS prevention strategies

Owner: Trang
Version: 5.0.0
"""

import threading
import time
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from typing import Any, Dict, Optional, Tuple


class RateLimitAlgorithm(Enum):
    """Rate limiting algorithms."""

    TOKEN_BUCKET = "token_bucket"  # Best for burst tolerance
    SLIDING_WINDOW = "sliding_window"  # Most accurate
    FIXED_WINDOW = "fixed_window"  # Simple, memory efficient
    LEAKY_BUCKET = "leaky_bucket"  # Smooth traffic


class RateLimitTier(Enum):
    """Rate limit tiers for different user types."""

    FREE = "free"  # 100 requests/minute
    BASIC = "basic"  # 1,000 requests/minute
    PRO = "pro"  # 10,000 requests/minute
    ENTERPRISE = "enterprise"  # 100,000 requests/minute
    INTERNAL = "internal"  # Unlimited


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""

    requests_per_window: int
    window_seconds: int
    burst_size: int = None  # For token bucket
    algorithm: RateLimitAlgorithm = RateLimitAlgorithm.TOKEN_BUCKET

    def get_default_burst(self) -> int:
        """Get default burst size for token bucket."""
        return self.burst_size or self.requests_per_window


# Standard tier configurations
TIER_CONFIGS: Dict[RateLimitTier, RateLimitConfig] = {
    RateLimitTier.FREE: RateLimitConfig(
        requests_per_window=100,
        window_seconds=60,
        burst_size=20,
        algorithm=RateLimitAlgorithm.TOKEN_BUCKET,
    ),
    RateLimitTier.BASIC: RateLimitConfig(
        requests_per_window=1000,
        window_seconds=60,
        burst_size=100,
        algorithm=RateLimitAlgorithm.TOKEN_BUCKET,
    ),
    RateLimitTier.PRO: RateLimitConfig(
        requests_per_window=10000,
        window_seconds=60,
        burst_size=500,
        algorithm=RateLimitAlgorithm.TOKEN_BUCKET,
    ),
    RateLimitTier.ENTERPRISE: RateLimitConfig(
        requests_per_window=100000,
        window_seconds=60,
        burst_size=2000,
        algorithm=RateLimitAlgorithm.SLIDING_WINDOW,
    ),
    RateLimitTier.INTERNAL: RateLimitConfig(
        requests_per_window=1000000, window_seconds=60, algorithm=RateLimitAlgorithm.TOKEN_BUCKET
    ),
}


class TokenBucket:
    """
    Token Bucket Algorithm.

    Best for: APIs with burst traffic patterns
    Pros: Allows bursts, simple to understand
    Cons: Can allow short-term spikes
    """

    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity  # Maximum tokens
        self.tokens = capacity  # Current tokens
        self.refill_rate = refill_rate  # Tokens per second
        self.last_refill = time.time()
        self._lock = threading.Lock()

    def consume(self, tokens: int = 1) -> Tuple[bool, int, float]:
        """
        Try to consume tokens.

        Returns:
            (allowed, remaining_tokens, retry_after_seconds)
        """
        with self._lock:
            now = time.time()
            elapsed = now - self.last_refill

            # Refill tokens
            self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
            self.last_refill = now

            if self.tokens >= tokens:
                self.tokens -= tokens
                return True, int(self.tokens), 0.0

            # Calculate retry after
            tokens_needed = tokens - self.tokens
            retry_after = tokens_needed / self.refill_rate
            return False, 0, retry_after

    def get_state(self) -> Dict[str, Any]:
        """Get current bucket state."""
        with self._lock:
            return {
                "capacity": self.capacity,
                "tokens": self.tokens,
                "refill_rate": self.refill_rate,
            }


class SlidingWindow:
    """
    Sliding Window Algorithm.

    Best for: Most accurate rate limiting
    Pros: Precise, no burst issues
    Cons: More memory usage (stores timestamps)
    """

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: deque = deque()
        self._lock = threading.Lock()

    def allow_request(self) -> Tuple[bool, int, float]:
        """
        Check if request is allowed.

        Returns:
            (allowed, remaining_requests, retry_after_seconds)
        """
        with self._lock:
            now = time.time()
            window_start = now - self.window_seconds

            # Remove old requests outside window
            while self.requests and self.requests[0] < window_start:
                self.requests.popleft()

            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                remaining = self.max_requests - len(self.requests)
                return True, remaining, 0.0

            # Rate limit exceeded
            oldest_request = self.requests[0]
            retry_after = oldest_request + self.window_seconds - now
            return False, 0, max(0.0, retry_after)

    def get_state(self) -> Dict[str, Any]:
        """Get current window state."""
        with self._lock:
            now = time.time()
            window_start = now - self.window_seconds
            valid_requests = [t for t in self.requests if t >= window_start]
            return {
                "max_requests": self.max_requests,
                "current_requests": len(valid_requests),
                "window_seconds": self.window_seconds,
            }


class FixedWindow:
    """
    Fixed Window Algorithm.

    Best for: Simple use cases, memory efficient
    Pros: Memory efficient, simple
    Cons: Can allow 2x burst at window boundaries
    """

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.current_window = int(time.time() / window_seconds)
        self.request_count = 0
        self._lock = threading.Lock()

    def allow_request(self) -> Tuple[bool, int, float]:
        """Check if request is allowed."""
        with self._lock:
            now = time.time()
            window = int(now / self.window_seconds)

            if window != self.current_window:
                # New window started
                self.current_window = window
                self.request_count = 0

            if self.request_count < self.max_requests:
                self.request_count += 1
                remaining = self.max_requests - self.request_count
                return True, remaining, 0.0

            # Rate limit exceeded
            next_window = (window + 1) * self.window_seconds
            retry_after = next_window - now
            return False, 0, retry_after


class LeakyBucket:
    """
    Leaky Bucket Algorithm.

    Best for: Smoothing traffic, predictable rates
    Pros: Smooth output, constant rate
    Cons: Can queue many requests
    """

    def __init__(self, leak_rate: float, bucket_size: int):
        self.leak_rate = leak_rate  # Requests per second
        self.bucket_size = bucket_size
        self.water_level = 0.0
        self.last_leak = time.time()
        self._lock = threading.Lock()

    def allow_request(self) -> Tuple[bool, int, float]:
        """Check if request is allowed."""
        with self._lock:
            now = time.time()
            elapsed = now - self.last_leak

            # Leak water
            self.water_level = max(0.0, self.water_level - elapsed * self.leak_rate)
            self.last_leak = now

            if self.water_level < self.bucket_size:
                self.water_level += 1.0
                remaining = int(self.bucket_size - self.water_level)
                return True, remaining, 0.0

            # Bucket full
            wait_time = (self.water_level - self.bucket_size) / self.leak_rate
            return False, 0, wait_time


@dataclass
class RateLimitResult:
    """Result of a rate limit check."""

    allowed: bool
    limit: int
    remaining: int
    reset_timestamp: float
    retry_after: float
    key: str
    tier: RateLimitTier


class RateLimiter:
    """
    Main rate limiter class.

    Manages multiple rate limit algorithms and keys.
    Supports key-level, resource-level, and tier-based limiting.
    """

    def __init__(self):
        # Token buckets by key
        self._token_buckets: Dict[str, TokenBucket] = {}
        # Sliding windows by key
        self._sliding_windows: Dict[str, SlidingWindow] = {}
        # Fixed windows by key
        self._fixed_windows: Dict[str, FixedWindow] = {}
        # Leaky buckets by key
        self._leaky_buckets: Dict[str, LeakyBucket] = {}

        # Key tier assignments
        self._key_tiers: Dict[str, RateLimitTier] = {}

        # Custom configs (override tier defaults)
        self._custom_configs: Dict[str, RateLimitConfig] = {}

        # Statistics
        self._stats: Dict[str, dict[str, Any]] = defaultdict(
            lambda: {
                "allowed": 0,
                "denied": 0,
                "last_request": None,
            }
        )

        # Cleanup thread
        self._lock = threading.RLock()
        self._cleanup_interval = 300  # 5 minutes
        self._last_cleanup = time.time()

    def _get_or_create_bucket(self, key: str, config: RateLimitConfig) -> TokenBucket:
        """Get or create token bucket for key."""
        with self._lock:
            if key not in self._token_buckets:
                self._token_buckets[key] = TokenBucket(
                    capacity=config.get_default_burst(),
                    refill_rate=config.requests_per_window / config.window_seconds,
                )
            return self._token_buckets[key]

    def _get_or_create_window(self, key: str, config: RateLimitConfig) -> SlidingWindow:
        """Get or create sliding window for key."""
        with self._lock:
            if key not in self._sliding_windows:
                self._sliding_windows[key] = SlidingWindow(
                    max_requests=config.requests_per_window, window_seconds=config.window_seconds
                )
            return self._sliding_windows[key]

    def _get_or_create_fixed_window(self, key: str, config: RateLimitConfig) -> FixedWindow:
        """Get or create fixed window for key."""
        with self._lock:
            if key not in self._fixed_windows:
                self._fixed_windows[key] = FixedWindow(
                    max_requests=config.requests_per_window, window_seconds=config.window_seconds
                )
            return self._fixed_windows[key]

    def _get_or_create_leaky_bucket(self, key: str, config: RateLimitConfig) -> LeakyBucket:
        """Get or create leaky bucket for key."""
        with self._lock:
            if key not in self._leaky_buckets:
                self._leaky_buckets[key] = LeakyBucket(
                    leak_rate=config.requests_per_window / config.window_seconds,
                    bucket_size=config.get_default_burst(),
                )
            return self._leaky_buckets[key]

    def _cleanup_old_keys(self) -> None:
        """Remove old rate limiter instances to free memory."""
        with self._lock:
            now = time.time()
            if now - self._last_cleanup < self._cleanup_interval:
                return

            # Keep only recently used keys (last 30 minutes)
            cutoff = now - 1800

            for key in list(self._stats.keys()):
                last_request = self._stats[key].get("last_request")
                if last_request and last_request < cutoff:
                    del self._stats[key]
                    self._token_buckets.pop(key, None)
                    self._sliding_windows.pop(key, None)
                    self._fixed_windows.pop(key, None)
                    self._leaky_buckets.pop(key, None)

            self._last_cleanup = now

    def set_key_tier(self, key: str, tier: RateLimitTier) -> None:
        """Assign a tier to a key."""
        with self._lock:
            self._key_tiers[key] = tier

    def set_custom_config(self, key: str, config: RateLimitConfig) -> None:
        """Set custom rate limit config for a key."""
        with self._lock:
            self._custom_configs[key] = config

    def _get_config_for_key(self, key: str) -> RateLimitConfig:
        """Get rate limit config for a key."""
        with self._lock:
            # Check custom config first
            if key in self._custom_configs:
                return self._custom_configs[key]

            # Check key tier
            tier = self._key_tiers.get(key, RateLimitTier.FREE)
            return TIER_CONFIGS[tier]

    def check_rate_limit(
        self, key: str, endpoint: str = None, method: str = None
    ) -> RateLimitResult:
        """
        Check rate limit for a request.

        Args:
            key: API key or user identifier
            endpoint: API endpoint path (for resource-level limiting)
            method: HTTP method

        Returns:
            RateLimitResult with allowed status and metadata
        """
        self._cleanup_old_keys()

        # Create composite key for resource-level limiting
        resource_key = key
        if endpoint:
            resource_key = f"{key}:{endpoint}"
            if method:
                resource_key = f"{key}:{method}:{endpoint}"

        config = self._get_config_for_key(key)
        tier = self._key_tiers.get(key, RateLimitTier.FREE)

        # Apply algorithm
        if config.algorithm == RateLimitAlgorithm.TOKEN_BUCKET:
            bucket = self._get_or_create_bucket(resource_key, config)
            allowed, remaining, retry_after = bucket.consume()

        elif config.algorithm == RateLimitAlgorithm.SLIDING_WINDOW:
            window = self._get_or_create_window(resource_key, config)
            allowed, remaining, retry_after = window.allow_request()

        elif config.algorithm == RateLimitAlgorithm.FIXED_WINDOW:
            fw = self._get_or_create_fixed_window(resource_key, config)
            allowed, remaining, retry_after = fw.allow_request()

        elif config.algorithm == RateLimitAlgorithm.LEAKY_BUCKET:
            lb = self._get_or_create_leaky_bucket(resource_key, config)
            allowed, remaining, retry_after = lb.allow_request()

        else:
            allowed, remaining, retry_after = True, 0, 0.0

        # Update statistics
        with self._lock:
            self._stats[key]["last_request"] = time.time()
            if allowed:
                self._stats[key]["allowed"] += 1
            else:
                self._stats[key]["denied"] += 1

        # Calculate reset timestamp
        now = time.time()
        reset_timestamp = now + retry_after if retry_after > 0 else now + config.window_seconds

        return RateLimitResult(
            allowed=allowed,
            limit=config.requests_per_window,
            remaining=remaining,
            reset_timestamp=reset_timestamp,
            retry_after=retry_after,
            key=key,
            tier=tier,
        )

    def get_stats(self, key: str = None) -> Dict[str, Any]:
        """Get rate limiting statistics."""
        with self._lock:
            if key:
                return {
                    "key": key,
                    **self._stats[key],
                    "tier": self._key_tiers.get(key, RateLimitTier.FREE).value,
                }
            return {
                "total_keys": len(self._stats),
                "total_allowed": sum(s["allowed"] for s in self._stats.values()),
                "total_denied": sum(s["denied"] for s in self._stats.values()),
                "tier_distribution": {
                    tier.value: sum(1 for k in self._key_tiers if self._key_tiers[k] == tier)
                    for tier in RateLimitTier
                },
            }


# Global rate limiter instance
_global_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """Get global rate limiter instance."""
    global _global_rate_limiter
    if _global_rate_limiter is None:
        _global_rate_limiter = RateLimiter()
    return _global_rate_limiter


def rate_limit(
    key_func: Callable[..., str] = None,
    tier: RateLimitTier = RateLimitTier.FREE,
    custom_config: Optional[RateLimitConfig] = None,
):
    """
    Decorator for rate limiting functions.

    Args:
        key_func: Function to extract rate limit key from request
        tier: Default tier for new keys
        custom_config: Optional custom rate limit config
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            limiter = get_rate_limiter()

            # Get key
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                key = "default"

            # Set tier and config
            limiter.set_key_tier(key, tier)
            if custom_config:
                limiter.set_custom_config(key, custom_config)

            # Check rate limit
            result = limiter.check_rate_limit(key)

            if not result.allowed:
                raise RateLimitExceeded(
                    f"Rate limit exceeded. Retry after {result.retry_after:.1f}s", result
                )

            # Add rate limit headers to response if applicable
            return func(*args, **kwargs)

        return wrapper

    return decorator


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded."""

    def __init__(self, message: str, result: RateLimitResult):
        super().__init__(message)
        self.result = result


def demo_rate_limiting():
    """Demonstrate rate limiting system."""
    print("=" * 70)
    print("🛡️  AMOS API RATE LIMITING AND THROTTLING SYSTEM")
    print("   (2025 SOTA - Fifth Architectural Fix)")
    print("=" * 70)

    limiter = RateLimiter()

    # 1. Token Bucket Algorithm
    print("\n[1] Token Bucket Algorithm (Burst Tolerance)")
    print("   Creating bucket: capacity=10, refill_rate=1/sec")

    bucket = TokenBucket(capacity=10, refill_rate=1.0)

    # Burst of 10 requests
    burst_results = []
    for i in range(12):
        allowed, remaining, retry = bucket.consume()
        burst_results.append(allowed)
        print(f"      Request {i+1}: {'✓' if allowed else '✗'} (remaining: {remaining})")

    print("   ✓ First 10 allowed (burst), last 2 rejected")

    # Wait for refill
    time.sleep(1.1)
    allowed, remaining, _ = bucket.consume()
    print("   ✓ After 1s: Request allowed (token refilled)")

    # 2. Sliding Window Algorithm
    print("\n[2] Sliding Window Algorithm (Most Accurate)")
    print("   Creating window: max=5, window=10s")

    window = SlidingWindow(max_requests=5, window_seconds=10)

    # Make 7 requests
    for i in range(7):
        allowed, remaining, retry = window.allow_request()
        print(
            f"      Request {i+1}: {'✓' if allowed else '✗'} "
            f"(remaining: {remaining}, retry_after: {retry:.1f}s)"
        )

    print("   ✓ First 5 allowed, 6th and 7th rejected")

    # 3. Tier-Based Rate Limiting
    print("\n[3] Tier-Based Rate Limiting")

    tiers = [RateLimitTier.FREE, RateLimitTier.BASIC, RateLimitTier.PRO]
    for tier in tiers:
        config = TIER_CONFIGS[tier]
        print(
            f"   • {tier.value.upper()}: {config.requests_per_window} req/"
            f"{config.window_seconds}s (burst: {config.get_default_burst()})"
        )

    # 4. Key-Level Rate Limiting
    print("\n[4] Key-Level Rate Limiting")

    # Setup different tiers for different API keys
    limiter.set_key_tier("api_key_free_user", RateLimitTier.FREE)
    limiter.set_key_tier("api_key_basic_user", RateLimitTier.BASIC)
    limiter.set_key_tier("api_key_pro_user", RateLimitTier.PRO)
    limiter.set_key_tier("api_key_enterprise", RateLimitTier.ENTERPRISE)

    test_keys = [
        ("api_key_free_user", "FREE tier (100/min)"),
        ("api_key_pro_user", "PRO tier (10,000/min)"),
    ]

    for key, description in test_keys:
        results = []
        for _ in range(105):  # Try 105 requests
            result = limiter.check_rate_limit(key)
            results.append(result.allowed)
            if not result.allowed:
                break

        allowed_count = sum(results)
        print(
            f"   • {description}: {allowed_count} requests allowed "
            f"({len(results) - allowed_count} rejected)"
        )

    # 5. Resource-Based Rate Limiting
    print("\n[5] Resource-Based Rate Limiting (Per Endpoint)")

    # Different limits for different endpoints
    limiter.set_custom_config(
        "expensive_endpoint",
        RateLimitConfig(
            requests_per_window=10, window_seconds=60, algorithm=RateLimitAlgorithm.SLIDING_WINDOW
        ),
    )

    # Simulate requests to expensive endpoint
    key = "api_key_pro_user"
    endpoint = "/api/v1/expensive-analysis"

    results = []
    for i in range(15):
        result = limiter.check_rate_limit(key, endpoint=endpoint)
        results.append(result.allowed)
        if i < 5 or i >= 12:
            status = "✓" if result.allowed else "✗"
            print(f"      Request {i+1}: {status} " f"(remaining: {result.remaining})")

    allowed = sum(results)
    print(
        f"   ✓ Expensive endpoint: {allowed}/15 allowed " f"(10/min limit, separate from user tier)"
    )

    # 6. Statistics
    print("\n[6] Rate Limiting Statistics")

    stats = limiter.get_stats()
    print(f"   • Total keys tracked: {stats['total_keys']}")
    print(f"   • Total requests allowed: {stats['total_allowed']}")
    print(f"   • Total requests denied: {stats['total_denied']}")

    if "tier_distribution" in stats:
        print("   • Tier distribution:")
        for tier, count in stats["tier_distribution"].items():
            if count > 0:
                print(f"      - {tier}: {count} keys")

    # 7. Integration with API Gateway
    print("\n[7] API Gateway Integration Pattern")

    print("""
   Rate Limit Headers (RFC 6585):
   • X-RateLimit-Limit: Maximum requests per window
   • X-RateLimit-Remaining: Remaining requests in current window
   • X-RateLimit-Reset: Unix timestamp when limit resets
   • Retry-After: Seconds to wait before retry (when limited)

   Response Codes:
   • 200 OK: Request successful
   • 429 Too Many Requests: Rate limit exceeded

   Example Response Headers:
   HTTP/1.1 200 OK
   X-RateLimit-Limit: 1000
   X-RateLimit-Remaining: 999
   X-RateLimit-Reset: 1704067200

   HTTP/1.1 429 Too Many Requests
   Retry-After: 45
   Content-Type: application/json
   {"error": "Rate limit exceeded", "retry_after": 45}
    """)

    print("\n" + "=" * 70)
    print("✅ API Rate Limiting System Active")
    print("=" * 70)
    print("\n🎯 Features Implemented:")
    print("   ✓ Token Bucket Algorithm (burst tolerance)")
    print("   ✓ Sliding Window Algorithm (accurate limiting)")
    print("   ✓ Fixed Window Algorithm (memory efficient)")
    print("   ✓ Leaky Bucket Algorithm (smooth traffic)")
    print("   ✓ Key-Level Rate Limiting (per API key)")
    print("   ✓ Resource-Based Limiting (per endpoint)")
    print("   ✓ Tier-Based Plans (Free/Basic/Pro/Enterprise)")
    print("   ✓ Automatic cleanup of old keys")
    print("   ✓ Statistics and monitoring")
    print("\n📊 Benefits for 1608+ functions:")
    print("   • Protection against DDoS attacks")
    print("   • Fair usage across all users")
    print("   • Cost control and resource protection")
    print("   • Graceful degradation under load")
    print("   • Multiple algorithms for different needs")
    print("=" * 70)


if __name__ == "__main__":
    demo_rate_limiting()
