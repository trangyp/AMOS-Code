#!/usr/bin/env python3
"""AMOS Brain Demo
================
Demonstrates AMOS Brain integration with clawspring.

Usage:
    python demo_amos.py [task]

Examples:
    python demo_amos.py analyze
    python demo_amos.py decide
    python demo_amos.py laws
    python demo_amos.py full
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent / "clawspring"))
sys.path.insert(0, str(Path(__file__).parent))


def demo_analyze():
    """Demo: AMOS Analysis on a software architecture problem."""
    print("=" * 60)
    print("DEMO: AMOS Brain Analysis")
    print("=" * 60)
    print("\nProblem: Should we migrate from monolith to microservices?")
    print("-" * 60)

    from tool_registry import execute_tool

    result = execute_tool(
        "AMOSReasoning",
        {
            "problem": (
                "Should we migrate from monolithic architecture to "
                "microservices? Consider scalability, complexity, "
                "team structure, and operational overhead."
            ),
            "context": {
                "team_size": 8,
                "current_users": 10000,
                "growth_rate": "2x per year",
                "deployment_frequency": "weekly",
            },
        },
        {},
    )

    print(result)
    print("\n" + "=" * 60)


def demo_decide():
    """Demo: AMOS Decision Analysis."""
    print("=" * 60)
    print("DEMO: AMOS Decision Analysis")
    print("=" * 60)
    print("\nDecision: Choose between three database options")
    print("-" * 60)

    from skill import execute_skill, find_skill

    skill = find_skill("/decide which database should we use?")
    if skill:
        result = execute_skill(
            skill.name,
            {
                "decision": "Database selection for high-throughput application",
                "options": [
                    "PostgreSQL with read replicas",
                    "MongoDB sharded cluster",
                    "CockroachDB distributed",
                ],
                "criteria": ["scalability", "consistency", "operational_complexity"],
            },
        )
        print(result)
    else:
        print("Skill not found - using tool directly")
        from tool_registry import execute_tool

        result = execute_tool(
            "AMOSReasoning",
            {
                "problem": (
                    "Decision: Database selection. Options: 1) PostgreSQL "
                    "with read replicas, 2) MongoDB sharded cluster, "
                    "3) CockroachDB distributed. Criteria: scalability, "
                    "consistency, operational complexity."
                )
            },
            {},
        )
        print(result)

    print("\n" + "=" * 60)


def demo_laws():
    """Demo: AMOS Global Laws."""
    print("=" * 60)
    print("DEMO: AMOS Global Laws")
    print("=" * 60)

    from tool_registry import execute_tool

    result = execute_tool("AMOSLaws", {}, {})
    print(result)

    print("\n" + "=" * 60)


def demo_status():
    """Demo: AMOS Brain Status."""
    print("=" * 60)
    print("DEMO: AMOS Brain Status")
    print("=" * 60)

    from tool_registry import execute_tool

    result = execute_tool("AMOSStatus", {}, {})
    print(result)

    print("\n" + "=" * 60)


def demo_full():
    """Full demo: All capabilities."""
    demo_status()
    print("\n")
    demo_laws()
    print("\n")
    demo_analyze()
    print("\n")
    demo_decide()


def main():
    parser = argparse.ArgumentParser(description="AMOS Brain Integration Demo")
    parser.add_argument(
        "task",
        nargs="?",
        default="full",
        choices=["analyze", "decide", "laws", "status", "full"],
        help="Which demo to run",
    )
    args = parser.parse_args()

    demos = {
        "analyze": demo_analyze,
        "decide": demo_decide,
        "laws": demo_laws,
        "status": demo_status,
        "full": demo_full,
    }

    try:
        demos[args.task]()
    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
