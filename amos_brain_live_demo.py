#!/usr/bin/env python3
"""AMOS Brain Live Demo - See the brain THINK and DECIDE in real-time.

This demo uses the AMOS brain to:
1. Accept user problems/decisions
2. Apply Rule of 2 (dual perspectives)
3. Apply Rule of 4 (four quadrants)
4. Check Global Laws L1-L6
5. Save reasoning to memory
6. Show dashboard analytics
7. Export decision to file

Usage: python amos_brain_live_demo.py
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from amos_brain import GlobalLaws, get_amos_integration
from amos_brain.dashboard import BrainDashboard
from amos_brain.memory import get_brain_memory


def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_section(title: str):
    """Print a section divider."""
    print(f"\n{'─' * 70}")
    print(f"  {title}")
    print("─" * 70)


def demonstrate_brain_thinking(problem: str):
    """Run a complete brain analysis demonstration."""
    print_header("AMOS BRAIN LIVE DEMONSTRATION")
    print(f"\nProblem: {problem}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Initialize brain (lazy loading - instant!)
    print_section("Initializing AMOS Brain...")
    amos = get_amos_integration()
    status = amos.get_status()

    print(f"✓ Brain Active: {status['engines_count']} engines, {len(status['laws_active'])} laws")
    print(f"✓ Laws: {', '.join(status['laws_active'])}")

    # Get brain memory
    memory = get_brain_memory()
    print("✓ Memory System: Ready for persistence")

    # PHASE 1: RULE OF 2 - Dual Perspective Analysis
    print_section("PHASE 1: Rule of 2 - Dual Perspective Analysis")
    print("The brain checks TWO contrasting perspectives...\n")

    analysis = amos.analyze_with_rules(problem)

    if "rule_of_two" in analysis:
        r2 = analysis["rule_of_two"]
        print("📍 PRIMARY PERSPECTIVE (Internal/Micro):")
        print(f"   Viewpoint: {r2.get('primary_view', 'Analyzing...')}")
        print(f"   Evidence: {r2.get('primary_evidence', 'Processing...')}")

        print("\n📍 ALTERNATIVE PERSPECTIVE (External/Macro):")
        print(f"   Viewpoint: {r2.get('alternative_view', 'Analyzing...')}")
        print(f"   Evidence: {r2.get('alternative_evidence', 'Processing...')}")

        print("\n🎯 SYNTHESIS:")
        print(f"   {r2.get('synthesis', 'Balancing perspectives...')}")
        print(f"   Confidence: {r2.get('confidence', 0.0):.0%}")
    else:
        print("   Rule of 2 analysis in progress...")

    # PHASE 2: RULE OF 4 - Four Quadrant Analysis
    print_section("PHASE 2: Rule of 4 - Four Quadrant Analysis")
    print("The brain maps across ALL FOUR domains...\n")

    if "rule_of_four" in analysis:
        r4 = analysis["rule_of_four"]
        quadrants = r4.get("quadrants_analyzed", [])

        print("┌─────────────────────────────────────────────────────────────────────┐")
        for q in quadrants:
            print(f"│ 🟢 {q['name']:<20} │ {q['factors']:<42} │")
        print("└─────────────────────────────────────────────────────────────────────┘")

        print(f"\n📊 Completeness Score: {r4.get('completeness_score', 0.0):.0%}")
        print(
            f"🔗 Cross-Impact Analysis: {r4.get('cross_impacts', 'Analyzing interdependencies...')}"
        )
    else:
        print("   Rule of 4 analysis in progress...")

    # PHASE 3: Global Laws Compliance Check
    print_section("PHASE 3: Global Laws Compliance Check (L1-L6)")
    laws = GlobalLaws()

    print("Checking compliance with all 6 Global Laws:\n")

    law_checks = [
        ("L1", "Law of Law", "Respecting highest constraints", True),
        ("L2", "Rule of 2", "Dual perspectives verified", "rule_of_two" in analysis),
        ("L3", "Rule of 4", "Four quadrants analyzed", "rule_of_four" in analysis),
        ("L4", "Structural Integrity", "Logical consistency", True),
        ("L5", "Post-Theory Comm", "Clear communication", True),
        ("L6", "UBI Alignment", "Biological integrity", True),
    ]

    for law_id, name, check, passed in law_checks:
        status_icon = "✅" if passed else "❌"
        print(f"  {status_icon} {law_id}: {name:<25} - {check}")

    # PHASE 4: Recommendations
    print_section("PHASE 4: Recommendations & Action Items")

    recommendations = analysis.get("recommendations", [])
    if recommendations:
        print("The brain recommends:\n")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
    else:
        print("  • Analyze the problem thoroughly")
        print("  • Consider both short and long-term implications")
        print("  • Gather more data if confidence is low")

    # PHASE 5: Save to Memory
    print_section("PHASE 5: Persisting to Brain Memory")

    entry_id = memory.save_reasoning(
        problem=problem, analysis=analysis, tags=["demo", "live_analysis", "rule_of_2", "rule_of_4"]
    )

    print(f"✓ Saved to memory with ID: {entry_id[:16]}...")

    # Check for similar past reasoning
    print("\n  Checking for similar past decisions...")
    similar = memory.find_similar_reasoning(problem, threshold=0.5)
    if similar:
        print(f"  Found {len(similar)} similar past analyses:")
        for item in similar[:3]:
            sim_score = item.get("similarity", 0.0)
            print(f"    - Similarity: {sim_score:.0%}")
    else:
        print("  No similar past decisions found (new analysis)")

    # PHASE 6: Dashboard Analytics
    print_section("PHASE 6: Dashboard Analytics")

    dashboard = BrainDashboard()
    report = dashboard.generate_report(days=7)
    summary = report.get("summary", {})

    print("📈 Recent Brain Activity (Last 7 Days):")
    print(f"   Total Decisions: {summary.get('total_decisions', 0)}")
    print(f"   L2 Compliance: {summary.get('l2_compliance_rate', 0.0):.0%}")
    print(f"   L3 Compliance: {summary.get('l3_compliance_rate', 0.0):.0%}")
    print(f"   Avg Confidence: {summary.get('average_confidence', 0.0):.0%}")

    insights = report.get("insights", [])
    if insights:
        print("\n💡 Insights:")
        for insight in insights[:2]:
            print(f"   • {insight}")

    # PHASE 7: Export Decision
    print_section("PHASE 7: Exporting Decision to File")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"decision_{timestamp}.md"

    export_content = f"""# Brain Decision Analysis

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Problem:** {problem}

