#!/usr/bin/env python3
"""AMOS Brain Enhanced Interactive UI
===================================

Cognitively-designed web interface based on brain's architecture analysis.
Implements the 7-layer cognitive stack visualization.

Owner: Trang
Version: 3.0.0
"""

import json
import sys
import webbrowser
from datetime import UTC, datetime, timezone

UTC = UTC
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any
from urllib.parse import urlparse

from amos_brain import decide, think, validate


class EnhancedBrainUIHandler(BaseHTTPRequestHandler):
    """Enhanced HTTP request handler with cognitive layer visualization."""

    brain: Any = None
    orchestrator: Any = None

    def log_message(self, format: str, *args: Any) -> None:
        pass

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        routes = {
            "/": self._serve_enhanced_ui,
            "/api/status": self._serve_status,
            "/api/thoughts": self._serve_thoughts,
            "/api/plans": self._serve_plans,
            "/api/subsystems": self._serve_subsystems,
            "/api/cognitive-layers": self._serve_cognitive_layers,
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

    def _serve_status(self) -> None:
        if not self.brain:
            self._send_json({"error": "Brain not initialized"}, 500)
            return

        status = self.brain.status()
        self._send_json(
            {
                "status": "active",
                "brain": status,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
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
            {"code": "01_BRAIN", "name": "Core Cognition", "layer": 1, "color": "#4CAF50"},
            {"code": "02_SENSES", "name": "Input Processing", "layer": 2, "color": "#2196F3"},
            {"code": "03_IMMUNE", "name": "Security", "layer": 2, "color": "#FF9800"},
            {"code": "04_BLOOD", "name": "Financial Engine", "layer": 3, "color": "#F44336"},
            {"code": "05_SKELETON", "name": "Structure & Rules", "layer": 3, "color": "#9C27B0"},
            {"code": "06_MUSCLE", "name": "Execution", "layer": 4, "color": "#3F51B5"},
            {"code": "07_METABOLISM", "name": "Pipelines", "layer": 4, "color": "#009688"},
            {"code": "08_WORLD_MODEL", "name": "Environment", "layer": 5, "color": "#00BCD4"},
            {
                "code": "09_SOCIAL_ENGINE",
                "name": "Agent Communication",
                "layer": 5,
                "color": "#8BC34A",
            },
            {"code": "10_LIFE_ENGINE", "name": "Life Management", "layer": 6, "color": "#FFEB3B"},
            {"code": "11_LEGAL_BRAIN", "name": "Compliance", "layer": 6, "color": "#795548"},
            {"code": "12_QUANTUM_LAYER", "name": "Probabilistic", "layer": 7, "color": "#607D8B"},
            {"code": "13_FACTORY", "name": "Agent Factory", "layer": 7, "color": "#E91E63"},
        ]
        self._send_json({"subsystems": subsystems})

    def _serve_cognitive_layers(self) -> None:
        layers = [
            {
                "level": 1,
                "name": "Perceptual",
                "description": "Raw sensory input processing",
                "color": "#2196F3",
                "icon": "👁️",
            },
            {
                "level": 2,
                "name": "Conceptual",
                "description": "Pattern recognition, categorization",
                "color": "#9C27B0",
                "icon": "🧩",
            },
            {
                "level": 3,
                "name": "Narrative",
                "description": "Story, timeline, sequence",
                "color": "#FF9800",
                "icon": "📖",
            },
            {
                "level": 4,
                "name": "Causal",
                "description": "Cause-effect reasoning",
                "color": "#F44336",
                "icon": "⚡",
            },
            {
                "level": 5,
                "name": "Systemic",
                "description": "Multi-system, multi-actor",
                "color": "#00BCD4",
                "icon": "🌐",
            },
            {
                "level": 6,
                "name": "Meta",
                "description": "Self-reflection, audit, ethics",
                "color": "#795548",
                "icon": "🔮",
            },
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
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            if hasattr(result, "to_dict"):
                response_data["result"] = result.to_dict()
            elif hasattr(result, "content"):
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
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            if hasattr(result, "to_dict"):
                response_data["decision"] = result.to_dict()
            elif hasattr(result, "approved"):
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
                "timestamp": datetime.now(timezone.utc).isoformat(),
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

    def _serve_enhanced_ui(self) -> None:
        html = self._generate_enhanced_html()
        self._send_html(html)

    def _generate_enhanced_html(self) -> str:
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AMOS Brain - Cognitive Interface</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        :root {
            --bg-deep: #050510;
            --bg-primary: #0a0a1a;
            --bg-secondary: #121225;
            --bg-card: rgba(255,255,255,0.03);
            --accent-cyan: #00d4ff;
            --accent-purple: #7b2cbf;
            --accent-green: #4CAF50;
            --accent-orange: #FF9800;
            --accent-red: #F44336;
            --text-primary: #ffffff;
            --text-secondary: #8890a0;
            --border: rgba(255,255,255,0.08);
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg-deep);
            color: var(--text-primary);
            min-height: 100vh;
            overflow-x: hidden;
        }

        /* Animated background */
        .bg-animation {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 0;
            opacity: 0.3;
        }

        .neural-node {
            position: absolute;
            width: 4px;
            height: 4px;
            background: var(--accent-cyan);
            border-radius: 50%;
            animation: pulse 3s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 0.3; transform: scale(1); }
            50% { opacity: 1; transform: scale(1.5); }
        }

        /* Header */
        .header {
            position: relative;
            z-index: 10;
            background: linear-gradient(180deg, var(--bg-secondary) 0%, transparent 100%);
            padding: 25px 40px;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 18px;
        }

        .brain-icon {
            width: 52px;
            height: 52px;
            background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 26px;
            box-shadow: 0 8px 32px rgba(0, 212, 255, 0.3);
            animation: glow 2s ease-in-out infinite alternate;
        }

        @keyframes glow {
            from { box-shadow: 0 8px 32px rgba(0, 212, 255, 0.3); }
            to { box-shadow: 0 8px 48px rgba(0, 212, 255, 0.5); }
        }

        .brand-text h1 {
            font-size: 26px;
            font-weight: 700;
            background: linear-gradient(90deg, var(--accent-cyan), var(--accent-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.5px;
        }

        .brand-text span {
            font-size: 13px;
            color: var(--text-secondary);
            letter-spacing: 2px;
            text-transform: uppercase;
        }

        /* Cognitive Layers - Vertical Stack */
        .cognitive-stack {
            position: fixed;
            left: 30px;
            top: 50%;
            transform: translateY(-50%);
            z-index: 10;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .layer {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 14px 18px;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.3s ease;
            opacity: 0.6;
        }

        .layer:hover, .layer.active {
            opacity: 1;
            transform: translateX(10px);
            border-color: var(--accent-cyan);
            background: rgba(0, 212, 255, 0.05);
        }

        .layer-icon {
            font-size: 20px;
        }

        .layer-info {
            display: flex;
            flex-direction: column;
        }

        .layer-name {
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .layer-desc {
            font-size: 10px;
            color: var(--text-secondary);
        }

        /* Main Content */
        .main-container {
            position: relative;
            z-index: 5;
            margin-left: 280px;
            margin-right: 340px;
            padding: 30px;
            min-height: calc(100vh - 100px);
        }

        /* Input Section */
        .input-section {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 25px;
        }

        .mode-selector {
            display: flex;
            gap: 12px;
            margin-bottom: 25px;
            padding-bottom: 20px;
            border-bottom: 1px solid var(--border);
        }

        .mode-btn {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 12px 24px;
            background: transparent;
            border: 1px solid var(--border);
            border-radius: 10px;
            color: var(--text-secondary);
            cursor: pointer;
            transition: all 0.3s;
            font-size: 14px;
        }

        .mode-btn:hover, .mode-btn.active {
            background: rgba(0, 212, 255, 0.1);
            border-color: var(--accent-cyan);
            color: var(--accent-cyan);
        }

        .input-area {
            position: relative;
        }

        .input-field {
            width: 100%;
            min-height: 140px;
            padding: 24px;
            background: rgba(0,0,0,0.3);
            border: 1px solid var(--border);
            border-radius: 16px;
            color: var(--text-primary);
            font-size: 16px;
            line-height: 1.7;
            resize: vertical;
            font-family: inherit;
            transition: all 0.3s;
        }

        .input-field:focus {
            outline: none;
            border-color: var(--accent-cyan);
            box-shadow: 0 0 30px rgba(0, 212, 255, 0.1);
        }

        .input-actions {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 20px;
        }

        .action-btns {
            display: flex;
            gap: 12px;
        }

        .btn {
            padding: 14px 28px;
            border-radius: 12px;
            border: none;
            cursor: pointer;
            font-size: 15px;
            font-weight: 600;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .btn-primary {
            background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
            color: white;
            box-shadow: 0 4px 20px rgba(0, 212, 255, 0.3);
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(0, 212, 255, 0.4);
        }

        .btn-secondary {
            background: rgba(255,255,255,0.05);
            color: var(--text-secondary);
            border: 1px solid var(--border);
        }

        .btn-secondary:hover {
            background: rgba(255,255,255,0.1);
            color: var(--text-primary);
        }

        /* Results Flow */
        .results-section {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .result-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 24px;
            animation: slideIn 0.4s ease;
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .result-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid var(--border);
        }

        .result-type {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 14px;
            color: var(--accent-cyan);
            font-weight: 600;
        }

        .result-time {
            font-size: 12px;
            color: var(--text-secondary);
        }

        .result-content {
            font-size: 15px;
            line-height: 1.9;
            color: var(--text-primary);
            white-space: pre-wrap;
        }

        .reasoning-path {
            margin-top: 20px;
            padding: 20px;
            background: rgba(0,0,0,0.2);
            border-radius: 12px;
            border-left: 3px solid var(--accent-purple);
        }

        .reasoning-title {
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--accent-purple);
            margin-bottom: 12px;
        }

        .reasoning-step {
            display: flex;
            align-items: flex-start;
            gap: 12px;
            padding: 10px 0;
            border-bottom: 1px solid var(--border);
            font-size: 13px;
        }

        .reasoning-step:last-child {
            border-bottom: none;
        }

        .step-num {
            width: 24px;
            height: 24px;
            background: var(--accent-purple);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 11px;
            font-weight: 600;
            flex-shrink: 0;
        }

        /* Right Panel - Stats & Activity */
        .right-panel {
            position: fixed;
            right: 0;
            top: 100px;
            width: 320px;
            height: calc(100vh - 100px);
            padding: 25px;
            overflow-y: auto;
            z-index: 10;
        }

        .panel-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 22px;
            margin-bottom: 20px;
        }

        .panel-title {
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: var(--text-secondary);
            margin-bottom: 18px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .stat-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid var(--border);
        }

        .stat-row:last-child {
            border-bottom: none;
        }

        .stat-label {
            font-size: 13px;
            color: var(--text-secondary);
        }

        .stat-value {
            font-size: 20px;
            font-weight: 700;
            background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .thought-stream {
            display: flex;
            flex-direction: column;
            gap: 12px;
            max-height: 300px;
            overflow-y: auto;
        }

        .thought-item {
            padding: 14px;
            background: rgba(0,0,0,0.2);
            border-radius: 10px;
            border-left: 3px solid var(--accent-cyan);
            font-size: 12px;
        }

        .thought-type {
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--accent-cyan);
            margin-bottom: 6px;
        }

        .thought-content {
            color: var(--text-primary);
            line-height: 1.5;
        }

        .thought-meta {
            font-size: 10px;
            color: var(--text-secondary);
            margin-top: 8px;
        }

        /* Loading State */
        .processing {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
            padding: 50px;
            color: var(--text-secondary);
        }

        .neural-spinner {
            display: flex;
            gap: 4px;
        }

        .neural-spinner span {
            width: 8px;
            height: 8px;
            background: var(--accent-cyan);
            border-radius: 50%;
            animation: bounce 1.4s ease-in-out infinite both;
        }

        .neural-spinner span:nth-child(1) { animation-delay: -0.32s; }
        .neural-spinner span:nth-child(2) { animation-delay: -0.16s; }

        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
        }

        /* Responsive */
        @media (max-width: 1200px) {
            .cognitive-stack { display: none; }
            .main-container { margin-left: 30px; margin-right: 30px; }
            .right-panel { position: relative; width: 100%; height: auto; }
        }

        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }

        ::-webkit-scrollbar-track {
            background: transparent;
        }

        ::-webkit-scrollbar-thumb {
            background: var(--border);
            border-radius: 3px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: var(--text-secondary);
        }
    </style>
</head>
<body>
    <!-- Animated Background -->
    <div class="bg-animation" id="bg-animation"></div>

    <!-- Header -->
    <header class="header">
        <div class="brand">
            <div class="brain-icon">🧠</div>
            <div class="brand-text">
                <h1>AMOS Brain</h1>
                <span>Cognitive Architecture Interface</span>
            </div>
        </div>
    </header>

    <!-- Cognitive Layers Stack -->
    <div class="cognitive-stack" id="cognitive-stack">
        <div class="layer active" data-layer="6">
            <span class="layer-icon">🔮</span>
            <div class="layer-info">
                <span class="layer-name">Meta</span>
                <span class="layer-desc">Self-reflection</span>
            </div>
        </div>
        <div class="layer" data-layer="5">
            <span class="layer-icon">🌐</span>
            <div class="layer-info">
                <span class="layer-name">Systemic</span>
                <span class="layer-desc">Multi-system</span>
            </div>
        </div>
        <div class="layer" data-layer="4">
            <span class="layer-icon">⚡</span>
            <div class="layer-info">
                <span class="layer-name">Causal</span>
                <span class="layer-desc">Cause-effect</span>
            </div>
        </div>
        <div class="layer" data-layer="3">
            <span class="layer-icon">📖</span>
            <div class="layer-info">
                <span class="layer-name">Narrative</span>
                <span class="layer-desc">Story & sequence</span>
            </div>
        </div>
        <div class="layer" data-layer="2">
            <span class="layer-icon">🧩</span>
            <div class="layer-info">
                <span class="layer-name">Conceptual</span>
                <span class="layer-desc">Pattern recognition</span>
            </div>
        </div>
        <div class="layer" data-layer="1">
            <span class="layer-icon">👁️</span>
            <div class="layer-info">
                <span class="layer-name">Perceptual</span>
                <span class="layer-desc">Raw input</span>
            </div>
        </div>
    </div>

    <!-- Main Content -->
    <main class="main-container">
        <!-- Input Section -->
        <section class="input-section">
            <div class="mode-selector">
                <button class="mode-btn active" onclick="setMode('think')">
                    <span>💭</span> Think
                </button>
                <button class="mode-btn" onclick="setMode('decide')">
                    <span>⚖️</span> Decide
                </button>
                <button class="mode-btn" onclick="setMode('validate')">
                    <span>✓</span> Validate
                </button>
                <button class="mode-btn" onclick="setMode('plan')">
                    <span>📋</span> Plan
                </button>
            </div>

            <div class="input-area">
                <textarea
                    id="main-input"
                    class="input-field"
                    placeholder="Enter your cognitive query here... The brain will process through all 7 layers from perceptual to meta-cognitive."
                ></textarea>

                <div class="input-actions">
                    <div class="action-btns">
                        <button class="btn btn-primary" onclick="processInput()">
                            <span>🚀</span> Process
                        </button>
                        <button class="btn btn-secondary" onclick="loadExample()">
                            <span>📄</span> Example
                        </button>
                    </div>
                    <button class="btn btn-secondary" onclick="clearAll()">
                        <span>🗑️</span> Clear
                    </button>
                </div>
            </div>
        </section>

        <!-- Results Section -->
        <section class="results-section" id="results-section">
            <!-- Results will be inserted here -->
        </section>
    </main>

    <!-- Right Panel -->
    <aside class="right-panel">
        <!-- Stats -->
        <div class="panel-card">
            <div class="panel-title">
                <span>📊</span> Cognitive Metrics
            </div>
            <div class="stat-row">
                <span class="stat-label">Thoughts</span>
                <span class="stat-value" id="thought-count">0</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Cycles</span>
                <span class="stat-value" id="cycle-count">0</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Active Plans</span>
                <span class="stat-value" id="plan-count">0</span>
            </div>
        </div>

        <!-- Thought Stream -->
        <div class="panel-card">
            <div class="panel-title">
                <span>💡</span> Thought Stream
            </div>
            <div class="thought-stream" id="thought-stream">
                <div style="text-align: center; color: var(--text-secondary); padding: 20px; font-size: 12px;">
                    No cognitive activity yet
                </div>
            </div>
        </div>
    </aside>

    <script>
        // State
        let currentMode = 'think';

        const examples = {
            think: "Analyze the trade-offs between monolithic and microservices architecture for a fintech platform handling 10M+ transactions daily.",
            decide: "Should we prioritize building new features or improving system reliability this quarter?",
            validate: "Implementing zero-trust security requires complete network segmentation.",
            plan: "Design and deploy a machine learning pipeline for real-time fraud detection."
        };

        const modeIcons = {
            think: '💭',
            decide: '⚖️',
            validate: '✓',
            plan: '📋'
        };

        // Initialize
        document.addEventListener('DOMContentLoaded', () => {
            createNeuralBackground();
            loadStatus();
            loadThoughts();

            // Auto-refresh
            setInterval(() => {
                loadStatus();
                loadThoughts();
            }, 5000);
        });

        // Create animated neural background
        function createNeuralBackground() {
            const container = document.getElementById('bg-animation');
            for (let i = 0; i < 30; i++) {
                const node = document.createElement('div');
                node.className = 'neural-node';
                node.style.left = Math.random() * 100 + '%';
                node.style.top = Math.random() * 100 + '%';
                node.style.animationDelay = Math.random() * 3 + 's';
                container.appendChild(node);
            }
        }

        // Mode switching
        function setMode(mode) {
            currentMode = mode;
            document.querySelectorAll('.mode-btn').forEach(btn => btn.classList.remove('active'));
            event.target.closest('.mode-btn').classList.add('active');

            const placeholders = {
                think: "Enter your cognitive query... The brain will process through all 7 layers.",
                decide: "Describe the decision scenario with options to analyze.",
                validate: "Enter the proposition to validate against global laws.",
                plan: "Define your goal for strategic planning."
            };

            document.getElementById('main-input').placeholder = placeholders[mode];
        }

        // Process input
        async function processInput() {
            const input = document.getElementById('main-input').value.trim();
            if (!input) {
                alert('Please enter input for cognitive processing');
                return;
            }

            const resultsSection = document.getElementById('results-section');
            resultsSection.innerHTML = `
                <div class="processing">
                    <div class="neural-spinner">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                    <span>Processing through cognitive layers...</span>
                </div>
            `;

            try {
                const endpoints = {
                    think: '/api/think',
                    decide: '/api/decide',
                    validate: '/api/validate',
                    plan: '/api/plan'
                };

                const bodies = {
                    think: { query: input },
                    decide: { scenario: input, options: [] },
                    validate: { proposition: input },
                    plan: { goal: input, horizon: 'medium-term' }
                };

                const response = await fetch(endpoints[currentMode], {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(bodies[currentMode])
                });

                const result = await response.json();
                displayResult(result);

                // Refresh data
                loadThoughts();
                loadStatus();

                // Animate layers
                animateCognitiveLayers();

            } catch (error) {
                resultsSection.innerHTML = `
                    <div class="result-card" style="border-color: var(--accent-red);">
                        <div class="result-header">
                            <span class="result-type" style="color: var(--accent-red);">❌ Error</span>
                        </div>
                        <div class="result-content">${error.message}</div>
                    </div>
                `;
            }
        }

        function displayResult(result) {
            const resultsSection = document.getElementById('results-section');
            const time = new Date().toLocaleTimeString();

            let content = '';
            let reasoning = [];

            if (result.result) {
                const r = result.result;
                if (r.content) content = r.content;
                else if (typeof r === 'object') content = JSON.stringify(r, null, 2);
                else content = String(r);

                if (r.reasoning) reasoning = r.reasoning;
            } else if (result.decision) {
                content = JSON.stringify(result.decision, null, 2);
            } else if (result.validation) {
                content = JSON.stringify(result.validation, null, 2);
            } else {
                content = JSON.stringify(result, null, 2);
            }

            let reasoningHtml = '';
            if (reasoning && reasoning.length > 0) {
                reasoningHtml = `
                    <div class="reasoning-path">
                        <div class="reasoning-title">🧠 Cognitive Reasoning Path</div>
                        ${reasoning.map((step, i) => `
                            <div class="reasoning-step">
                                <span class="step-num">${i + 1}</span>
                                <span>${step}</span>
                            </div>
                        `).join('')}
                    </div>
                `;
            }

            resultsSection.innerHTML = `
                <div class="result-card">
                    <div class="result-header">
                        <span class="result-type">
                            ${modeIcons[currentMode]} ${currentMode.toUpperCase()} RESULT
                        </span>
                        <span class="result-time">${time}</span>
                    </div>
                    <div class="result-content">${content.replace(/\\n/g, '<br>')}</div>
                    ${reasoningHtml}
                </div>
            `;
        }

        function animateCognitiveLayers() {
            const layers = document.querySelectorAll('.layer');
            layers.forEach((layer, index) => {
                setTimeout(() => {
                    layer.classList.add('active');
                    setTimeout(() => layer.classList.remove('active'), 500);
                }, index * 200);
            });
        }

        // Data loading
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

                const stream = document.getElementById('thought-stream');
                if (data.thoughts && data.thoughts.length > 0) {
                    stream.innerHTML = data.thoughts.slice(0, 5).map(t => `
                        <div class="thought-item" style="border-left-color: ${getTypeColor(t.type)}">
                            <div class="thought-type">${t.type}</div>
                            <div class="thought-content">${t.content.substring(0, 80)}${t.content.length > 80 ? '...' : ''}</div>
                            <div class="thought-meta">${new Date(t.timestamp).toLocaleTimeString()}</div>
                        </div>
                    `).join('');
                }
            } catch (e) {
                console.error('Thoughts load failed:', e);
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
            document.getElementById('results-section').innerHTML = '';
        }

        // Keyboard shortcut
        document.getElementById('main-input').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.metaKey) {
                processInput();
            }
        });
    </script>
