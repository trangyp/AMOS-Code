#!/usr/bin/env python3
"""AMOS API Server Enhanced - Full Ecosystem Exposure
====================================================

Complete REST API exposing all 9 built components:
- 14-Subsystem Organism OS
- 6 Global Laws Brain
- 50MB+ Knowledge Base
- Interactive Shell Commands

Endpoints:
  GET  /                    - API info & status
  GET  /status              - Complete system status
  GET  /health              - Health check

  POST /think               - Knowledge-enhanced thinking
  POST /query               - Query knowledge base

  GET  /subsystems          - List all subsystems
  GET  /subsystems/<name>   - Get subsystem details

  GET  /countries           - List loaded countries
  GET  /countries/<code>    - Get country details

  GET  /sectors             - List loaded sectors
  GET  /sectors/<code>      - Get sector details

  POST /demo                - Run demonstrations

Usage:
  python amos_api_enhanced.py

Then visit: http://localhost:5000

Owner: Trang
"""

import sys
from datetime import datetime
from pathlib import Path

from flask import Flask, Response, jsonify, request
from flask_cors import CORS

# Add paths
REPO_ROOT = Path(__file__).parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "AMOS_ORGANISM_OS"))
sys.path.insert(0, str(REPO_ROOT / "amos_brain"))
sys.path.insert(0, str(REPO_ROOT / "backend"))

# Import RAG
from backend.rag_api import register_rag_routes


# Async helper for safe event loop handling
def _run_async(coro):
    """Run async coroutine safely, handling existing event loops."""
    import asyncio

    try:
        # Try to get running loop
        loop = asyncio.get_running_loop()
        # If we're already in an async context, we can't use run_until_complete
        # Create a new thread to run the coroutine
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(asyncio.run, coro)
            return future.result()
    except RuntimeError:
        # No running loop, safe to use asyncio.run
        return asyncio.run(coro)


app = Flask(__name__)
CORS(app)

# Global AMOS instance
amos_system = None


def get_amos():
    """Get or initialize AMOS system."""
    global amos_system
    if amos_system is None:
        try:
            from amos_unified_enhanced import AMOSUnifiedEnhanced

            amos_system = AMOSUnifiedEnhanced()
            amos_system.initialize(auto_load_knowledge=True)
        except Exception as e:
            print(f"Warning: Could not initialize AMOS: {e}")
            return None
    return amos_system


@app.route("/", methods=["GET"])
def api_info():
    """API information and status."""
    return jsonify(
        {
            "name": "AMOS API Server Enhanced",
            "version": "1.0.0",
            "description": "Complete AMOS ecosystem REST API",
            "endpoints": {
                "status": "/status",
                "health": "/health",
                "think": "POST /think",
                "query": "POST /query",
                "subsystems": "/subsystems",
                "countries": "/countries",
                "sectors": "/sectors",
            },
            "documentation": "See /help for detailed endpoint info",
        }
    )


@app.route("/help", methods=["GET"])
def api_help():
    """Detailed API documentation."""
    return jsonify(
        {
            "endpoints": {
                "/": {"method": "GET", "description": "API information and available endpoints"},
                "/status": {
                    "method": "GET",
                    "description": "Complete system status including organism, brain, and knowledge",
                },
                "/health": {"method": "GET", "description": "Quick health check"},
                "/think": {
                    "method": "POST",
                    "description": "Knowledge-enhanced thinking",
                    "body": {"problem": "string", "context": "optional object"},
                    "example": {"problem": "Best architecture for microservices?"},
                },
                "/query": {
                    "method": "POST",
                    "description": "Query knowledge base",
                    "body": {
                        "query": "string",
                        "domain": "optional string",
                        "limit": "optional int",
                    },
                    "example": {"query": "scalability", "limit": 5},
                },
                "/subsystems": {"method": "GET", "description": "List all 14 subsystems"},
                "/subsystems/<name>": {
                    "method": "GET",
                    "description": "Get specific subsystem details",
                },
                "/countries": {"method": "GET", "description": "List all 55 loaded countries"},
                "/countries/<code>": {
                    "method": "GET",
                    "description": "Get specific country details",
                },
                "/sectors": {"method": "GET", "description": "List all 19 loaded sectors"},
                "/sectors/<code>": {"method": "GET", "description": "Get specific sector details"},
            }
        }
    )


