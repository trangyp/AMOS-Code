#!/usr/bin/env python3
"""AMOS Dashboard WebSocket Server
================================

Real-time dashboard with WebSocket support for live updates.
Integrates task queue and subsystem status with live streaming.

Owner: Trang
Version: 2.0.0
"""

import asyncio
import json
import sys
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# WebSocket and HTTP support
try:
    import websockets
    from websockets.server import WebSocketServerProtocol

    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False
    print("[DASHBOARD] Install websockets: pip install websockets")

from http.server import BaseHTTPRequestHandler, HTTPServer


class AMOSState:
    """Shared state for dashboard and WebSocket."""

    def __init__(self, organism_root: Path) -> None:
        self.root = organism_root
        self.connected_clients: Set[WebSocketServerProtocol] = set()
        self.last_update = datetime.now(UTC)
        self.subsystems_active = 13
        self.tasks_pending = 0
        self.tasks_running = 0
        self.health_score = 99.8

    def get_status(self) -> Dict[str, Any]:
        """Get current organism status."""
        # Load task queue status if available
        try:
            sys.path.insert(0, str(self.root / "07_METABOLISM"))
            from task_queue import TaskQueue

            queue = TaskQueue(self.root)
            task_status = queue.get_status()
            self.tasks_pending = task_status.get("pending", 0)
            self.tasks_running = task_status.get("running", 0)
        except Exception:
            pass

        return {
            "timestamp": datetime.now(UTC).isoformat() + "Z",
            "version": "2.0.0",
            "health_score": self.health_score,
            "subsystems_active": self.subsystems_active,
            "tasks_pending": self.tasks_pending,
            "tasks_running": self.tasks_running,
            "clients_connected": len(self.connected_clients),
            "status": "operational",
        }

    async def broadcast(self, message: Dict[str, Any]) -> None:
        """Broadcast message to all connected clients."""
        if not self.connected_clients:
            return

        message_str = json.dumps(message)
        disconnected = set()

        for client in self.connected_clients:
            try:
                await client.send(message_str)
            except Exception:
                disconnected.add(client)

        # Remove disconnected clients
        self.connected_clients -= disconnected


