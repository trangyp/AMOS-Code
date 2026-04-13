"""
API Server — REST API for AMOS Organism.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any, Dict, Optional


class APIServer:
    """
    HTTP API server for AMOS Organism.

    Endpoints:
    - GET /status: Organism status
    - POST /brain/perceive: Send perception to brain
    - POST /brain/plan: Create a plan
    - POST /route: Route an action
    - POST /muscle/execute: Execute command
    - GET /memory/search: Search memory
    """

    def __init__(self, organism, host: str = "localhost", port: int = 8765):
        self.organism = organism
        self.host = host
        self.port = port
        self._server: Optional[HTTPServer] = None

    def start(self):
        """Start the API server."""
        handler = self._make_handler()
        self._server = HTTPServer((self.host, self.port), handler)
        print(f"AMOS API server running on http://{self.host}:{self.port}")
        self._server.serve_forever()

    def stop(self):
        """Stop the API server."""
        if self._server:
            self._server.shutdown()

    def _make_handler(self):
        """Create request handler class."""
        organism = self.organism

        class RequestHandler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                # Suppress default logging
                pass

            def do_GET(self):
                if self.path == "/status":
                    self._send_json(organism.status())
                elif self.path == "/health":
                    self._send_json({"status": "healthy"})
                else:
                    self._send_json({"error": "Not found"}, 404)

            def do_POST(self):
                content_len = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_len).decode('utf-8')
                try:
                    data = json.loads(body) if body else {}
                except json.JSONDecodeError:
                    self._send_json({"error": "Invalid JSON"}, 400)
                    return

                if self.path == "/brain/perceive":
                    content = data.get("content", "")
                    thought = organism.brain.perceive(content)
                    self._send_json({"id": thought.id, "content": thought.content})

                elif self.path == "/brain/plan":
                    goal = data.get("goal", "")
                    plan = organism.brain.create_plan(goal)
                    self._send_json({"id": plan.id, "goal": plan.goal, "steps": plan.steps})

                elif self.path == "/route":
                    action = data.get("action", "")
                    params = data.get("params", {})
                    decision = organism.router.route(action, params)
                    self._send_json({
                        "target": decision.target,
                        "action": decision.action,
                        "reason": decision.reason,
                    })

                else:
                    self._send_json({"error": "Not found"}, 404)

            def _send_json(self, data: Dict, status: int = 200):
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(data).encode('utf-8'))

        return RequestHandler
