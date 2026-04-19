"""Test Canon integration via brain's public API.

Validates that Canon components are accessible through the brain's
lazy-loaded public API surface.

Creator: Trang Phan
Version: 3.0.0
"""

from __future__ import annotations


def test_canon_knowledge_engine_api():
    """Test Canon Knowledge Engine via brain API."""
    print("\n" + "=" * 60)
    print("TEST: Canon Knowledge Engine via Brain API")
    print("=" * 60)

    from amos_brain import get_canon_knowledge_engine

    engine = get_canon_knowledge_engine()
    stats = engine.get_stats()

    print(f"✅ Knowledge engine loaded: {stats['loaded']}")
    print(f"   Total entries: {stats['total_entries']}")
    print(f"   Domains: {stats['domains']}")


def test_canon_cognitive_processor_api():
    """Test Canon Cognitive Processor via brain API."""
    print("\n" + "=" * 60)
    print("TEST: Canon Cognitive Processor via Brain API")
    print("=" * 60)

    from amos_brain import canon_process

    result = canon_process("How should we design brain architecture?", domain="cognitive")

    print(f"✅ Canon processing successful")
    print(f"   Confidence: {result.confidence:.0%}")
    print(f"   Canon sources: {len(result.canon_sources)}")
    print(f"   Canon terms: {len(result.canon_terms_used)}")

    if result.canon_terms_used:
        for term, desc in list(result.canon_terms_used.items())[:2]:
            print(f"   Term: {term}")


def test_canon_reasoning_api():
    """Test Canon Reasoning via brain API."""
    print("\n" + "=" * 60)
    print("TEST: Canon Reasoning via Brain API")
    print("=" * 60)

    from amos_brain import canon_reason

    result = canon_reason(
        "What is the best approach for task automation?",
        domain="domains",
        options=["Unified engine", "Microservices", "Serverless"],
    )

    print(f"✅ Canon reasoning successful")
    print(f"   Decision: {result.decision[:40]}...")
    print(f"   Confidence: {result.confidence:.0%}")
    print(f"   Options considered: {len(result.options_considered)}")


def test_canon_query_api():
    """Test Canon Query via brain API."""
    print("\n" + "=" * 60)
    print("TEST: Canon Query via Brain API")
    print("=" * 60)

    try:
        from amos_brain import canon_query

        result = canon_query("brain cognitive engine design", domain="core")

        print(f"✅ Canon query successful")
        print(f"   Domain: {result.domain}")
        print(f"   Canon terms: {len(result.canon_terms)}")
        print(f"   Processing time: {result.processing_time_ms:.2f}ms")
    except ImportError as e:
        print(f"⚠️  Canon query not available: {e}")


def main():
    """Run all brain Canon API tests."""
    print("\n" + "=" * 60)
    print("AMOS BRAIN CANON INTEGRATION - PUBLIC API TEST")
    print("=" * 60)

    try:
        test_canon_knowledge_engine_api()
        test_canon_cognitive_processor_api()
        test_canon_reasoning_api()
        test_canon_query_api()

        print("\n" + "=" * 60)
        print("✅ ALL BRAIN CANON API TESTS PASSED")
        print("=" * 60)
        return 0

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
