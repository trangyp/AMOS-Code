#!/usr/bin/env python3
"""AMOS Brain Complete UI - Production Server
==========================================

Single consolidated server combining all UI features.
Replaces: amos_brain_ui.py, amos_brain_enhanced_ui.py, amos_brain_unified_ui.py

Owner: Trang
Version: 5.0.0
"""

from __future__ import annotations

import json
import sys
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any
from urllib.parse import urlparse

from amos_brain import decide, think, validate


class CompleteBrainUIHandler(BaseHTTPRequestHandler):
    """Complete HTTP handler with all UI features."""

    brain: Any = None
    orchestrator: Any = None

    def log_message(self, format: str, *args: Any) -> None:
        pass

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        routes = {
            "/": self._serve_complete_ui,
            "/api/status": self._serve_status,
            "/api/thoughts": self._serve_thoughts,
            "/api/plans": self._serve_plans,
            "/api/subsystems": self._serve_subsystems,
            "/api/layers": self._serve_layers,
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

    def _serve_status(self) -> None:
        if not self.brain:
            self._send_json({"error": "Brain not initialized"}, 500)
            return
        self._send_json(
            {
                "status": "active",
                "brain": self.brain.status(),
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    def _serve_thoughts(self) -> None:
        if not self.brain:
            self._send_json({"error": "Brain not initialized"}, 500)
            return
        thoughts = [
            {"id": t.id, "type": t.type.value, "content": t.content, "timestamp": t.timestamp}
            for t in self.brain.state.get_recent_thoughts(20)
        ]
        self._send_json({"thoughts": thoughts})

    def _serve_plans(self) -> None:
        if not self.brain:
            self._send_json({"error": "Brain not initialized"}, 500)
            return
        plans = [
            {"id": p.id, "goal": p.goal, "status": p.status, "steps": len(p.steps)}
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

    def _serve_layers(self) -> None:
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
            self._send_json({"error": "No query"}, 400)
            return
        try:
            result = think(query)
            if self.brain:
                self.brain.perceive(query, "user_ui")
            response = {"success": True, "query": query, "timestamp": datetime.utcnow().isoformat()}
            if hasattr(result, "content"):
                response["result"] = {
                    "content": result.content,
                    "reasoning": result.reasoning if hasattr(result, "reasoning") else [],
                    "confidence": result.confidence if hasattr(result, "confidence") else "medium",
                    "law_compliant": result.law_compliant
                    if hasattr(result, "law_compliant")
                    else True,
                }
            else:
                response["result"] = {"content": str(result)}
            self._send_json(response)
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _handle_decide(self, data: dict) -> None:
        scenario = data.get("scenario", "")
        options = data.get("options", [])
        if not scenario:
            self._send_json({"error": "No scenario"}, 400)
            return
        try:
            if options and len(options) >= 2:
                result = decide(scenario, options=options)
            else:
                result = decide(scenario)
            response = {
                "success": True,
                "scenario": scenario,
                "timestamp": datetime.utcnow().isoformat(),
            }
            if hasattr(result, "approved"):
                response["decision"] = {
                    "approved": result.approved,
                    "reasoning": result.reasoning if hasattr(result, "reasoning") else "",
                    "risk_level": result.risk_level if hasattr(result, "risk_level") else "low",
                }
            else:
                response["decision"] = {"content": str(result)}
            self._send_json(response)
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _handle_validate(self, data: dict) -> None:
        proposition = data.get("proposition", "")
        if not proposition:
            self._send_json({"error": "No proposition"}, 400)
            return
        try:
            result = validate(proposition)
            self._send_json(
                {
                    "success": True,
                    "proposition": proposition,
                    "timestamp": datetime.utcnow().isoformat(),
                    "validation": {"result": str(result)},
                }
            )
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _handle_plan(self, data: dict) -> None:
        goal = data.get("goal", "")
        horizon = data.get("horizon", "medium-term")
        if not goal:
            self._send_json({"error": "No goal"}, 400)
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

    def _serve_complete_ui(self) -> None:
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AMOS Brain - Complete Interface</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        :root {
            --bg: #0a0a1a;
            --bg-card: rgba(255,255,255,0.03);
            --accent: #00d4ff;
            --accent2: #7b2cbf;
            --text: #ffffff;
            --text2: #8890a0;
            --border: rgba(255,255,255,0.08);
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
        }
        .header {
            background: linear-gradient(180deg, #121225 0%, transparent 100%);
            padding: 20px 30px;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .brand {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .brain-icon {
            width: 48px; height: 48px;
            background: linear-gradient(135deg, var(--accent), var(--accent2));
            border-radius: 12px;
            display: flex; align-items: center; justify-content: center;
            font-size: 24px;
            box-shadow: 0 8px 32px rgba(0, 212, 255, 0.3);
        }
        .brand h1 {
            font-size: 24px;
            background: linear-gradient(90deg, var(--accent), var(--accent2));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .main {
            display: grid;
            grid-template-columns: 220px 1fr 300px;
            gap: 20px;
            padding: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }
        .sidebar {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .layer {
            display: flex; align-items: center; gap: 10px;
            padding: 12px;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 10px;
            font-size: 12px;
            opacity: 0.7;
            transition: all 0.3s;
        }
        .layer:hover, .layer.active {
            opacity: 1;
            border-color: var(--accent);
            transform: translateX(5px);
        }
        .center {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 25px;
        }
        .modes {
            display: flex; gap: 10px;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid var(--border);
        }
        .mode-btn {
            padding: 10px 20px;
            background: transparent;
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text2);
            cursor: pointer;
            transition: all 0.3s;
        }
        .mode-btn:hover, .mode-btn.active {
            background: rgba(0, 212, 255, 0.1);
            border-color: var(--accent);
            color: var(--accent);
        }
        textarea {
            width: 100%; min-height: 120px;
            padding: 15px;
            background: rgba(0,0,0,0.3);
            border: 1px solid var(--border);
            border-radius: 10px;
            color: var(--text);
            font-size: 14px;
            resize: vertical;
        }
        textarea:focus { outline: none; border-color: var(--accent); }
        .actions {
            display: flex; gap: 10px;
            margin-top: 15px;
        }
        .btn {
            padding: 12px 24px;
            border-radius: 8px;
            border: none;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
        }
        .btn-primary {
            background: linear-gradient(135deg, var(--accent), var(--accent2));
            color: white;
        }
        .results {
            margin-top: 20px;
            display: flex; flex-direction: column; gap: 15px;
        }
        .result-card {
            background: rgba(0,0,0,0.2);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 15px;
        }
        .right-panel {
            display: flex; flex-direction: column; gap: 15px;
        }
        .panel {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 15px;
        }
        .panel h3 {
            font-size: 12px;
            text-transform: uppercase;
            color: var(--text2);
            margin-bottom: 12px;
        }
        .stat {
            display: flex; justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid var(--border);
            font-size: 13px;
        }
        .thought-stream {
            display: flex; flex-direction: column;
            gap: 8px; max-height: 200px;
            overflow-y: auto;
        }
        .thought-item {
            padding: 10px;
            background: rgba(0,0,0,0.2);
            border-radius: 6px;
            border-left: 2px solid var(--accent);
            font-size: 11px;
        }
        @media (max-width: 1000px) {
            .main { grid-template-columns: 1fr; }
            .sidebar, .right-panel { display: none; }
        }
    </style>
</head>
<body>
    <header class="header">
        <div class="brand">
            <div class="brain-icon">🧠</div>
            <h1>AMOS Brain Complete</h1>
        </div>
    </header>
    <main class="main">
        <aside class="sidebar">
            <div class="layer active"><span>🔮</span> Meta</div>
            <div class="layer"><span>🌐</span> Systemic</div>
            <div class="layer"><span>⚡</span> Causal</div>
            <div class="layer"><span>📖</span> Narrative</div>
            <div class="layer"><span>🧩</span> Conceptual</div>
            <div class="layer"><span>👁️</span> Perceptual</div>
        </aside>
        <section class="center">
            <div class="modes">
                <button class="mode-btn active" onclick="setMode(\'think\')">💭 Think</button>
                <button class="mode-btn" onclick="setMode(\'decide\')">⚖️ Decide</button>
                <button class="mode-btn" onclick="setMode(\'validate\')">✓ Validate</button>
                <button class="mode-btn" onclick="setMode(\'plan\')">📋 Plan</button>
            </div>
            <textarea id="input" placeholder="Enter your cognitive query..."></textarea>
            <div class="actions">
                <button class="btn btn-primary" onclick="process()">🚀 Process</button>
                <button class="btn" onclick="clearAll()" style="background:rgba(255,255,255,0.05);color:var(--text2);">🗑️ Clear</button>
            </div>
            <div class="results" id="results"></div>
        </section>
        <aside class="right-panel">
            <div class="panel">
                <h3>📊 Metrics</h3>
                <div class="stat"><span>Thoughts</span><span id="thought-count" style="color:var(--accent);font-weight:700;">0</span></div>
                <div class="stat"><span>Cycles</span><span id="cycle-count" style="color:var(--accent);font-weight:700;">0</span></div>
                <div class="stat"><span>Plans</span><span id="plan-count" style="color:var(--accent);font-weight:700;">0</span></div>
            </div>
            <div class="panel">
                <h3>💡 Thought Stream</h3>
                <div class="thought-stream" id="thoughts">
                    <div style="color:var(--text2);text-align:center;padding:10px;">No activity</div>
                </div>
            </div>
        </aside>
    </main>
    <script>
        let mode = \'think\';
        function setMode(m) {
            mode = m;
            document.querySelectorAll(\'.mode-btn\').forEach(b => b.classList.remove(\'active\'));
            event.target.classList.add(\'active\');
        }
        async function process() {
            const input = document.getElementById(\'input\').value.trim();
            if (!input) return;
            const results = document.getElementById(\'results\');
            results.innerHTML = \'<div style="padding:20px;text-align:center;color:var(--text2);">Processing...</div>\';
            const endpoints = {think: \'/api/think\', decide: \'/api/decide\', validate: \'/api/validate\', plan: \'/api/plan\'};
            const bodies = {think: {query: input}, decide: {scenario: input}, validate: {proposition: input}, plan: {goal: input}};
            try {
                const res = await fetch(endpoints[mode], {
                    method: \'POST\',
                    headers: {\'Content-Type\': \'application/json\'},
                    body: JSON.stringify(bodies[mode])
                });
                const data = await res.json();
                let content = data.result?.content || data.decision?.approved || JSON.stringify(data);
                results.innerHTML = `<div class="result-card"><div style="color:var(--accent);font-size:12px;font-weight:600;margin-bottom:10px;">${mode.toUpperCase()} RESULT</div><div style="white-space:pre-wrap;font-size:13px;line-height:1.6;">${content}</div></div>`;
                loadStats();
            } catch (e) {
                results.innerHTML = `<div class="result-card" style="border-color:#F44336;">Error: ${e.message}</div>`;
            }
        }
        async function loadStats() {
            try {
                const res = await fetch(\'/api/status\');
                const data = await res.json();
                if (data.brain) {
                    document.getElementById(\'thought-count\').textContent = data.brain.thought_count || 0;
                    document.getElementById(\'cycle-count\').textContent = data.brain.cycle_count || 0;
                    document.getElementById(\'plan-count\').textContent = data.brain.active_plans || 0;
                }
            } catch (e) {}
        }
        function clearAll() {
            document.getElementById(\'input\').value = \'\';
            document.getElementById(\'results\').innerHTML = \'\';
        }
        document.getElementById(\'input\').addEventListener(\'keydown\', e => {
            if (e.key === \'Enter\' && e.metaKey) process();
        });
        loadStats();
        setInterval(loadStats, 5000);
    </script>
</body>
</html>"""
        self._send_html(html)


def run_complete_server(port: int = 9000) -> None:
    """Run the complete Brain UI server."""
    print("🧠 Initializing AMOS Brain Complete UI...")
    try:
        from AMOS_ORGANISM_OS.organism import AmosOrganism

        organism = AmosOrganism()
        CompleteBrainUIHandler.orchestrator = organism
        CompleteBrainUIHandler.brain = organism.brain
        print(f"   ✓ Brain loaded: {organism.brain.state.session_id}")
    except Exception as e:
        print(f"   ⚠ Brain init warning: {e}")
        from AMOS_ORGANISM_OS.BRAIN.brain_os import BrainOS

        brain = BrainOS()
        CompleteBrainUIHandler.brain = brain
        print(f"   ✓ Brain loaded (fallback): {brain.state.session_id}")

    server = HTTPServer(("", port), CompleteBrainUIHandler)
    url = f"http://localhost:{port}"

    print("=" * 60)
    print("🌐 AMOS Brain Complete Interface")
    print("=" * 60)
    print(f"\n📍 Server running at: {url}")
    print("\nFeatures:")
    print("   • 7-Layer Cognitive Stack")
    print("   • Think / Decide / Validate / Plan modes")
    print("   • Real-time metrics and thought stream")
    print("   • Clean, modern interface")
    print("\nPress Ctrl+C to stop")
    print("=" * 60)

    webbrowser.open(url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
        server.shutdown()


def main() -> int:
    """Main entry point."""
    port = 9000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass

    run_complete_server(port)
    return 0


if __name__ == "__main__":
    sys.exit(main())
