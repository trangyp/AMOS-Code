"""Admin API Endpoints for AMOS Brain

Endpoints:
    POST /admin/keys - Generate new API key
    GET /admin/keys - List active keys (with master key)
    GET /admin/stats - API usage statistics
    DELETE /admin/keys/<key> - Revoke API key
"""

from flask import Blueprint, request, jsonify
from auth_middleware import generate_api_key, get_key_stats, _api_keys
from rate_limiter import RateLimiter
import os

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Master key for admin access (set in environment)
MASTER_KEY = os.environ.get('ADMIN_MASTER_KEY', 'dev-master-key')

# Shared rate limiter
limiter = RateLimiter(requests_per_minute=1000)  # Higher limit for admin


def require_master_key(f):
    """Decorator to require master key for admin endpoints."""
    from functools import wraps
    
    @wraps(f)
    def decorated(*args, **kwargs):
        provided = request.headers.get('X-Master-Key') or request.headers.get('Authorization', '').replace('Bearer ', '')
        if provided != MASTER_KEY:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/keys', methods=['POST'])
@require_master_key
def create_key():
    """Generate new API key."""
    key = generate_api_key()
    return jsonify({
        'api_key': key,
        'message': 'Store this key securely. It cannot be retrieved again.'
    })


@admin_bp.route('/keys', methods=['GET'])
@require_master_key
def list_keys():
    """List API keys with stats."""
    keys_info = []
    for key_hash, data in _api_keys.items():
        keys_info.append({
            'id': key_hash[:16] + '...',
            'active': data['active'],
            'requests': data['requests']
        })
    return jsonify({'keys': keys_info})


@admin_bp.route('/stats', methods=['GET'])
@require_master_key
def get_stats():
    """Get API usage statistics."""
    auth_stats = get_key_stats()
    rate_stats = limiter.get_stats('global')
    
    return jsonify({
        'authentication': auth_stats,
        'rate_limiting': rate_stats,
        'domain': 'neurosyncai.tech'
    })


@admin_bp.route('/health', methods=['GET'])
def admin_health():
    """Public health check for admin service."""
    return jsonify({'status': 'admin service operational'})
