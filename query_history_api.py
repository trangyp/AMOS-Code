"""Query History API Endpoints

Provides endpoints for retrieving and managing query history.
"""

from flask import Blueprint, request, jsonify
from database import db
from auth_middleware import require_api_key
import hashlib

history_bp = Blueprint('history', __name__, url_prefix='/history')


def get_api_key_hash():
    """Get hash of current API key from request."""
    key = request.headers.get('X-API-Key') or request.headers.get('Authorization', '').replace('Bearer ', '')
    return hashlib.sha256(key.encode()).hexdigest() if key else 'anonymous'


@history_bp.route('/queries', methods=['GET'])
@require_api_key
def get_query_history():
    """Get query history for the authenticated API key."""
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    api_key_hash = get_api_key_hash()
    
    try:
        history = db.get_query_history(api_key_hash, limit=limit, offset=offset)
        
        return jsonify({
            'success': True,
            'queries': history,
            'count': len(history),
            'limit': limit,
            'offset': offset
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@history_bp.route('/stats', methods=['GET'])
@require_api_key
def get_user_stats():
    """Get usage statistics for the authenticated API key."""
    days = request.args.get('days', 7, type=int)
    
    try:
        stats = db.get_usage_stats(days)
        
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@history_bp.route('/query/<int:query_id>', methods=['GET'])
@require_api_key
def get_query_detail(query_id):
    """Get details of a specific query."""
    api_key_hash = get_api_key_hash()
    
    try:
        history = db.get_query_history(api_key_hash, limit=1)
        
        if not history:
            return jsonify({'success': False, 'error': 'Query not found'}), 404
        
        return jsonify({
            'success': True,
            'query': history[0]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
