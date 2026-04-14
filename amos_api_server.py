#!/usr/bin/env python3
"""
AMOS Brain API Server
====================

Exposes AMOS cognitive capabilities via REST API for neurosyncai.tech

Endpoints:
  POST /think    - Cognitive analysis
  POST /decide   - Decision making
  POST /validate - Action validation
  GET  /status   - Brain status
  GET  /health   - Health check

Usage:
  python amos_api_server.py
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from amos_brain import BrainClient
from amosl import parse, compile_program, validate_invariants
from amos_monitoring_middleware import init_monitoring
from amos_coherence_engine import AMOSCoherenceEngine
import os
import sys
import logging
from pathlib import Path


def get_organism_root() -> Path:
    """Get the AMOS organism root directory."""
    # Try environment variable first
    env_root = os.environ.get('AMOS_ROOT')
    if env_root:
        return Path(env_root)
    # Default to AMOS_ORGANISM_OS in repo root
    current = Path(__file__).parent
    return current / "AMOS_ORGANISM_OS"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='templates')
# Configure CORS with restricted origins
CORS(app, origins=["http://localhost:3000", "https://neurosyncai.tech"])

# Initialize services with error handling (prevents startup crashes)
brain = None
coherence_engine = None
monitoring = None

try:
    brain = BrainClient()
    logger.info("Brain client initialized")
except Exception as e:
    logger.warning(f"Brain client not available: {e}")

try:
    coherence_engine = AMOSCoherenceEngine()
    logger.info("Coherence engine initialized")
except Exception as e:
    logger.warning(f"Coherence engine not available: {e}")

try:
    monitoring = init_monitoring(app)
    logger.info("Monitoring middleware initialized")
except Exception as e:
    logger.warning(f"Monitoring not available: {e}")


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'amos-brain-api',
        'domain': 'neurosyncai.tech'
    })


@app.route('/status', methods=['GET'])
def brain_status():
    """Get full brain status."""
    if brain is None:
        return jsonify({
            'success': False,
            'error': 'Brain client not available'
        }), 503
    try:
        status = brain.get_status()
        return jsonify({
            'success': True,
            'status': status
        })
    except Exception as e:
        logger.error(f"Status error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/think', methods=['POST'])
def think_endpoint():
    """Think endpoint - cognitive analysis."""
    import time
    from database import db
    
    start_time = time.time()
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Missing required field: query'}), 400
        
        query = data['query']
        domain = data.get('domain', 'general')
        
        logger.info(f"Think request: {query[:50]}...")
        
        result = brain.think(query, domain=domain)
        
        # Log to database
        processing_time = int((time.time() - start_time) * 1000)
        db.log_query(
            api_key_hash='public',
            endpoint='think',
            query=query[:200],
            domain=domain,
            response_summary=result.content[:200],
            confidence=str(result.confidence),
            law_compliant=result.law_compliant,
            processing_time_ms=processing_time
        )
        
        return jsonify({
            'success': True,
            'content': result.content,
            'reasoning': result.reasoning,
            'confidence': result.confidence,
            'law_compliant': result.law_compliant,
            'domain': result.domain
        })
    except Exception as e:
        logger.error(f"Think error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/decide', methods=['POST'])
def decide_endpoint():
    """
    Decision making endpoint.

    Request body:
        {
            "question": "Should we use X?",
            "options": ["option1", "option2"] (optional)
        }
    """
    try:
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({'error': 'Missing required field: question'}), 400

        question = data['question']
        options = data.get('options')

        logger.info(f"Decide request: {question[:50]}...")

        decision = brain.decide(question, options=options)

        return jsonify({
            'approved': decision.approved,
            'decision_id': decision.decision_id,
            'reasoning': decision.reasoning,
            'risk_level': decision.risk_level,
            'law_violations': decision.law_violations,
            'alternative_actions': decision.alternative_actions
        })
    except Exception as e:
        logger.error(f"Decide error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/validate', methods=['POST'])
def validate_endpoint():
    """
    Action validation endpoint.

    Request body:
        {
            "action": "Description of action to validate"
        }
    """
    try:
        data = request.get_json()
        if not data or 'action' not in data:
            return jsonify({'error': 'Missing required field: action'}), 400

        action = data['action']

        logger.info(f"Validate request: {action[:50]}...")

        is_valid, violations = brain.validate_action(action)

        return jsonify({
            'valid': is_valid,
            'violations': violations,
            'action': action
        })
    except Exception as e:
        logger.error(f"Validate error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/coherence', methods=['POST'])
def coherence_endpoint():
    """
    Coherence Engine endpoint - Human coherence induction.

    Request body:
        {
            "message": "I can't do this, it's impossible."
        }

    Response:
        {
            "success": true,
            "response": "It sounds less like inability and more like fear...",
            "state": "overloaded",
            "intervention": "separate",
            "signal": "fear entering before action",
            "capacity": 0.3,
            "clarity": 0.45,
            "safety_maintained": true
        }
    """
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Missing required field: message'}), 400

        message = data['message']
        logger.info(f"Coherence request: {message[:50]}...")

        # Process through coherence engine
        result = coherence_engine.process(message)

        return jsonify({
            'success': True,
            'response': result.response,
            'state': result.detected_state.value,
            'intervention': result.intervention_mode.value,
            'signal': result.signal_detected,
            'noise_reduced': result.noise_reduced,
            'capacity': result.estimated_capacity,
            'clarity': result.clarity_increase,
            'agency_preserved': result.agency_preserved,
            'safety_maintained': result.safety_maintained
        })
    except Exception as e:
        logger.error(f"Coherence error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/amosl/compile', methods=['POST'])
def amosl_compile():
    """
    AMOSL compiler endpoint.

    Request body:
        {
            "source": "ontology { ... }"
        }

    Response:
        {
            "success": true,
            "cir": { ... },
            "qir": { ... },
            "bir": { ... },
            "hir": { ... },
            "invariants_valid": true
        }
    """
    try:
        data = request.get_json()
        if not data or 'source' not in data:
            return jsonify({'error': 'Missing required field: source'}), 400

        source = data['source']
        logger.info(f"AMOSL compile request: {source[:50]}...")

        # Parse AMOSL source
        program = parse(source)

        # Validate invariants
        inv_valid, violations = validate_invariants(program)

        # Compile to 4 IRs
        cir, qir, bir, hir = compile_program(program)

        return jsonify({
            'success': True,
            'invariants_valid': inv_valid,
            'invariant_violations': violations,
            'ir': {
                'cir_blocks': len(cir.blocks),
                'qir_registers': len(qir.registers),
                'bir_species': len(bir.species),
                'hir_bridges': len(hir.bridges)
            }
        })
    except Exception as e:
        logger.error(f"AMOSL compile error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/dashboard', methods=['GET'])
def dashboard():
    """Serve the AMOS Brain Dashboard."""
    dashboard_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dashboard')
    return send_from_directory(dashboard_path, 'index.html')


@app.route('/dashboard/<path:filename>')
def dashboard_static(filename):
    """Serve dashboard static files."""
    dashboard_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dashboard')
    return send_from_directory(dashboard_path, filename)


@app.route('/admin', methods=['GET'])
def admin_dashboard():
    """Serve the Admin Dashboard."""
    admin_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'admin-dashboard')
    return send_from_directory(admin_path, 'index.html')


@app.route('/admin/<path:filename>')
def admin_static(filename):
    """Serve admin dashboard static files."""
    admin_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'admin-dashboard')
    return send_from_directory(admin_path, filename)


@app.route('/api/history', methods=['GET'])
def get_history():
    """Get query history."""
    from database import db
    limit = request.args.get('limit', 100, type=int)
    history = db.get_query_history(limit=limit)
    return jsonify({'success': True, 'history': history})


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get API usage statistics."""
    from database import db
    stats = db.get_usage_stats(days=days)
    return jsonify({'success': True, 'stats': stats})


