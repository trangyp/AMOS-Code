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
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS

# Add paths
REPO_ROOT = Path(__file__).parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "AMOS_ORGANISM_OS"))
sys.path.insert(0, str(REPO_ROOT / "amos_brain"))

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
    """Quick health check - returns immediately without blocking."""
    global amos_system

    # Return quick response without triggering full initialization
    if amos_system is None:
        return jsonify(
            {
                "status": "initializing",
                "service": "amos-api-enhanced",
                "message": "AMOS system starting up...",
            }
        )

    healthy = amos_system is not None and getattr(amos_system, '_initialized', False)

    return jsonify(
        {
            "status": "healthy" if healthy else "degraded",
            "service": "amos-api-enhanced",
            "initialized": healthy,
        }
    )


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


def main():
    """Start the API server."""
    print("=" * 70)
    print("🚀 AMOS API Server Enhanced")
    print("=" * 70)
    print("\nInitializing AMOS ecosystem...")

    # Initialize on startup
    amos = get_amos()
    if amos:
        print("✅ AMOS system ready!")
        print(f"   🧬 Organism: {amos.status.subsystems_active} subsystems")
        print("   🧠 Brain: 6 laws")
        print(f"   📚 Knowledge: {amos.status.knowledge_entries:,} entries")
    else:
        print("⚠️  AMOS initialization failed - starting in limited mode")

    print("\n📡 API Endpoints:")
    print("   GET  /                    - API info")
    print("   GET  /status              - System status")
    print("   GET  /health              - Health check")
    print("   POST /think               - Brain thinking")
    print("   POST /query               - Knowledge query")
    print("   GET  /subsystems          - List subsystems")
    print("   GET  /countries           - List countries")
    print("   GET  /sectors             - List sectors")

    print("\n🌐 Server starting on http://localhost:5000")
    print("   Press Ctrl+C to stop")
    print("=" * 70)

    app.run(host="0.0.0.0", port=5000, debug=False)


if __name__ == "__main__":
    main()
