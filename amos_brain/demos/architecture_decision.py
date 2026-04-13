#!/usr/bin/env python3
"""
AMOS Brain Demo: Architecture Decision Records
===============================================

Demonstrates the ArchitectureDecision cookbook recipe.

Usage:
  python architecture_decision.py
"""
from amos_brain import ArchitectureDecision


def demo_microservices_decision():
    """Demo: Microservices vs Monolith decision."""
    print("=" * 60)
    print("DEMO: Microservices vs Monolith")
    print("=" * 60)
    
    result = ArchitectureDecision.analyze(
        question="Should we migrate from monolith to microservices?",
        context={
            "team_size": 12,
            "current_scale": "medium",
            "growth_expectation": "high"
        }
    )
    
    print(f"\n📋 Recipe: {result.recipe_name}")
    print(f"✓ Confidence: {result.confidence}")
    print(f"✓ Law compliant: {result.law_compliant}")
    print(f"✓ Session ID: {result.session_id}")
    
    print(f"\n📝 Analysis:")
    print("-" * 60)
    print(result.analysis[:400] + "...")
    
    print(f"\n💡 Top Recommendations:")
    for i, rec in enumerate(result.recommendations, 1):
        print(f"  {i}. {rec[:60]}...")
    print()


def demo_database_selection():
    """Demo: Database technology selection."""
    print("=" * 60)
    print("DEMO: Database Technology Selection")
    print("=" * 60)
    
    result = ArchitectureDecision.analyze(
        question="Should we use PostgreSQL or MongoDB for our data layer?",
        context={
            "data_structure": "relational with some documents",
            "scale": "millions of records",
            "team_experience": "SQL strong"
        }
    )
    
    print(f"\n📋 Recipe: {result.recipe_name}")
    print(f"✓ Confidence: {result.confidence}")
    
    print(f"\n💡 Recommendations:")
    for i, rec in enumerate(result.recommendations, 1):
        print(f"  {i}. {rec[:60]}...")
    print()


def demo_api_design():
    """Demo: API design decision."""
    print("=" * 60)
    print("DEMO: API Design Patterns")
    print("=" * 60)
    
    result = ArchitectureDecision.analyze(
        question="Should we use REST or GraphQL for our public API?",
        context={
            "client_types": ["web", "mobile", "third-party"],
            "data_complexity": "medium",
            "team_size": 8
        }
    )
    
    print(f"\n✓ Analysis complete with {result.confidence} confidence")
    print(f"\n💡 Key points:")
    for rec in result.recommendations[:2]:
        print(f"  • {rec[:70]}...")
    print()


def main():
    """Run all ADR demos."""
    print("\n" + "=" * 60)
    print("AMOS BRAIN: ARCHITECTURE DECISION RECORDS DEMO")
    print("=" * 60)
    print("\nDemonstrates cognitive architecture analysis.\n")
    
    demo_microservices_decision()
    demo_database_selection()
    demo_api_design()
    
    print("=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)
    print("\nThe ArchitectureDecision recipe provides:")
    print("  • Structured analysis of architectural choices")
    print("  • Rule of 2/4 compliance checking")
    print("  • Context-aware recommendations")
    print("  • Audit trail via session tracking")
    print()


if __name__ == "__main__":
    main()