</body>
</html>"""


def run_enhanced_server(port: int = 8889) -> None:
    """Run the enhanced Brain UI server."""
    print("🧠 Initializing AMOS Brain...")
    try:
        from AMOS_ORGANISM_OS.organism import AmosOrganism

        organism = AmosOrganism()
        EnhancedBrainUIHandler.orchestrator = organism
        EnhancedBrainUIHandler.brain = organism.brain
        print(f"   ✓ Brain loaded: {organism.brain.state.session_id}")
    except Exception as e:
        print(f"   ⚠ Brain init warning: {e}")
        from AMOS_ORGANISM_OS.BRAIN.brain_os import BrainOS

        brain = BrainOS()
        EnhancedBrainUIHandler.brain = brain
        print(f"   ✓ Brain loaded (fallback): {brain.state.session_id}")

    server = HTTPServer(("", port), EnhancedBrainUIHandler)
    url = f"http://localhost:{port}"

    print("=" * 60)
    print("🌐 AMOS Brain Enhanced Cognitive Interface")
    print("=" * 60)
    print(f"\n📍 Server running at: {url}")
    print("\nFeatures:")
    print("   • 7-Layer Cognitive Stack Visualization")
    print("   • Real-time Neural Background Animation")
    print("   • Cognitive Reasoning Path Display")
    print("   • Interactive Mode Switching")
    print("   • Live Thought Stream")
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
    port = 8889
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass

    run_enhanced_server(port)
    return 0


if __name__ == "__main__":
    sys.exit(main())
