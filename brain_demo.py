#!/usr/bin/env python3
"""AMOS Brain Demonstration
Shows how to use the AMOS cognitive architecture.
"""

import sys

sys.path.insert(0, "clawspring")

from amos_brain import (
    get_agent_bridge,
    get_amos_integration,
    get_meta_controller,
    get_state_manager,
)


def demo_brain_thinking():
    """Demonstrate brain cognition."""
    print("\n" + "=" * 60)
    print("🧠 AMOS BRAIN: COGNITIVE DEMONSTRATION")
    print("=" * 60)

    # Get brain integration
    amos = get_amos_integration()
    status = amos.get_status()

    print("\n✓ Brain Status:")
    print(f"  - Initialized: {status['initialized']}")
    print(f"  - Brain Loaded: {status['brain_loaded']}")
    print(f"  - Engines: {status['engines_count']}")
    print(f"  - Laws Active: {len(status['laws_active'])}")

    # Pre-process a thought
    print("\n💭 Thinking: 'How should I approach this problem?'")
    result = amos.pre_process(
        "How should I approach this problem?",
        context={"domain": "software_design", "complexity": "high"},
    )
    print(f"  ✓ Processed: {result.get('thought_id', 'N/A')}")

    return amos


def demo_agent_bridge():
    """Demonstrate agent bridge."""
    print("\n" + "=" * 60)
    print("🤖 AMOS AGENT BRIDGE")
    print("=" * 60)

    bridge = get_agent_bridge()

    # Simulate a tool decision
    print("\n📋 Tool Decision:")
    print("  Query: 'execute shell command'")
    decision = bridge.decide_tool_use("execute shell command")
    print(f"  ✓ Decision: {decision.action}")
    print(f"  ✓ Reason: {decision.reason}")

    return bridge


def demo_meta_controller():
    """Demonstrate meta-cognitive control."""
    print("\n" + "=" * 60)
    print("🎯 AMOS META-CONTROLLER")
    print("=" * 60)

    controller = get_meta_controller()

    # Orchestrate a goal
    print("\n🎬 Orchestrating Goal: 'Build a feature'")
    plan = controller.orchestrate_goal("Build a feature")

    print(f"  ✓ Plan ID: {plan.plan_id}")
    print(f"  ✓ Steps: {len(plan.steps)}")
    for i, step in enumerate(plan.steps[:3], 1):
        print(f"    {i}. {step.get('action', 'Unknown')}")

    return controller


def demo_state_management():
    """Demonstrate state management."""
    print("\n" + "=" * 60)
    print("💾 AMOS STATE MANAGER")
    print("=" * 60)

    manager = get_state_manager()

    # Create a session
    print("\n📝 Creating Workflow Session")
    session = manager.create_session("demo_workflow")
    print(f"  ✓ Session ID: {session.session_id}")

    # Add reasoning step
    step = manager.add_reasoning_step(
        session.session_id, "analysis", "Analyzed the requirements", confidence=0.85
    )
    print(f"  ✓ Step added: {step.step_id}")

    return manager


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 60)
    print("🚀 AMOS COGNITIVE SYSTEM DEMO")
    print("=" * 60)
    print("\nInitializing AMOS Brain...")

    try:
        # Run demonstrations
        amos = demo_brain_thinking()
        bridge = demo_agent_bridge()
        controller = demo_meta_controller()
        manager = demo_state_management()

        # Summary
        print("\n" + "=" * 60)
        print("✅ ALL DEMONSTRATIONS COMPLETE")
        print("=" * 60)
        print("\nAMOS Brain Capabilities Demonstrated:")
        print("  ✓ Cognitive Processing (thinking, perception)")
        print("  ✓ Agent Bridge (tool decisions, execution)")
        print("  ✓ Meta-Controller (goal orchestration)")
        print("  ✓ State Management (sessions, reasoning)")
        print("\nThe AMOS brain is operational and ready to use!")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