@app.route("/status", methods=["GET"])
def system_status():
    """Get complete system status."""
    amos = get_amos()
    if not amos or not amos.status:
        return jsonify({"error": "System not initialized", "status": "unavailable"}), 503

    return jsonify(
        {
            "system": {
                "name": "AMOS Unified Enhanced",
                "status": "operational",
                "initialized": amos._initialized if hasattr(amos, "_initialized") else False,
            },
            "organism": {
                "ready": amos.status.organism_ready,
                "subsystems_active": amos.status.subsystems_active,
            },
            "brain": {"ready": amos.status.brain_ready, "laws_active": 6},
            "knowledge": {
                "ready": amos.status.knowledge_ready,
                "core_entries": amos.status.knowledge_entries,
                "domains": amos.status.knowledge_domains,
                "memory_mb": amos.status.knowledge_mb,
            },
            "integration": {
                "fully_integrated": all(
                    [
                        amos.status.organism_ready,
                        amos.status.brain_ready,
                        amos.status.knowledge_ready,
                    ]
                )
            },
        }
    )


@app.route("/health", methods=["GET"])
def health_check():
    """Liveness probe - quick check that server is running."""
    return jsonify(
        {
            "status": "healthy",
            "service": "amos-api-enhanced",
            "timestamp": datetime.now(UTC).isoformat(),
        }
    )


@app.route("/ready", methods=["GET"])
def readiness_check():
    """Readiness probe - check if AMOS is initialized and ready to serve."""
    global amos_system

    if amos_system is None:
        return jsonify(
            {
                "status": "not_ready",
                "service": "amos-api-enhanced",
                "reason": "AMOS system not initialized",
                "initialized": False,
            }
        ), 503

    initialized = getattr(amos_system, "_initialized", False)

    if initialized:
        return jsonify(
            {
                "status": "ready",
                "service": "amos-api-enhanced",
                "initialized": True,
                "subsystems": amos_system.status.subsystems_active
                if hasattr(amos_system, "status")
                else 0,
            }
        )
    else:
        return jsonify(
            {
                "status": "initializing",
                "service": "amos-api-enhanced",
                "initialized": False,
                "message": "AMOS system still loading knowledge base...",
            }
        ), 503


