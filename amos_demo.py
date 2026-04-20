#!/usr/bin/env python3
"""AMOS Brain Demo - Shows real working features.

This demonstrates actual implemented capabilities:
1. Cognitive Engine V2 with LLM integration
2. MCP Tools (filesystem, git, web)
3. Brain Server (FastAPI with session management)
4. Law-governed reasoning
"""


def demo_cognitive_engine():
    """Demo: Cognitive Engine V2"""
    print("\n" + "=" * 60)
    print("DEMO 1: Cognitive Engine V2")
    print("=" * 60)

    try:
        from amos_brain.cognitive_engine_v2 import get_cognitive_engine_v2

        # Create engine (works even without API keys)
        engine = get_cognitive_engine_v2(provider="anthropic")
        print(f"✓ Engine created: {engine.llm_provider}/{engine.model_id}")
        print(f"  - Max reasoning steps: {engine.max_reasoning_steps}")
        print(f"  - Laws enabled: {engine.enable_laws}")
        print(f"  - Tools registered: {len(engine._tools)}")

        # Show tool registry
        for name in engine._tools:
            print(f"    - {name}")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def demo_mcp_tools():
    """Demo: MCP Tools Bridge"""
    print("\n" + "=" * 60)
    print("DEMO 2: MCP Tools Bridge")
    print("=" * 60)

    try:
        from amos_brain.mcp_tools_bridge import MCPToolsBridge

        bridge = MCPToolsBridge(root_path=".")
        print("✓ MCP Tools Bridge created")

        # Test filesystem
        result = bridge.fs_read_file(".")
        if result.get("success"):
            content = result.get("result", {}).get("content", "")
            lines = content.split("\n") if content else []
            print(f"✓ fs_read_file('.') - {len(lines)} items in directory")

        # Test git
        result = bridge.git_status()
        print(f"✓ git_status() - success={result.get('success')}")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def demo_laws():
    """Demo: AMOS Laws"""
    print("\n" + "=" * 60)
    print("DEMO 3: AMOS Laws")
    print("=" * 60)

    try:
        from amos_brain.laws import GlobalLaws

        laws = GlobalLaws()
        print("✓ Global Laws initialized")

        # Test L4
        consistent, issues = laws.check_l4_integrity(["Sky is blue", "Water is wet"])
        print(f"✓ L4 Structural Integrity: consistent={consistent}")

        # Test L5
        ok, violations = laws.l5_communication_check("Normal sentence here.")
        print(f"✓ L5 Communication: ok={ok}")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def demo_server():
    """Demo: Brain Server"""
    print("\n" + "=" * 60)
    print("DEMO 4: Brain Server (FastAPI)")
    print("=" * 60)

    try:
        from amos_brain_server import app, brain_server

        routes = [r.path for r in app.routes if hasattr(r, "path")]
        print(f"✓ FastAPI app with {len(routes)} routes:")
        for route in routes[:6]:
            print(f"    {route}")

        # Create session
        session = brain_server.create_session()
        print(f"✓ Session created: {session.session_id}")

        # Check metrics
        metrics = brain_server.get_metrics()
        print(f"✓ Metrics: active_sessions={metrics.get('active_sessions')}")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    """Run all demos."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║           AMOS Brain - Real Features Demo                    ║
║                                                              ║
║  Demonstrates working cognitive, tools, laws, and server     ║
╚══════════════════════════════════════════════════════════════╝
""")

    results = []
    results.append(("Cognitive Engine V2", demo_cognitive_engine()))
    results.append(("MCP Tools Bridge", demo_mcp_tools()))
    results.append(("AMOS Laws", demo_laws()))
    results.append(("Brain Server", demo_server()))

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    for name, ok in results:
        status = "✓ PASS" if ok else "✗ FAIL"
        print(f"{status}: {name}")

    print("""
Features built:
1. cognitive_engine_v2.py - Production-grade reasoning with LLMs
2. amos_brain_server.py - FastAPI server with session management
3. MCP tools integration (filesystem, git, web)
4. AMOS law governance (L1-L7)

Usage:
  # Start server
  python amos_brain_server.py

  # Use cognitive engine
  from amos_brain.cognitive_engine_v2 import get_cognitive_engine_v2
  engine = get_cognitive_engine_v2()
  result = engine.think("Your query")
""")


if __name__ == "__main__":
    main()
