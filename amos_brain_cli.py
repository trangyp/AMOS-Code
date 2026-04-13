#!/usr/bin/env python3
"""
AMOS Brain CLI - Interactive command-line interface for brain queries.

Provides commands:
  /decide <problem>    - Analyze decision with Rule of 2 + Rule of 4
  /analyze <topic>     - Deep systems analysis
  /status              - Show brain status
  /laws                - Show global laws
  /history             - Show reasoning history
  /recall <problem>    - Recall similar past reasoning
  /audit               - Show reasoning audit trail
  /help                - Show this help
  /quit                - Exit

Usage:
  python amos_brain_cli.py
"""
from __future__ import annotations

import sys
import os

# Setup paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from amos_brain import get_amos_integration, RuleOfTwo, RuleOfFour, GlobalLaws
from amos_brain.memory import get_brain_memory


# ANSI colors
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


def print_banner():
    """Print CLI banner."""
    print()
    print(clr("╔══════════════════════════════════════════════════════════╗", "cyan", "bold"))
    print(clr("║              AMOS BRAIN COMMAND INTERFACE                ║", "cyan", "bold"))
    print(clr("║     Rule of 2 × Rule of 4 × Global Laws L1-L6          ║", "cyan"))
    print(clr("╚══════════════════════════════════════════════════════════╝", "cyan", "bold"))
    print()
    print("Type /help for available commands, /quit to exit.")
    print()


def print_help():
    """Print help message."""
    print(clr("\nAvailable Commands:", "bold"))
    print()
    print("  /decide <problem>   - Analyze decision with Rule of 2 + Rule of 4")
    print("  /analyze <topic>    - Deep systems analysis")
    print("  /status             - Show brain status (engines, laws, domains)")
    print("  /laws               - Show all 6 global laws")
    print("  /history [n]        - Show last n reasoning entries (default: 5)")
    print("  /recall <problem>   - Find similar past reasoning")
    print("  /audit              - Show reasoning audit trail with compliance stats")
    print("  /help               - Show this help")
    print("  /quit               - Exit the CLI")
    print()


def cmd_decide(amos, memory, problem: str):
    """Execute /decide command."""
    print(clr(f"\n[Analyzing: {problem}]", "cyan"))
    print("Applying Rule of 2 (dual perspectives) and Rule of 4 (four quadrants)...")
    print()

    # Get analysis
    analysis = amos.analyze_with_rules(problem)

    # Check for prior similar reasoning
    recall = memory.recall_for_problem(problem)
    if recall.get("has_prior_reasoning"):
        print(clr("[Similar past reasoning found - incorporating context]", "yellow"))
        for entry in recall.get("similar_entries", [])[:2]:
            print(f"  - Similarity: {entry['similarity']:.0%} | {entry['past_problem'][:50]}...")
        print()

    # Display Rule of 2 results
    if "rule_of_two" in analysis:
        r2 = analysis["rule_of_two"]
        print(clr("┌─ Rule of 2: Dual Perspective Analysis ─", "bold"))

        for i, p in enumerate(r2.get("perspectives", []), 1):
            name = p.name if hasattr(p, 'name') else f"Perspective {i}"
            viewpoint = p.viewpoint if hasattr(p, 'viewpoint') else str(p)
            print(f"│ {clr(name, 'cyan')}")
            print(f"│   View: {viewpoint[:60]}...")
            if hasattr(p, 'supporting_evidence'):
                print(f"│   Evidence: {len(p.supporting_evidence)} points")
        print("│")
        print(f"│ {clr('Synthesis:', 'green')} {r2.get('recommendation', 'No clear recommendation')}")
        print(f"│ {clr('Confidence:', 'green')} {r2.get('confidence', 0):.0%}")
        print(clr("└─────────────────────────────────────────", "bold"))
        print()

    # Display Rule of 4 results
    if "rule_of_four" in analysis:
        r4 = analysis["rule_of_four"]
        print(clr("┌─ Rule of 4: Four Quadrant Analysis ─", "bold"))
        print(f"│ Quadrants: {', '.join(r4.get('quadrants_analyzed', []))}")
        print(f"│ Completeness: {r4.get('completeness_score', 0):.0%}")

        integration = r4.get("integration", {})
        if integration:
            print(f"│ {clr('Key Quadrants:', 'green')} {', '.join(integration.get('key_quadrants', []))}")
            print(f"│ {clr('Recommendation:', 'green')} {integration.get('integrated_recommendation', 'N/A')}")
        print(clr("└───────────────────────────────────────", "bold"))
        print()

    # Display recommendations
    print(clr("┌─ Final Recommendations ─", "bold"))
    for rec in analysis.get("recommendations", []):
        print(f"│ • {rec}")
    print(clr("└─────────────────────────", "bold"))
    print()

    # Save to memory
    entry_id = memory.save_reasoning(problem, analysis)
    print(f"[Saved to memory: {entry_id[:8]}...]")
    print()


