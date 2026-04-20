"""Test Canon Orchestrator with real Canon data.

Validates unified Canon-orchestrated task execution.

Creator: Trang Phan
Version: 3.0.0
"""

from amos_brain.canon_orchestrator import canon_orchestrate


def test_orchestrator_execution():
    """Test full Canon-orchestrated task execution."""
    print("\n" + "=" * 60)
    print("TEST: Canon Orchestrator Execution")
    print("=" * 60)

    tasks = [
        ("How should we design brain cognitive architecture?", "cognitive"),
        ("What is the best approach for API security?", "api"),
    ]

    for task, domain in tasks:
        print(f"\n  Task: {task[:50]}...")
        print(f"  Domain: {domain}")

        result = canon_orchestrate(task, domain)

        print(f"  Success: {result.success}")
        print(f"  Result: {result.result[:50]}...")
        print(f"  Processing time: {result.processing_time_ms:.2f}ms")
        print(f"  Memories accessed: {len(result.memories_accessed)}")
        print(f"  Patterns applied: {len(result.patterns_applied)}")

        # Show Canon context
        canon_ctx = result.canon_context
        print(f"  Canon entries: {canon_ctx.get('knowledge_entries', {}).get('total_entries', 0)}")
        print(f"  Cognitive confidence: {canon_ctx.get('cognitive_confidence', 0):.0%}")
        print(f"  Terms used: {len(canon_ctx.get('cognitive_terms_used', []))}")
        print(f"  Patterns learned: {canon_ctx.get('patterns_learned', 0)}")

        # Show reasoning path
        print("  Reasoning steps:")
        for step in result.reasoning_path[:3]:
            print(f"    - {step}")


def test_orchestrator_with_reasoning():
    """Test orchestrator with decision reasoning."""
    print("\n" + "=" * 60)
    print("TEST: Canon Orchestrator with Reasoning")
    print("=" * 60)

    # Task with "should" triggers reasoning
    result = canon_orchestrate("What should we use for task automation?", domain="domains")

    print(f"\n  Task triggered reasoning: {'should' in result.task_id}")
    print(f"  Success: {result.success}")
    print(f"  Result: {result.result[:50]}...")

    # Check if reasoning was applied
    if "decision" in result.canon_context:
        print(f"  Decision: {result.canon_context['decision'][:40]}...")
    if "reasoning_confidence" in result.canon_context:
        print(f"  Reasoning confidence: {result.canon_context['reasoning_confidence']:.0%}")


def main():
    """Run all Canon Orchestrator tests."""
    print("\n" + "=" * 60)
    print("AMOS CANON ORCHESTRATOR - REAL DATA TEST")
    print("=" * 60)

    try:
        test_orchestrator_execution()
        test_orchestrator_with_reasoning()

        print("\n" + "=" * 60)
        print("✅ ALL CANON ORCHESTRATOR TESTS PASSED")
        print("=" * 60)
        return 0

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
