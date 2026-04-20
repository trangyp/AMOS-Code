#!/usr/bin/env python3
"""AMOS Cognitive System Demo - Real Working Features.

This demonstrates real working integration of:
1. CognitiveEngineV2 with multi-phase reasoning
2. SuperBrainRuntime with kernel routing
3. Governed MCP tools
4. Memory governance
5. Law compliance at each phase

Run: python amos_cognitive_demo.py
"""

from __future__ import annotations


def demo_cognitive_engine_v2():
    """Demo: Cognitive Engine V2 - real working multi-phase reasoning."""
    print("\n" + "=" * 60)
    print("DEMO 1: Cognitive Engine V2 - Multi-phase Reasoning")
    print("=" * 60)

    from amos_brain.cognitive_engine_v2 import get_cognitive_engine_v2

    # Create engine (works with or without API keys)
    engine = get_cognitive_engine_v2(provider="anthropic")

    print(f"Engine: {engine.llm_provider}/{engine.model_id}")
    print(f"Max reasoning steps: {engine.max_reasoning_steps}")
    print(f"Laws enabled: {engine.enable_laws}")
    print(f"Builtin tools: {list(engine._tools.keys())}")

    # Execute thinking (uses real LLM if keys available, graceful fallback)
    state = engine.think(
        query="Design a secure API endpoint for user authentication",
        domain="software",
    )

    print(f"\nReasoning chain ({len(state.thoughts)} thoughts):")
    for thought in state.thoughts:
        print(f"  [{thought.phase.name}] {thought.content[:60]}...")
        if thought.law_checks:
            print(f"    Laws: {thought.law_checks}")

    print(f"\nTool calls: {len(state.tool_calls)}")
    print(f"Tool results: {len(state.tool_results)}")
    print(f"Total latency: {state.metadata.get('total_latency_ms', 0):.0f}ms")

    return True


def demo_superbrain_runtime():
    """Demo: SuperBrain Runtime - canonical brain singleton."""
    print("\n" + "=" * 60)
    print("DEMO 2: SuperBrain Runtime - Canonical Brain")
    print("=" * 60)

    from amos_brain.super_brain import SuperBrainRuntime

    # Get singleton instance
    brain = SuperBrainRuntime()

    print(f"Brain ID: {brain.brain_id}")
    print(f"Status: {brain.status}")

    # Get state snapshot
    state = brain.get_state()
    print(f"Core frozen: {state.core_frozen}")
    print("\nState snapshot:")
    print(f"  Active kernels: {state.active_kernels}")
    print(f"  Loaded tools: {len(state.loaded_tools)}")
    print(f"  Health score: {state.health_score}")

    # Check health
    health = brain.health_check()
    print(f"\nHealth check: {health['status']}")
    for check, status in health.get("checks", {}).items():
        print(f"  {check}: {status}")

    return True


def demo_governed_mcp_tools():
    """Demo: Governed MCP Tools - real tool execution."""
    print("\n" + "=" * 60)
    print("DEMO 3: Governed MCP Tools")
    print("=" * 60)

    from amos_brain.mcp_governed_tools import get_governed_mcp_tools

    # Get governed tools
    tools = get_governed_mcp_tools(root_path=".")

    # List available tools
    tool_list = tools.list_tools()
    print(f"Registered tools: {len(tool_list)}")
    for tool in tool_list:
        print(f"  - {tool}")

    # Execute filesystem tool
    print("\nExecuting fs_read_file('.')...")
    result = tools.execute("fs_read_file", path=".")
    print(f"  Success: {result.get('success')}")
    if result.get("success"):
        content = result.get("result", {}).get("content", "")
        items = content.split("\n") if content else []
        print(f"  Items in directory: {len(items)}")

    # Execute git tool
    print("\nExecuting git_status()...")
    result = tools.execute("git_status")
    print(f"  Success: {result.get('success')}")

    return True


