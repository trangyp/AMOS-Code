#!/usr/bin/env python3
"""AMOS Brain Interactive UI
===========================

Web-based interactive interface for the AMOS Brain system.
Allows users to interact with cognitive reasoning, decision-making,
and thought processing through a modern web UI.

Owner: Trang
Version: 2.0.0
"""

import json
import sys
import threading
import webbrowser
from datetime import datetime, timezone
UTC = timezone.utc

UTC = UTC
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any
from urllib.parse import urlparse

# Import AMOS Brain
from amos_brain import decide, think, validate


class BrainUIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Brain Interactive UI."""

    brain: Any = None
    orchestrator: Any = None

    def log_message(self, format: str, *args: Any) -> None:
        """Suppress default logging."""
        pass

    def do_GET(self) -> None:
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path = parsed.path

        routes = {
            "/": self._serve_ui,
            "/api/status": self._serve_status,
            "/api/thoughts": self._serve_thoughts,
            "/api/plans": self._serve_plans,
            "/api/reasoning": self._serve_reasoning_history,
            "/api/subsystems": self._serve_subsystems,
        }

        handler = routes.get(path, self._send_404)
        handler()

    def do_POST(self) -> None:
        """Handle POST requests."""
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
            "/api/query": self._handle_query,
        }

        handler = routes.get(path)
        if handler:
            handler(data)
        else:
            self._send_json({"error": "Not found"}, 404)

    def _send_json(self, data: dict, status: int = 200) -> None:
        """Send JSON response."""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

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

    # API Handlers
    def _serve_status(self) -> None:
        """Get brain status."""
        if not self.brain:
            self._send_json({"error": "Brain not initialized"}, 500)
            return

        status = self.brain.status()
        self._send_json(
            {"status": "active", "brain": status, "timestamp": datetime.now(UTC).isoformat()}
        )

    def _serve_thoughts(self) -> None:
        """Get recent thoughts."""
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
        """Get active plans."""
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

    def _serve_reasoning_history(self) -> None:
        """Get reasoning history."""
        # Try to get from memory if available
        try:
            from amos_brain.memory import get_brain_memory

            memory = get_brain_memory()
            history = memory.get_reasoning_history(limit=50)
            self._send_json({"reasoning": history})
        except Exception as e:
            self._send_json({"reasoning": [], "error": str(e)})

    def _serve_subsystems(self) -> None:
        """Get all subsystems info."""
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
            {
                "code": "05_SKELETON",
                "name": "Structure & Rules",
                "status": "active",
                "color": "#9C27B0",
            },
            {"code": "06_MUSCLE", "name": "Execution", "status": "active", "color": "#3F51B5"},
            {"code": "07_METABOLISM", "name": "Pipelines", "status": "active", "color": "#009688"},
            {
                "code": "08_WORLD_MODEL",
                "name": "Environment",
                "status": "active",
                "color": "#00BCD4",
            },
            {
                "code": "09_SOCIAL_ENGINE",
                "name": "Agent Communication",
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
        self._send_json({"subsystems": subsystems})

    # Action Handlers
    def _handle_think(self, data: dict) -> None:
        """Process a thinking request."""
        query = data.get("query", "")
        if not query:
            self._send_json({"error": "No query provided"}, 400)
            return

        try:
            # Use the brain think function
            result = think(query)

            # Also add to brain state
            if self.brain:
                self.brain.perceive(query, "user_ui")

            self._send_json(
                {
                    "success": True,
                    "query": query,
                    "result": result.to_dict() if hasattr(result, "to_dict") else str(result),
                    "timestamp": datetime.now(UTC).isoformat(),
                }
            )
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _handle_decide(self, data: dict) -> None:
        """Process a decision request."""
        scenario = data.get("scenario", "")
        options = data.get("options", [])

        if not scenario:
            self._send_json({"error": "No scenario provided"}, 400)
            return

        try:
            # Use the decide function with options if provided
            if options and len(options) >= 2:
                result = decide(scenario, options=options)
            else:
                result = decide(scenario)

            self._send_json(
                {
                    "success": True,
                    "scenario": scenario,
                    "decision": result.to_dict() if hasattr(result, "to_dict") else str(result),
                    "timestamp": datetime.now(UTC).isoformat(),
                }
            )
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _handle_validate(self, data: dict) -> None:
        """Process a validation request."""
        proposition = data.get("proposition", "")
        if not proposition:
            self._send_json({"error": "No proposition provided"}, 400)
            return

        try:
            result = validate(proposition)
            self._send_json(
                {
                    "success": True,
                    "proposition": proposition,
                    "validation": result.to_dict() if hasattr(result, "to_dict") else str(result),
                    "timestamp": datetime.now(UTC).isoformat(),
                }
            )
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _handle_perceive(self, data: dict) -> None:
        """Process a perception."""
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
        """Create a plan."""
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

    def _handle_query(self, data: dict) -> None:
        """Handle orchestrator query."""
        query = data.get("query", "")
        if not query:
            self._send_json({"error": "No query provided"}, 400)
            return

        try:
            if self.orchestrator:
                result = self.orchestrator.process(query)
                self._send_json(
                    {
                        "success": True,
                        "query": query,
                        "result": result,
                        "timestamp": datetime.now(UTC).isoformat(),
                    }
                )
            else:
                # Fallback to simple think
                result = think(query)
                self._send_json(
                    {
                        "success": True,
                        "query": query,
                        "result": result.to_dict() if hasattr(result, "to_dict") else str(result),
                        "timestamp": datetime.now(UTC).isoformat(),
                    }
                )
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _serve_ui(self) -> None:
        """Serve the main interactive UI HTML."""
        html = self._generate_ui_html()
        self._send_html(html)

    def _generate_ui_html(self) -> str:
        """Generate the interactive UI HTML with embedded CSS and JS."""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AMOS Brain Interactive</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        :root {
            --bg-primary: #0a0a1a;
            --bg-secondary: #151528;
            --bg-card: rgba(255,255,255,0.03);
            --accent-primary: #00d4ff;
            --accent-secondary: #7b2cbf;
            --accent-success: #4CAF50;
            --accent-warning: #FF9800;
            --accent-error: #F44336;
            --text-primary: #ffffff;
            --text-secondary: #8888a0;
            --border: rgba(255,255,255,0.1);
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            line-height: 1.6;
        }

        /* Header */
        .header {
            background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-primary) 100%);
            padding: 20px 30px;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 100;
        }

        .logo {
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .logo-icon {
            width: 45px;
            height: 45px;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            font-weight: bold;
        }

        .logo-text h1 {
            font-size: 22px;
            font-weight: 700;
            background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .logo-text span {
            font-size: 12px;
            color: var(--text-secondary);
        }

        .status-badge {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            background: rgba(76, 175, 80, 0.1);
            border: 1px solid rgba(76, 175, 80, 0.3);
            border-radius: 20px;
            font-size: 13px;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            background: var(--accent-success);
            border-radius: 50%;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.4; }
        }

        /* Main Layout */
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 30px;
            display: grid;
            grid-template-columns: 280px 1fr 320px;
            gap: 25px;
        }

        /* Sidebar */
        .sidebar {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .nav-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 20px;
        }

        .nav-card h3 {
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-secondary);
            margin-bottom: 15px;
        }

        .nav-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.2s;
            margin-bottom: 5px;
        }

        .nav-item:hover, .nav-item.active {
            background: rgba(0, 212, 255, 0.1);
        }

        .nav-item.active {
            border-left: 3px solid var(--accent-primary);
        }

        .nav-item-icon {
            width: 36px;
            height: 36px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
        }

        .subsystem-list {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .subsystem-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px;
            border-radius: 8px;
            font-size: 12px;
            transition: all 0.2s;
        }

        .subsystem-item:hover {
            background: rgba(255,255,255,0.05);
        }

        .subsystem-indicator {
            width: 4px;
            height: 30px;
            border-radius: 2px;
        }

        /* Main Content */
        .main-content {
            display: flex;
            flex-direction: column;
            gap: 25px;
        }

        .card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 16px;
            overflow: hidden;
        }

        .card-header {
            padding: 20px 25px;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .card-header h2 {
            font-size: 16px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .card-body {
            padding: 25px;
        }

        /* Input Area */
        .input-area {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        .input-tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 10px;
        }

        .tab-btn {
            padding: 10px 20px;
            background: transparent;
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text-secondary);
            cursor: pointer;
            transition: all 0.2s;
            font-size: 13px;
        }

        .tab-btn.active, .tab-btn:hover {
            background: rgba(0, 212, 255, 0.1);
            border-color: var(--accent-primary);
            color: var(--accent-primary);
        }

        .input-field {
            width: 100%;
            min-height: 120px;
            padding: 20px;
            background: rgba(0,0,0,0.2);
            border: 1px solid var(--border);
            border-radius: 12px;
            color: var(--text-primary);
            font-size: 15px;
            resize: vertical;
            font-family: inherit;
        }

        .input-field:focus {
            outline: none;
            border-color: var(--accent-primary);
        }

        .options-input {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .option-row {
            display: flex;
            gap: 10px;
            align-items: center;
        }

        .option-input {
            flex: 1;
            padding: 12px 15px;
            background: rgba(0,0,0,0.2);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text-primary);
            font-size: 14px;
        }

        .btn {
            padding: 12px 24px;
            border-radius: 10px;
            border: none;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .btn-primary {
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            color: white;
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 212, 255, 0.3);
        }

        .btn-secondary {
            background: rgba(255,255,255,0.1);
            color: var(--text-primary);
        }

        .btn-secondary:hover {
            background: rgba(255,255,255,0.15);
        }

        /* Results Area */
        .results-area {
            margin-top: 25px;
            min-height: 200px;
        }

        .result-card {
            background: rgba(0,0,0,0.2);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
        }

        .result-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }

        .result-type {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 13px;
            color: var(--accent-primary);
        }

        .result-time {
            font-size: 12px;
            color: var(--text-secondary);
        }

        .result-content {
            font-size: 15px;
            line-height: 1.8;
            white-space: pre-wrap;
        }

        .result-meta {
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid var(--border);
            display: flex;
            gap: 20px;
            font-size: 12px;
            color: var(--text-secondary);
        }

        /* Stats Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
        }

        .stat-card {
            background: rgba(0,0,0,0.2);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
        }

        .stat-value {
            font-size: 32px;
            font-weight: 700;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .stat-label {
            font-size: 12px;
            color: var(--text-secondary);
            margin-top: 5px;
        }

        /* Right Panel */
        .right-panel {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .thought-list {
            display: flex;
            flex-direction: column;
            gap: 12px;
            max-height: 400px;
            overflow-y: auto;
        }

        .thought-item {
            background: rgba(0,0,0,0.2);
            border-radius: 10px;
            padding: 15px;
            border-left: 3px solid var(--accent-primary);
        }

        .thought-type {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--accent-primary);
            margin-bottom: 8px;
        }

        .thought-content {
            font-size: 13px;
            line-height: 1.6;
            color: var(--text-primary);
        }

        .thought-meta {
            font-size: 11px;
            color: var(--text-secondary);
            margin-top: 8px;
        }

        /* Loading State */
        .loading {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            padding: 40px;
            color: var(--text-secondary);
        }

        .spinner {
            width: 24px;
            height: 24px;
            border: 2px solid var(--border);
            border-top-color: var(--accent-primary);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        /* Responsive */
        @media (max-width: 1200px) {
            .container {
                grid-template-columns: 1fr;
            }
            .sidebar, .right-panel {
                order: 2;
            }
            .main-content {
                order: 1;
            }
        }

        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }

        ::-webkit-scrollbar-track {
            background: var(--bg-primary);
        }

        ::-webkit-scrollbar-thumb {
            background: var(--border);
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: var(--text-secondary);
        }
    </style>
</head>
<body>
    <header class="header">
        <div class="logo">
            <div class="logo-icon">🧠</div>
            <div class="logo-text">
                <h1>AMOS Brain</h1>
                <span>Interactive Cognitive Interface</span>
            </div>
        </div>
        <div class="status-badge">
            <span class="status-dot"></span>
            <span id="system-status">System Online</span>
        </div>
    </header>

    <div class="container">
        <!-- Left Sidebar -->
        <aside class="sidebar">
            <div class="nav-card">
                <h3>Actions</h3>
                <div class="nav-item active" onclick="switchMode('think')">
                    <div class="nav-item-icon" style="background: rgba(0, 212, 255, 0.1);">💭</div>
                    <div>
                        <div style="font-weight: 500;">Think</div>
                        <div style="font-size: 12px; color: var(--text-secondary);">Process & analyze</div>
                    </div>
                </div>
                <div class="nav-item" onclick="switchMode('decide')">
                    <div class="nav-item-icon" style="background: rgba(123, 44, 191, 0.1);">⚖️</div>
                    <div>
                        <div style="font-weight: 500;">Decide</div>
                        <div style="font-size: 12px; color: var(--text-secondary);">Make decisions</div>
                    </div>
                </div>
                <div class="nav-item" onclick="switchMode('validate')">
                    <div class="nav-item-icon" style="background: rgba(76, 175, 80, 0.1);">✓</div>
                    <div>
                        <div style="font-weight: 500;">Validate</div>
                        <div style="font-size: 12px; color: var(--text-secondary);">Check logic</div>
                    </div>
                </div>
                <div class="nav-item" onclick="switchMode('plan')">
                    <div class="nav-item-icon" style="background: rgba(255, 152, 0, 0.1);">📋</div>
                    <div>
                        <div style="font-weight: 500;">Plan</div>
                        <div style="font-size: 12px; color: var(--text-secondary);">Create goals</div>
                    </div>
                </div>
            </div>

            <div class="nav-card">
                <h3>Subsystems</h3>
                <div class="subsystem-list" id="subsystem-list">
                    <!-- Populated by JS -->
                </div>
            </div>
        </aside>

        <!-- Main Content -->
        <main class="main-content">
            <!-- Stats -->
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value" id="thought-count">0</div>
                    <div class="stat-label">Thoughts</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="cycle-count">0</div>
                    <div class="stat-label">Cycles</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="plan-count">0</div>
                    <div class="stat-label">Plans</div>
                </div>
            </div>

            <!-- Input Card -->
            <div class="card">
                <div class="card-header">
                    <h2><span id="current-mode-icon">💭</span> <span id="current-mode-title">Think</span></h2>
                    <button class="btn btn-secondary" onclick="clearAll()">
                        <span>🗑️</span> Clear
                    </button>
                </div>
                <div class="card-body">
                    <div class="input-area">
                        <div class="input-tabs">
                            <button class="tab-btn active" onclick="switchMode('think')">Think</button>
                            <button class="tab-btn" onclick="switchMode('decide')">Decide</button>
                            <button class="tab-btn" onclick="switchMode('validate')">Validate</button>
                            <button class="tab-btn" onclick="switchMode('plan')">Plan</button>
                        </div>

                        <textarea
                            id="main-input"
                            class="input-field"
                            placeholder="Enter your query or problem to think about..."
                        ></textarea>

                        <!-- Options for Decide mode -->
                        <div id="options-area" class="options-input" style="display: none;">
                            <div class="option-row">
                                <span>Option 1:</span>
                                <input type="text" class="option-input" id="option-1" placeholder="First option...">
                            </div>
                            <div class="option-row">
                                <span>Option 2:</span>
                                <input type="text" class="option-input" id="option-2" placeholder="Second option...">
                            </div>
                        </div>

                        <div style="display: flex; gap: 10px;">
                            <button class="btn btn-primary" onclick="submitAction()">
                                <span id="action-icon">🚀</span>
                                <span id="action-text">Process</span>
                            </button>
                            <button class="btn btn-secondary" onclick="loadExample()">
                                <span>📄</span> Example
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Results Card -->
            <div class="card" id="results-card" style="display: none;">
                <div class="card-header">
                    <h2>📝 Results</h2>
                </div>
                <div class="card-body">
                    <div class="results-area" id="results-area">
                        <!-- Results populated here -->
                    </div>
                </div>
            </div>
        </main>

        <!-- Right Panel -->
        <aside class="right-panel">
            <div class="card">
                <div class="card-header">
                    <h2>💡 Recent Thoughts</h2>
                </div>
                <div class="card-body">
                    <div class="thought-list" id="thought-list">
                        <div class="loading">
                            <div class="spinner"></div>
                            <span>Loading...</span>
                        </div>
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <h2>📋 Active Plans</h2>
                </div>
                <div class="card-body">
                    <div id="plans-list">
                        <div style="text-align: center; color: var(--text-secondary); padding: 20px;">
                            No active plans
                        </div>
                    </div>
                </div>
            </div>
        </aside>
    </div>

    <script>
        // State
        let currentMode = 'think';
        const examples = {
            think: "Analyze the implications of implementing a microservices architecture for a growing e-commerce platform with 1M+ users.",
            decide: "Should we prioritize feature development or technical debt reduction this quarter?",
            validate: "All software systems must have 99.99% uptime to be considered production-ready.",
            plan: "Launch a new AI-powered recommendation engine for the platform."
        };

        // Initialize
        document.addEventListener('DOMContentLoaded', () => {
            loadStatus();
            loadThoughts();
            loadSubsystems();

            // Auto-refresh every 5 seconds
            setInterval(() => {
                loadStatus();
                loadThoughts();
            }, 5000);
        });

        // Mode switching
        function switchMode(mode) {
            currentMode = mode;

            // Update tabs
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');

            // Update sidebar
            document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
            event.target.closest('.nav-item')?.classList.add('active');

            // Update UI
            const icons = { think: '💭', decide: '⚖️', validate: '✓', plan: '📋' };
            const titles = { think: 'Think', decide: 'Decide', validate: 'Validate', plan: 'Plan' };
            const placeholders = {
                think: "Enter your query or problem to analyze...",
                decide: "Describe the decision scenario...",
                validate: "Enter the proposition to validate...",
                plan: "Enter your goal or objective..."
            };

            document.getElementById('current-mode-icon').textContent = icons[mode];
            document.getElementById('current-mode-title').textContent = titles[mode];
            document.getElementById('main-input').placeholder = placeholders[mode];
            document.getElementById('action-text').textContent = mode === 'think' ? 'Process' : mode.charAt(0).toUpperCase() + mode.slice(1);

            // Show/hide options for decide mode
            document.getElementById('options-area').style.display = mode === 'decide' ? 'flex' : 'none';
        }

        // API Calls
        async function submitAction() {
            const input = document.getElementById('main-input').value.trim();
            if (!input) {
                alert('Please enter some input');
                return;
            }

            const resultsArea = document.getElementById('results-area');
            const resultsCard = document.getElementById('results-card');

            resultsCard.style.display = 'block';
            resultsArea.innerHTML = `
                <div class="loading">
                    <div class="spinner"></div>
                    <span>Processing with AMOS Brain...</span>
                </div>
            `;

            try {
                let endpoint, body;

                switch(currentMode) {
                    case 'think':
                        endpoint = '/api/think';
                        body = { query: input };
                        break;
                    case 'decide':
                        endpoint = '/api/decide';
                        const opt1 = document.getElementById('option-1').value.trim();
                        const opt2 = document.getElementById('option-2').value.trim();
                        body = {
                            scenario: input,
                            options: opt1 && opt2 ? [opt1, opt2] : []
                        };
                        break;
                    case 'validate':
                        endpoint = '/api/validate';
                        body = { proposition: input };
                        break;
                    case 'plan':
                        endpoint = '/api/plan';
                        body = { goal: input, horizon: 'medium-term' };
                        break;
                }

                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(body)
                });

                const result = await response.json();
                displayResult(result);

                // Refresh thoughts
                loadThoughts();
                loadStatus();

            } catch (error) {
                resultsArea.innerHTML = `
                    <div class="result-card" style="border-color: var(--accent-error);">
                        <div class="result-header">
                            <span class="result-type">❌ Error</span>
                        </div>
                        <div class="result-content">${error.message}</div>
                    </div>
                `;
            }
        }

        function displayResult(result) {
            const resultsArea = document.getElementById('results-area');
            const time = new Date().toLocaleTimeString();

            let content = '';
            if (result.result) {
                const r = result.result;
                if (typeof r === 'object') {
                    content = Object.entries(r).map(([k, v]) => {
                        if (typeof v === 'object') {
                            return `<strong>${k}:</strong>\n${JSON.stringify(v, null, 2)}`;
                        }
                        return `<strong>${k}:</strong> ${v}`;
                    }).join('\n\n');
                } else {
                    content = String(r);
                }
            } else if (result.decision) {
                content = `<strong>Decision:</strong> ${result.decision.recommendation || JSON.stringify(result.decision)}`;
            } else if (result.validation) {
                content = `<strong>Validation:</strong> ${JSON.stringify(result.validation)}`;
            } else if (result.plan_id) {
                content = `<strong>Plan Created:</strong> ${result.goal}\nID: ${result.plan_id}`;
            } else {
                content = JSON.stringify(result, null, 2);
            }

            resultsArea.innerHTML = `
                <div class="result-card">
                    <div class="result-header">
                        <span class="result-type">${getModeIcon()} ${currentMode.toUpperCase()} Result</span>
                        <span class="result-time">${time}</span>
                    </div>
                    <div class="result-content">${content.replace(/\n/g, '<br>')}</div>
                    <div class="result-meta">
                        <span>✓ Success</span>
                        <span>${result.timestamp ? new Date(result.timestamp).toLocaleString() : time}</span>
                    </div>
                </div>
            `;
        }

        function getModeIcon() {
            const icons = { think: '💭', decide: '⚖️', validate: '✓', plan: '📋' };
            return icons[currentMode];
        }

        async function loadStatus() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();

                if (data.brain) {
                    document.getElementById('thought-count').textContent = data.brain.thought_count || 0;
                    document.getElementById('cycle-count').textContent = data.brain.cycle_count || 0;
                    document.getElementById('plan-count').textContent = data.brain.active_plans || 0;
                }
            } catch (e) {
                console.error('Status load failed:', e);
            }
        }

        async function loadThoughts() {
            try {
                const response = await fetch('/api/thoughts');
                const data = await response.json();

                const list = document.getElementById('thought-list');
                if (data.thoughts && data.thoughts.length > 0) {
                    list.innerHTML = data.thoughts.slice(0, 5).map(t => `
                        <div class="thought-item" style="border-left-color: ${getTypeColor(t.type)}">
                            <div class="thought-type">${t.type}</div>
                            <div class="thought-content">${t.content.substring(0, 100)}${t.content.length > 100 ? '...' : ''}</div>
                            <div class="thought-meta">${t.source} • ${new Date(t.timestamp).toLocaleTimeString()}</div>
                        </div>
                    `).join('');
                } else {
                    list.innerHTML = '<div style="text-align: center; color: var(--text-secondary); padding: 20px;">No thoughts yet</div>';
                }
            } catch (e) {
                console.error('Thoughts load failed:', e);
            }
        }

        async function loadSubsystems() {
            try {
                const response = await fetch('/api/subsystems');
                const data = await response.json();

                const list = document.getElementById('subsystem-list');
                if (data.subsystems) {
                    list.innerHTML = data.subsystems.map(s => `
                        <div class="subsystem-item">
                            <div class="subsystem-indicator" style="background: ${s.color}"></div>
                            <div>
                                <div style="font-weight: 500;">${s.code}</div>
                                <div style="color: var(--text-secondary);">${s.name}</div>
                            </div>
                        </div>
                    `).join('');
                }
            } catch (e) {
                console.error('Subsystems load failed:', e);
            }
        }

        function getTypeColor(type) {
            const colors = {
                perceptual: '#2196F3',
                conceptual: '#9C27B0',
                narrative: '#FF9800',
                causal: '#F44336',
                systemic: '#00BCD4',
                meta: '#795548'
            };
            return colors[type] || '#00d4ff';
        }

        function loadExample() {
            document.getElementById('main-input').value = examples[currentMode];
        }

        function clearAll() {
            document.getElementById('main-input').value = '';
            document.getElementById('results-area').innerHTML = '';
            document.getElementById('results-card').style.display = 'none';
            document.getElementById('option-1').value = '';
            document.getElementById('option-2').value = '';
        }

        // Enter key to submit
        document.getElementById('main-input')?.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
                submitAction();
            }
        });
    </script>
</body>
</html>"""


