#!/usr/bin/env python3
"""AMOS Brain Simple API
=====================
Lightweight HTTP API for AMOS Brain using built-in Python libraries.

Endpoints:
  POST /api/think     - Cognitive analysis
  POST /api/reason    - Rule of 2 + Rule of 4 reasoning
  GET  /api/status    - Brain status
  GET  /api/laws      - Global laws
  GET  /api/engines   - List cognitive engines
  GET  /api/health    - Health check

Usage:
  python amos_api_simple.py [--port 8080]

Example:
  curl -X POST http://localhost:8080/api/think \
    -H "Content-Type: application/json" \
    -d '{"problem": "Should we use microservices?"}'
"""

import argparse
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

# Add paths
sys.path.insert(0, str(Path(__file__).parent / "clawspring"))
sys.path.insert(0, str(Path(__file__).parent))


class AMOSAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for AMOS API."""

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass

    def _send_json(self, data: dict[str, Any], status: int = 200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _send_error(self, message: str, status: int = 400):
        """Send error response."""
        self._send_json({"error": message}, status)

    def do_GET(self):
        """Handle GET requests."""
        path = self.path

        if path == "/api/health":
            self._send_json({"status": "healthy", "amos": "ready"})

        elif path == "/api/status":
            try:
                from amos_brain import get_amos_integration

                amos = get_amos_integration()
                status = amos.get_status()
                self._send_json(status)
            except Exception as e:
                self._send_error(str(e), 500)

        elif path == "/api/laws":
            try:
                from amos_brain.laws import GlobalLaws

                laws = GlobalLaws()
                result = {
                    "laws": [
                        {"id": lid, "name": l.name, "priority": l.priority}
                        for lid, l in laws.LAWS.items()
                    ]
                }
                self._send_json(result)
            except Exception as e:
                self._send_error(str(e), 500)

        elif path == "/api/engines":
            try:
                from amos_brain import get_amos_integration

                amos = get_amos_integration()
                stack = amos.cognitive_stack
                engines = [
                    {"name": name, "active": getattr(e, "active", False)}
                    for name, e in stack.engines.items()
                ]
                self._send_json({"engines": engines, "count": len(engines)})
            except Exception as e:
                self._send_error(str(e), 500)

        elif path == "/":
            self._send_json(
                {
                    "name": "AMOS Brain API",
                    "version": "1.0",
                    "endpoints": [
                        "GET /api/health",
                        "GET /api/status",
                        "GET /api/laws",
                        "GET /api/engines",
                        "POST /api/think",
                        "POST /api/reason",
                    ],
                }
            )

        else:
            self._send_error("Not found", 404)

    def do_POST(self):
        """Handle POST requests."""
        path = self.path

        # Read request body
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode() if content_length > 0 else "{}"

        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self._send_error("Invalid JSON", 400)
            return

        if path == "/api/think":
            try:
                from amos_brain import get_amos_integration

                amos = get_amos_integration()

                problem = data.get("problem", "")
                if not problem:
                    self._send_error("Missing 'problem' field", 400)
                    return

                # Run pre-processing
                pre = amos.pre_process(problem)

                # Run reasoning if available
                reasoning_result = None
                if hasattr(amos, "reasoning") and amos.reasoning:
                    reasoning_result = amos.reasoning.full_analysis(problem)

                self._send_json(
                    {
                        "problem": problem,
                        "pre_processing": pre,
                        "reasoning": reasoning_result,
                        "status": "completed",
                    }
                )
            except Exception as e:
                self._send_error(str(e), 500)

        elif path == "/api/reason":
            try:
                from amos_brain import get_amos_integration

                amos = get_amos_integration()

                problem = data.get("problem", "")
                if not problem:
                    self._send_error("Missing 'problem' field", 400)
                    return

                # Run reasoning
                if hasattr(amos, "reasoning") and amos.reasoning:
                    result = amos.reasoning.full_analysis(problem)
                    self._send_json(
                        {
                            "problem": problem,
                            "rule_of_two": result.get("rule_of_two"),
                            "rule_of_four": result.get("rule_of_four"),
                            "cross_validation": result.get("cross_validation"),
                            "confidence": result.get("confidence", 0),
                            "recommendation": result.get("recommendation", ""),
                        }
                    )
                else:
                    self._send_error("Reasoning engine not available", 500)
            except Exception as e:
                self._send_error(str(e), 500)

        else:
            self._send_error("Not found", 404)

    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


def run_server(port: int = 8080):
    """Run the AMOS API server."""
    server = HTTPServer(("", port), AMOSAPIHandler)
    print(f"AMOS Brain API running on http://localhost:{port}")
    print("Endpoints:")
    print(f"  GET  http://localhost:{port}/api/health")
    print(f"  GET  http://localhost:{port}/api/status")
    print(f"  GET  http://localhost:{port}/api/laws")
    print(f"  GET  http://localhost:{port}/api/engines")
    print(f"  POST http://localhost:{port}/api/think")
    print(f"  POST http://localhost:{port}/api/reason")
    print("\nPress Ctrl+C to stop")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.shutdown()


def main():
    parser = argparse.ArgumentParser(description="AMOS Brain Simple API")
    parser.add_argument("--port", type=int, default=8080, help="Port to run on")
    args = parser.parse_args()

    run_server(args.port)


if __name__ == "__main__":
    sys.exit(main())