def cmd_analyze(amos, topic: str):
    """Execute /analyze command."""
    print(clr(f"\n[Deep Analysis: {topic}]", "cyan"))
    print("Routing through cognitive stack engines...")
    print()

    # Route query
    from amos_brain.cognitive_stack import CognitiveStack
    stack = CognitiveStack()
    engines = stack.route_query(topic)

    print(f"Engines activated: {', '.join(engines[:3])}")
    if len(engines) > 3:
        print(f"  (and {len(engines) - 3} more)")
    print()

    # Multi-scale analysis
    print(clr("┌─ Multi-Scale Analysis ─", "bold"))
    print("│ Micro (Immediate): Direct factors and local constraints")
    print("│ Meso (Organizational): Structure, patterns, sector dynamics")
    print("│ Macro (Systemic): Long-term trends, global implications")
    print(clr("└────────────────────────", "bold"))
    print()

    # Temporal analysis
    print(clr("┌─ Temporal Analysis ─", "bold"))
    print("│ Short-term (0-1 year): Quick wins, immediate risks")
    print("│ Medium-term (1-5 years): Implementation, adaptation")
    print("│ Long-term (5+ years): Strategic positioning, paradigm shifts")
    print(clr("└──────────────────────", "bold"))
    print()

    # Get full reasoning
    analysis = amos.analyze_with_rules(topic)

    # Display synthesis
    print(clr("┌─ Synthesis ─", "bold"))
    for rec in analysis.get("recommendations", []):
        print(f"│ • {rec}")
    print(clr("└──────────────", "bold"))
    print()


def cmd_status(amos):
    """Execute /status command."""
    status = amos.get_status()

    print(clr("\n┌─ AMOS Brain Status ─", "bold"))
    print(f"│ Initialized: {status.get('initialized', False)}")
    print(f"│ Brain Loaded: {status.get('brain_loaded', False)}")
    print(f"│ Engines Available: {status.get('engines_count', 0)}")
    print(f"│ Laws Active: {len(status.get('laws_active', []))}")
    print(f"│ Domains Covered: {len(status.get('domains_covered', []))}")
    print(clr("└─────────────────────", "bold"))
    print()


def cmd_laws():
    """Execute /laws command."""
    laws = GlobalLaws()
    print()
    print(clr("═ AMOS Global Laws ═", "bold", "cyan"))
    print()

    for law_id in sorted(laws.LAWS.keys(), key=lambda x: laws.LAWS[x].priority):
        law = laws.LAWS[law_id]
        print(f"{clr(law.id, 'yellow', 'bold')}: {clr(law.name, 'bold')}")
        print(f"  Priority: {law.priority}")
        print(f"  {law.description}")
        print()


def cmd_history(memory, args: list[str]):
    """Execute /history command."""
    limit = int(args[0]) if args else 5
    history = memory.get_reasoning_history(limit=limit)

    print(clr(f"\n┌─ Reasoning History (last {len(history)}) ─", "bold"))

    for i, entry in enumerate(history, 1):
        ts = entry.get('timestamp', 'unknown')[:16] if entry.get('timestamp') else 'unknown'
        problem = entry.get('problem_preview', 'N/A')[:50]
        r2 = entry.get('rule_of_two_applied', False)
        r4 = entry.get('rule_of_four_applied', False)

        print(f"│ {i}. [{ts}] {problem}...")
        print(f"│    Rule2: {'✓' if r2 else '✗'} | Rule4: {'✓' if r4 else '✗'} | "
              f"Confidence: {entry.get('confidence_score', 0):.0%}")

    print(clr("└──────────────────────────────", "bold"))
    print()