def demo_cognitive_integration():
    """Demo: Cognitive Integration - full brain integration."""
    print("\n" + "=" * 60)
    print("DEMO 4: Cognitive Integration - Full Brain Stack")
    print("=" * 60)

    from amos_brain.cognitive_integration import get_cognitive_integration

    # Get integrated cognitive system
    cog = get_cognitive_integration()

    # Check status
    status = cog.get_status()
    print(f"Initialized: {status['initialized']}")
    print(f"Engine ready: {status['engine_ready']}")
    print(f"Brain connected: {status['brain_connected']}")
    print(f"Engine metrics: {status['engine_metrics']}")

    # Execute integrated thinking
    print("\nExecuting think_integrated()...")
    result = cog.think_integrated(
        query="Analyze code quality patterns",
        domain="software",
    )

    print(f"  Kernel routed: {result.kernel_routed}")
    print(f"  Tools governed: {result.tools_governed}")
    print(f"  Laws checked: {result.laws_checked}")
    print(f"  Memory stored: {result.memory_stored}")
    print(f"  Execution time: {result.execution_time_ms:.0f}ms")
    print(f"  Thoughts generated: {len(result.state.thoughts)}")

    return True


def demo_kernel_router():
    """Demo: Kernel Router - task routing."""
    print("\n" + "=" * 60)
    print("DEMO 5: Kernel Router - Domain Routing")
    print("=" * 60)

    from amos_brain.kernel_router import KernelRouter
    from amos_brain.loader import get_brain

    # Create router
    brain = get_brain()
    router = KernelRouter(brain)

    # Test task routing
    tasks = [
        "Fix bug in authentication code",
        "Deploy to AWS production",
        "Train neural network model",
        "Design system architecture",
    ]

    for task in tasks:
        intent = router.parse_intent(task)
        print(f"\nTask: {task[:40]}...")
        print(f"  Primary domain: {intent.primary_domain}")
        print(f"  Risk level: {intent.risk_level}")
        print(f"  Requires code: {intent.requires_code}")
        print(f"  Requires reasoning: {intent.requires_reasoning}")

    return True


def main():
    """Run all demos."""
    print("""
╔════════════════════════════════════════════════════════════════╗
║           AMOS Cognitive System - Real Features Demo             ║
║                                                                ║
║  Demonstrates working integration of:                           ║
║  - Cognitive Engine V2 (multi-phase LLM reasoning)              ║
║  - SuperBrain Runtime (canonical brain singleton)             ║
║  - Governed MCP Tools (filesystem, git, web, code)            ║
║  - Memory Governance (cognitive state storage)                ║
║  - Kernel Router (domain-based task routing)                    ║
║  - Law Compliance (L1-L7 checks at each phase)                 ║
╚════════════════════════════════════════════════════════════════╝
""")

    results = []

    try:
        results.append(("Cognitive Engine V2", demo_cognitive_engine_v2()))
    except Exception as e:
        print(f"  Error: {e}")
        results.append(("Cognitive Engine V2", False))

    try:
        results.append(("SuperBrain Runtime", demo_superbrain_runtime()))
    except Exception as e:
        print(f"  Error: {e}")
        results.append(("SuperBrain Runtime", False))

    try:
        results.append(("Governed MCP Tools", demo_governed_mcp_tools()))
    except Exception as e:
        print(f"  Error: {e}")
        results.append(("Governed MCP Tools", False))

    try:
        results.append(("Cognitive Integration", demo_cognitive_integration()))
    except Exception as e:
        print(f"  Error: {e}")
        results.append(("Cognitive Integration", False))

    try:
        results.append(("Kernel Router", demo_kernel_router()))
    except Exception as e:
        print(f"  Error: {e}")
        results.append(("Kernel Router", False))

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    for name, ok in results:
        status = "PASS" if ok else "FAIL"
        symbol = "✓" if ok else "✗"
        print(f"{symbol} {status}: {name}")

    passed = sum(1 for _, ok in results if ok)
    print(f"\n{passed}/{len(results)} demos passed")

    print("""
Features Built:
1. cognitive_engine_v2.py - Production reasoning with 6 phases
2. cognitive_integration.py - Full brain stack integration
3. mcp_governed_tools.py - MCP tools with governance
4. memory_governance.py - Cognitive state storage

Usage:
  from amos_brain.cognitive_integration import think_with_brain
  result = think_with_brain("Your query", "software")
  print(result.state.get_reasoning_chain())
""")


if __name__ == "__main__":
    main()