@app.route('/api/workflows', methods=['GET'])
def api_workflows_list():
    """List all workflows."""
    try:
        organism_root = get_organism_root()
        sys.path.insert(0, str(organism_root / "06_MUSCLE"))
        from workflow_engine import WorkflowEngine
        engine = WorkflowEngine()
        workflows = [
            {"id": w.id, "name": w.name, "status": w.status, "steps": len(w.steps)}
            for w in engine.list_workflows()
        ]
        return jsonify({"workflows": workflows, "count": len(workflows)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/workflows/<workflow_id>/run', methods=['POST'])
def api_workflow_run(workflow_id):
    """Run a specific workflow."""
    try:
        organism_root = get_organism_root()
        sys.path.insert(0, str(organism_root / "06_MUSCLE"))
        from workflow_engine import WorkflowEngine
        engine = WorkflowEngine()
        result = engine.run_workflow(workflow_id)
        return jsonify({
            "success": True,
            "workflow_id": workflow_id,
            "status": result.status,
            "steps_completed": len([s for s in result.steps if s.status.value == "success"])
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Extended API: Pipeline Engine
@app.route('/api/pipelines', methods=['GET'])
def api_pipelines_list():
    """List all pipelines."""
    try:
        organism_root = get_organism_root()
        sys.path.insert(0, str(organism_root / "07_METABOLISM"))
        from pipeline_engine import PipelineEngine
        engine = PipelineEngine()
        pipelines = [
            {"id": p.id, "name": p.name, "status": p.status, "stages": len(p.stages)}
            for p in engine.pipelines.values()
        ]
        return jsonify({"pipelines": pipelines, "count": len(pipelines)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/pipelines/<pipeline_id>/run', methods=['POST'])
def api_pipeline_run(pipeline_id):
    """Run a specific pipeline."""
    try:
        data = request.get_json() or {}
        organism_root = get_organism_root()
        sys.path.insert(0, str(organism_root / "07_METABOLISM"))
        from pipeline_engine import PipelineEngine
        engine = PipelineEngine()
        result = engine.execute_pipeline(pipeline_id, initial_data=data.get("data"))
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Extended API: Alerting System (Organism Integration)
@app.route('/api/alerts/active', methods=['GET'], endpoint='organism_alerts_active')
def organism_alerts_active():
    """Get active alerts from organism immune system."""
    try:
        organism_root = get_organism_root()
        sys.path.insert(0, str(organism_root / "03_IMMUNE"))
        from alert_manager import AlertManager
        manager = AlertManager(organism_root)
        alerts = manager.get_active_alerts()
        return jsonify({"alerts": alerts, "count": len(alerts)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/alerts/evaluate', methods=['POST'])
def api_alerts_evaluate():
    """Evaluate metrics and trigger alerts."""
    try:
        data = request.get_json() or {}
        metrics = data.get("metrics", {})
        organism_root = get_organism_root()
        sys.path.insert(0, str(organism_root / "03_IMMUNE"))
        from alert_manager import AlertManager
        manager = AlertManager(organism_root)
        alerts = manager.evaluate_and_alert(metrics)
        return jsonify({"alerts_triggered": alerts, "count": len(alerts)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Extended API: Orchestrator
@app.route('/api/orchestrator/cycle', methods=['POST'])
def api_orchestrator_cycle():
    """Trigger orchestrator cycle."""
    try:
        organism_root = get_organism_root()
        sys.path.insert(0, str(organism_root))
        from AMOS_MASTER_ORCHESTRATOR import AMOSOrganismOrchestrator
        orch = AMOSOrganismOrchestrator(organism_root)
        result = orch.cycle()
        return jsonify({
            "success": True,
            "cycle": result.cycle_number,
            "status": result.global_state.status,
            "processed": len(result.processed_handlers)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/', methods=['GET'])
def root():
    """Root endpoint with API info."""
    return jsonify({
        'service': 'AMOS Brain API',
        'domain': 'neurosyncai.tech',
        'version': '1.1.0',
        'dashboard': '/dashboard',
        'admin': '/admin',
        'monitoring': '/monitoring',
        'features': [
            'Cognitive Analysis (think)',
            'Decision Making (decide)',
            'Action Validation (validate)',
            'Coherence Engine (coherence)',
            'AMOSL Compiler (amosl/compile)',
            'Query History (history)',
            'Usage Stats (stats)',
            'Real-time WebSocket (ws://)',
            'Admin Dashboard (admin)',
            'Production Monitoring (monitoring)',
            'Health Checks (api/health)',
            'Metrics Export (api/metrics)',
            'Alert Management (api/alerts)',
            'Workflow Engine (api/workflows)',
            'Pipeline Engine (api/pipelines)',
            'Orchestrator Control (api/orchestrator)'
        ],
        'endpoints': {
            'health': '/health',
            'status': '/status',
            'think': 'POST /think',
            'decide': 'POST /decide',
            'validate': 'POST /validate',
            'coherence': 'POST /coherence',
            'amosl_compile': 'POST /amosl/compile',
            'history': 'GET /api/history',
            'stats': 'GET /api/stats',
            'dashboard': '/dashboard',
            'admin': '/admin',
            'monitoring': '/monitoring',
            'api_health': '/api/health',
            'api_metrics': '/api/metrics',
            'api_alerts': '/api/alerts/active',
            'api_workflows': 'GET /api/workflows',
            'api_workflow_run': 'POST /api/workflows/<id>/run',
            'api_pipelines': 'GET /api/pipelines',
            'api_pipeline_run': 'POST /api/pipelines/<id>/run',
            'api_orchestrator_cycle': 'POST /api/orchestrator/cycle'
        }
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'

    logger.info("Starting AMOS Brain API on port %s", port)
    logger.info("Domain: neurosyncai.tech")

    app.run(host='0.0.0.0', port=port, debug=debug)
