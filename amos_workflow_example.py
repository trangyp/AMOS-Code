#!/usr/bin/env python3
"""AMOS Brain Workflow Example
============================
Real-world demonstration: Using AMOS to analyze and improve code architecture.

This example shows how AMOS Brain helps with:
1. Code review with dual perspective (Rule of 2)
2. Architecture analysis across 4 quadrants (Rule of 4)
3. Law compliance checking (L1-L6)
4. Actionable recommendations

Usage:
    python amos_workflow_example.py [task]

Tasks:
    review      Review a Python file with AMOS
    architect   Analyze architecture decision
    refactor    Get refactoring recommendations
    full        Run complete workflow
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

# Add paths
sys.path.insert(0, str(Path(__file__).parent / "clawspring"))
sys.path.insert(0, str(Path(__file__).parent))


class AMOSWorkflow:
    """Demonstrates AMOS Brain in real-world workflows."""

    def __init__(self):
        self.integration = None

    def _load_amos(self):
        """Lazy load AMOS integration."""
        if self.integration is None:
            from amos_brain import get_amos_integration

            self.integration = get_amos_integration()
        return self.integration

    def code_review(self, filepath: str) -> dict[str, Any]:
        """Review code with AMOS Brain.

        Applies Rule of 2 (optimistic + critical perspectives)
        and checks L1-L6 law compliance.
        """
        print("=" * 60)
        print("AMOS CODE REVIEW")
        print("=" * 60)
        print(f"\nFile: {filepath}")
        print("-" * 60)

        # Read the code
        path = Path(filepath)
        if not path.exists():
            return {"error": f"File not found: {filepath}"}

        code = path.read_text()
        lines = len(code.splitlines())
        print(f"Lines: {lines}")

        # Prepare review context
        review_context = {
            "file": filepath,
            "language": path.suffix or "unknown",
            "lines": lines,
            "has_tests": "test" in code.lower() or "Test" in code,
            "has_docs": '"""' in code or "'''" in code or "#" in code,
            "has_types": "def " in code
            and (
                "-> " in code or ": " in code.split("def")[1].split(":")[0]
                if "def " in code
                else False
            ),
        }

        # Run AMOS analysis
        amos = self._load_amos()

        # Rule of 2: Dual perspective analysis
        problem = f"""Review this code for quality, maintainability, and potential issues:

File: {filepath} ({lines} lines)
Language: {review_context['language']}
Has tests: {review_context['has_tests']}
Has documentation: {review_context['has_docs']}
Has type hints: {review_context['has_types']}

Provide:
1. Optimistic view: What's good about this code?
2. Critical view: What could be improved?
3. Rule of 4 analysis across all quadrants
4. Specific actionable recommendations
"""

        print("\n[Stage 1] Pre-processing (Laws check)...")
        pre = amos.pre_process(problem)
        print(f"  Blocked: {pre.get('blocked', False)}")
        if pre.get("blocked"):
            return {"error": pre.get("reason", "Blocked by laws")}

        print("\n[Stage 2] Rule of 2 Reasoning...")
        if hasattr(amos, "reasoning") and amos.reasoning:
            analysis = amos.reasoning.full_analysis(problem)

            # Extract Rule of 2 results
            rule_of_two = analysis.get("rule_of_two", {})
            print(f"  Confidence: {rule_of_two.get('confidence', 'N/A')}")
            print(
                f"  Primary perspective: {rule_of_two.get('perspectives', [{}])[0].get('name', 'N/A')}"
            )
            print(
                f"  Alternative perspective: {rule_of_two.get('perspectives', [{}, {}])[1].get('name', 'N/A')}"
            )

            # Extract Rule of 4 results
            rule_of_four = analysis.get("rule_of_four", {})
            quadrants = rule_of_four.get("quadrants", {})
            print("\n[Stage 3] Rule of 4 Analysis...")
            for q_name, q_data in quadrants.items():
                print(f"  {q_name}: {q_data.get('status', 'N/A')}")

            return {
                "file": filepath,
                "analysis": analysis,
                "recommendations": analysis.get("recommendation", "No specific recommendation"),
                "confidence": rule_of_two.get("confidence", 0),
            }

        return {"error": "Reasoning engine not available"}

    def architecture_decision(self, decision: str, options: list[str]) -> dict[str, Any]:
        """Analyze an architecture decision with AMOS.

        Uses Rule of 2 to evaluate options from multiple perspectives
        and Rule of 4 to consider all quadrants.
        """
        print("=" * 60)
        print("AMOS ARCHITECTURE DECISION")
        print("=" * 60)
        print(f"\nDecision: {decision}")
        print(f"Options: {', '.join(options)}")
        print("-" * 60)

        amos = self._load_amos()

        # Build decision problem
        options_str = "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(options)])
        problem = f"""Architecture Decision: {decision}

Options:
{options_str}

Analyze each option using:
- Rule of 2: Two contrasting perspectives for each
- Rule of 4: Impact across all four quadrants
- L1-L6 compliance: Does it violate any global laws?

Recommend the best option with justification.
"""

        print("\n[Stage 1] Laws compliance check...")
        pre = amos.pre_process(problem)
        if pre.get("blocked"):
            return {"error": pre.get("reason")}
        print("  L1-L6: Compliant")

        print("\n[Stage 2] Multi-option analysis...")
        if hasattr(amos, "reasoning") and amos.reasoning:
            analysis = amos.reasoning.full_analysis(problem)

            # Get recommendation
            recommendation = analysis.get("recommendation", "No clear recommendation")

            print("\n[Stage 3] Cross-validation...")
            validation = analysis.get("cross_validation", {})
            consistency = validation.get("consistency_score", 0)
            print(f"  Consistency: {consistency:.2f}")

            print(f"\n{'='*60}")
            print(f"RECOMMENDATION: {recommendation}")
            print(f"{'='*60}")

            return {
                "decision": decision,
                "options": options,
                "analysis": analysis,
                "recommendation": recommendation,
                "consistency": consistency,
            }

        return {"error": "Reasoning engine not available"}

    def refactoring_plan(self, target: str, issues: list[str]) -> dict[str, Any]:
        """Generate a refactoring plan with AMOS guidance."""
        print("=" * 60)
        print("AMOS REFACTORING PLAN")
        print("=" * 60)
        print(f"\nTarget: {target}")
        print(f"Issues: {', '.join(issues)}")
        print("-" * 60)

        amos = self._load_amos()

        problem = f"""Refactoring Task: {target}

Known Issues:
{chr(10).join(f'- {issue}' for issue in issues)}

Create a refactoring plan that:
1. Addresses all issues systematically
2. Follows Rule of 2 (consider risks and benefits)
3. Respects Rule of 4 (all quadrant impacts)
4. Complies with L1-L6 laws
5. Provides step-by-step execution order
"""

        print("\n[Stage 1] Pre-analysis...")
        pre = amos.pre_process(problem)
        routing = pre.get("routing", [])
        print(f"  Suggested engines: {routing}")

        print("\n[Stage 2] Generating plan...")
        if hasattr(amos, "reasoning") and amos.reasoning:
            analysis = amos.reasoning.full_analysis(problem)

            # Extract plan components
            rule_of_two = analysis.get("rule_of_two", {})
            rule_of_four = analysis.get("rule_of_four", {})

            print("\n[Stage 3] Plan validation...")
            print(f"  Dual perspective confidence: {rule_of_two.get('confidence', 0):.2f}")
            print(f"  Quadrant coverage: {len(rule_of_four.get('quadrants', {}))}/4")

            recommendation = analysis.get("recommendation", "No plan generated")

            print(f"\n{'='*60}")
            print("REFACTORING PLAN")
            print(f"{'='*60}")
            print(recommendation)

            return {
                "target": target,
                "issues": issues,
                "plan": recommendation,
                "analysis": analysis,
            }

        return {"error": "Reasoning engine not available"}


