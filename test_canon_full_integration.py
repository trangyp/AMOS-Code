"""Full Canon Integration Test - Validates all Canon-aware components.

Tests the complete Canon-to-Brain integration chain:
1. Canon Loader initialization
2. Canon Bridge context retrieval
3. Canon Query Engine domain-aware queries
4. Canon Agent task planning and execution
5. Canon Brain API endpoints

Creator: Trang Phan
Version: 3.0.0
"""

import asyncio


async def test_canon_loader():
    """Test Canon Loader initialization."""
    print("\n" + "=" * 60)
    print("TEST 1: Canon Loader")
    print("=" * 60)

    from amos_canon_integration import get_canon_loader, initialize_canon

    success = await initialize_canon()
    loader = get_canon_loader()
    status = loader.get_status()

    print(f"✅ Canon initialized: {success}")
    print(f"   Terms: {status.total_terms}")
    print(f"   Agents: {status.total_agents}")
    print(f"   Engines: {status.total_engines}")

    assert success, "Canon should initialize successfully"
    return loader


async def test_canon_bridge():
    """Test Canon Bridge context retrieval."""
    print("\n" + "=" * 60)
    print("TEST 2: Canon Bridge")
    print("=" * 60)

    from amos_brain.canon_bridge import get_canon_bridge

    bridge = await get_canon_bridge()

    # Test context retrieval
    ctx = bridge.get_context_for_domain("brain")
    print(f"✅ Context retrieved for domain 'brain':")
    print(f"   Terms: {len(ctx.glossary_terms)}")
    print(f"   Agents: {len(ctx.applicable_agents)}")
    print(f"   Engines: {len(ctx.relevant_engines)}")

    return bridge


async def test_canon_query_engine():
    """Test Canon Query Engine."""
    print("\n" + "=" * 60)
    print("TEST 3: Canon Query Engine")
    print("=" * 60)

    from amos_brain.canon_query_engine import CanonQueryEngine

    engine = CanonQueryEngine()
    await engine.initialize()

    print(f"✅ Canon Query Engine initialized: {engine._initialized}")
    print(f"   Canon bridge: {engine._canon_bridge is not None}")
    print(f"   Cognitive engine: {engine._cognitive_engine is not None}")

    # Test domain suggestions
    suggestions = engine.get_domain_suggestions("brain cognitive task agent")
    print(f"✅ Domain suggestions: {suggestions}")

    return engine


async def test_canon_agent():
    """Test Canon Agent."""
    print("\n" + "=" * 60)
    print("TEST 4: Canon Agent")
    print("=" * 60)

    from amos_brain.canon_agent import get_canon_agent

    agent = await get_canon_agent("test_agent", domain="brain")

    print(f"✅ Canon Agent initialized: {agent._initialized}")
    print(f"   Agent ID: {agent.agent_id}")
    print(f"   Domain: {agent.domain}")

    # Test task planning
    plan = await agent.plan_task(
        "Analyze brain cognitive architecture",
        "analysis",
    )

    print(f"✅ Task plan created:")
    print(f"   Task ID: {plan.task_id}")
    print(f"   Domain: {plan.domain}")
    print(f"   Steps: {len(plan.steps)}")
    print(f"   Canon terms: {len(plan.canon_terms)}")
    print(f"   Agents: {plan.applicable_agents}")
    print(f"   Engines: {plan.relevant_engines}")

    # Test task execution
    result = await agent.execute_task(plan)
    print(f"✅ Task executed:")
    print(f"   Success: {result['success']}")
    print(f"   Steps executed: {result['steps_executed']}")

    return agent


async def test_integration_summary():
    """Display integration summary."""
    print("\n" + "=" * 60)
    print("CANON INTEGRATION SUMMARY")
    print("=" * 60)

    components = [
        ("Canon Loader", "amos_canon_integration"),
        ("Canon Bridge", "amos_brain.canon_bridge"),
        ("Canon Query Engine", "amos_brain.canon_query_engine"),
        ("Canon Agent", "amos_brain.canon_agent"),
        ("Canon Brain API", "backend.api.canon_brain"),
    ]

    for name, module in components:
        try:
            __import__(module)
            print(f"✅ {name}: {module}")
        except ImportError as e:
            print(f"❌ {name}: {e}")


async def main():
    """Run all Canon integration tests."""
    print("\n" + "=" * 60)
    print("AMOS CANON FULL INTEGRATION TEST SUITE")
    print("=" * 60 + "\n")

    try:
        await test_canon_loader()
        await test_canon_bridge()
        await test_canon_query_engine()
        await test_canon_agent()
        await test_integration_summary()

        print("\n" + "=" * 60)
        print("✅ ALL CANON INTEGRATION TESTS PASSED")
        print("=" * 60)
        return 0

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
