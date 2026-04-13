#!/usr/bin/env python3
"""AMOS Monitoring Middleware - Flask Middleware for Metrics Collection

Integrates metrics collection into the AMOS API Server:
- Request/response timing
- Error tracking
- Health check integration
- Alert evaluation

Usage:
    from amos_monitoring_middleware import MonitoringMiddleware
    middleware = MonitoringMiddleware(app)
"""

import time
import logging
from functools import wraps
from flask import Flask, request, jsonify, g
from typing import Optional

from amos_metrics_collector import get_metrics_collector
from amos_health_monitor import get_health_monitor, init_default_health_checks
from amos_alerting import init_default_alerting

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MonitoringMiddleware:
    """Flask middleware for monitoring integration."""
    
    def __init__(self, app: Optional[Flask] = None):
        self.metrics = get_metrics_collector()
        self.health = init_default_health_checks()
        self.alerting = init_default_alerting()
        self.app = app
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize middleware with Flask app."""
        self.app = app
        
        # Register before/after request handlers
        app.before_request(self._before_request)
        app.after_request(self._after_request)
        
        # Register monitoring endpoints
        self._register_routes(app)
        
        logger.info("Monitoring middleware initialized")
    
    def _before_request(self):
        """Start timing before request."""
        g.start_time = time.time()
    
    def _after_request(self, response):
        """Record metrics after request."""
        duration_ms = (time.time() - g.get('start_time', time.time())) * 1000
        
        # Extract client info
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        user_agent = request.headers.get('User-Agent', '')[:100]
        
        # Record the request
        self.metrics.record_request(
            path=request.path,
            method=request.method,
            status_code=response.status_code,
            duration_ms=duration_ms,
            client_ip=client_ip or '',
            user_agent=user_agent
        )
        
        # Check for alerts every 100 requests
        if len(self.metrics.requests) % 100 == 0:
            self._check_alerts()
        
        return response
    
    def _check_alerts(self):
        """Evaluate alert rules against current metrics."""
        try:
            summary = self.metrics.get_summary(minutes=5)
            
            metrics_data = {
                'error_rate': summary.get('error_rate', 0),
                'avg_response_time_ms': summary.get('response_time_ms', {}).get('avg', 0),
                'requests_per_second': summary.get('requests_per_second', 0),
            }
            
            # Add system metrics if available
            if summary.get('gauges'):
                metrics_data['cpu_percent'] = summary['gauges'].get('cpu_percent', 0)
                metrics_data['memory_percent'] = summary['gauges'].get('memory_percent', 0)
            
            new_alerts = self.alerting.evaluate_rules(metrics_data)
            
            if new_alerts:
                asyncio = __import__('asyncio')
                asyncio.create_task(self.alerting.send_notifications(new_alerts))
                
        except Exception as e:
            logger.error(f"Alert check failed: {e}")
    
    def _register_routes(self, app: Flask):
        """Register monitoring API routes."""
        
        @app.route('/api/health', methods=['GET'])
        def api_health():
            """Detailed health check."""
            import asyncio
            
            try:
                health = asyncio.get_event_loop().run_until_complete(
                    self.health.check_health()
                )
                return jsonify(self.health.to_dict(health))
            except:
                # Fallback to cached health
                health = self.health.get_health()
                return jsonify(self.health.to_dict(health))
        
        @app.route('/api/metrics/summary', methods=['GET'])
        def api_metrics_summary():
            """Get metrics summary."""
            minutes = request.args.get('minutes', 5, type=int)
            return jsonify(self.metrics.get_summary(minutes=minutes))
        
        @app.route('/api/metrics/prometheus', methods=['GET'])
        def api_metrics_prometheus():
            """Get Prometheus-formatted metrics."""
            from flask import Response
            return Response(
                self.metrics.get_prometheus_metrics(),
                mimetype='text/plain'
            )
        
        @app.route('/api/metrics', methods=['GET'])
        def api_metrics_full():
            """Get full metrics export."""
            from flask import Response
            return Response(
                self.metrics.to_json(),
                mimetype='application/json'
            )
        
        @app.route('/api/alerts/active', methods=['GET'])
        def api_alerts_active():
            """Get active alerts."""
            return jsonify({
                'alerts': [
                    {
                        'id': a.id,
                        'rule': a.rule_name,
                        'severity': a.severity.value,
                        'status': a.status.value,
                        'message': a.message,
                        'timestamp': a.timestamp.isoformat()
                    }
                    for a in self.alerting.get_active_alerts()
                ]
            })
        
        @app.route('/api/alerts/history', methods=['GET'])
        def api_alerts_history():
            """Get alert history."""
            hours = request.args.get('hours', 24, type=int)
            return jsonify({
                'alerts': [
                    {
                        'id': a.id,
                        'rule': a.rule_name,
                        'severity': a.severity.value,
                        'status': a.status.value,
                        'message': a.message,
                        'timestamp': a.timestamp.isoformat()
                    }
                    for a in self.alerting.get_alert_history(hours)
                ]
            })
        
        @app.route('/api/alerts/acknowledge', methods=['POST'])
        def api_alerts_acknowledge():
            """Acknowledge an alert."""
            data = request.get_json()
            alert_id = data.get('alert_id')
            user = data.get('user', 'unknown')
            
            if not alert_id:
                return jsonify({'error': 'Missing alert_id'}), 400
            
            success = self.alerting.acknowledge_alert(alert_id, user)
            return jsonify({'success': success})
        
        @app.route('/api/health/trend', methods=['GET'])
        def api_health_trend():
            """Get health trend over time."""
            hours = request.args.get('hours', 24, type=int)
            return jsonify(self.health.get_health_trend(hours))
        
        @app.route('/api/endpoints/stats', methods=['GET'])
        def api_endpoint_stats():
            """Get stats for specific endpoint."""
            path = request.args.get('path', '/think')
            hours = request.args.get('hours', 24, type=int)
            return jsonify(self.metrics.get_endpoint_stats(path, hours))
        
        @app.route('/monitoring', methods=['GET'])
        def monitoring_dashboard():
            """Serve monitoring dashboard."""
            from flask import render_template_string
            try:
                template_path = app.root_path / 'templates' / 'monitoring.html'
                if template_path.exists():
                    return template_path.read_text()
                else:
                    # Fallback: return simple status
                    return jsonify({
                        'status': 'monitoring',
                        'metrics': self.metrics.get_summary(),
                        'health': self.health.to_dict(self.health.get_health()),
                        'alerts': self.alerting.to_dict()
                    })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        logger.info("Monitoring routes registered")


def init_monitoring(app: Flask) -> MonitoringMiddleware:
    """Convenience function to initialize monitoring on app."""
    return MonitoringMiddleware(app)


if __name__ == '__main__':
    # Test middleware
    from flask import Flask
    
    test_app = Flask(__name__)
    middleware = MonitoringMiddleware(test_app)
    
    @test_app.route('/test')
    def test():
        return {'message': 'test'}
    
    # Simulate some requests
    with test_app.test_client() as client:
        for i in range(10):
            client.get('/test')
            client.get('/api/health')
    
    print("Metrics summary:")
    import json
    print(json.dumps(middleware.metrics.get_summary(), indent=2))
    
    print("\nHealth status:")
    print(json.dumps(middleware.health.to_dict(middleware.health.get_health()), indent=2))
