#!/usr/bin/env python3
"""AMOS 57-Component API Server.

REST API exposing the complete 57-component autonomous system.
Provides stateful access to all layers with real-time health monitoring.

State-of-the-art autonomous system API patterns:
- Stateful architecture (maintains governance context)
- Real-time health endpoints
- Async operation support
- Comprehensive observability

Endpoints:
  GET  /health          - System health check
  GET  /status          - Full 57-component status
  POST /orchestrate     - Start/stop orchestrator
  POST /process         - Process message via coherence
  GET  /governance      - Meta-architecture governance status
  GET  /components      - List all 57 components
  POST /heal           - Trigger self-healing

Usage:
  python amos_57_api_server.py
"""

import logging
import time
from datetime import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS

# Import 57-component orchestrator
try:
    from amos_57_master_orchestrator import (
        AMOS57MasterOrchestrator,
        OrchestratorConfig,
    )

    ORCHESTRATOR_AVAILABLE = True
except ImportError as e:
    ORCHESTRATOR_AVAILABLE = False
    print(f"Warning: 57-component orchestrator not available: {e}")

# Import legacy components as fallback
try:
    from amos_coherence_engine import AMOSCoherenceEngine

    COHERENCE_AVAILABLE = True
except ImportError:
    COHERENCE_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://localhost:8080"])

# Global orchestrator instance
orchestrator = None
start_time = time.time()


def get_orchestrator() -> AMOS57MasterOrchestrator:
    """Get or create orchestrator instance."""
    global orchestrator
    if orchestrator is None and ORCHESTRATOR_AVAILABLE:
        config = OrchestratorConfig(
            health_check_interval=5.0,
            self_healing_enabled=True,
            api_enabled=True,
        )
        orchestrator = AMOS57MasterOrchestrator(config)
    return orchestrator


@app.route("/health", methods=["GET"])
def health_check():
    """Basic health check endpoint."""
    uptime = time.time() - start_time
    return jsonify(
        {
            "status": "healthy",
            "service": "amos-57-api",
            "uptime_seconds": round(uptime, 1),
            "orchestrator_available": ORCHESTRATOR_AVAILABLE,
            "timestamp": datetime.now().isoformat(),
        }
    )


@app.route("/status", methods=["GET"])
def system_status():
    """Get full 57-component system status."""
    orch = get_orchestrator()

    if orch is None:
        return jsonify(
            {
                "success": False,
                "error": "57-component orchestrator not available",
                "fallback": COHERENCE_AVAILABLE,
            }
        ), 503

    if not orch.initialized:
        return jsonify(
            {
                "success": False,
                "error": "Orchestrator not initialized",
                "initialized": False,
            }
        ), 503

    status = orch.get_status()
    return jsonify(
        {
            "success": True,
            "status": status,
            "components": 57,
            "api_version": "57.0.0",
        }
    )


@app.route("/orchestrate", methods=["POST"])
def orchestrate():
    """Control the master orchestrator.

    Request body:
        {"action": "start" | "stop" | "status"}
    """
    if not ORCHESTRATOR_AVAILABLE:
        return jsonify(
            {
                "success": False,
                "error": "Orchestrator not available",
            }
        ), 503

    try:
        data = request.get_json() or {}
        action = data.get("action", "status")

        orch = get_orchestrator()

        if action == "start":
            if not orch.initialized:
                orch.initialize()
            if not orch.running:
                orch.start()
            return jsonify(
                {
                    "success": True,
                    "action": "start",
                    "initialized": orch.initialized,
                    "running": orch.running,
                }
            )

        elif action == "stop":
            if orch.running:
                orch.stop()
            return jsonify(
                {
                    "success": True,
                    "action": "stop",
                    "running": orch.running,
                }
            )

        elif action == "status":
            return jsonify(
                {
                    "success": True,
                    "action": "status",
                    "initialized": orch.initialized,
                    "running": orch.running,
                }
            )

        else:
            return jsonify(
                {
                    "success": False,
                    "error": f"Unknown action: {action}",
                }
            ), 400

    except Exception as e:
        logger.error(f"Orchestrate error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/process", methods=["POST"])
def process_message():
    """Process a message through the 57-component system.

    Request body:
        {"message": "text to process"}
    """
    try:
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"error": "Missing required field: message"}), 400

        message = data["message"]
        logger.info(f"Process request: {message[:50]}...")

        orch = get_orchestrator()

        if orch and orch.initialized:
            # Use 57-component orchestrator
            result = orch.process_message(message)
        elif COHERENCE_AVAILABLE:
            # Fallback to coherence engine
            engine = AMOSCoherenceEngine()
            result = engine.process(message)
            result = {
                "success": True,
                "response": result.response,
                "state": result.detected_state.value,
                "intervention": result.intervention_mode.value,
                "source": "coherence_engine",
            }
        else:
            return jsonify(
                {
                    "success": False,
                    "error": "No processing engine available",
                }
            ), 503

        return jsonify(result)

    except Exception as e:
        logger.error(f"Process error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/governance", methods=["GET"])
