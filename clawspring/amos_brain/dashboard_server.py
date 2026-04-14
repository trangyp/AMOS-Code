"""AMOS Dashboard Server - HTTP server for cognitive dashboard."""

import json
import sys
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# Add parent for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from amos_brain.cognitive_audit import get_audit_trail
    from amos_brain.feedback_loop import get_feedback_loop
except ImportError:
    from cognitive_audit import get_audit_trail
    from feedback_loop import get_feedback_loop


DASHBOARD_HTML = Path(__file__).parent / "dashboard.html"


class DashboardHandler(BaseHTTPRequestHandler):
    """Handle dashboard requests."""

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass

    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/dashboard":
            self._serve_dashboard()
        elif path == "/api/amos/audit":
            self._serve_audit_data()
        else:
            self._send_404()

    def _serve_dashboard(self):
        """Serve the HTML dashboard."""
        try:
            html = DASHBOARD_HTML.read_text()
            self._send_response(200, "text/html", html)
        except FileNotFoundError:
            self._send_response(500, "text/plain", "Dashboard HTML not found")

    def _serve_audit_data(self):
        """Serve audit data as JSON."""
        try:
            audit = get_audit_trail()
            loop = get_feedback_loop()

            stats = audit.get_statistics()
            entries = audit.get_recent(50)
            insights = loop.analyze_patterns()

            # Convert insights to serializable format
            insights_data = [
                {
                    "pattern": i.pattern,
                    "recommended_engines": i.recommended_engines,
                    "avg_consensus_score": i.avg_consensus_score,
                    "violation_rate": i.violation_rate,
                    "confidence": i.confidence
                }
                for i in insights
            ]

            # Convert entries to serializable format
            entries_data = [
                {
                    "timestamp": e.timestamp,
                    "task_preview": e.task_preview,
                    "domain": e.domain,
                    "risk_level": e.risk_level,
                    "engines_selected": e.engines_selected,
                    "consensus_score": e.consensus_score,
                    "violations_found": e.violations_found,
                    "execution_time_ms": e.execution_time_ms
                }
                for e in entries
            ]

            data = {
                "stats": stats,
                "entries": entries_data,
                "insights": insights_data
            }

            self._send_response(200, "application/json", json.dumps(data))
        except Exception as e:
            self._send_response(500, "application/json", json.dumps({"error": str(e)}))

    def _send_response(self, code, content_type, body):
        """Send HTTP response."""
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        if isinstance(body, str):
            body = body.encode()
        self.wfile.write(body)

    def _send_404(self):
        """Send 404 response."""
        self._send_response(404, "text/plain", "Not Found")


def start_dashboard_server(port=8080):
    """Start the dashboard HTTP server."""
    server = HTTPServer(("localhost", port), DashboardHandler)
    print(f"AMOS Dashboard: http://localhost:{port}")
    print("Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AMOS Dashboard Server")
    parser.add_argument("--port", type=int, default=8080, help="Port to serve on")
    args = parser.parse_args()
    start_dashboard_server(args.port)