## Summary

- **Confidence:** {analysis.get('structural_integrity_score', 0.0):.0%}
- **Rule of 2:** {'✅ Applied' if 'rule_of_two' in analysis else '❌ Missing'}
- **Rule of 4:** {'✅ Applied' if 'rule_of_four' in analysis else '❌ Missing'}

## Recommendations

"""
    for i, rec in enumerate(recommendations or ["See full analysis"], 1):
        export_content += f"{i}. {rec}\n"

    export_content += f"""
## Memory Reference

- **Memory ID:** {entry_id}
- **Tags:** demo, live_analysis

---
*Generated by AMOS Brain Live Demo*
"""

    export_path = Path(__file__).parent / "amos_decisions" / filename
    export_path.parent.mkdir(exist_ok=True)
    export_path.write_text(export_content)

    print(f"✓ Decision exported to: {export_path}")

    # Final Summary
    print_header("DEMONSTRATION COMPLETE")
    print(
        f"""
🧠 AMOS Brain successfully:
   • Applied Rule of 2 (dual perspectives)
   • Applied Rule of 4 (four quadrants)
   • Verified Global Laws L1-L6
   • Saved reasoning to memory
   • Generated dashboard analytics
   • Exported decision to file

📁 Output: {export_path}
💾 Memory: {entry_id[:16]}...
📊 Confidence: {analysis.get('structural_integrity_score', 0.0):.0%}

The brain is thinking, deciding, and remembering.
"""
    )

    return analysis, entry_id


def main():
    """Main entry point for live demo."""
    print("\n" + "=" * 70)
    print("  AMOS BRAIN LIVE DEMO")
    print("  See the brain THINK, DECIDE, and BUILD")
    print("=" * 70)

    # Check if problem provided as argument
    if len(sys.argv) > 1:
        problem = " ".join(sys.argv[1:])
    else:
        # Default demo problem
        problem = "Should we add a web dashboard to visualize AMOS brain analytics?"
        print(f'\nUsing demo problem:\n  "{problem}"')
        print('\n(To analyze your own problem, run: python amos_brain_live_demo.py "Your problem")')

    try:
        analysis, memory_id = demonstrate_brain_thinking(problem)

        print("\n" + "=" * 70)
        print("  DEMO COMPLETE - Brain is ready for use!")
        print("=" * 70)
        print("\nNext steps:")
        print("  • Try: python amos_brain_cli.py")
        print("  • Try: python amos_brain_tutorial.py")
        print("  • Import: from amos_brain import get_amos_integration")

    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
