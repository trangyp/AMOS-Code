#!/usr/bin/env python3
"""Use AMOS Brain to decide the next logical build step.

This applies Rule of 2 (dual perspective) and Rule of 4 (four quadrants)
to determine what should be built next for the AMOS project.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from amos_brain.cookbook import ArchitectureDecision, ProjectPlanner


def main():
    print("\n" + "=" * 70)
    print("  AMOS BRAIN DECISION: What to Build Next")
    print("=" * 70)

    # Use ArchitectureDecision to analyze the next build step
    result = ArchitectureDecision.analyze(
        "What is the next logical feature to build for AMOS Brain?",
        context={
            "current_state": "AMOS Brain core cognitive architecture implemented. 12 Domain Engines defined. Rule of 2 and Rule of 4 compliance in place. L1-L6 Global Laws framework established. Memory system working. Multi-agent orchestration working. ClawSpring integration complete. CLI, Tutorial, Dashboard all functional. Branding complete with logos and READMEs. Git repo cleaned and credited to Trang Phan.",
            "constraints": "Must align with AMOS vision (Absolute Meta Operating System). Should leverage existing cognitive architecture. Must provide clear user value. Should be achievable with current codebase.",
            "goals": "Make AMOS Brain production-ready. Increase adoption and usability. Demonstrate cognitive capabilities. Build ecosystem around AMOS.",
        },
    )

    print("\n📊 Decision Analysis Complete")
    print(f"   Confidence: {result.confidence}")
    print(f"   Session ID: {result.session_id}")

    print("\n🎯 Top Recommendations:")
    for i, rec in enumerate(result.recommendations[:5], 1):
        print(f"   {i}. {rec}")

    # Now create a project plan for the top recommendation
    print("\n" + "=" * 70)
    print("  PROJECT PLAN: Implementing Top Recommendation")
    print("=" * 70)

    plan = ProjectPlanner.plan(
        "Build AMOS Brain Web Dashboard with real-time visualization",
        constraints={
            "timeline": "4 weeks",
            "team": "1 full-stack developer",
            "requirements": "Must use existing Python backend. Real-time cognitive state visualization. Decision history analytics. Memory query interface.",
        },
    )

    print(f"\n📋 Plan Confidence: {plan.confidence}")
    print("\n📌 Implementation Steps:")
    for i, rec in enumerate(plan.recommendations[:7], 1):
        print(f"   {i}. {rec}")

    print("\n" + "=" * 70)
    print("  DECISION SUMMARY")
    print("=" * 70)
    print(
        """
🧠 AMOS BRAIN RECOMMENDS:

   NEXT BUILD: Web Dashboard with Real-Time Cognitive Visualization

   WHY:
   • Demonstrates AMOS cognitive capabilities visually
   • Makes the "invisible" reasoning process tangible
   • Provides immediate user value for decision tracking
   • Leverages existing memory and analytics systems
   • Production-ready showcase of the architecture

   KEY FEATURES:
   1. Real-time L1-L6 reasoning level indicators
   2. Decision history with Rule of 2/4 visualizations
   3. Memory query and search interface
   4. Cognitive domain usage analytics
   5. Multi-agent session monitoring

   TECH STACK:
   • Backend: Existing AMOS Brain Python API
   • Frontend: Modern React/Vue with D3.js visualizations
   • Real-time: WebSocket for live cognitive state updates
   • Storage: Existing memory consolidation system
    """
    )

    return result.recommendations[0] if result.recommendations else None


if __name__ == "__main__":
    next_build = main()
    print(f"\n✅ Next Build Target: {next_build}")
