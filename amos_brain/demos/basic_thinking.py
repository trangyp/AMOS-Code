#!/usr/bin/env python3
"""AMOS Brain Demo: Basic Thinking
================================

Simple demonstration of core brain capabilities.

Usage:
  python basic_thinking.py
"""
from amos_brain import BrainClient, decide, think, validate


def demo_simple_think():
    """Demo 1: Simple one-line thinking."""
    print("=" * 60)
    print("DEMO 1: Simple think()")
    print("=" * 60)

    response = think("What are the benefits of TypeScript over JavaScript?")

    print(f"\n✓ Success: {response.success}")
    print(f"✓ Confidence: {response.confidence}")
    print(f"✓ Law compliant: {response.law_compliant}")
    print("\nAnalysis preview:")
    print("-" * 60)
    print(response.content[:300] + "...")
    print()


def demo_decision():
    """Demo 2: Decision making with reasoning."""
    print("=" * 60)
    print("DEMO 2: decide()")
    print("=" * 60)

    decision = decide(
        "Should our team adopt GraphQL or stick with REST?",
        options=["GraphQL", "REST API", "Hybrid approach"],
    )

    print(f"\n✓ Approved: {decision.approved}")
    print(f"✓ Risk level: {decision.risk_level}")
    print(f"✓ Decision ID: {decision.decision_id}")
    print("\nReasoning:")
    print("-" * 60)
    print(decision.reasoning[:300] + "...")
    print()


def demo_validation():
    """Demo 3: Quick validation."""
    print("=" * 60)
    print("DEMO 3: validate()")
    print("=" * 60)

    # Safe action
    is_valid, issues = validate("Implement comprehensive logging")
    print("\n'Safe' action:")
    print(f"  Valid: {is_valid}")
    print(f"  Issues: {issues}")

    # Potentially risky action
    is_valid, issues = validate("Delete production database without backup")
    print("\n'Risky' action:")
    print(f"  Valid: {is_valid}")
    print(f"  Issues: {issues}")
    print()


def demo_brain_client():
    """Demo 4: Full BrainClient usage."""
    print("=" * 60)
    print("DEMO 4: BrainClient (full capabilities)")
    print("=" * 60)

    client = BrainClient()

    # Get status
    print("\nSystem Status:")
    status = client.get_status()
    print(f"  Status: {status['status']}")
    print(f"  Layers: {len(status['layers'])}")
    print(f"  Laws: {len(status['global_laws'])}")

    # Orchestrate a goal
    print("\nOrchestrating goal...")
    plan = client.orchestrate("Design a scalable notification system")
    print(f"  Plan ID: {plan['plan_id']}")
    print(f"  Total tasks: {plan['total_tasks']}")
    print("  First 3 tasks:")
    for task in plan["tasks"][:3]:
        print(f"    - [{task['status']}] {task['description'][:40]}...")
    print()


def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("AMOS BRAIN: BASIC THINKING DEMO")
    print("=" * 60)
    print("\nThis demo shows the simplest way to use AMOS Brain.\n")

    demo_simple_think()
    demo_decision()
    demo_validation()
    demo_brain_client()

    print("=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)
    print("\nNext steps:")
    print("  - Try: python architecture_decision.py")
    print("  - Try: python code_review_example.py")
    print("  - Read the SDK documentation")
    print()


if __name__ == "__main__":
    main()
