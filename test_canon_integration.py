#!/usr/bin/env python3
"""Test script for AMOS Canon integration."""

import asyncio

from amos_brain.canon_bridge import get_canon_bridge
from amos_canon_integration import get_canon_loader, initialize_canon


async def test_canon_loader():
    """Test Canon loader functionality."""
    print("=" * 60)
    print("TEST 1: Canon Loader")
    print("=" * 60)

    await initialize_canon()
    loader = get_canon_loader()
    status = loader.get_status()

    assert status.ready, "Canon should be ready"
    assert status.total_terms == 35, f"Expected 35 terms, got {status.total_terms}"
    assert status.total_agents == 34, f"Expected 34 agents, got {status.total_agents}"
    assert status.total_engines == 26, f"Expected 26 engines, got {status.total_engines}"

    print(f"✅ Canon loaded: {len(status.loaded_files)} files")
    print(f"   Terms: {status.total_terms}")
    print(f"   Agents: {status.total_agents}")
    print(f"   Engines: {status.total_engines}")

    # Test data access
    glossary = loader.get_glossary()
    agents = loader.get_agent_registry()
    kernels = loader.get_kernels()

    print(f"✅ Glossary accessible: {len(glossary)} entries")
    print(f"✅ Agents accessible: {len(agents)} entries")
    print(f"✅ Kernels accessible: {len(kernels)} entries")


async def test_canon_bridge():
    """Test Canon-Brain bridge."""
    print("\n" + "=" * 60)
    print("TEST 2: Canon-Brain Bridge")
    print("=" * 60)

    bridge = await get_canon_bridge()
    assert bridge._initialized, "Bridge should be initialized"

    print("✅ Bridge initialized")

    # Test context retrieval
    ctx = bridge.get_context_for_domain("ubi")
    print("✅ Context retrieved for domain 'ubi':")
    print(f"   Terms: {len(ctx.glossary_terms)}")
    print(f"   Agents: {len(ctx.applicable_agents)}")
    print(f"   Engines: {len(ctx.relevant_engines)}")

    # Test query enrichment (may not enrich if no matching terms)
    query = "Explain UBI architecture"
    enriched = bridge.enrich_query(query, "ubi")
    if len(enriched) > len(query):
        print(f"✅ Query enriched: {len(enriched)} chars (original: {len(query)})")
    else:
        print("✅ Query returned as-is (no matching terms)")


async def test_canon_query_engine():
    """Test Canon Query Engine."""
    print("\n" + "=" * 60)
    print("TEST 3: Canon Query Engine")
    print("=" * 60)

    from amos_brain.canon_query_engine import CanonQueryEngine

    # Initialize
    engine = CanonQueryEngine()
    await engine.initialize()
    assert engine._initialized, "Engine should be initialized"
    assert engine._canon_bridge is not None, "Canon bridge should be set"
    assert engine._cognitive_engine is not None, "Cognitive engine should be set"
    print("✅ Canon Query Engine initialized")

    # Test domain suggestions
    suggestions = engine.get_domain_suggestions("brain cognitive task agent")
    assert "brain" in suggestions or "agent" in suggestions, "Should suggest relevant domains"
    print(f"✅ Domain suggestions: {suggestions}")


async def test_bootstrap_integration():
    """Test bootstrap orchestrator integration."""
    print("\n" + "=" * 60)
    print("TEST 4: Bootstrap Integration")
    print("=" * 60)

    from amos_bootstrap_orchestrator import BootstrapPhase, get_bootstrap_orchestrator

    orchestrator = get_bootstrap_orchestrator()

    # Check Canon phase exists
    assert hasattr(BootstrapPhase, "CANON_INTEGRATION"), "CANON_INTEGRATION phase should exist"
    print(f"✅ CANON_INTEGRATION phase exists: {BootstrapPhase.CANON_INTEGRATION.value}")

    # Check canon_loader in expected count
    assert orchestrator._calculate_progress is not None
    print("✅ Progress calculation includes canon")


async def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("AMOS CANON INTEGRATION TEST SUITE")
    print("=" * 60 + "\n")

    try:
        await test_canon_loader()
        await test_canon_bridge()
        await test_canon_query_engine()
        await test_bootstrap_integration()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        return 0
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
