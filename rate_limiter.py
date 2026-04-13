"""Rate Limiting for AMOS Brain API

Usage:
    from rate_limiter import RateLimiter, require_rate_limit
    
    limiter = RateLimiter(requests_per_minute=100)
    
    @app.route('/think')
    @require_rate_limit(limiter)
    def think():
        ...
"""

import time
from functools import wraps
from flask import request, jsonify


class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self, requests_per_minute=100, burst_size=10):
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.requests = {}
    
    def is_allowed(self, key):
        """Check if request is allowed for given key."""
        now = time.time()
        window = 60  # 1 minute
        
        if key not in self.requests:
            self.requests[key] = []
        
        # Clean old requests
        self.requests[key] = [
            ts for ts in self.requests[key] 
            if now - ts < window
        ]
        
        # Check limit
        if len(self.requests[key]) >= self.requests_per_minute:
            return False
        
        # Record request
        self.requests[key].append(now)
        return True
    
    def get_stats(self, key):
        """Get rate limit stats for key."""
        now = time.time()
        window = 60
        
        if key not in self.requests:
            return {'current': 0, 'limit': self.requests_per_minute, 'remaining': self.requests_per_minute}
        
        current = len([ts for ts in self.requests[key] if now - ts < window])
        return {
            'current': current,
            'limit': self.requests_per_minute,
            'remaining': max(0, self.requests_per_minute - current)
        }


def require_rate_limit(limiter):
    """Decorator factory for rate limiting."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Get client identifier (API key or IP)
            key = request.headers.get('X-API-Key') or request.remote_addr or 'anonymous'
            
            if not limiter.is_allowed(key):
                stats = limiter.get_stats(key)
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'limit': stats['limit'],
                    'retry_after': 60
                }), 429
            
            return f(*args, **kwargs)
        return wrapped
    return decorator