def main():
    parser = argparse.ArgumentParser(description="AMOS Brain Workflow Examples")
    parser.add_argument(
        "task",
        nargs="?",
        default="full",
        choices=["review", "architect", "refactor", "full"],
        help="Workflow task to demonstrate",
    )
    parser.add_argument(
        "--file", default="clawspring/agent.py", help="File to review (for review task)"
    )
    parser.add_argument(
        "--decision",
        default="Should we use async or sync I/O?",
        help="Decision to analyze (for architect task)",
    )
    args = parser.parse_args()

    workflow = AMOSWorkflow()

    try:
        if args.task == "review":
            result = workflow.code_review(args.file)
            if "error" in result:
                print(f"\nError: {result['error']}")
                return 1

        elif args.task == "architect":
            result = workflow.architecture_decision(
                args.decision, ["async/await", "threading", "sync with pools"]
            )
            if "error" in result:
                print(f"\nError: {result['error']}")
                return 1

        elif args.task == "refactor":
            result = workflow.refactoring_plan(
                "clawspring/tools.py", ["Line too long", "Unused imports", "Complex functions"]
            )
            if "error" in result:
                print(f"\nError: {result['error']}")
                return 1

        elif args.task == "full":
            print("\n" + "=" * 60)
            print("COMPLETE AMOS WORKFLOW DEMONSTRATION")
            print("=" * 60)

            # Task 1: Code Review
            print("\n\n>>> TASK 1: CODE REVIEW <<<")
            workflow.code_review("clawspring/agent.py")

            # Task 2: Architecture Decision
            print("\n\n>>> TASK 2: ARCHITECTURE DECISION <<<")
            workflow.architecture_decision(
                "Should we use async or sync I/O?", ["async/await", "threading", "sync with pools"]
            )

            # Task 3: Refactoring Plan
            print("\n\n>>> TASK 3: REFACTORING PLAN <<<")
            workflow.refactoring_plan("clawspring/tools.py", ["Line too long", "Unused imports"])

            print("\n\n" + "=" * 60)
            print("WORKFLOW COMPLETE")
            print("=" * 60)
            print("\nAMOS Brain demonstrated:")
            print("  - Rule of 2: Dual perspective analysis")
            print("  - Rule of 4: Four-quadrant coverage")
            print("  - L1-L6: Global laws compliance")
            print("  - Actionable recommendations")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
