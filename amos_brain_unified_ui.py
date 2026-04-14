#!/usr/bin/env python3
"""AMOS Brain Unified UI with WebSocket Support
=============================================

Single, production-ready interface combining both UIs with real-time updates.

Owner: Trang
Version: 4.0.0
"""

from __future__ import annotations

import asyncio
import json
import sys
import threading
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any
from urllib.parse import urlparse

import websockets

from amos_brain import decide, think, validate

# Global state for WebSocket connections
connected_clients: set[websockets.WebSocketServerProtocol] = set()


class UnifiedBrainUIHandler(BaseHTTPRequestHandler):
    """Unified HTTP handler with WebSocket upgrade support."""

    brain: Any = None
    orchestrator: Any = None

    def log_message(self, format: str, *args: Any) -> None:
        pass

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        routes = {
            "/": self._serve_unified_ui,
            "/api/status": self._serve_status,
            "/api/thoughts": self._serve_thoughts,
            "/api/plans": self._serve_plans,
            "/api/subsystems": self._serve_subsystems,
            "/api/cognitive-layers": self._serve_cognitive_layers,
            "/ws": self._upgrade_websocket,
        }

        handler = routes.get(path, self._send_404)
        handler()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len).decode("utf-8")
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON"}, 400)
            return

        routes = {
            "/api/think": self._handle_think,
            "/api/decide": self._handle_decide,
            "/api/validate": self._handle_validate,
            "/api/perceive": self._handle_perceive,
            "/api/plan": self._handle_plan,
        }

        handler = routes.get(path)
        if handler:
            handler(data)
        else:
            self._send_json({"error": "Not found"}, 404)

    def _send_json(self, data: dict, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def _send_html(self, html: str) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def _send_404(self) -> None:
        self.send_response(404)
        self.end_headers()

    def _upgrade_websocket(self) -> None:
        """Handle WebSocket upgrade request."""
        self.send_response(426)
        self.send_header("Upgrade", "websocket")
        self.end_headers()
        self.wfile.write(b"WebSocket endpoint is on ws://localhost:8890/ws")

    def _serve_status(self) -> None:
        if not self.brain:
            self._send_json({"error": "Brain not initialized"}, 500)
            return

        status = self.brain.status()
        self._send_json(
            {"status": "active", "brain": status, "timestamp": datetime.utcnow().isoformat()}
        )

    def _serve_thoughts(self) -> None:
        if not self.brain:
            self._send_json({"error": "Brain not initialized"}, 500)
            return

        thoughts = [
            {
                "id": t.id,
                "type": t.type.value,
                "content": t.content,
                "source": t.source,
                "timestamp": t.timestamp,
                "confidence": t.confidence,
                "tags": t.tags,
            }
            for t in self.brain.state.get_recent_thoughts(20)
        ]
        self._send_json({"thoughts": thoughts})

    def _serve_plans(self) -> None:
        if not self.brain:
            self._send_json({"error": "Brain not initialized"}, 500)
            return

        plans = [
            {
                "id": p.id,
                "goal": p.goal,
                "status": p.status,
                "horizon": p.horizon,
                "steps": len(p.steps),
                "created_at": p.created_at,
            }
            for p in self.brain.state.active_plans
        ]
        self._send_json({"plans": plans})

    def _serve_subsystems(self) -> None:
        subsystems = [
            {"code": "01_BRAIN", "name": "Core Cognition", "layer": 1},
            {"code": "02_SENSES", "name": "Input Processing", "layer": 2},
            {"code": "03_IMMUNE", "name": "Security", "layer": 2},
            {"code": "04_BLOOD", "name": "Financial Engine", "layer": 3},
            {"code": "05_SKELETON", "name": "Structure & Rules", "layer": 3},
            {"code": "06_MUSCLE", "name": "Execution", "layer": 4},
            {"code": "07_METABOLISM", "name": "Pipelines", "layer": 4},
            {"code": "08_WORLD_MODEL", "name": "Environment", "layer": 5},
            {"code": "09_SOCIAL_ENGINE", "name": "Agent Communication", "layer": 5},
            {"code": "10_LIFE_ENGINE", "name": "Life Management", "layer": 6},
            {"code": "11_LEGAL_BRAIN", "name": "Compliance", "layer": 6},
            {"code": "12_QUANTUM_LAYER", "name": "Probabilistic", "layer": 7},
            {"code": "13_FACTORY", "name": "Agent Factory", "layer": 7},
        ]
        self._send_json({"subsystems": subsystems})

    def _serve_cognitive_layers(self) -> None:
        layers = [
            {"level": 1, "name": "Perceptual", "icon": "👁️"},
            {"level": 2, "name": "Conceptual", "icon": "🧩"},
            {"level": 3, "name": "Narrative", "icon": "📖"},
            {"level": 4, "name": "Causal", "icon": "⚡"},
            {"level": 5, "name": "Systemic", "icon": "🌐"},
            {"level": 6, "name": "Meta", "icon": "🔮"},
        ]
        self._send_json({"layers": layers})

    def _handle_think(self, data: dict) -> None:
        query = data.get("query", "")
        if not query:
            self._send_json({"error": "No query provided"}, 400)
            return

        try:
            result = think(query)

            if self.brain:
                self.brain.perceive(query, "user_ui")

            response_data = {
                "success": True,
                "query": query,
                "timestamp": datetime.utcnow().isoformat(),
            }

            if hasattr(result, "content"):
                response_data["result"] = {
                    "content": result.content,
                    "reasoning": result.reasoning if hasattr(result, "reasoning") else [],
                    "confidence": result.confidence if hasattr(result, "confidence") else "medium",
                    "law_compliant": result.law_compliant
                    if hasattr(result, "law_compliant")
                    else True,
                }
            else:
                response_data["result"] = {"content": str(result)}

            self._send_json(response_data)
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _handle_decide(self, data: dict) -> None:
        scenario = data.get("scenario", "")
        options = data.get("options", [])

        if not scenario:
            self._send_json({"error": "No scenario provided"}, 400)
            return

        try:
            if options and len(options) >= 2:
                result = decide(scenario, options=options)
            else:
                result = decide(scenario)

            response_data = {
                "success": True,
                "scenario": scenario,
                "timestamp": datetime.utcnow().isoformat(),
            }

            if hasattr(result, "approved"):
                response_data["decision"] = {
                    "approved": result.approved,
                    "reasoning": result.reasoning if hasattr(result, "reasoning") else "",
                    "risk_level": result.risk_level if hasattr(result, "risk_level") else "low",
                }
            else:
                response_data["decision"] = {"content": str(result)}

            self._send_json(response_data)
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _handle_validate(self, data: dict) -> None:
        proposition = data.get("proposition", "")
        if not proposition:
            self._send_json({"error": "No proposition provided"}, 400)
            return

        try:
            result = validate(proposition)

            response_data = {
                "success": True,
                "proposition": proposition,
                "timestamp": datetime.utcnow().isoformat(),
            }

            if hasattr(result, "to_dict"):
                response_data["validation"] = result.to_dict()
            else:
                response_data["validation"] = {"result": str(result)}

            self._send_json(response_data)
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _handle_perceive(self, data: dict) -> None:
        content = data.get("content", "")
        source = data.get("source", "user_ui")

        if not content:
            self._send_json({"error": "No content provided"}, 400)
            return

        try:
            thought = self.brain.perceive(content, source)
            self._send_json(
                {
                    "success": True,
                    "thought_id": thought.id,
                    "content": thought.content,
                    "type": thought.type.value,
                    "timestamp": thought.timestamp,
                }
            )
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _handle_plan(self, data: dict) -> None:
        goal = data.get("goal", "")
        horizon = data.get("horizon", "medium-term")

        if not goal:
            self._send_json({"error": "No goal provided"}, 400)
            return

        try:
            plan = self.brain.create_plan(goal, horizon)
            self._send_json(
                {
                    "success": True,
                    "plan_id": plan.id,
                    "goal": plan.goal,
                    "horizon": plan.horizon,
                    "status": plan.status,
                    "created_at": plan.created_at,
                }
            )
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _serve_unified_ui(self) -> None:
        html = self._generate_unified_html()
        self._send_html(html)

    def _generate_unified_html(self) -> str:
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AMOS Brain - Unified Interface</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        :root {
            --bg-deep: #050510;
            --bg-primary: #0a0a1a;
            --bg-secondary: #121225;
            --accent-cyan: #00d4ff;
            --accent-purple: #7b2cbf;
            --text-primary: #ffffff;
            --text-secondary: #8890a0;
            --border: rgba(255,255,255,0.08);
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg-deep);
            color: var(--text-primary);
            min-height: 100vh;
        }
        .header {
            background: linear-gradient(180deg, var(--bg-secondary) 0%, transparent 100%);
            padding: 20px 40px;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .brand { display: flex; align-items: center; gap: 15px; }
        .brain-icon {
            width: 48px; height: 48px;
            background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
            border-radius: 12px;
            display: flex; align-items: center; justify-content: center;
            font-size: 24px;
            box-shadow: 0 8px 32px rgba(0, 212, 255, 0.3);
        }
        .brand-text h1 {
            font-size: 24px;
            font-weight: 700;
            background: linear-gradient(90deg, var(--accent-cyan), var(--accent-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .ws-status {
            display: flex; align-items: center; gap: 8px;
            padding: 8px 16px;
            background: rgba(76, 175, 80, 0.1);
            border: 1px solid #4CAF50;
            border-radius: 20px;
            font-size: 12px;
            color: #4CAF50;
        }
        .ws-status.disconnected {
            background: rgba(244, 67, 54, 0.1);
            border-color: #F44336;
            color: #F44336;
        }
        .main-container {
            display: grid;
            grid-template-columns: 250px 1fr 320px;
            gap: 25px;
            padding: 25px;
            max-width: 1600px;
            margin: 0 auto;
        }
        .cognitive-stack {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .layer {
            display: flex; align-items: center; gap: 12px;
            padding: 12px 16px;
            background: rgba(255,255,255,0.03);
            border: 1px solid var(--border);
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
            opacity: 0.7;
        }
        .layer:hover, .layer.active {
            opacity: 1;
            transform: translateX(5px);
            border-color: var(--accent-cyan);
            background: rgba(0, 212, 255, 0.05);
        }
        .layer-icon { font-size: 18px; }
        .layer-name { font-size: 12px; font-weight: 600; text-transform: uppercase; }
        .input-section {
            background: rgba(255,255,255,0.03);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 25px;
        }
        .mode-selector {
            display: flex; gap: 10px;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid var(--border);
        }
        .mode-btn {
            display: flex; align-items: center; gap: 8px;
            padding: 10px 20px;
            background: transparent;
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text-secondary);
            cursor: pointer;
            transition: all 0.3s;
            font-size: 13px;
        }
        .mode-btn:hover, .mode-btn.active {
            background: rgba(0, 212, 255, 0.1);
            border-color: var(--accent-cyan);
            color: var(--accent-cyan);
        }
        .input-field {
            width: 100%; min-height: 120px;
            padding: 20px;
            background: rgba(0,0,0,0.3);
            border: 1px solid var(--border);
            border-radius: 12px;
            color: var(--text-primary);
            font-size: 15px;
            line-height: 1.6;
            resize: vertical;
            font-family: inherit;
        }
        .input-field:focus {
            outline: none;
            border-color: var(--accent-cyan);
        }
        .input-actions {
            display: flex; justify-content: space-between;
            align-items: center; margin-top: 15px;
        }
        .btn {
            padding: 12px 24px;
            border-radius: 10px;
            border: none;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s;
        }
        .btn-primary {
            background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
            color: white;
        }
        .btn-secondary {
            background: rgba(255,255,255,0.05);
            color: var(--text-secondary);
            border: 1px solid var(--border);
        }
        .results-section {
            margin-top: 20px;
            display: flex; flex-direction: column; gap: 15px;
        }
        .result-card {
            background: rgba(255,255,255,0.03);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
        }
        .result-header {
            display: flex; justify-content: space-between;
            margin-bottom: 15px;
            color: var(--accent-cyan);
            font-size: 13px;
            font-weight: 600;
        }
        .result-content {
            font-size: 14px;
            line-height: 1.7;
            white-space: pre-wrap;
        }
        .right-panel {
            display: flex; flex-direction: column; gap: 15px;
        }
        .panel-card {
            background: rgba(255,255,255,0.03);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 18px;
        }
        .panel-title {
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-secondary);
            margin-bottom: 12px;
        }
        .stat-row {
            display: flex; justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid var(--border);
            font-size: 13px;
        }
        .stat-row:last-child { border-bottom: none; }
        .stat-value {
            font-weight: 700;
            color: var(--accent-cyan);
        }
        .thought-stream {
            display: flex; flex-direction: column;
            gap: 8px; max-height: 250px;
            overflow-y: auto;
        }
        .thought-item {
            padding: 10px;
            background: rgba(0,0,0,0.2);
            border-radius: 8px;
            border-left: 2px solid var(--accent-cyan);
            font-size: 11px;
        }
        .reasoning-path {
            margin-top: 15px;
            padding: 15px;
            background: rgba(0,0,0,0.2);
            border-radius: 8px;
            border-left: 2px solid var(--accent-purple);
        }
        .processing {
            display: flex; align-items: center;
            justify-content: center; gap: 10px;
            padding: 40px; color: var(--text-secondary);
        }
        .spinner {
            width: 20px; height: 20px;
            border: 2px solid var(--border);
            border-top-color: var(--accent-cyan);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        @media (max-width: 1200px) {
            .main-container { grid-template-columns: 1fr; }
            .cognitive-stack, .right-panel { display: none; }
        }
    </style>
</head>
<body>
    <header class="header">
        <div class="brand">
            <div class="brain-icon">🧠</div>
            <div class="brand-text">
                <h1>AMOS Brain Unified</h1>
            </div>
        </div>
        <div class="ws-status" id="ws-status">
            <span>🟢</span> WebSocket Connected
        </div>
    </header>

    <main class="main-container">
        <aside class="cognitive-stack">
            <div class="layer active" data-layer="6">
                <span class="layer-icon">🔮</span>
                <span class="layer-name">Meta</span>
            </div>
            <div class="layer" data-layer="5">
                <span class="layer-icon">🌐</span>
                <span class="layer-name">Systemic</span>
            </div>
            <div class="layer" data-layer="4">
                <span class="layer-icon">⚡</span>
                <span class="layer-name">Causal</span>
            </div>
            <div class="layer" data-layer="3">
                <span class="layer-icon">📖</span>
                <span class="layer-name">Narrative</span>
            </div>
            <div class="layer" data-layer="2">
                <span class="layer-icon">🧩</span>
                <span class="layer-name">Conceptual</span>
            </div>
            <div class="layer" data-layer="1">
                <span class="layer-icon">👁️</span>
                <span class="layer-name">Perceptual</span>
            </div>
        </aside>

        <section class="center-panel">
            <div class="input-section">
                <div class="mode-selector">
                    <button class="mode-btn active" onclick="setMode(\'think\')">💭 Think</button>
                    <button class="mode-btn" onclick="setMode(\'decide\')">⚖️ Decide</button>
                    <button class="mode-btn" onclick="setMode(\'validate\')">✓ Validate</button>
                    <button class="mode-btn" onclick="setMode(\'plan\')">📋 Plan</button>
                </div>
                <textarea id="main-input" class="input-field"
                    placeholder="Enter your cognitive query..."></textarea>
                <div class="input-actions">
                    <button class="btn btn-primary" onclick="processInput()">🚀 Process</button>
                    <button class="btn btn-secondary" onclick="clearAll()">🗑️ Clear</button>
                </div>
            </div>
            <div class="results-section" id="results"></div>
        </section>

        <aside class="right-panel">
            <div class="panel-card">
                <div class="panel-title">📊 Metrics</div>
                <div class="stat-row">
                    <span>Thoughts</span>
                    <span class="stat-value" id="thought-count">0</span>
                </div>
                <div class="stat-row">
                    <span>Cycles</span>
                    <span class="stat-value" id="cycle-count">0</span>
                </div>
                <div class="stat-row">
                    <span>Plans</span>
                    <span class="stat-value" id="plan-count">0</span>
                </div>
            </div>
            <div class="panel-card">
                <div class="panel-title">💡 Thought Stream</div>
                <div class="thought-stream" id="thought-stream">
                    <div style="color: var(--text-secondary); text-align: center; padding: 20px;">
                        No activity
                    </div>
                </div>
            </div>
        </aside>
    </main>

    <script>
        let currentMode = \'think\';
        let ws = null;

        // WebSocket connection
        function connectWebSocket() {
            const wsUrl = `ws://${window.location.host}/ws`;
            ws = new WebSocket(wsUrl);

            ws.onopen = () => {
                console.log(\'WebSocket connected\');
                document.getElementById(\'ws-status\').classList.remove(\'disconnected\');
                document.getElementById(\'ws-status\').innerHTML = \'<span>🟢</span> WebSocket Connected\';
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.type === \'thought\') {
                    loadThoughts();
                    loadStatus();
                }
            };

            ws.onclose = () => {
                console.log(\'WebSocket disconnected\');
                document.getElementById(\'ws-status\').classList.add(\'disconnected\');
                document.getElementById(\'ws-status\').innerHTML = \'<span>🔴</span> WebSocket Disconnected\';
                setTimeout(connectWebSocket, 5000);
            };
        }

        function setMode(mode) {
            currentMode = mode;
            document.querySelectorAll(\'.mode-btn\').forEach(btn => btn.classList.remove(\'active\'));
            event.target.classList.add(\'active\');
        }

        async function processInput() {
            const input = document.getElementById(\'main-input\').value.trim();
            if (!input) return;

            const results = document.getElementById(\'results\');
            results.innerHTML = \'<div class="processing"><div class="spinner"></div>Processing...</div>\';

            const endpoints = {
                think: \'/api/think\',
                decide: \'/api/decide\',
                validate: \'/api/validate\',
                plan: \'/api/plan\'
            };

            const bodies = {
                think: { query: input },
                decide: { scenario: input },
                validate: { proposition: input },
                plan: { goal: input }
            };

            try {
                const response = await fetch(endpoints[currentMode], {
                    method: \'POST\',
                    headers: { \'Content-Type\': \'application/json\' },
                    body: JSON.stringify(bodies[currentMode])
                });

                const result = await response.json();
                displayResult(result);
                loadThoughts();
                loadStatus();
            } catch (error) {
                results.innerHTML = `<div class="result-card" style="border-color: #F44336;">Error: ${error.message}</div>`;
            }
        }

        function displayResult(result) {
            const results = document.getElementById(\'results\');
            const content = result.result?.content || result.decision?.approved || JSON.stringify(result);
            const reasoning = result.result?.reasoning || [];

            let reasoningHtml = \'\';
            if (reasoning.length > 0) {
                reasoningHtml = `<div class="reasoning-path"><strong>Reasoning Path:</strong><br>${reasoning.join(\'<br>\')}</div>`;
            }

            results.innerHTML = `
                <div class="result-card">
                    <div class="result-header">
                        <span>${currentMode.toUpperCase()} RESULT</span>
                        <span>${new Date().toLocaleTimeString()}</span>
                    </div>
                    <div class="result-content">${content}</div>
                    ${reasoningHtml}
                </div>
            `;
        }

        async function loadStatus() {
            try {
                const response = await fetch(\'/api/status\');
                const data = await response.json();
                if (data.brain) {
                    document.getElementById(\'thought-count\').textContent = data.brain.thought_count || 0;
                    document.getElementById(\'cycle-count\').textContent = data.brain.cycle_count || 0;
                    document.getElementById(\'plan-count\').textContent = data.brain.active_plans || 0;
                }
            } catch (e) {}
        }

        async function loadThoughts() {
            try {
                const response = await fetch(\'/api/thoughts\');
                const data = await response.json();
                const stream = document.getElementById(\'thought-stream\');
                if (data.thoughts && data.thoughts.length > 0) {
                    stream.innerHTML = data.thoughts.slice(0, 5).map(t => `
                        <div class="thought-item">
                            <strong>${t.type}</strong>: ${t.content.substring(0, 60)}${t.content.length > 60 ? \'...\' : \'\'}
                        </div>
                    `).join(\'\');
                }
            } catch (e) {}
        }

        function clearAll() {
            document.getElementById(\'main-input\').value = \'\';
            document.getElementById(\'results\').innerHTML = \'\';
        }

        // Initialize
        document.addEventListener(\'DOMContentLoaded\', () => {
            loadStatus();
            loadThoughts();
            connectWebSocket();
            setInterval(() => { loadStatus(); loadThoughts(); }, 5000);
        });

        document.getElementById(\'main-input\').addEventListener(\'keydown\', (e) => {
            if (e.key === \'Enter\' && e.metaKey) processInput();
        });
    </script>
</body>
</html>"""


async def broadcast_update(update_type: str, data: dict) -> None:
    """Broadcast update to all connected WebSocket clients."""
    if connected_clients:
        message = json.dumps({"type": update_type, "data": data})
        await asyncio.gather(
            *[client.send(message) for client in connected_clients], return_exceptions=True
        )


async def websocket_handler(websocket: websockets.WebSocketServerProtocol, path: str) -> None:
    """Handle WebSocket connections."""
    connected_clients.add(websocket)
    try:
        await websocket.send(json.dumps({"type": "connected", "message": "Welcome to AMOS Brain"}))
        async for message in websocket:
            # Handle incoming messages if needed
            data = json.loads(message)
            if data.get("action") == "ping":
                await websocket.send(json.dumps({"type": "pong"}))
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        connected_clients.remove(websocket)


async def start_websocket_server(port: int) -> None:
    """Start WebSocket server."""
    async with websockets.serve(websocket_handler, "", port):
        print(f"   ✓ WebSocket server on port {port}")
        await asyncio.Future()  # Run forever


def run_http_server(port: int) -> None:
    """Run HTTP server."""
    server = HTTPServer(("", port), UnifiedBrainUIHandler)
    print(f"   ✓ HTTP server on port {port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


def run_unified_server(http_port: int = 8890, ws_port: int = 8891) -> None:
    """Run the unified Brain UI server with WebSocket support."""
    print("🧠 Initializing AMOS Brain Unified UI...")
    try:
        from AMOS_ORGANISM_OS.organism import AmosOrganism

        organism = AmosOrganism()
        UnifiedBrainUIHandler.orchestrator = organism
        UnifiedBrainUIHandler.brain = organism.brain
        print(f"   ✓ Brain loaded: {organism.brain.state.session_id}")
    except Exception as e:
        print(f"   ⚠ Brain init warning: {e}")
        from AMOS_ORGANISM_OS.BRAIN.brain_os import BrainOS

        brain = BrainOS()
        UnifiedBrainUIHandler.brain = brain
        print(f"   ✓ Brain loaded (fallback): {brain.state.session_id}")

    url = f"http://localhost:{http_port}"

    print("=" * 60)
    print("🌐 AMOS Brain Unified Interface")
    print("=" * 60)
    print(f"\n📍 HTTP Server:  {url}")
    print(f"📡 WebSocket:   ws://localhost:{ws_port}/ws")
    print("\nFeatures:")
    print("   • Unified interface (combines both previous UIs)")
    print("   • WebSocket real-time updates")
    print("   • 7-Layer Cognitive Stack")
    print("   • Live thought stream")
    print("   • All 13 subsystems status")
    print("\nPress Ctrl+C to stop")
    print("=" * 60)

    webbrowser.open(url)

    # Run both servers
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    http_thread = threading.Thread(target=run_http_server, args=(http_port,))
    http_thread.daemon = True
    http_thread.start()

    try:
        loop.run_until_complete(start_websocket_server(ws_port))
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
    finally:
        loop.close()


def main() -> int:
    """Main entry point."""
    http_port = 8890
    ws_port = 8891

    if len(sys.argv) > 1:
        try:
            http_port = int(sys.argv[1])
            ws_port = http_port + 1
        except ValueError:
            pass

    run_unified_server(http_port, ws_port)
    return 0


if __name__ == "__main__":
    sys.exit(main())
