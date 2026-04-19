"""Test Canon Cognitive Processor with real Canon data.

Validates that the processor actually loads and uses Canon knowledge
from real AMOS Canon JSON files during cognitive processing.

Creator: Trang Phan
Version: 3.0.0
"""

from __future__ import annotations

from amos_brain.canon_cognitive_processor import (
    get_canon_cognitive_processor,
    canon_process,
)


def test_processor_initialization():
    """Test that processor initializes with Canon knowledge."""
    print("\n" + "=" * 60)
    print("TEST: Processor Initialization")
    print("=" * 60)

    processor = get_canon_cognitive_processor()

    print(f"Initialized: {processor._initialized}")
    print(f"Knowledge engine loaded: {processor._knowledge_engine._loaded}")

    stats = processor.get_canon_stats()
    print(f"Canon entries: {stats['total_entries']}")
    print(f"Domains: {stats['domains']}")


def test_canon_processing():
    """Test cognitive processing with Canon enrichment."""
    print("\n" + "=" * 60)
    print("TEST: Canon-Enriched Processing")
    print("=" * 60)

    queries = [
        ("How does AMOS cognition work?", "cognitive"),
        ("Explain brain intelligence", "core"),
        ("What engines handle automation?", "domains"),
    ]

    for query, domain in queries:
        print(f"\n  Query: {query}")
        print(f"  Domain: {domain}")

        result = canon_process(query, domain)

        print(f"  Confidence: {result.confidence:.2%}")
        print(f"  Processing time: {result.processing_time_ms:.2f}ms")
        print(f"  Canon sources: {len(result.canon_sources)}")
        print(f"  Canon terms: {len(result.canon_terms_used)}")

        if result.canon_sources:
            print(f"    Sources: {result.canon_sources[:2]}")

        if result.canon_terms_used:
            for term, desc in list(result.canon_terms_used.items())[:2]:
                print(f"    Term: {term}")
                print(f"      {desc[:60]}...")


def test_entry_retrieval():
    """Test that real Canon entries are retrieved."""
    print("\n" + "=" * 60)
    print("TEST: Canon Entry Retrieval")
    print("=" * 60)

    processor = get_canon_cognitive_processor()

    # Test finding entries
    entries = processor._find_relevant_knowledge("brain cognition", "core")

    print(f"\n  Found {len(entries)} relevant entries")

    for entry in entries[:3]:
        print(f"\n    Entry: {entry.key}")
        print(f"    Type: {entry.entry_type}")
        print(f"    Domain: {entry.domain}")

        # Extract meta info
        if isinstance(entry.content, dict) and "meta" in entry.content:
            meta = entry.content["meta"]
            if "codename" in meta:
                print(f"    Codename: {meta['codename']}")
            if "description" in meta:
                print(f"    Description: {meta['description'][:80]}...")


def test_term_extraction():
    """Test Canon term extraction."""
    print("\n" + "=" * 60)
    print("TEST: Canon Term Extraction")
    print("=" * 60)

    processor = get_canon_cognitive_processor()

    # Get entries and extract terms
    entries = processor._find_relevant_knowledge("agent engine", "core")
    terms = processor._extract_canon_terms(entries)

    print(f"\n  Extracted {len(terms)} terms from {len(entries)} entries")

    for term, description in list(terms.items())[:5]:
        print(f"\n    {term}:")
        print(f"      {description[:70]}...")


def main():
    """Run all Canon Cognitive Processor tests."""
    print("\n" + "=" * 60)
    print("AMOS CANON COGNITIVE PROCESSOR - REAL DATA TEST")
    print("=" * 60)

    try:
        test_processor_initialization()
        test_canon_processing()
        test_entry_retrieval()
        test_term_extraction()

        print("\n" + "=" * 60)
        print("✅ ALL CANON COGNITIVE PROCESSOR TESTS PASSED")
        print("=" * 60)
        return 0

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