def run_ui_server(port: int = 8888, open_browser: bool = True) -> None:
    """Run the Brain UI server."""
    # Initialize brain
    print("🧠 Initializing AMOS Brain...")
    try:
        from AMOS_ORGANISM_OS.organism import AmosOrganism

        organism = AmosOrganism()
        BrainUIHandler.orchestrator = organism
        BrainUIHandler.brain = organism.brain
        print(f"   ✓ Brain loaded: {organism.brain.state.session_id}")
    except Exception as e:
        print(f"   ⚠ Brain init warning: {e}")
        # Fallback to BrainOS directly
        from AMOS_ORGANISM_OS.AMOS_MASTER_ORCHESTRATOR import BrainOS

        brain = BrainOS()
        BrainUIHandler.brain = brain
        print(f"   ✓ Brain loaded (fallback): {brain.state.session_id}")

    # Start server
    server = HTTPServer(("", port), BrainUIHandler)
    url = f"http://localhost:{port}"

    print("=" * 50)
    print("🌐 AMOS Brain Interactive UI")
    print("=" * 50)
    print(f"\n📍 Server running at: {url}")
    print("\nAvailable endpoints:")
    print("   GET  /                    - Interactive UI")
    print("   GET  /api/status          - Brain status")
    print("   GET  /api/thoughts        - Recent thoughts")
    print("   GET  /api/subsystems      - Subsystem status")
    print("   POST /api/think           - Process thinking")
    print("   POST /api/decide          - Make decision")
    print("   POST /api/validate        - Validate proposition")
    print("   POST /api/plan            - Create plan")
    print("\nPress Ctrl+C to stop")
    print("=" * 50)

    if open_browser:
        threading.Timer(1.5, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
        server.shutdown()


def main() -> int:
    """Main entry point."""
    port = 8888
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass

    run_ui_server(port)
    return 0


if __name__ == "__main__":
    sys.exit(main())
