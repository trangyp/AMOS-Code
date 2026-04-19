"""Test Canon components via brain's public API.

Validates all Canon components are accessible through amos_brain.

Creator: Trang Phan
Version: 3.0.0
"""


def test_public_api_imports():
    """Test all Canon functions are importable from amos_brain."""
    print("\n" + "="*60)
    print("TEST: Canon Public API Imports")
    print("="*60)

    from amos_brain import (
        get_canon_knowledge_engine,
        get_canon_cognitive_processor,
        canon_process,
        get_canon_reasoning_engine,
        canon_reason,
        get_canon_learning_engine,
        canon_learn,
        get_canon_memory_system,
        canon_store,
        canon_search,
        get_canon_orchestrator,
        canon_orchestrate,
    )

    print("✅ All Canon functions imported successfully")
    print("  - get_canon_knowledge_engine")
    print("  - get_canon_cognitive_processor")
    print("  - canon_process")
    print("  - get_canon_reasoning_engine")
    print("  - canon_reason")
    print("  - get_canon_learning_engine")
    print("  - canon_learn")
    print("  - get_canon_memory_system")
    print("  - canon_store")
    print("  - canon_search")
    print("  - get_canon_orchestrator")
    print("  - canon_orchestrate")


def test_public_api_execution():
    """Test Canon functions work via public API."""
    print("\n" + "="*60)
    print("TEST: Canon Public API Execution")
    print("="*60)

    from amos_brain import (
        get_canon_knowledge_engine,
        canon_process,
        canon_reason,
        canon_learn,
        canon_store,
        canon_search,
        canon_orchestrate,
    )

    # Test knowledge engine
    engine = get_canon_knowledge_engine()
    stats = engine.get_stats()
    print(f"✅ Knowledge Engine: {stats['total_entries']} entries")

    # Test cognitive processing
    cog_result = canon_process("Brain architecture design", "cognitive")
    print(f"✅ Cognitive Processor: {cog_result.confidence:.0%} confidence")

    # Test reasoning
    reason_result = canon_reason("Best approach?", "domains", ["A", "B"])
    print(f"✅ Reasoning Engine: {reason_result.confidence:.0%} confidence")

    # Test learning
    learn_result = canon_learn("Task", "domain", "Outcome", True)
    print(f"✅ Learning Engine: {len(learn_result.learned_patterns)} patterns")

    # Test memory
    mem = canon_store("Test memory", "test")
    print(f"✅ Memory System: Stored {mem.memory_id}")

    results = canon_search("test")
    print(f"✅ Memory Search: Found {len(results)} memories")

    # Test orchestrator
    orch_result = canon_orchestrate("Test task", "test")
    print(f"✅ Orchestrator: {orch_result.success} (processed in {orch_result.processing_time_ms:.1f}ms)")


def main():
    """Run all Canon public API tests."""
    print("\n" + "="*60)
    print("AMOS CANON PUBLIC API - FULL TEST")
    print("="*60)

    try:
        test_public_api_imports()
        test_public_api_execution()

        print("\n" + "="*60)
        print("✅ ALL CANON PUBLIC API TESTS PASSED")
        print("="*60)
        print("\nAll Canon components accessible via amos_brain:")
        print("  from amos_brain import canon_orchestrate, canon_process, ...")
        return 0

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