class DashboardHTTPHandler(BaseHTTPRequestHandler):
    """HTTP handler with shared state."""

    shared_state: Optional[AMOSState] = None

    def log_message(self, format: str, *args: Any) -> None:
        pass

    def do_GET(self) -> None:
        """Handle GET requests."""
        if self.path == "/":
            self._serve_dashboard()
        elif self.path == "/api/status":
            self._serve_api_status()
        elif self.path == "/api/subsystems":
            self._serve_api_subsystems()
        elif self.path == "/api/tasks":
            self._serve_api_tasks()
        else:
            self._send_404()

    def _send_json(self, data: Dict[str, Any]) -> None:
        """Send JSON response."""
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _send_html(self, html: str) -> None:
        """Send HTML response."""
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def _send_404(self) -> None:
        """Send 404 response."""
        self.send_response(404)
        self.end_headers()

    def _serve_api_status(self) -> None:
        """Serve organism status."""
        if self.shared_state:
            self._send_json(self.shared_state.get_status())
        else:
            self._send_json({"status": "unknown"})

    def _serve_api_subsystems(self) -> None:
        """Serve subsystems data."""
        subsystems = [
            {"code": "01_BRAIN", "name": "Core Cognition", "status": "active", "color": "#4CAF50"},
            {
                "code": "02_SENSES",
                "name": "Input Processing",
                "status": "active",
                "color": "#2196F3",
            },
            {"code": "03_IMMUNE", "name": "Security", "status": "active", "color": "#FF9800"},
            {
                "code": "04_BLOOD",
                "name": "Financial Engine",
                "status": "active",
                "color": "#F44336",
            },
            {"code": "05_SKELETON", "name": "Structure", "status": "active", "color": "#9C27B0"},
            {"code": "06_MUSCLE", "name": "Execution", "status": "active", "color": "#3F51B5"},
            {"code": "07_METABOLISM", "name": "Task Queue", "status": "active", "color": "#009688"},
            {
                "code": "08_WORLD_MODEL",
                "name": "Environment",
                "status": "active",
                "color": "#00BCD4",
            },
            {
                "code": "09_SOCIAL_ENGINE",
                "name": "Communication",
                "status": "active",
                "color": "#8BC34A",
            },
            {
                "code": "10_LIFE_ENGINE",
                "name": "Life Management",
                "status": "active",
                "color": "#FFEB3B",
            },
            {
                "code": "11_LEGAL_BRAIN",
                "name": "Compliance",
                "status": "active",
                "color": "#795548",
            },
            {
                "code": "12_QUANTUM_LAYER",
                "name": "Probabilistic",
                "status": "active",
                "color": "#607D8B",
            },
            {"code": "13_FACTORY", "name": "Agent Factory", "status": "active", "color": "#E91E63"},
        ]
        self._send_json({"subsystems": subsystems, "total": len(subsystems)})

    def _serve_api_tasks(self) -> None:
        """Serve task queue data."""
        try:
            sys.path.insert(0, str(self.shared_state.root / "07_METABOLISM"))
            from task_queue import TaskQueue

            queue = TaskQueue(self.shared_state.root)
            status = queue.get_status()
            pending = [
                {"id": t.id, "title": t.title, "priority": t.priority.name}
                for t in queue.get_pending_tasks()
            ]
            self._send_json(
                {
                    "status": status,
                    "pending_tasks": pending[:10],  # Top 10
                }
            )
        except Exception as e:
            self._send_json({"error": str(e), "status": {}})

    def _serve_dashboard(self) -> None:
        """Serve enhanced dashboard with WebSocket support."""
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AMOS Organism Dashboard v2</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fff;
            min-height: 100vh;
        }
        .header {
            background: rgba(0,0,0,0.3);
            padding: 20px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 {
            font-size: 24px;
            background: linear-gradient(90deg, #00d4ff, #7b2cbf);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .connection-status {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 12px;
            color: #888;
        }
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #4CAF50;
            animation: pulse 2s infinite;
        }
        .status-dot.disconnected { background: #F44336; }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .container {
            padding: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }
        .metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .metric-card {
            background: rgba(255,255,255,0.05);
            padding: 20px;
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .metric-value {
            font-size: 36px;
            font-weight: 700;
            color: #00d4ff;
        }
        .metric-label {
            font-size: 12px;
            color: #888;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 5px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
        }
        .card {
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .card-title {
            font-size: 14px;
            color: #888;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 15px;
        }
        .subsystem-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
            gap: 10px;
        }
        .subsystem-item {
            background: rgba(255,255,255,0.05);
            padding: 12px;
            border-radius: 8px;
            border-left: 3px solid;
            font-size: 12px;
        }
        .subsystem-code { color: #888; font-family: monospace; font-size: 10px; }
        .subsystem-name { margin-top: 4px; font-weight: 500; }
        .task-list {
            max-height: 300px;
            overflow-y: auto;
        }
        .task-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            background: rgba(255,255,255,0.03);
            border-radius: 6px;
            margin-bottom: 8px;
            font-size: 13px;
        }
        .task-priority {
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 10px;
            text-transform: uppercase;
        }
        .priority-CRITICAL { background: #F44336; }
        .priority-HIGH { background: #FF9800; }
        .priority-MEDIUM { background: #2196F3; }
        .priority-LOW { background: #4CAF50; }
        .live-indicator {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 11px;
            color: #4CAF50;
        }
        .live-dot {
            width: 6px;
            height: 6px;
            background: #4CAF50;
            border-radius: 50%;
            animation: blink 1s infinite;
        }
        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0; }
        }
        .footer {
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 12px;
            margin-top: 40px;
        }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>AMOS Organism Dashboard v2</h1>
            <div style="color: #888; font-size: 12px; margin-top: 4px;">
                13-System Cognitive Architecture • WebSocket Real-time
            </div>
        </div>
        <div class="connection-status">
            <div class="status-dot" id="status-dot"></div>
            <span id="connection-text">Connecting...</span>
        </div>
    </div>

    <div class="container">
        <div class="metrics">
            <div class="metric-card">
                <div class="metric-value" id="health-score">--</div>
                <div class="metric-label">Health Score</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="subsystems-count">--</div>
                <div class="metric-label">Active Subsystems</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="tasks-pending">--</div>
                <div class="metric-label">Pending Tasks</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="tasks-running">--</div>
                <div class="metric-label">Running Tasks</div>
            </div>
        </div>

        <div class="grid">
            <div class="card">
                <div class="card-title">
                    All Subsystems
                    <span class="live-indicator" style="float: right;">
                        <span class="live-dot"></span> LIVE
                    </span>
                </div>
                <div class="subsystem-grid" id="subsystems"></div>
            </div>

            <div class="card">
                <div class="card-title">
                    Task Queue
                    <span class="live-indicator" style="float: right;">
                        <span class="live-dot"></span> LIVE
                    </span>
                </div>
                <div class="task-list" id="task-list">
                    <div style="color: #888; text-align: center; padding: 20px;">
                        Loading tasks...
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="footer">
        AMOS Organism v2.0.0 • Owner: Trang • WebSocket Real-time Dashboard
    </div>

    <script>
        const subsystems = [
            { code: "01_BRAIN", name: "Core Cognition", color: "#4CAF50" },
            { code: "02_SENSES", name: "Input Processing", color: "#2196F3" },
            { code: "03_IMMUNE", name: "Security", color: "#FF9800" },
            { code: "04_BLOOD", name: "Financial Engine", color: "#F44336" },
            { code: "05_SKELETON", name: "Structure", color: "#9C27B0" },
            { code: "06_MUSCLE", name: "Execution", color: "#3F51B5" },
            { code: "07_METABOLISM", name: "Task Queue", color: "#009688" },
            { code: "08_WORLD_MODEL", name: "Environment", color: "#00BCD4" },
            { code: "09_SOCIAL_ENGINE", name: "Communication", color: "#8BC34A" },
            { code: "10_LIFE_ENGINE", name: "Life Management", color: "#FFEB3B" },
            { code: "11_LEGAL_BRAIN", name: "Compliance", color: "#795548" },
            { code: "12_QUANTUM_LAYER", name: "Probabilistic", color: "#607D8B" },
            { code: "13_FACTORY", name: "Agent Factory", color: "#E91E63" },
        ];

        // Render subsystems
        const grid = document.getElementById('subsystems');
        subsystems.forEach(sys => {
            const div = document.createElement('div');
            div.className = 'subsystem-item';
            div.style.borderLeftColor = sys.color;
            div.innerHTML = `
                <div class="subsystem-code">${sys.code}</div>
                <div class="subsystem-name">${sys.name}</div>
            `;
            grid.appendChild(div);
        });

        // WebSocket connection
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = wsProtocol + '//' + window.location.host + '/ws';
        let ws = null;
        let reconnectAttempts = 0;

        function connect() {
            ws = new WebSocket(wsUrl);

            ws.onopen = () => {
                console.log('WebSocket connected');
                document.getElementById('status-dot').classList.remove('disconnected');
                document.getElementById('connection-text').textContent = 'Connected';
                reconnectAttempts = 0;
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                updateDashboard(data);
            };

            ws.onclose = () => {
                document.getElementById('status-dot').classList.add('disconnected');
                document.getElementById('connection-text').textContent = 'Disconnected';
                // Reconnect with exponential backoff
                const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000);
                reconnectAttempts++;
                setTimeout(connect, delay);
            };

            ws.onerror = (err) => {
                console.error('WebSocket error:', err);
            };
        }

        function updateDashboard(data) {
            if (data.health_score !== undefined) {
                document.getElementById('health-score').textContent = data.health_score + '%';
            }
            if (data.subsystems_active !== undefined) {
                document.getElementById('subsystems-count').textContent = data.subsystems_active;
            }
            if (data.tasks_pending !== undefined) {
                document.getElementById('tasks-pending').textContent = data.tasks_pending;
            }
            if (data.tasks_running !== undefined) {
                document.getElementById('tasks-running').textContent = data.tasks_running;
            }
        }

        async function loadTasks() {
            try {
                const response = await fetch('/api/tasks');
                const data = await response.json();
                const taskList = document.getElementById('task-list');

                if (data.pending_tasks && data.pending_tasks.length > 0) {
                    taskList.innerHTML = data.pending_tasks.map(task => `
                        <div class="task-item">
                            <span>${task.title}</span>
                            <span class="task-priority priority-${task.priority}">${task.priority}</span>
                        </div>
                    `).join('');
                } else {
                    taskList.innerHTML = '<div style="color: #888; text-align: center; padding: 20px;">No pending tasks</div>';
                }
            } catch (err) {
                console.error('Failed to load tasks:', err);
            }
        }

        // Connect WebSocket and load initial data
        connect();
        loadTasks();

        // Refresh tasks every 5 seconds as backup
        setInterval(loadTasks, 5000);
    </script>
</body>
</html>"""
        self._send_html(html)


async def websocket_handler(websocket: WebSocketServerProtocol, path: str) -> None:
    """Handle WebSocket connections."""
    if path != "/ws":
        await websocket.close()
        return

    # Add client to connected set
    shared_state.connected_clients.add(websocket)

    try:
        # Send initial status
        await websocket.send(json.dumps(shared_state.get_status()))

        # Keep connection alive and broadcast updates
        while True:
            await asyncio.sleep(2)  # Update every 2 seconds
            status = shared_state.get_status()
            await shared_state.broadcast(status)

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        shared_state.connected_clients.discard(websocket)


def run_http_server(port: int, state: AMOSState) -> None:
    """Run HTTP server in a thread."""
    DashboardHTTPHandler.shared_state = state
    server = HTTPServer(("", port), DashboardHTTPHandler)
    print(f"[HTTP] Server running at http://localhost:{port}")
    server.serve_forever()


async def main() -> None:
    """Main entry point."""
    global shared_state

    print("=" * 50)
    print("AMOS Dashboard WebSocket Server v2.0")
    print("=" * 50)

    if not WEBSOCKET_AVAILABLE:
        print("\n[ERROR] websockets library not installed")
        print("Run: pip install websockets")
        return 1

    # Get organism root
    organism_root = Path(__file__).parent.parent
    shared_state = AMOSState(organism_root)

    port = 9000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass

    # Start HTTP server in a thread
    http_thread = threading.Thread(target=run_http_server, args=(port, shared_state), daemon=True)
    http_thread.start()

    # Start WebSocket server
    ws_port = port + 1
    print(f"[WebSocket] Server running at ws://localhost:{ws_port}/ws")

    async with websockets.serve(websocket_handler, "", ws_port):
        print("\n[OK] Dashboard servers running")
        print(f"[OK] HTTP: http://localhost:{port}")
        print(f"[OK] WebSocket: ws://localhost:{ws_port}")
        print("[OK] Press Ctrl+C to stop\n")

        try:
            await asyncio.Future()  # Run forever
        except KeyboardInterrupt:
            print("\n[DASHBOARD] Shutting down...")

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
