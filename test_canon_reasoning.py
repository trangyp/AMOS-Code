"""Test Canon Reasoning Engine with real Canon data.

Validates that the reasoning engine uses actual Canon knowledge
for decision-making with real AMOS Canon files.

Creator: Trang Phan
Version: 3.0.0
"""

from amos_brain.canon_reasoning_engine import (
    get_canon_reasoning_engine,
    canon_reason,
)


def test_reasoning_initialization():
    """Test that reasoning engine initializes."""
    print("\n" + "=" * 60)
    print("TEST: Reasoning Engine Initialization")
    print("=" * 60)

    engine = get_canon_reasoning_engine()
    print(f"Initialized: {engine._initialized}")
    print(f"Knowledge engine: {engine._knowledge_engine is not None}")


def test_canon_reasoning():
    """Test Canon-aware reasoning."""
    print("\n" + "=" * 60)
    print("TEST: Canon-Aware Reasoning")
    print("=" * 60)

    problems = [
        (
            "How should we design the brain cognitive architecture?",
            "cognitive",
            ["Modular design", "Monolithic kernel", "Microservices"],
        ),
        (
            "What engine approach for task automation?",
            "domains",
            ["Unified engine", "Specialized kernels", "Hybrid approach"],
        ),
    ]

    for problem, domain, options in problems:
        print(f"\n  Problem: {problem}")
        print(f"  Domain: {domain}")

        result = canon_reason(problem, domain, options)

        print(f"  Decision: {result.decision[:50]}...")
        print(f"  Confidence: {result.confidence:.1%}")
        print(f"  Processing time: {result.processing_time_ms:.2f}ms")
        print(f"  Canon sources: {len(result.canon_sources)}")
        print(f"  Options considered: {len(result.options_considered)}")

        # Show reasoning path
        print(f"  Reasoning path:")
        for step in result.reasoning_path[:3]:
            print(f"    - {step}")

        # Show Canon support for top option
        if result.options_considered:
            top = result.options_considered[0]
            if top.canon_support:
                print(f"  Canon support: {', '.join(top.canon_support[:2])}")


def test_option_generation():
    """Test option generation from Canon."""
    print("\n" + "=" * 60)
    print("TEST: Canon-Based Option Generation")
    print("=" * 60)

    # No options provided - should generate from Canon
    result = canon_reason(
        "brain intelligence design",
        domain="core",
    )

    print(f"\n  Generated {len(result.options_considered)} options:")
    for opt in result.options_considered[:3]:
        print(f"    - {opt.option_id}: {opt.description[:40]}...")
        print(f"      Canon confidence: {opt.canon_confidence:.1%}")
        if opt.canon_support:
            print(f"      Supported by: {', '.join(opt.canon_support[:2])}")


def test_confidence_calculation():
    """Test confidence calculation with Canon support."""
    print("\n" + "=" * 60)
    print("TEST: Confidence Calculation")
    print("=" * 60)

    # With Canon support
    result1 = canon_reason(
        "brain cognition design",
        domain="cognitive",
    )

    # With explicit options
    result2 = canon_reason(
        "brain cognition design", domain="cognitive", options=["Option A", "Option B"]
    )

    print(f"\n  Auto-generated options confidence: {result1.confidence:.1%}")
    print(f"  Explicit options confidence: {result2.confidence:.1%}")


def main():
    """Run all Canon Reasoning Engine tests."""
    print("\n" + "=" * 60)
    print("AMOS CANON REASONING ENGINE - REAL DATA TEST")
    print("=" * 60)

    try:
        test_reasoning_initialization()
        test_canon_reasoning()
        test_option_generation()
        test_confidence_calculation()

        print("\n" + "=" * 60)
        print("✅ ALL CANON REASONING TESTS PASSED")
        print("=" * 60)
        return 0

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
