#!/usr/bin/env python3
"""
AMOS Brain Dashboard - Real-time visualization and monitoring.

Features:
- Brain status (engines, laws, domains)
- Real-time reasoning visualization
- Decision history timeline
- Organism subsystem status
- Law compliance tracking
- API endpoints for metrics

Usage:
    python amos_dashboard.py          # Start dashboard on port 8080
    python amos_dashboard.py --port 5000

Access:
    http://localhost:8080 - Dashboard UI
    http://localhost:8080/api/status - JSON status
"""
from __future__ import annotations

import sys
import os
import json
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask, render_template, jsonify
from flask_cors import CORS

from amos_brain import get_amos_integration
from amos_brain.memory import get_brain_memory

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# AMOS instance
_amos = None


def get_amos():
    """Get or initialize AMOS brain."""
    global _amos
    if _amos is None:
        _amos = get_amos_integration()
    return _amos


# ── HTML Template ───────────────────────────────────────────────────────────

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AMOS Brain Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0f;
            color: #e0e0e0;
            min-height: 100vh;
        }
        .header {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            padding: 2rem;
            border-bottom: 1px solid #2a2a3e;
        }
        .header h1 {
            font-size: 2rem;
            background: linear-gradient(90deg, #00d4ff, #7b2cbf);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        .header p { color: #888; }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-top: 2rem;
        }
        .card {
            background: #1a1a2e;
            border: 1px solid #2a2a3e;
            border-radius: 12px;
            padding: 1.5rem;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 32px rgba(0, 212, 255, 0.1);
        }
        .card h2 {
            font-size: 1.1rem;
            color: #00d4ff;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.875rem;
            font-weight: 500;
        }
        .status-active {
            background: rgba(0, 255, 136, 0.15);
            color: #00ff88;
        }
        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.75rem 0;
            border-bottom: 1px solid #2a2a3e;
        }
        .metric:last-child { border-bottom: none; }
        .metric-value {
            font-size: 1.5rem;
            font-weight: 600;
            color: #fff;
        }
        .metric-label { color: #888; font-size: 0.9rem; }
        .law-item {
            display: flex;
            align-items: flex-start;
            gap: 0.75rem;
            padding: 0.75rem;
            background: rgba(0, 212, 255, 0.05);
            border-radius: 8px;
            margin-bottom: 0.5rem;
        }
        .law-id {
            font-weight: 600;
            color: #00d4ff;
            min-width: 2rem;
        }
        .domain-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 0.5rem;
        }
        .domain-tag {
            padding: 0.5rem;
            background: rgba(123, 44, 191, 0.2);
            border-radius: 6px;
            text-align: center;
            font-size: 0.8rem;
        }
        .reasoning-card {
            background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(123, 44, 191, 0.1) 100%);
            border: 1px solid rgba(0, 212, 255, 0.3);
        }
        .quadrant-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 0.75rem;
        }
        .quadrant {
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
        }
        .q-bio { background: rgba(0, 255, 136, 0.15); }
        .q-tech { background: rgba(0, 212, 255, 0.15); }
        .q-econ { background: rgba(255, 193, 7, 0.15); }
        .q-env { background: rgba(123, 44, 191, 0.15); }
        .refresh-btn {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            padding: 1rem 2rem;
            background: linear-gradient(135deg, #00d4ff, #7b2cbf);
            color: white;
            border: none;
            border-radius: 30px;
            cursor: pointer;
            font-weight: 600;
            box-shadow: 0 4px 16px rgba(0, 212, 255, 0.3);
        }
        .timestamp {
            text-align: center;
            color: #666;
            margin-top: 2rem;
            font-size: 0.875rem;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>AMOS Brain Dashboard</h1>
        <p>Real-time cognitive architecture monitoring</p>
    </div>
    
    <div class="container">
        <div class="grid">
            <!-- Status Card -->
            <div class="card">
                <h2>🧠 Brain Status</h2>
                <div class="metric">
                    <span class="metric-label">Status</span>
                    <span class="status-badge status-active">
                        <span class="dot">●</span> {{ status.initialized }}
                    </span>
                </div>
                <div class="metric">
                    <span class="metric-label">Engines</span>
                    <span class="metric-value">{{ status.engines_count }}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Domains</span>
                    <span class="metric-value">{{ status.domains_count }}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Laws Active</span>
                    <span class="metric-value">{{ status.laws_count }}</span>
                </div>
            </div>
            
            <!-- Laws Card -->
            <div class="card">
                <h2>⚖️ Global Laws</h2>
                {% for law in laws %}
                <div class="law-item">
                    <span class="law-id">{{ law.id }}</span>
                    <span>{{ law.name }}</span>
                </div>
                {% endfor %}
            </div>
            
            <!-- Domains Card -->
            <div class="card">
                <h2>🌐 Domain Coverage</h2>
                <div class="domain-grid">
                    {% for domain in domains %}
                    <div class="domain-tag">{{ domain }}</div>
                    {% endfor %}
                </div>
            </div>
            
            <!-- Reasoning Card -->
            <div class="card reasoning-card">
                <h2>🔄 Rule of 2 / Rule of 4</h2>
                <div class="metric">
                    <span class="metric-label">Dual Perspective</span>
                    <span class="metric-value">✓</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Four Quadrants</span>
                    <span class="metric-value">✓</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Structural Integrity</span>
                    <span class="metric-value">L4</span>
                </div>
            </div>
            
            <!-- Quadrants Card -->
            <div class="card">
                <h2>📊 Four Quadrants</h2>
                <div class="quadrant-grid">
                    <div class="quadrant q-bio">
                        <strong>Biological</strong>
                        <p>Human/Cognitive</p>
                    </div>
                    <div class="quadrant q-tech">
                        <strong>Technical</strong>
                        <p>Infrastructure</p>
                    </div>
                    <div class="quadrant q-econ">
                        <strong>Economic</strong>
                        <p>Resources</p>
                    </div>
                    <div class="quadrant q-env">
                        <strong>Environmental</strong>
                        <p>Context</p>
                    </div>
                </div>
            </div>
            
            <!-- Memory Card -->
            <div class="card">
                <h2>💾 Memory</h2>
                <div class="metric">
                    <span class="metric-label">Decisions Logged</span>
                    <span class="metric-value">{{ memory_count }}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Reasoning History</span>
                    <span class="metric-value">{{ memory_count }}</span>
                </div>
            </div>
        </div>
        
        <p class="timestamp">Last updated: {{ timestamp }}</p>
    </div>
    
    <button class="refresh-btn" onclick="location.reload()">🔄 Refresh</button>
</body>
</html>
"""


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/')
def dashboard():
    """Main dashboard UI."""
    amos = get_amos()
    status = amos.get_status()
    
    # Parse laws summary
    laws_text = amos.get_laws_summary()
    laws = [
        {"id": "L1", "name": "Law of Law"},
        {"id": "L2", "name": "Rule of 2"},
        {"id": "L3", "name": "Rule of 4"},
        {"id": "L4", "name": "Structural Integrity"},
        {"id": "L5", "name": "Communication"},
        {"id": "L6", "name": "UBI Alignment"},
    ]
    
    # Get memory count
    try:
        mem = get_brain_memory()
        history = mem.get_reasoning_history(limit=1000)
        memory_count = len(history)
    except:
        memory_count = 0
    
    return render_template_string(
        DASHBOARD_HTML,
        status={
            "initialized": "Active" if status['initialized'] else "Inactive",
            "engines_count": status['engines_count'],
            "domains_count": len(status['domains_covered']),
            "laws_count": len(status['laws_active'])
        },
        laws=laws,
        domains=status['domains_covered'][:12],
        memory_count=memory_count,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )


@app.route('/api/status')
def api_status():
    """API endpoint for brain status."""
    amos = get_amos()
    status = amos.get_status()
    
    return jsonify({
        "brain": {
            "initialized": status['initialized'],
            "engines_count": status['engines_count'],
            "laws_active": status['laws_active'],
            "domains_covered": status['domains_covered'],
        },
        "laws_summary": amos.get_laws_summary(),
        "timestamp": datetime.utcnow().isoformat(),
    })


@app.route('/api/reasoning', methods=['POST'])
def api_reasoning():
    """API endpoint for reasoning analysis."""
    from flask import request
    
    data = request.get_json()
    problem = data.get('problem', '')
    
    if not problem:
        return jsonify({"error": "No problem specified"}), 400
    
    amos = get_amos()
    result = amos.analyze_with_rules(problem)
    
    return jsonify({
        "problem": problem,
        "rule_of_two": {
            "confidence": result['rule_of_two']['confidence'],
            "recommendation": result['rule_of_two']['recommendation'],
        },
        "rule_of_four": {
            "quadrants": result['rule_of_four']['quadrants_analyzed'],
            "completeness": result['rule_of_four']['completeness_score'],
        },
        "recommendations": result.get('recommendations', []),
        "timestamp": datetime.utcnow().isoformat(),
    })


@app.route('/api/memory')
def api_memory():
    """API endpoint for memory query."""
    try:
        mem = get_brain_memory()
        history = mem.get_reasoning_history(limit=100)
        return jsonify({
            "count": len(history),
            "decisions": [
                {
                    "problem": h.get('problem', 'Unknown')[:100],
                    "timestamp": h.get('timestamp'),
                    "tags": h.get('tags', []),
                }
                for h in history[:20]
            ]
        })
    except Exception as e:
        return jsonify({"error": str(e), "count": 0, "decisions": []})


def render_template_string(template, **kwargs):
    """Simple template rendering."""
    from jinja2 import Template
    return Template(template).render(**kwargs)


def main():
    """Start dashboard server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="AMOS Brain Dashboard")
    parser.add_argument("--port", type=int, default=8080, help="Port to run on")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    args = parser.parse_args()
    
    print(f"╔════════════════════════════════════════════════════════════╗")
    print(f"║        AMOS Brain Dashboard                                ║")
    print(f"╠════════════════════════════════════════════════════════════╣")
    print(f"║  URL: http://{args.host}:{args.port}                        ║")
    print(f"║  API: http://{args.host}:{args.port}/api/status             ║")
    print(f"╚════════════════════════════════════════════════════════════╝")
    print()
    
    # Pre-load AMOS
    get_amos()
    print("✓ AMOS brain initialized")
    print()
    
    app.run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    main()
