"""AMOS Real Learning Engine Demonstration.

This demonstrates:
1. Procedure extraction from successful tasks
2. Pattern detection and classification
3. Automatic procedure reuse
4. Decision recording
5. Failure memory
6. Continuous improvement
"""

import sys
sys.path.insert(0, "/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code")

from amos_brain.real_learning_engine import (
    RealLearningEngine,
    learn_from_task,
    attempt_procedure_reuse,
    get_learning_engine,
)


def demo_learning_engine():
    """Demonstrate Real Learning Engine capabilities."""
    print("=" * 70)
    print("AMOS REAL LEARNING ENGINE - LIVE DEMONSTRATION")
    print("=" * 70)

    # Initialize
    print("\n[1] INITIALIZING LEARNING ENGINE")
    print("-" * 40)
    engine = RealLearningEngine(storage_path="./amos_learning_demo")
    state = engine.get_learning_state()
    print(f"Procedures stored: {state['procedures_stored']}")
    print(f"Patterns stored: {state['patterns_stored']}")
    print(f"Decisions stored: {state['decisions_stored']}")

    # Learn from successful tasks
    print("\n[2] LEARNING FROM SUCCESSFUL TASKS")
    print("-" * 40)

    tasks = [
        {
            "description": "Fix import error for missing module",
            "steps": [
                "Check if module exists in project structure",
                "Add missing __init__.py if needed",
                "Verify import path is correct",
                "Test import to confirm fix",
            ],
            "context": {"error_type": "import", "language": "python"},
        },
        {
            "description": "Optimize slow database query",
            "steps": [
                "Analyze query execution plan",
                "Identify missing indexes",
                "Add appropriate indexes",
                "Verify performance improvement",
            ],
            "context": {"error_type": "performance", "component": "database"},
        },
        {
            "description": "Fix memory leak in data processing",
            "steps": [
                "Profile memory usage",
                "Identify unreleased resources",
                "Add proper cleanup code",
                "Verify memory stays stable",
            ],
            "context": {"error_type": "memory", "component": "processing"},
        },
    ]

    for i, task in enumerate(tasks, 1):
        print(f"\n  Learning task {i}: {task['description']}")
        procedure = learn_from_task(
            task_description=task["description"],
            solution_steps=task["steps"],
            outcome={"success": True, "time_ms": 500},
            execution_time_ms=500,
            context=task["context"],
        )
        if procedure:
            print(f"    ✓ Extracted: {procedure.name}")
            print(f"    ✓ Confidence: {procedure.confidence:.2f}")
            print(f"    ✓ Steps: {len(procedure.execution_steps)}")

    # Show what was learned
    print("\n[3] LEARNING STATE AFTER ACQUISITION")
    print("-" * 40)
    state = engine.get_learning_state()
    print(f"Procedures stored: {state['procedures_stored']}")
    print(f"Patterns stored: {state['patterns_stored']}")
    print(f"Avg confidence: {state['avg_procedure_confidence']:.2f}")

    # Test pattern matching and reuse
    print("\n[4] TESTING PROCEDURE REUSE")
    print("-" * 40)

    similar_tasks = [
        "Fix import error in new module",
        "Optimize database query performance",
        "Fix memory issue in processing pipeline",
    ]

    for task in similar_tasks:
        print(f"\n  Trying to reuse for: {task}")
        result = attempt_procedure_reuse(task, {})
        if result and result.get("reused"):
            print(f"    ✓ REUSED: {result['procedure_name']}")
            print(f"    ✓ Confidence: {result['confidence']:.2f}")
            print(f"    ✓ Bypass analysis: {result['bypass_analysis']}")
        else:
            print(f"    → No match found")

    # Record decisions
    print("\n[5] RECORDING DECISIONS")
    print("-" * 40)

    decisions = [
        {
            "type": "tool_selection",
            "chosen": "edit",
            "rejected": ["manual"],
            "rationale": "Direct edit is faster",
        },
        {
            "type": "approach",
            "chosen": "pattern_reuse",
            "rejected": ["full_analysis"],
            "rationale": "Similar pattern found in memory",
        },
    ]

    for decision in decisions:
        d = engine.record_decision(
            decision_type=decision["type"],
            context={"task": "demo"},
            chosen_option=decision["chosen"],
            rejected_options=decision["rejected"],
            rationale=decision["rationale"],
            outcome={"success": True},
        )
        print(f"  ✓ Recorded: {d.decision_type} -> {d.chosen_option}")

    # Record failures
    print("\n[6] RECORDING FAILURES")
    print("-" * 40)

    engine.record_failure(
        what_was_tried="Manual file editing without tests",
        why_it_failed="Introduced syntax error",
        conditions={"task_type": "edit", "complexity": "high"},
        alternative_procedure=None,
    )
    print(f"  ✓ Failures recorded: {len(engine.failures)}")

    # Final state
    print("\n[7] FINAL LEARNING STATE")
    print("-" * 40)
    state = engine.get_learning_state()
    print(f"Procedures: {state['procedures_stored']}")
    print(f"Patterns: {state['patterns_stored']}")
    print(f"Decisions: {state['decisions_stored']}")
    print(f"Failures: {state['failures_recorded']}")
    print(f"Avg confidence: {state['avg_procedure_confidence']:.2f}")

    print("\n" + "=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)
    print("\nKey Capabilities Demonstrated:")
    print("  ✓ Procedure extraction from successful tasks")
    print("  ✓ Pattern detection and classification")
    print("  ✓ Automatic procedure reuse")
    print("  ✓ Decision recording with rationale")
    print("  ✓ Failure memory to avoid repetition")
    print("  ✓ Minimal storage (no chat logs, no embedding spam)")

    return True


if __name__ == "__main__":
    demo_learning_engine()
