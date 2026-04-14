#!/usr/bin/env python3
"""AMOS Brain Interactive Tutorial - Learn brain features hands-on.

Guides users through:
  1. Rule of 2 (dual perspective decision analysis)
  2. Rule of 4 (four quadrant systems analysis)
  3. Memory & Recall (reasoning persistence)
  4. Dashboard (analytics and insights)
  5. Laws (L1-L6 compliance checking)

Usage:
  python amos_brain_tutorial.py
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from amos_brain import GlobalLaws, get_amos_integration
from amos_brain.dashboard import print_dashboard
from amos_brain.memory import get_brain_memory

C = {
    "cyan": "\033[36m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "red": "\033[31m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "bold": "\033[1m",
    "reset": "\033[0m",
}


def clr(text: str, *keys: str) -> str:
    return "".join(C[k] for k in keys) + str(text) + C["reset"]


def pause():
    """Pause for user to read."""
    input(clr("\n[Press Enter to continue...]", "yellow"))


def section(title: str):
    """Print section header."""
    print()
    print(clr("═" * 60, "cyan"))
    print(clr(f"  {title}", "cyan", "bold"))
    print(clr("═" * 60, "cyan"))
    print()


def lesson(title: str, content: str):
    """Print lesson block."""
    print(clr(f"📚 {title}", "green", "bold"))
    print(content)
    print()


def demo_decide(amos, memory):
    """Lesson 1: Rule of 2 + Rule of 4 decision analysis."""
    section("LESSON 1: Structured Decision Analysis (/decide)")

    lesson(
        "The Problem",
        "You need to make a decision but aren't sure which approach is best.\n"
        "Without structured analysis, you might miss critical perspectives.",
    )

    lesson(
        "AMOS Solution: Rule of 2",
        "The Rule of 2 requires checking TWO contrasting perspectives:\n"
        "  1. Primary (Internal/Micro) - Direct factors, immediate impact\n"
        "  2. Alternative (External/Macro) - Systemic factors, long-term\n\n"
        "This prevents confirmation bias and ensures balanced analysis.",
    )

    lesson(
        "AMOS Solution: Rule of 4",
        "The Rule of 4 requires analyzing across FOUR quadrants:\n"
        "  1. Biological/Human - Human capacity, wellbeing, safety\n"
        "  2. Technical/Infrastructural - Feasibility, reliability, complexity\n"
        "  3. Economic/Organizational - Cost, ROI, resources\n"
        "  4. Environmental/Planetary - Sustainability, impact\n\n"
        "This ensures comprehensive coverage of all system dimensions.",
    )

    print(clr("🎯 LIVE DEMO: Analyzing a real decision", "magenta", "bold"))
    print()

    problem = "Should our team adopt remote work permanently?"
    print(f"Decision: {clr(problem, 'cyan')}")
    print()
    print("Analyzing with Rule of 2 and Rule of 4...")
    print()

    # Run analysis
    analysis = amos.analyze_with_rules(problem)

    # Show Rule of 2 results
    if "rule_of_two" in analysis:
        r2 = analysis["rule_of_two"]
        print(clr("┌─ Rule of 2 Results ─", "bold"))

        for i, p in enumerate(r2.get("perspectives", []), 1):
            name = p.name if hasattr(p, "name") else f"Perspective {i}"
            print(
                f"│ {clr(name, 'cyan')}: {p.viewpoint[:50] if hasattr(p, 'viewpoint') else str(p)[:50]}..."
            )

        print(f"│ Synthesis: {r2.get('recommendation', 'N/A')[:50]}...")
        print(f"│ Confidence: {r2.get('confidence', 0):.0%}")
        print(clr("└───────────────────────", "bold"))
        print()

    # Show Rule of 4 results
    if "rule_of_four" in analysis:
        r4 = analysis["rule_of_four"]
        print(clr("┌─ Rule of 4 Results ─", "bold"))
        print(f"│ Quadrants analyzed: {len(r4.get('quadrants_analyzed', []))}/4")
        print(f"│ Completeness: {r4.get('completeness_score', 0):.0%}")

        integration = r4.get("integration", {})
        if integration.get("key_quadrants"):
            print(f"│ Key quadrants: {', '.join(integration['key_quadrants'])}")
        print(clr("└───────────────────────", "bold"))
        print()

    # Save to memory
    entry_id = memory.save_reasoning(problem, analysis, tags=["tutorial", "hr"])
    print(f"✓ Analysis saved to memory: {entry_id[:8]}...")
    print()

    lesson(
        "Key Takeaway",
        "Use `python amos_brain_cli.py decide <problem>` whenever you need structured analysis.\n"
        "The brain automatically applies Rule of 2 and Rule of 4,\n"
        "saving you time while ensuring comprehensive coverage.",
    )


def demo_analyze(amos, memory):
    """Lesson 2: Deep systems analysis."""
    section("LESSON 2: Deep Systems Analysis (/analyze)")

    lesson(
        "The Problem",
        "You need to understand a complex system or topic deeply.\n"
        "Surface-level analysis misses second-order effects and\n"
        "interconnections between different domains.",
    )

    lesson(
        "AMOS Solution: Cognitive Stack Routing",
        "The brain routes your query through relevant cognitive engines:\n"
        "  - Biology engine for human factors\n"
        "  - Engineering engine for technical feasibility\n"
        "  - Economics engine for financial analysis\n"
        "  - Strategy engine for competitive dynamics\n\n"
        "Multi-scale analysis at Micro, Meso, and Macro levels.",
    )

    print(clr("🎯 LIVE DEMO: Systems analysis", "magenta", "bold"))
    print()

    topic = "Impact of AI on software development"
    print(f"Topic: {clr(topic, 'cyan')}")
    print()

    # Route to engines
    from amos_brain.cognitive_stack import CognitiveStack

    stack = CognitiveStack()
    engines = stack.route_query(topic)

    print(f"Engines activated: {clr(', '.join(engines[:3]), 'green')}")
    if len(engines) > 3:
        print(f"  (and {len(engines) - 3} more)")
    print()

    print(clr("Multi-scale analysis:", "bold"))
    print("  Micro: Developer productivity, code quality changes")
    print("  Meso: Team structures, hiring patterns, skill requirements")
    print("  Macro: Industry transformation, economic shifts, education")
    print()

    # Run full analysis
    analysis = amos.analyze_with_rules(topic)

    print(clr("┌─ Analysis Results ─", "bold"))
    for rec in analysis.get("recommendations", [])[:3]:
        print(f"│ • {rec[:60]}...")
    print(clr("└────────────────────", "bold"))
    print()

    # Save
    entry_id = memory.save_reasoning(topic, analysis, tags=["tutorial", "ai"])
    print(f"✓ Analysis saved to memory: {entry_id[:8]}...")
    print()

    lesson(
        "Key Takeaway",
        "Use `python amos_brain_cli.py analyze <topic>` for deep systems understanding.\n"
        "The brain automatically routes through relevant engines\n"
        "and provides multi-scale, multi-domain analysis.",
    )


def demo_memory_recall(memory):
    """Lesson 3: Memory and recall."""
    section("LESSON 3: Memory & Recall (/recall)")

    lesson(
        "The Problem",
        "You've analyzed similar problems before but can't remember\n"
        "the details. You repeat analysis unnecessarily.",
    )

    lesson(
        "AMOS Solution: Intelligent Recall",
        "The brain automatically:\n"
        "  - Saves all reasoning with metadata\n"
        "  - Finds similar past problems\n"
        "  - Surfaces relevant recommendations\n\n"
        "Uses Jaccard similarity with stop-word filtering.",
    )

    print(clr("🎯 LIVE DEMO: Recall similar reasoning", "magenta", "bold"))
    print()

    # Add another problem to memory first
    problem2 = "Should we allow permanent remote work for developers?"
    print(f"New problem: {clr(problem2, 'cyan')}")
    print()

    print("Checking for similar past reasoning...")
    recall = memory.recall_for_problem(problem2)

    if recall.get("has_prior_reasoning"):
        print()
        print(clr("✓ Similar reasoning found!", "green", "bold"))

        for item in recall.get("similar_entries", []):
            entry = item.get("entry", {})
            sim = item.get("similarity", 0)
            print()
            print(f"  Similarity: {clr(f'{sim:.0%}', 'yellow')}")
            print(f"  Original: {entry.get('problem_preview', 'N/A')}")
            print("  Past recommendations:")
            for rec in entry.get("recommendations", [])[:2]:
                print(f"    • {rec[:50]}...")
    else:
        print(clr("No similar reasoning found.", "yellow"))

    print()

    lesson(
        "Key Takeaway",
        "The brain automatically recalls similar past reasoning\n"
        "when you use `decide` or `analyze`. Check `history` and `recall`\n"
        "to leverage your decision history.",
    )


def demo_dashboard():
    """Lesson 4: Dashboard and analytics."""
    section("LESSON 4: Analytics Dashboard (/dashboard)")

    lesson(
        "The Problem",
        "You don't know if you're using the brain effectively.\n"
        "Are you consistently applying Rule of 2? Is your\n"
        "confidence trending up or down?",
    )

    lesson(
        "AMOS Solution: Reasoning Analytics",
        "The dashboard provides:\n"
        "  - Compliance rates (L2, L3)\n"
        "  - Confidence trends over time\n"
        "  - Decision velocity (decisions per day)\n"
        "  - Domain pattern analysis\n"
        "  - Personalized insights and recommendations",
    )

    print(clr("🎯 LIVE DEMO: Dashboard view", "magenta", "bold"))
    print()

    print_dashboard(days=30)

    lesson(
        "Key Takeaway",
        "Use /dashboard regularly to track your reasoning patterns.\n"
        "The insights help you improve decision quality over time.",
    )


def demo_laws():
    """Lesson 5: Global Laws."""
    section("LESSON 5: Global Laws (L1-L6)")

    lesson(
        "The Foundation",
        "All AMOS reasoning is governed by 6 Global Laws:\n"
        "These ensure consistent, high-quality analysis.",
    )

    laws = GlobalLaws()

    print(clr("The 6 Laws:", "bold"))
    print()

    for law_id in sorted(laws.LAWS.keys(), key=lambda x: laws.LAWS[x].priority):
        law = laws.LAWS[law_id]
        print(f"{clr(law.id, 'yellow', 'bold')}: {clr(law.name, 'bold')}")
        print(f"  {law.description}")
        print()

    lesson(
        "Compliance Checking",
        "The brain automatically checks:\n"
        "  - L2: At least 2 perspectives checked\n"
        "  - L3: All 4 quadrants considered\n"
        "  - L4: No contradictions in output\n\n"
        "Use `python amos_brain_cli.py audit --text ...` to validate text against the laws.",
    )


def demo_practical_exercises(amos, memory):
    """Lesson 6: Practical exercises."""
    section("LESSON 6: Practice Exercises")

    print(clr("Try these exercises to build your skills:", "green", "bold"))
    print()

    exercises = [
        ("Exercise 1", "Run /decide on a work decision you're facing"),
        ("Exercise 2", "Run /analyze on a technology trend"),
        ("Exercise 3", "Check /history to see your saved reasoning"),
        ("Exercise 4", "Run /recall on a problem similar to one you've analyzed"),
        ("Exercise 5", "Check /dashboard to see your analytics"),
        ("Exercise 6", "Run /audit to check law compliance"),
    ]

    for title, desc in exercises:
        print(f"{clr(title, 'cyan', 'bold')}: {desc}")
    print()

    lesson(
        "Next Steps",
        "Start using the AMOS Brain CLI:\n"
        "  python amos_brain_cli.py\n\n"
        "Or integrate into clawspring:\n"
        "  python amos_clawspring.py\n\n"
        "Use /help anytime to see available commands.",
    )


def main():
    """Run the interactive tutorial."""
    print()
    print(clr("╔══════════════════════════════════════════════════════════╗", "cyan", "bold"))
    print(clr("║         AMOS BRAIN INTERACTIVE TUTORIAL                  ║", "cyan", "bold"))
    print(clr("║     Learn Rule of 2, Rule of 4, and Global Laws        ║", "cyan"))
    print(clr("╚══════════════════════════════════════════════════════════╝", "cyan", "bold"))
    print()

    print("Initializing brain...")
    amos = get_amos_integration()
    memory = get_brain_memory()

    status = amos.get_status()
    if not status.get("initialized"):
        print(clr("Error: Brain initialization failed", "red"))
        return

    print(f"✓ {status.get('engines_count', 0)} engines ready")
    print("✓ 6 global laws active")
    print()

    print(clr("This tutorial will teach you:", "green"))
    print("  1. Structured decision analysis (/decide)")
    print("  2. Deep systems analysis (/analyze)")
    print("  3. Memory and recall (/recall)")
    print("  4. Analytics dashboard (/dashboard)")
    print("  5. Global Laws (L1-L6)")
    print("  6. Practice exercises")
    print()

    pause()

    # Run lessons
    demo_decide(amos, memory)
    pause()

    demo_analyze(amos, memory)
    pause()

    demo_memory_recall(memory)
    pause()

    demo_dashboard()
    pause()

    demo_laws()
    pause()

    demo_practical_exercises(amos, memory)

    # Final
    print()
    print(clr("═" * 60, "green"))
    print(clr("  TUTORIAL COMPLETE", "green", "bold"))
    print(clr("  You are now ready to use the AMOS Brain!", "green"))
    print(clr("═" * 60, "green"))
    print()
    print("Next: Run python amos_brain_cli.py to practice")
    print()


if __name__ == "__main__":
    main()
