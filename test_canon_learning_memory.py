"""Test Canon Learning and Memory systems with real Canon data.

Validates Canon-integrated learning and memory functionality.

Creator: Trang Phan
Version: 3.0.0
"""

from amos_brain.canon_learning_engine import canon_learn
from amos_brain.canon_memory_system import canon_store, canon_search


def test_canon_learning():
    """Test Canon-guided learning."""
    print("\n" + "=" * 60)
    print("TEST: Canon Learning Engine")
    print("=" * 60)

    result = canon_learn(
        task="Design secure API authentication with JWT tokens",
        domain="api",
        outcome="Implemented JWT middleware with 256-bit encryption",
        success=True,
    )

    print(f"✅ Learning successful")
    print(f"   Patterns learned: {len(result.learned_patterns)}")
    print(f"   Canon sources: {len(result.canon_sources_used)}")
    print(f"   Learning time: {result.learning_time_ms:.2f}ms")

    for pattern in result.learned_patterns[:3]:
        print(f"\n   Pattern: {pattern.pattern_id}")
        print(f"     Domain: {pattern.domain}")
        print(f"     Description: {pattern.description[:50]}...")
        print(f"     Applicability: {pattern.applicability_score:.1%}")
        if pattern.canon_sources:
            print(f"     Canon sources: {', '.join(pattern.canon_sources[:2])}")


def test_canon_memory():
    """Test Canon memory storage and retrieval."""
    print("\n" + "=" * 60)
    print("TEST: Canon Memory System")
    print("=" * 60)

    # Store memories
    memories = [
        canon_store("Implemented brain cognition kernel", "brain"),
        canon_store("Designed agent orchestration system", "agent"),
        canon_store("Created Canon knowledge integration", "cognitive"),
    ]

    print(f"✅ Stored {len(memories)} memories with Canon context")

    for mem in memories:
        print(f"\n   Memory: {mem.memory_id}")
        print(f"     Content: {mem.content[:40]}...")
        print(f"     Domain: {mem.domain}")
        print(f"     Canon terms: {len(mem.canon_terms)}")
        if mem.canon_terms:
            for term, desc in list(mem.canon_terms.items())[:2]:
                print(f"       - {term}: {desc[:40]}...")


def test_canon_memory_search():
    """Test Canon-enhanced memory search."""
    print("\n" + "=" * 60)
    print("TEST: Canon Memory Search")
    print("=" * 60)

    queries = ["brain cognition", "agent system", "knowledge integration"]

    for query in queries:
        print(f"\n  Query: '{query}'")
        results = canon_search(query)

        print(f"  Found {len(results)} memories")
        for mem in results[:2]:
            print(f"    - {mem.content[:40]}... (domain: {mem.domain})")


def test_learning_stats():
    """Test learning engine statistics."""
    print("\n" + "=" * 60)
    print("TEST: Learning Engine Stats")
    print("=" * 60)

    from amos_brain.canon_learning_engine import get_canon_learning_engine

    engine = get_canon_learning_engine()
    stats = engine.get_learning_stats()

    print(f"✅ Learning stats:")
    print(f"   Patterns cached: {stats['patterns_cached']}")
    print(f"   Domains: {stats['domains']}")
    print(f"   Canon entries available: {stats['canon_entries_available']}")


def test_memory_stats():
    """Test memory system statistics."""
    print("\n" + "=" * 60)
    print("TEST: Memory System Stats")
    print("=" * 60)

    from amos_brain.canon_memory_system import get_canon_memory_system

    system = get_canon_memory_system()
    stats = system.get_memory_stats()

    print(f"✅ Memory stats:")
    print(f"   Total memories: {stats['total_memories']}")
    print(f"   Domains: {stats['domains']}")
    print(f"   Domain breakdown: {stats['domain_breakdown']}")


def main():
    """Run all Canon Learning and Memory tests."""
    print("\n" + "=" * 60)
    print("AMOS CANON LEARNING & MEMORY - REAL DATA TEST")
    print("=" * 60)

    try:
        test_canon_learning()
        test_canon_memory()
        test_canon_memory_search()
        test_learning_stats()
        test_memory_stats()

        print("\n" + "=" * 60)
        print("✅ ALL CANON LEARNING & MEMORY TESTS PASSED")
        print("=" * 60)
        return 0

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
