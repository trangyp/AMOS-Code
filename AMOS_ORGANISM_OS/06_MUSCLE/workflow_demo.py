#!/usr/bin/env python3
"""
Workflow Engine Demo with Handlers
=====================================

Demonstrates workflow execution with registered action handlers.

Owner: Trang
Version: 1.0.0
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from workflow_engine import WorkflowEngine, Workflow, StepStatus


def demo_analyze(params: dict, context: dict) -> dict:
    """Demo analyze action handler."""
    print(f"  [ANALYZE] Analyzing target: {params.get('target', 'unknown')}")
    return {"status": "analyzed", "issues_found": 0}


def demo_transform(params: dict, context: dict) -> dict:
    """Demo transform action handler."""
    print(f"  [TRANSFORM] Transforming type: {params.get('type', 'unknown')}")
    return {"status": "transformed", "changes": 3}


def demo_validate(params: dict, context: dict) -> dict:
    """Demo validate action handler."""
    print("  [VALIDATE] Running validation checks")
    return {"status": "valid", "errors": 0}


def demo_generate(params: dict, context: dict) -> dict:
    """Demo generate action handler."""
    print("  [GENERATE] Generating output")
    return {"status": "generated", "files": 1}


def main():
    """Run workflow demo."""
    print("=" * 50)
    print("AMOS Workflow Engine Demo")
    print("=" * 50)

    # Create engine and register handlers
    engine = WorkflowEngine()
    engine.register_handler("analyze", demo_analyze)
    engine.register_handler("transform", demo_transform)
    engine.register_handler("validate", demo_validate)
    engine.register_handler("generate", demo_generate)

    # Create a sample workflow
    print("\n1. Creating workflow...")
    workflow = engine.create_workflow(
        "Code Quality Workflow",
        "Analyze, transform, and validate code"
    )

    # Add steps with dependencies
    step1 = workflow.add_step("Analyze Code", "analyze", {"target": "python"})
    step2 = workflow.add_step("Auto-fix Issues", "transform", {"type": "refactor"}, depends_on=[step1.id])
    step3 = workflow.add_step("Validate Changes", "validate", {}, depends_on=[step2.id])
    step4 = workflow.add_step("Generate Report", "generate", {}, depends_on=[step3.id])

    print(f"   Created: {workflow.id}")
    print(f"   Steps: {len(workflow.steps)}")

    # Run workflow
    print("\n2. Running workflow...")
    result = engine.run_workflow(workflow.id)

    # Show results
    print("\n3. Results:")
    print(f"   Status: {result.status}")
    print(f"   Steps completed:")
    for step in result.steps:
        icon = "✓" if step.status == StepStatus.SUCCESS else "✗" if step.status == StepStatus.FAILED else "○"
        print(f"     {icon} {step.name}: {step.status.value}")
        if step.result:
            print(f"       Result: {step.result}")

    # Save workflow
    engine._save_workflow(result)

    print("\n" + "=" * 50)
    print("Demo complete! Workflow saved.")
    print("=" * 50)

    return 0


if __name__ == "__main__":
    sys.exit(main())