@app.route("/think", methods=["POST"])
def think():
    """Knowledge-enhanced thinking endpoint."""
    amos = get_amos()
    if not amos:
        return jsonify({"error": "System not available"}), 503

    data = request.get_json() or {}
    problem = data.get("problem")
    context = data.get("context", {})

    if not problem:
        return jsonify({"error": "Missing problem field"}), 400

    try:
        result = amos.think(problem, context)
        return jsonify({"problem": problem, "result": result, "status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/query", methods=["POST"])
def query_knowledge():
    """Query knowledge base endpoint."""
    amos = get_amos()
    if not amos:
        return jsonify({"error": "System not available"}), 503

    data = request.get_json() or {}
    query = data.get("query")
    domain = data.get("domain")
    limit = data.get("limit", 5)

    if not query:
        return jsonify({"error": "Missing query field"}), 400

    try:
        results = amos.query_knowledge(query, domain, limit)
        return jsonify(
            {
                "query": query,
                "domain": domain,
                "results": results,
                "count": len(results),
                "status": "success",
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/subsystems", methods=["GET"])
def list_subsystems():
    """List all subsystems."""
    amos = get_amos()
    if not amos or not amos.organism:
        return jsonify({"error": "Organism not available"}), 503

    try:
        status = amos.organism.status()
        subsystems = status.get("active_subsystems", [])
        return jsonify(
            {
                "count": len(subsystems),
                "subsystems": subsystems,
                "session_id": status.get("session_id"),
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/subsystems/<name>", methods=["GET"])
def get_subsystem(name):
    """Get specific subsystem."""
    amos = get_amos()
    if not amos:
        return jsonify({"error": "System not available"}), 503

    try:
        subsystem = amos.get_subsystem(name)
        if subsystem:
            return jsonify({"name": name, "available": True, "type": type(subsystem).__name__})
        else:
            return jsonify({"name": name, "available": False, "error": "Subsystem not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/countries", methods=["GET"])
def list_countries():
    """List all loaded countries."""
    try:
        from amos_brain.extended_knowledge_loader import get_comprehensive_knowledge

        system = get_comprehensive_knowledge()
        if not system.initialized:
            system.initialize()

        countries = system.extended_loader.list_countries()
        return jsonify({"count": len(countries), "countries": countries})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/countries/<code>", methods=["GET"])
def get_country(code):
    """Get specific country details."""
    try:
        from amos_brain.extended_knowledge_loader import get_comprehensive_knowledge

        system = get_comprehensive_knowledge()
        if not system.initialized:
            system.initialize()

        country = system.extended_loader.get_country(code.upper())
        if country:
            return jsonify(
                {
                    "code": country.country_code,
                    "name": country.country_name,
                    "geography": country.geography,
                    "economy": country.economy,
                    "culture": country.culture,
                    "regulations": country.regulations,
                    "tags": country.tags,
                }
            )
        else:
            return jsonify({"error": f"Country {code} not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/sectors", methods=["GET"])
def list_sectors():
    """List all loaded sectors."""
    try:
        from amos_brain.extended_knowledge_loader import get_comprehensive_knowledge

        system = get_comprehensive_knowledge()
        if not system.initialized:
            system.initialize()

        sectors = system.extended_loader.list_sectors()
        return jsonify({"count": len(sectors), "sectors": sectors})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/sectors/<code>", methods=["GET"])
def get_sector(code):
    """Get specific sector details."""
    try:
        from amos_brain.extended_knowledge_loader import get_comprehensive_knowledge

        system = get_comprehensive_knowledge()
        if not system.initialized:
            system.initialize()

        sector = system.extended_loader.get_sector(code.upper())
        if sector:
            return jsonify(
                {
                    "code": sector.sector_code,
                    "name": sector.sector_name,
                    "domain": sector.domain,
                    "expertise": sector.expertise,
                    "standards": sector.standards,
                    "tags": sector.tags,
                }
            )
        else:
            return jsonify({"error": f"Sector {code} not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/demo", methods=["POST"])
def run_demo():
    """Run system demonstration."""
    amos = get_amos()
    if not amos:
        return jsonify({"error": "System not available"}), 503

    data = request.get_json() or {}
    demo_type = data.get("type", "all")

    demos = {
        "organism": "14 subsystems active",
        "brain": "6 laws operational",
        "knowledge": "50MB+ knowledge loaded",
        "integration": "All components integrated",
    }

    return jsonify({"demo_type": demo_type, "demos": demos, "status": "success"})


# ============================================================================
# COGNITIVE API ENDPOINTS - UBI + LLM Integration
# ============================================================================


@app.route("/chat", methods=["POST"])
def chat():
    """
    Biologically-aware chat endpoint with conversation memory.

    Request Body:
    {
        "message": "Explain quantum computing",
        "context": "Feeling tired, 6 hours working",
        "model": "llama3.2",
        "session_id": "abc123",  # Optional: continue existing session
        "create_new_session": false  # Optional: force new session
    }

    Response:
    {
        "content": "Here's a simple explanation...",
        "model": "llama3.2",
        "provider": "ollama",
        "session_id": "abc123",
        "biological_context": {...},
        "ui_guidelines": {...},
        "context_window": 6  # Number of previous exchanges included
    }
    """
    try:
        data = request.get_json() or {}
        user_message = data.get("message", "")
        biological_context = data.get("context", "")
        model = data.get("model")
        session_id = data.get("session_id")
        create_new = data.get("create_new_session", False)

        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        # Import cognitive infrastructure
        from backend.llm_providers_complete import Message, get_provider_manager
        from clawspring.amos_cognitive_bridge import get_cognitive_bridge
        from memory.conversation_memory import get_conversation_memory

        # Get conversation memory manager
        memory = get_conversation_memory()

        # Get or create session
        if not session_id or create_new:
            session = memory.create_session()
            session_id = session.session_id
        else:
            session = memory.get_session(session_id)
            if not session:
                # Session not found, create new
                session = memory.create_session()
                session_id = session.session_id

        # Get biological context if provided
        ui_guidelines = {}
        bio_context_dict = {}

        if biological_context:
            bridge = get_cognitive_bridge()
            bio_context = bridge.analyze_user_state(biological_context)
            ui_guidelines = bridge.get_response_guidelines()
            bio_context_dict = {
                "cognitive_load": bio_context.cognitive_load,
                "emotional_state": bio_context.emotional_state,
                "body_comfort": bio_context.body_comfort,
                "environmental_fit": bio_context.environmental_fit,
            }

        # Get previous conversation context
        context_messages = memory.get_context_window(session_id)

        # Build message list with history + current message
        messages = []
        for msg in context_messages:
            messages.append(Message(role=msg["role"], content=msg["content"]))
        messages.append(Message(role="user", content=user_message))

        # Save user message to session
        memory.add_message(
            session_id=session_id,
            role="user",
            content=user_message,
            biological_context=bio_context_dict if biological_context else None,
            ui_guidelines=ui_guidelines if biological_context else None,
        )

        # Get provider manager
        manager = get_provider_manager()

        # Run async completion safely
        response = _run_async(
            manager.complete(
                messages=messages, model=model, biological_context_description=biological_context
            )
        )

        # Save assistant response to session
        memory.add_message(
            session_id=session_id,
            role="assistant",
            content=response.content,
            biological_context=None,  # Response doesn't have bio context
            ui_guidelines=None,
        )

        return jsonify(
            {
                "content": response.content,
                "model": response.model,
                "provider": response.provider,
                "session_id": session_id,
                "latency_ms": response.latency_ms,
                "biological_context": bio_context_dict,
                "ui_guidelines": ui_guidelines,
                "context_window": len(context_messages),
                "timestamp": response.timestamp,
            }
        )

    except Exception as e:
        return jsonify(
            {
                "error": str(e),
                "message": "Failed to generate response. Ensure Ollama is running (ollama serve) or set OPENAI_API_KEY.",
            }
        ), 500


@app.route("/chat/stream", methods=["POST"])
def chat_stream():
    """
    Streaming biologically-aware chat endpoint.

    Returns Server-Sent Events (SSE) stream.
    First chunk contains metadata (biological_context, ui_guidelines, provider info).
    Subsequent chunks contain the streaming response content.
    """
    try:
        data = request.get_json() or {}
        user_message = data.get("message", "")
        biological_context = data.get("context", "")
        model = data.get("model")

        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        import json

        from backend.llm_providers_complete import Message, get_provider_manager
        from clawspring.amos_cognitive_bridge import get_cognitive_bridge

        # Get biological context if provided
        bio_context_dict = {}
        ui_guidelines = {}

        if biological_context:
            bridge = get_cognitive_bridge()
            bio_context = bridge.analyze_user_state(biological_context)
            ui_guidelines = bridge.get_response_guidelines()
            bio_context_dict = {
                "cognitive_load": bio_context.cognitive_load,
                "emotional_state": bio_context.emotional_state,
                "body_comfort": bio_context.body_comfort,
                "environmental_fit": bio_context.environmental_fit,
            }

        manager = get_provider_manager()
        messages = [Message(role="user", content=user_message)]

        def generate():
            import asyncio
            from concurrent.futures import ThreadPoolExecutor

            # First, send metadata as JSON
            metadata = {
                "biological_context": bio_context_dict,
                "ui_guidelines": ui_guidelines,
                "provider": "unknown",
                "model": model or "auto",
            }
            yield f"data: {json.dumps(metadata)}\n\n"

            # Then stream the content in a separate thread with its own event loop
            async def stream_response():
                chunks = []
                async for chunk in manager.complete_stream(
                    messages=messages,
                    model=model,
                    biological_context_description=biological_context,
                ):
                    if isinstance(chunk, str):
                        chunks.append(chunk)
                    else:
                        chunks.append(str(chunk))
                return chunks

            # Run in thread pool to avoid event loop conflicts
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(asyncio.run, stream_response())
                try:
                    chunks = future.result()
                    for chunk in chunks:
                        if chunk:
                            yield f"data: {chunk}\n\n"
                    yield "data: [DONE]\n\n"
                except Exception as stream_err:
                    yield f"data: {{'error': '{str(stream_err)}'}}\n\n"

        return Response(generate(), mimetype="text/event-stream")

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/providers", methods=["GET"])
def list_providers():
    """
    List all available LLM providers and their models.

    Response:
    {
        "providers": {
            "ollama": ["llama3.2", "mistral", "phi4"],
            "openai": ["gpt-4o", "gpt-4o-mini"]
        },
        "recommended": "ollama"
    }
    """
    try:
        from backend.llm_providers_complete import get_provider_manager

        manager = get_provider_manager()

        # Run async call safely
        models = _run_async(manager.get_available_models())

        # Determine recommended provider
        recommended = "ollama" if "ollama" in models and models["ollama"] else "openai"

        return jsonify(
            {
                "providers": models,
                "recommended": recommended,
                "status": "available" if models else "unavailable",
            }
        )

    except Exception as e:
        return jsonify({"providers": {}, "recommended": None, "status": "error", "error": str(e)})


@app.route("/analyze", methods=["POST"])
def analyze_biological_state():
    """
    Analyze biological state using UBI Engine.

    Request Body:
    {
        "description": "Feeling overwhelmed, 6 hours working, screen glare"
    }

    Response:
    {
        "cognitive_load": "high",
        "emotional_state": "stressed",
        "body_comfort": "strained",
        "environmental_fit": "poor",
        "ui_guidelines": {
            "font_size": "18px",
            "chunking": true,
            "tone": "calm"
        }
    }
    """
    try:
        data = request.get_json() or {}
        description = data.get("description", "")

        if not description:
            return jsonify({"error": "Description is required"}), 400

        from clawspring.amos_cognitive_bridge import get_cognitive_bridge

        bridge = get_cognitive_bridge()
        bio_context = bridge.analyze_user_state(description)
        ui_guidelines = bridge.get_response_guidelines()

        return jsonify(
            {
                "cognitive_load": bio_context.cognitive_load,
                "emotional_state": bio_context.emotional_state,
                "body_comfort": bio_context.body_comfort,
                "environmental_fit": bio_context.environmental_fit,
                "timestamp": bio_context.timestamp.isoformat(),
                "ui_guidelines": ui_guidelines,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/sessions", methods=["GET"])
def list_sessions():
    """
    List all conversation sessions.

    Response:
    {
        "sessions": [
            {
                "session_id": "abc123",
                "title": "Python Discussion",
                "created_at": "2024-01-15T14:32:00",
                "updated_at": "2024-01-15T14:35:00",
                "message_count": 5
            }
        ]
    }
    """
    try:
        from memory.conversation_memory import get_conversation_memory

        memory = get_conversation_memory()
        sessions = memory.get_all_sessions()

        return jsonify(
            {
                "sessions": [
                    {
                        "session_id": s.session_id,
                        "title": s.title,
                        "created_at": s.created_at,
                        "updated_at": s.updated_at,
                        "message_count": len(s.messages),
                        "biological_state_summary": s.biological_state_summary,
                    }
                    for s in sessions
                ]
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/sessions", methods=["POST"])
def create_session():
    """
    Create new conversation session.

    Request: {"title": "Optional Title"}
    Response: {"session_id": "abc123", "title": "...", "created_at": "..."}
    """
    try:
        from memory.conversation_memory import get_conversation_memory

        data = request.get_json() or {}
        title = data.get("title")

        memory = get_conversation_memory()
        session = memory.create_session(title=title)

        return jsonify(
            {
                "session_id": session.session_id,
                "title": session.title,
                "created_at": session.created_at,
                "status": "created",
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/sessions/<session_id>", methods=["GET"])
def get_session(session_id):
    """
    Get conversation session details.

    Response:
    {
        "session_id": "abc123",
        "title": "Python Discussion",
        "messages": [...],
        "biological_state_summary": {...}
    }
    """
    try:
        from memory.conversation_memory import get_conversation_memory

        memory = get_conversation_memory()
        session = memory.get_session(session_id)

        if not session:
            return jsonify({"error": "Session not found"}), 404

        return jsonify(
            {
                "session_id": session.session_id,
                "title": session.title,
                "created_at": session.created_at,
                "updated_at": session.updated_at,
                "messages": [m.to_dict() for m in session.messages],
                "biological_state_summary": session.biological_state_summary,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/sessions/<session_id>", methods=["DELETE"])
def delete_session(session_id):
    """Delete conversation session."""
    try:
        from memory.conversation_memory import get_conversation_memory

        memory = get_conversation_memory()
        success = memory.delete_session(session_id)

        if not success:
            return jsonify({"error": "Session not found"}), 404

        return jsonify({"status": "deleted", "session_id": session_id})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================


def _init_amos_background():
    """Initialize AMOS in background thread."""
    global amos_system
    try:
        from amos_unified_enhanced import AMOSUnifiedEnhanced

        amos_system = AMOSUnifiedEnhanced()
        amos_system.initialize(auto_load_knowledge=True)
        print("\n✅ AMOS background initialization complete!")
    except Exception as e:
        print(f"\n⚠️  AMOS background initialization failed: {e}")


def main():
    """Start the API server."""
    print("=" * 70)
    print("🚀 AMOS API Server Enhanced")
    print("=" * 70)

    # Start AMOS initialization in background so server starts immediately
    import threading

    # Register RAG routes
    register_rag_routes(app)

    init_thread = threading.Thread(target=_init_amos_background, daemon=True)
    init_thread.start()
    print("\n⏳ AMOS initializing in background...")
    print("   Server will start immediately.")

    print("\n📡 API Endpoints:")
    print("   GET  /                    - API info")
    print("   GET  /status              - System status")
    print("   GET  /health              - Health check")
    print("   POST /think               - Brain thinking")
    print("   POST /query               - Knowledge query")
    print("   GET  /subsystems          - List subsystems")
    print("   GET  /countries           - List countries")
    print("   GET  /sectors             - List sectors")
    print("\n🗄️  RAG Endpoints (Document Knowledge):")
    print("   POST /rag/documents       - Upload document")
    print("   GET  /rag/documents       - List documents")
    print("   DELETE /rag/documents/:id - Delete document")
    print("   POST /rag/retrieve        - Semantic search")
    print("   POST /rag/chat            - RAG-augmented chat")

    print("\n🌐 Server starting on http://localhost:5000")
    print("   Press Ctrl+C to stop")
    print("=" * 70)

    app.run(host="0.0.0.0", port=5000, debug=False)


if __name__ == "__main__":
    main()