def governance_status():
    """Get meta-architecture governance status."""
    orch = get_orchestrator()

    if orch is None or not orch.initialized:
        return jsonify(
            {
                "success": False,
                "error": "Orchestrator not initialized",
            }
        ), 503

    try:
        status = orch.get_status()
        governance = status.get("components", {})

        return jsonify(
            {
                "success": True,
                "governance": {
                    "meta_architecture": governance.get("meta_architecture"),
                    "meta_ontological": governance.get("meta_ontological"),
                    "formal_core": governance.get("formal_core"),
                    "production": governance.get("production"),
                },
                "systems": [
                    "Promise",
                    "Breach",
                    "Identity-Over-Time",
                    "Equivalence",
                    "Memory/Forgetting",
                    "Disagreement Resolution",
                    "Legitimacy",
                    "Self-Modification",
                    "Semantic Survival",
                    "Meta-Governance",
                ],
            }
        )

    except Exception as e:
        logger.error(f"Governance error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/components", methods=["GET"])
def list_components():
    """List all 57 components."""
    components = {
        "meta_architecture": {
            "count": 10,
            "systems": [
                "Promise System",
                "Breach System",
                "Identity-Over-Time",
                "Equivalence System",
                "Memory/Forgetting",
                "Disagreement Resolution",
                "Legitimacy",
                "Self-Modification",
                "Semantic Survival",
                "Meta-Governance",
            ],
        },
        "meta_ontological": {
            "count": 12,
            "components": [
                "Energy Budget",
                "Temporal Hierarchy",
                "Self-Representation",
                "Identity Manifold",
                "Observer State",
                "Sheaf of Truths",
                "Agency Field",
                "Embodiment Operator",
                "Program Deformation",
                "Renormalization Operator",
                "Meta-Semantic Evaluator",
                "Ethical Boundary",
            ],
        },
        "formal_core": {
            "count": 21,
            "components": [
                "State Bundle",
                "Intent Field",
                "Syntax Structure",
                "Ontology Frame",
                "Dynamics Field",
                "Action Universe",
                "Bridge Morphism",
                "Measurement Projection",
                "Verification Kernel",
                "Ledger Entry",
                "Uncertainty Field",
                "Observation Filter",
                "Constraint Field",
                "Topology",
                "Sheaf",
                "Bundle Metric",
                "Entropy Gradient",
                "Evolution Operator",
                "Reduction Map",
                "Equilibrium State",
                "AMOS Formal System",
            ],
        },
        "production": {
            "count": 46,
            "description": "Coherence Engine and operational components",
        },
    }

    return jsonify(
        {
            "success": True,
            "total_components": 57,
            "layers": components,
            "orchestrator_available": ORCHESTRATOR_AVAILABLE,
        }
    )


@app.route("/heal", methods=["POST"])
def trigger_healing():
    """Trigger self-healing actions."""
    orch = get_orchestrator()

    if orch is None or not orch.initialized:
        return jsonify(
            {
                "success": False,
                "error": "Orchestrator not initialized",
            }
        ), 503

    try:
        # Force health check and healing
        status_before = orch.get_status()

        # Trigger healing if health check method exists
        if hasattr(orch, "_execute_self_healing"):
            orch._execute_self_healing()
            orch.healing_actions += 1

        status_after = orch.get_status()

        return jsonify(
            {
                "success": True,
                "status_before": status_before.get("status"),
                "status_after": status_after.get("status"),
                "coherence_before": status_before.get("coherence_score"),
                "coherence_after": status_after.get("coherence_score"),
                "healing_actions": orch.healing_actions,
            }
        )

    except Exception as e:
        logger.error(f"Healing error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/health/history", methods=["GET"])
def health_history():
    """Get health check history."""
    orch = get_orchestrator()

    if orch is None or not orch.initialized:
        return jsonify(
            {
                "success": False,
                "error": "Orchestrator not initialized",
            }
        ), 503

    try:
        history = orch.health_history[-100:] if hasattr(orch, "health_history") else []

        return jsonify(
            {
                "success": True,
                "history_length": len(history),
                "cycles_completed": orch.cycles,
                "recent_checks": [
                    {
                        "timestamp": h.timestamp,
                        "status": h.overall_status,
                        "coherence": h.coherence_score,
                    }
                    for h in history[-10:]
                ],
            }
        )

    except Exception as e:
        logger.error(f"Health history error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


def main():
    """Run the 57-component API server."""
    import argparse

    parser = argparse.ArgumentParser(description="AMOS 57-Component API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("AMOS 57-Component API Server")
    print("=" * 70)
    print(f"Orchestrator Available: {ORCHESTRATOR_AVAILABLE}")
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"Debug: {args.debug}")
    print("\nEndpoints:")
    print("  GET  /health          - Health check")
    print("  GET  /status          - System status")
    print("  POST /orchestrate     - Control orchestrator")
    print("  POST /process         - Process message")
    print("  GET  /governance      - Governance status")
    print("  GET  /components      - List components")
    print("  POST /heal            - Trigger healing")
    print("  GET  /health/history  - Health history")
    print("=" * 70)

    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
