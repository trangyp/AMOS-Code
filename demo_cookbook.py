#!/usr/bin/env python3
"""AMOS Brain Cookbook Demo - Showcase real-world workflows.

Demonstrates:
  - Architecture Decision workflow
  - Project Planning workflow
  - Problem Diagnosis workflow
  - Technology Selection workflow
  - Risk Assessment workflow

Usage:
  python demo_cookbook.py
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from amos_brain.cookbook import (
    ArchitectureDecision,
    ProblemDiagnosis,
    ProjectPlanner,
    RiskAssessment,
    TechnologySelection,
)

C = {
    "cyan": "\033[36m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "red": "\033[31m",
    "bold": "\033[1m",
    "reset": "\033[0m",
}


def clr(text: str, *keys: str) -> str:
    return "".join(C[k] for k in keys) + str(text) + C["reset"]


def print_result(result):
    """Print workflow result."""
    print()
    print(clr(f"Workflow: {result.workflow_name}", "cyan", "bold"))
    print(clr(f"Problem: {result.input_data}", "bold"))
    print(f"Confidence: {clr(f'{result.confidence:.0%}', 'green')}")
    mid = result.memory_id[:8] if result.memory_id else "n/a"
    print(f"Memory ID: {mid}...")
    print()

    if result.recommendations:
        print(clr("Recommendations:", "bold"))
        for rec in result.recommendations[:5]:
            print(f"  • {rec[:70]}...")
    print()


def main():
    """Run cookbook workflow demos."""
    print()
    print(clr("╔══════════════════════════════════════════════════════════╗", "cyan", "bold"))
    print(clr("║         AMOS BRAIN COOKBOOK DEMO                         ║", "cyan", "bold"))
    print(clr("║     Real-World Workflow Examples                         ║", "cyan"))
    print(clr("╚══════════════════════════════════════════════════════════╝", "cyan", "bold"))
    print()

    # Demo 1: Architecture Decision
    print(clr("─" * 60, "yellow"))
    print(clr("DEMO 1: Architecture Decision", "yellow", "bold"))
    print(clr("─" * 60, "yellow"))
    print()

    result = ArchitectureDecision.run(
        "Should we migrate from REST to GraphQL?",
        context={
            "current_stack": "REST APIs with 50+ endpoints",
            "constraints": "Mobile app requires efficient data fetching",
            "scale": "1M requests/day",
        },
    )
    print_result(result)

    # Demo 2: Project Planning
    print(clr("─" * 60, "yellow"))
    print(clr("DEMO 2: Project Planning", "yellow", "bold"))
    print(clr("─" * 60, "yellow"))
    print()

    result = ProjectPlanner.run(
        "Build real-time notification system",
        timeline="6 weeks",
        constraints={
            "team": "2 backend engineers, 1 DevOps",
            "constraints": ["must handle 10k concurrent", "99.9% uptime SLA"],
        },
    )
    print_result(result)

    # Demo 3: Problem Diagnosis
    print(clr("─" * 60, "yellow"))
    print(clr("DEMO 3: Problem Diagnosis", "yellow", "bold"))
    print(clr("─" * 60, "yellow"))
    print()

    result = ProblemDiagnosis.run(
        "Database connection pool exhaustion",
        symptoms=["500 errors after 2 hours", "gradual increase in latency"],
        context="Checked: query performance, indexes. Timeline: Started 3 days ago, daily occurrence.",
    )
    print_result(result)

    # Demo 4: Technology Selection
    print(clr("─" * 60, "yellow"))
    print(clr("DEMO 4: Technology Selection", "yellow", "bold"))
    print(clr("─" * 60, "yellow"))
    print()

    result = TechnologySelection.run(
        "Message Queue",
        options=["RabbitMQ", "Apache Kafka", "AWS SQS"],
        criteria=[
            "scalability",
            "operational-complexity",
            "cost",
            "persistent messages",
            "high-throughput",
        ],
    )
    print_result(result)

    # Demo 5: Risk Assessment
    print(clr("─" * 60, "yellow"))
    print(clr("DEMO 5: Risk Assessment", "yellow", "bold"))
    print(clr("─" * 60, "yellow"))
    print()

    result = RiskAssessment.run(
        "Migrate production database to new cloud provider",
        impacts=[
            "revenue",
            "customer-trust",
            "data-integrity",
            "parallel-run",
            "automated-rollback",
            "dry-run-testing",
            "high-severity migration",
        ],
    )
    print_result(result)

    # Summary
    print()
    print(clr("═" * 60, "green"))
    print(clr("  COOKBOOK DEMO COMPLETE", "green", "bold"))
    print(clr("═" * 60, "green"))
    print()
    print("All workflows completed and saved to memory.")
    print()
    print("Try in your code:")
    print("  from amos_brain.cookbook import ArchitectureDecision")
    print("  result = ArchitectureDecision.run('Your decision here')")
    print()


if __name__ == "__main__":
    main()