def cmd_recall(memory, problem: str):
    """Execute /recall command."""
    recall = memory.recall_for_problem(problem)

    print(clr(f"\n[Recalling for: {problem[:60]}...]", "cyan"))
    print()

    if recall.get("has_prior_reasoning"):
        print(clr("Similar past reasoning found:", "green", "bold"))

        for item in recall.get("similar_entries", []):
            entry = item.get("entry", {})
            sim = item.get("similarity", 0)
            print()
            print(f"  Similarity: {sim:.0%}")
            print(f"  Problem: {entry.get('problem_preview', 'N/A')}")
            print(f"  Date: {entry.get('timestamp', 'unknown')[:16]}")
            print(f"  Confidence: {entry.get('confidence_score', 0):.0%}")

            if item.get("recommendations"):
                print("  Recommendations:")
                for rec in item["recommendations"][:3]:
                    print(f"    • {rec[:60]}...")
    else:
        print(clr("No similar past reasoning found.", "yellow"))

    print()


def cmd_audit(memory):
    """Execute /audit command."""
    audit = memory.get_audit_trail()

    print(clr("\n┌─ Reasoning Audit Trail ─", "bold"))
    print(f"│ Total Entries: {audit.get('total_entries', 0)}")
    print(f"│ With Rule of 2: {audit.get('rule_of_two_applied', 0)}")
    print(f"│ With Rule of 4: {audit.get('rule_of_four_applied', 0)}")
    print(f"│ Avg Confidence: {audit.get('average_confidence', 0):.1%}")
    print()

    compliance = audit.get("law_compliance", {})
    print(f"│ {clr('Law Compliance:', 'cyan')}")
    print(f"│   L2 (Rule of 2): {compliance.get('L2_compliance_rate', 0):.0%}")
    print(f"│   L3 (Rule of 4): {compliance.get('L3_compliance_rate', 0):.0%}")
    print(clr("└─────────────────────────", "bold"))
    print()


def main():
    """Main CLI loop."""
    print_banner()

    # Initialize brain
    print("Initializing AMOS Brain...")
    amos = get_amos_integration()
    memory = get_brain_memory()

    status = amos.get_status()
    if status.get('initialized'):
        print(clr("✓ Brain initialized", "green"))
        print(f"  {status.get('engines_count', 0)} engines | 6 laws | 12 domains")
    else:
        print(clr("✗ Brain initialization failed", "red"))
        return

    print()

    # Command loop
    while True:
        try:
            user_input = input(clr("amos> ", "cyan", "bold")).strip()
        except EOFError:
            break
        except KeyboardInterrupt:
            print("\n")
            break

        if not user_input:
            continue

        # Parse command
        parts = user_input.split()
        cmd = parts[0].lower()
        args = parts[1:]
        rest = " ".join(args)

        if cmd in ["/quit", "/exit", "quit", "exit"]:
            print(clr("Shutting down AMOS Brain CLI...", "cyan"))
            break

        elif cmd == "/help":
            print_help()

        elif cmd == "/decide":
            if not rest:
                print(clr("Usage: /decide <problem to analyze>", "yellow"))
                continue
            cmd_decide(amos, memory, rest)

        elif cmd == "/analyze":
            if not rest:
                print(clr("Usage: /analyze <topic to analyze>", "yellow"))
                continue
            cmd_analyze(amos, rest)

        elif cmd == "/status":
            cmd_status(amos)

        elif cmd == "/laws":
            cmd_laws()

        elif cmd == "/history":
            cmd_history(memory, args)

        elif cmd == "/recall":
            if not rest:
                print(clr("Usage: /recall <problem to find similar reasoning>", "yellow"))
                continue
            cmd_recall(memory, rest)

        elif cmd == "/audit":
            cmd_audit(memory)

        else:
            print(clr(f"Unknown command: {cmd}. Type /help for available commands.", "yellow"))

    print()
    print(clr("AMOS Brain CLI terminated.", "cyan"))


if __name__ == "__main__":
    main()
