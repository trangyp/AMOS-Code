"""API Server — REST API for AMOS Organism."""

import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Optional


class APIServer:
    """HTTP API server for AMOS Organism.

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
                elif self.path == "/agents/list":
                    # List available agents
                    agents = [
                        {
                            "name": "TaskExecutor",
                            "type": "execution",
                            "capabilities": ["run_command", "check_status"],
                            "endpoint": "/agents/execute",
                        }
                    ]
                    self._send_json({"agents": agents, "count": len(agents)})
                else:
                    self._send_json({"error": "Not found"}, 404)

            def do_POST(self):
                content_len = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_len).decode("utf-8")
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

                elif self.path == "/brain/think":
                    # Multi-layer cognitive processing
                    content = data.get("content", "")
                    perception = organism.brain.perceive(content)
                    concept = organism.brain.conceptualize(perception, "api_request")
                    self._send_json(
                        {
                            "perception_id": perception.id,
                            "perception": perception.content,
                            "concept_id": concept.id,
                            "concept": concept.content,
                            "cognitive_layers": ["perceptual", "conceptual"],
                            "brain_session": organism.brain.state.session_id,
                        }
                    )

                elif self.path == "/brain/analyze":
                    # Systemic multi-perspective analysis
                    topic = data.get("topic", "")
                    perception = organism.brain.perceive(topic, source="analysis_request")

                    # Get world model context
                    world_sectors = []
                    if hasattr(organism, "knowledge"):
                        world_sectors = list(organism.knowledge.nodes.keys())[:5]

                    # Get legal constraints
                    legal_rules = []
                    if hasattr(organism, "policy_engine"):
                        legal_rules = ["safety", "compliance", "ethics"]

                    analysis = {
                        "topic": topic,
                        "perception_id": perception.id,
                        "world_context": {
                            "sectors_available": world_sectors,
                            "legal_framework": legal_rules,
                        },
                        "subsystems_active": organism.status().get("active_subsystems", []),
                        "analysis_timestamp": organism.brain.state.last_update,
                    }
                    self._send_json(analysis)

                elif self.path == "/route":
                    action = data.get("action", "")
                    params = data.get("params", {})
                    decision = organism.router.route(action, params)
                    self._send_json(
                        {
                            "target": decision.target,
                            "action": decision.action,
                            "reason": decision.reason,
                        }
                    )

                elif self.path == "/agents/execute":
                    # Execute command via TaskExecutor agent
                    command = data.get("command", "")
                    if not command:
                        self._send_json({"error": "Command required"}, 400)
                        return

                    # Import and use agent
                    try:
                        sys.path.insert(0, "agents")
                        from task_executor import create_agent

                        agent = create_agent()
                        result = agent.run_command(command)
                        self._send_json(
                            {
                                "success": result.success,
                                "stdout": result.stdout,
                                "stderr": result.stderr,
                                "exit_code": result.exit_code,
                                "command": result.command,
                                "executed_at": result.executed_at,
                            }
                        )
                    except Exception as e:
                        self._send_json({"error": str(e)}, 500)

                else:
                    self._send_json({"error": "Not found"}, 404)

            def _send_json(self, data: dict, status: int = 200):
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(data).encode("utf-8"))

        return RequestHandler
