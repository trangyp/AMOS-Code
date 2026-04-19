#!/usr/bin/env python3
"""Quick integration test for fast thinking system."""

import asyncio
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "clawspring"))
sys.path.insert(0, str(Path(__file__).parent / "clawspring" / "amos_brain"))


async def test_fast_thinking():
    """Test fast thinking engine directly."""
    from amos_fast_thinking import get_fast_thinking_engine

    engine = get_fast_thinking_engine()

    # Test 1: Simple greeting (should hit rule-based)
    result = await engine.think_fast("Hello", {})
    assert result.confidence > 0.8
    assert result.response is not None
    print(f"✓ Test 1 passed: Greeting (confidence: {result.confidence:.2f})")

    # Test 2: Status check (should hit rules)
    result = await engine.think_fast("What is the system status?", {})
    assert result.confidence > 0.5
    print(f"✓ Test 2 passed: Status check (confidence: {result.confidence:.2f})")

    # Test 3: Cache hit (second call should be faster)
    start = time.perf_counter()
    result1 = await engine.think_fast("Test cache query", {})
    first_ms = (time.perf_counter() - start) * 1000

    start = time.perf_counter()
    result2 = await engine.think_fast("Test cache query", {})
    second_ms = (time.perf_counter() - start) * 1000

    assert result1.response == result2.response
    assert second_ms < first_ms  # Cache hit should be faster
    print(f"✓ Test 3 passed: Cache hit (first: {first_ms:.2f}ms, second: {second_ms:.2f}ms)")

    print("\n✅ Fast thinking engine tests passed!")
    return True


async def test_dual_process():
    """Test dual-process brain."""
    try:
        from amos_dual_process_brain import get_dual_process_brain

        brain = get_dual_process_brain()

        # Test simple query (should use fast path)
        start = time.perf_counter()
        result = await brain.think("Hello world", prefer_fast=True)
        elapsed = (time.perf_counter() - start) * 1000

        assert result.response is not None
        assert result.thinking_mode in ["fast_only", "slow_only", "combined"]
        assert result.confidence > 0
        print(f"✓ Dual-process test passed: {result.thinking_mode} in {elapsed:.1f}ms")

        print("\n✅ Dual-process brain tests passed!")
        return True
    except ImportError as e:
        print(f"⚠️  Dual-process brain not available: {e}")
        return False


async def main():
    """Run all integration tests."""
    print("=" * 70)
    print("  Fast Thinking Integration Tests")
    print("=" * 70)
    print()

    try:
        await test_fast_thinking()
        print()
        await test_dual_process()
        print()
        print("=" * 70)
        print("  ✅ All integration tests passed!")
        print("=" * 70)
        return 0
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
