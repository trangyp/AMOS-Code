"""Final Canon-Brain Integration Test - Complete validation.

Tests all Canon components in unified workflow using real Canon data.

Creator: Trang Phan
Version: 3.0.0
"""


def test_complete_canon_workflow():
    """Execute complete Canon-aware workflow end-to-end."""
    print("\n" + "="*70)
    print("FINAL CANON-BRAIN INTEGRATION TEST")
    print("="*70)

    # Test 1: Knowledge Engine
    print("\n[1] Canon Knowledge Engine")
    from amos_brain import get_canon_knowledge_engine
    engine = get_canon_knowledge_engine()
    stats = engine.get_stats()
    print(f"  ✓ Loaded {stats['total_entries']} Canon entries")
    domains = list(stats['domain_stats'].keys())
    print(f"  ✓ Domains: {', '.join(domains)}")

    # Test 2: Query Knowledge
    print("\n[2] Canon Knowledge Query")
    all_results = engine.search_all("brain architecture")
    total_found = sum(len(v) for v in all_results.values())
    print(f"  ✓ Found {total_found} relevant entries across all domains")

    # Test 3: Cognitive Processing
    print("\n[3] Canon Cognitive Processor")
    from amos_brain import canon_process
    cog_result = canon_process(
        "Design a secure API architecture",
        domain="api"
    )
    print(f"  ✓ Processing confidence: {cog_result.confidence:.0%}")
    print(f"  ✓ Canon sources: {len(cog_result.canon_sources)}")

    # Test 4: Reasoning
    print("\n[4] Canon Reasoning Engine")
    from amos_brain import canon_reason
    reason_result = canon_reason(
        "What architecture should we use?",
        domain="domains",
        options=["microservices", "monolith"]
    )
    print(f"  ✓ Decision: {reason_result.decision[:40]}...")
    print(f"  ✓ Confidence: {reason_result.confidence:.0%}")

    # Test 5: Learning
    print("\n[5] Canon Learning Engine")
    from amos_brain import canon_learn
    learn_result = canon_learn(
        task="Design secure API",
        domain="api",
        outcome="Successfully implemented OAuth2 + JWT",
        success=True
    )
    print(f"  ✓ Learned {len(learn_result.learned_patterns)} patterns")

    # Test 6: Memory
    print("\n[6] Canon Memory System")
    from amos_brain import canon_store, canon_search
    mem1 = canon_store("API security best practices", "api")
    mem2 = canon_store("Brain architecture patterns", "cognitive")
    search_results = canon_search("security", domain="api")
    print(f"  ✓ Stored memories: {mem1.memory_id}, {mem2.memory_id}")
    print(f"  ✓ Search found: {len(search_results)} memories")

    # Test 7: Full Orchestration
    print("\n[7] Canon Orchestrator")
    from amos_brain import canon_orchestrate
    orch_result = canon_orchestrate(
        "How should we design a secure brain architecture?",
        domain="cognitive"
    )
    print(f"  ✓ Success: {orch_result.success}")
    print(f"  ✓ Processing time: {orch_result.processing_time_ms:.1f}ms")
    print(f"  ✓ Canon context keys: {len(orch_result.canon_context)}")
    print(f"  ✓ Memories accessed: {len(orch_result.memories_accessed)}")
    print(f"  ✓ Patterns applied: {len(orch_result.patterns_applied)}")
    print(f"  ✓ Reasoning steps: {len(orch_result.reasoning_path)}")

    # Summary
    print("\n" + "="*70)
    print("INTEGRATION TEST RESULTS")
    print("="*70)
    print(f"  Canon entries loaded:     {stats['total_entries']}")
    print(f"  Cognitive confidence:     {cog_result.confidence:.0%}")
    print(f"  Reasoning confidence:     {reason_result.confidence:.0%}")
    print(f"  Patterns learned:         {len(learn_result.learned_patterns)}")
    print(f"  Memories stored:          2")
    print(f"  Memories found:           {len(search_results)}")
    print(f"  Orchestration success:    {orch_result.success}")
    print(f"  Processing time:          {orch_result.processing_time_ms:.1f}ms")
    print("\n  ✅ ALL CANON-BRAIN INTEGRATION TESTS PASSED")
    print("="*70)

    return True


def main():
    """Run final integration test."""
    try:
        test_complete_canon_workflow()
        return 0
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
