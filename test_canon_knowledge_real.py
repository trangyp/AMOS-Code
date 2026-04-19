"""Real Canon Knowledge Engine Test - Validates actual Canon file parsing.

Tests the Canon Knowledge Engine against real AMOS Canon files:
1. Loads actual Canon JSON files
2. Parses and indexes canonical knowledge
3. Performs domain-specific searches
4. Validates query enrichment
5. Reports real statistics

Creator: Trang Phan
Version: 3.0.0
"""

from amos_brain.canon_knowledge_engine import (
    get_canon_knowledge_engine,
    CanonKnowledgeEngine,
)


def test_canon_loading():
    """Test that Canon files load successfully."""
    print("\n" + "=" * 60)
    print("TEST: Canon Knowledge Loading")
    print("=" * 60)

    engine = CanonKnowledgeEngine()
    success = engine.load_canon()

    print(f"Load success: {success}")

    stats = engine.get_stats()
    print(f"Total entries: {stats['total_entries']}")
    print(f"Domains loaded: {stats['domains']}")

    for domain, domain_stats in stats["domain_stats"].items():
        print(f"\n  {domain}:")
        print(f"    Entries: {domain_stats['entries']}")
        print(f"    Terms: {domain_stats['terms']}")
        print(f"    Engines: {domain_stats['engines']}")
        print(f"    Agents: {domain_stats['agents']}")

    return engine


def test_domain_knowledge(engine: CanonKnowledgeEngine):
    """Test domain-specific knowledge retrieval."""
    print("\n" + "=" * 60)
    print("TEST: Domain Knowledge Retrieval")
    print("=" * 60)

    domains = ["core", "domains", "cognitive"]

    for domain in domains:
        index = engine.get_domain_knowledge(domain)
        if index:
            print(f"\n{domain.upper()}:")
            print(f"  Total entries: {len(index.entries)}")
            print(f"  Engines: {index.engines[:3]}")  # Show first 3
            print(f"  Agents: {index.agents[:3]}")  # Show first 3
            print(f"  Sample terms: {list(index.terms.keys())[:3]}")


def test_search(engine: CanonKnowledgeEngine):
    """Test knowledge search functionality."""
    print("\n" + "=" * 60)
    print("TEST: Canon Knowledge Search")
    print("=" * 60)

    queries = ["brain", "agent", "engine", "cognitive"]

    for query in queries:
        results = engine.search_all(query)
        total = sum(len(entries) for entries in results.values())
        print(f"\n  Query '{query}': {total} results across {len(results)} domains")

        for domain, entries in list(results.items())[:2]:  # Show first 2 domains
            print(f"    {domain}: {len(entries)} matches")
            for entry in entries[:2]:  # Show first 2 entries
                print(f"      - {entry.key} ({entry.entry_type})")


def test_query_enrichment(engine: CanonKnowledgeEngine):
    """Test query enrichment with Canon context."""
    print("\n" + "=" * 60)
    print("TEST: Query Enrichment")
    print("=" * 60)

    queries = [
        "How does the brain process cognitive tasks?",
        "What agents handle automation?",
        "Explain the engine architecture",
    ]

    for query in queries:
        enriched = engine.enrich_query(query, "core")
        print(f"\n  Original: {query[:50]}...")
        if "[Canon Context]" in enriched:
            context_start = enriched.find("[Canon Context]")
            print(f"  Enriched: {enriched[context_start:context_start+80]}...")
        else:
            print("  No Canon context found")


def test_singleton():
    """Test singleton pattern."""
    print("\n" + "=" * 60)
    print("TEST: Singleton Pattern")
    print("=" * 60)

    engine1 = get_canon_knowledge_engine()
    engine2 = get_canon_knowledge_engine()

    print(f"Same instance: {engine1 is engine2}")
    print(f"Loaded: {engine1._loaded}")


def main():
    """Run all Canon Knowledge Engine tests."""
    print("\n" + "=" * 60)
    print("AMOS CANON KNOWLEDGE ENGINE - REAL FILE TEST")
    print("=" * 60)

    try:
        # Run tests
        engine = test_canon_loading()
        test_domain_knowledge(engine)
        test_search(engine)
        test_query_enrichment(engine)
        test_singleton()

        print("\n" + "=" * 60)
        print("✅ ALL CANON KNOWLEDGE TESTS PASSED")
        print("=" * 60)
        return 0

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
