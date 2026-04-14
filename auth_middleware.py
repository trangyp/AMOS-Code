"""API Key Authentication for AMOS Brain API

Usage:
    from auth_middleware import require_api_key

    @app.route('/protected')
    @require_api_key
    def protected_route():
        return jsonify({'message': 'Success'})
"""

import hashlib
import os
import secrets
from functools import wraps

from flask import jsonify, request

# In-memory store (use Redis/DB in production)
_api_keys = {}


def generate_api_key():
    """Generate a new API key."""
    key = secrets.token_urlsafe(32)
    key_hash = hashlib.sha256(key.encode()).hexdigest()
    _api_keys[key_hash] = {
        "created": os.time() if hasattr(os, "time") else 0,
        "requests": 0,
        "active": True,
    }
    return key


def validate_api_key(key):
    """Validate an API key."""
    if not key:
        return False
    key_hash = hashlib.sha256(key.encode()).hexdigest()
    if key_hash in _api_keys and _api_keys[key_hash]["active"]:
        _api_keys[key_hash]["requests"] += 1
        return True
    return False


def require_api_key(f):
    """Decorator to require API key for endpoint."""

    @wraps(f)
    def decorated(*args, **kwargs):
        # Skip auth in development
        if os.environ.get("DEBUG") == "true":
            return f(*args, **kwargs)

        # Check header
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            api_key = request.headers.get("Authorization", "").replace("Bearer ", "")

        if not validate_api_key(api_key):
            return jsonify({"error": "Invalid or missing API key"}), 401

        return f(*args, **kwargs)

    return decorated


def get_key_stats():
    """Get API key usage statistics."""
    return {
        "total_keys": len(_api_keys),
        "active_keys": sum(1 for k in _api_keys.values() if k["active"]),
        "total_requests": sum(k["requests"] for k in _api_keys.values()),
    }
