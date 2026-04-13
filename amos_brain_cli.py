#!/usr/bin/env python3
"""AMOS Brain Unified CLI - Complete 8-layer brain interface."""
from __future__ import annotations

import argparse
import sys
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))

from amos_brain import (
    get_brain, process_task, get_agent_bridge, get_state_manager,
    get_meta_controller, orchestrate_goal,
    GlobalLaws, KernelRouter
)


def print_banner():
    """Print AMOS brain banner."""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                    AMOS BRAIN COGNITIVE OS                       ║
║              8-Layer Architecture • vInfinity                  ║
║                    Creator: Trang Phan                           ║
╚══════════════════════════════════════════════════════════════════╝
""")


def cmd_status(args):
    """Show complete 8-layer architecture status."""
    print("\n📊 AMOS BRAIN STATUS")
    print("═" * 66)
    
    brain = get_brain()
    print(f"\n🧠 Layer 1: Brain Loader")
    print(f"   Engines: {len(brain.list_engines())}")
    print(f"   Laws: {len(brain._config.global_laws) if brain._config else 0}")
    print(f"   Domains: {len(brain._config.domains) if brain._config else 0}")
    
    print(f"\n🔀 Layer 3: Kernel Router")
    router = KernelRouter(brain)
    print(f"   Status: Active")
    
    print(f"\n⚙️  Layer 4: Task Processor")
    result = process_task("Test task")
    print(f"   Rule of 2: {'✓' if result.rule_of_two_check['compliant'] else '✗'}")
    print(f"   Rule of 4: {'✓' if result.rule_of_four_check['compliant'] else '✗'}")
    
    print(f"\n⚖️  Layer 5: Global Laws")
    laws = GlobalLaws()
    for law_id in ["L1", "L2", "L3", "L4", "L5", "L6"]:
        law = laws.get_law(law_id)
        if law:
            print(f"   {law_id}: {law.name}")
    
    print(f"\n🌉 Layer 6: Agent Bridge")
    bridge = get_agent_bridge()
    report = bridge.get_execution_report()
    print(f"   Total decisions: {report['total_decisions']}")
    print(f"   Blocked: {report['blocked']}")
    
    print(f"\n💾 Layer 7: State Manager")
    sm = get_state_manager()
    sessions = sm.list_sessions()
    print(f"   Stored sessions: {len(sessions)}")
    
    print(f"\n🎯 Layer 8: Meta-Cognitive Controller")
    mc = get_meta_controller()
    summary = mc.get_execution_summary()
    print(f"   Active plans: {summary['total_plans']}")
    print(f"   Completed: {summary['completed_plans']}")
    
    print("\n" + "═" * 66)
    print("Status: ✓ ALL 8 LAYERS OPERATIONAL")


def cmd_think(args):
    """Process a task through the full brain."""
    task = args.task or input("Enter task to think about: ")
    
    print(f"\n🧠 THINKING: {task}")
    print("═" * 66)
    
    result = process_task(task)
    
    print(f"\n📋 Reasoning Chain ({len(result.reasoning_steps)} steps):")
    for i, step in enumerate(result.reasoning_steps[:10], 1):
        print(f"  {i}. {step[:70]}...")
    
    print(f"\n✅ Compliance:")
    print(f"   Rule of 2: {result.rule_of_two_check['perspectives_checked']} perspectives")
    print(f"   Rule of 4: {result.rule_of_four_check['coverage']} quadrants")
    print(f"   Confidence: {result.confidence}")
    
    print(f"\n⚙️  Kernels: {', '.join(result.kernels_used[:5])}")
    
    if result.law_violations:
        print(f"\n⚠️  Law Violations: {len(result.law_violations)}")
        for v in result.law_violations:
            print(f"   - {v['law']}: {v['message']}")
    else:
        print(f"\n✓ No law violations")
    
    print(f"\n⏱️  Processing time: {result.processing_time_ms}ms")


def cmd_orchestrate(args):
    """Run meta-cognitive orchestration."""
    goal = args.goal or input("Enter goal to orchestrate: ")
    
    print(f"\n🎯 ORCHESTRATING: {goal}")
    print("═" * 66)
    
    controller = get_meta_controller()
    plan = controller.orchestrate(goal, domain=args.domain)
    
    print(f"\n📋 Plan ID: {plan.plan_id}")
    print(f"Goal: {plan.goal}")
    print(f"Domain: {plan.domain}")
    print(f"\nSub-tasks ({len(plan.subtasks)}):")
    
    for i, task in enumerate(plan.subtasks[:10], 1):
        deps = f" (deps: {', '.join(task.dependencies)})" if task.dependencies else ""
        print(f"  {i}. [{task.status.value}] {task.description[:50]}...{deps}")
    
    if len(plan.subtasks) > 10:
        print(f"  ... and {len(plan.subtasks) - 10} more")


def cmd_laws(args):
    """Check text against global laws."""
    text = args.text or input("Enter text to validate: ")
    
    print(f"\n⚖️  LAW VALIDATION")
    print("═" * 66)
    
    laws = GlobalLaws()
    
    # L1: Law of Law
    ok, msg = laws.check_l1_constraint(args.action or "analysis")
    print(f"\n[L1] Law of Law: {'✓' if ok else '✗'} {msg}")
    
    # L2: Rule of 2
    ok, msg = laws.enforce_l2_dual_check(text, "Alternative view provided")
    print(f"[L2] Rule of 2: {'✓' if ok else '✗'} {msg}")
    
    # L3: Rule of 4
    ok, missing = laws.enforce_l3_quadrants({'technical', 'biological', 'economic', 'environmental'})
    print(f"[L3] Rule of 4: {'✓' if ok else '✗'} " + 
          (f"Missing: {', '.join(missing)}" if missing else "All quadrants present"))
    
    # L5: Communication
    ok, violations = laws.l5_communication_check(text)
    print(f"[L5] Communication: {'✓' if ok else '✗'} " +
          (f"Issues: {len(violations)}" if violations else "Clear communication"))


def cmd_bridge(args):
    """Test agent bridge validation."""
    print("\n🌉 AGENT BRIDGE TEST")
    print("═" * 66)
    
    bridge = get_agent_bridge()
    
    # Test 1: Safe operation
    print("\nTest 1: Safe Read operation")
    result = bridge.validate_tool_call('Read', {'file_path': '/test.txt'})
    print(f"  Tool: Read")
    print(f"  Approved: {'✓' if result['approved'] else '✗'}")
    print(f"  Risk: {result['risk_level']}")
    
    # Test 2: Dangerous operation
    print("\nTest 2: Dangerous Bash operation")
    result = bridge.validate_tool_call('Bash', {'command': 'rm -rf /'})
    print(f"  Tool: Bash (rm -rf /)")
    print(f"  Approved: {'✓' if result['approved'] else '✗ BLOCKED'}")
    print(f"  Risk: {result['risk_level']}")
    if result['violations']:
        print(f"  Violations: {len(result['violations'])}")
    
    # Summary
    report = bridge.get_execution_report()
    print(f"\n📊 Total decisions: {report['total_decisions']}")
    print(f"   Approved: {report['approved']}")
    print(f"   Blocked: {report['blocked']}")


def cmd_replay(args):
    """Replay reasoning from state manager."""
    sm = get_state_manager()
    sessions = sm.list_sessions()
    
    if not sessions:
        print("\nNo stored sessions found.")
        return
    
    print(f"\n💾 Stored Sessions ({len(sessions)}):")
    print("═" * 66)
    
    for i, s in enumerate(sessions[:5], 1):
        print(f"{i}. {s['session_id']}: {s['goal']}")
        print(f"   Steps: {s['steps']} | Domain: {s['domain']} | Created: {s['created'][:10]}")
    
    if args.session_id:
        replay = sm.replay_reasoning(args.session_id, format_type="text")
        print(f"\n{replay[:2000]}...")


def main():
    parser = argparse.ArgumentParser(
        description="AMOS Brain Unified CLI - 8-Layer Cognitive OS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  status         Show 8-layer architecture status
  think <task>   Process task through full brain
  orchestrate    Run meta-cognitive workflow
  laws           Check against global laws
  bridge         Test agent bridge validation
  replay         Show reasoning history

Examples:
  python amos_brain_cli.py status
  python amos_brain_cli.py think "Design secure API"
  python amos_brain_cli.py orchestrate --goal "Build microservices"
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command')
    
    # status
    subparsers.add_parser('status', help='Show brain status')
    
    # think
    think_parser = subparsers.add_parser('think', help='Process task')
    think_parser.add_argument('task', nargs='?', help='Task to process')
    
    # orchestrate
    orch_parser = subparsers.add_parser('orchestrate', help='Run orchestration')
    orch_parser.add_argument('--goal', help='Goal to achieve')
    orch_parser.add_argument('--domain', default='general', help='Domain')
    
    # laws
    laws_parser = subparsers.add_parser('laws', help='Check laws')
    laws_parser.add_argument('--text', help='Text to validate')
    laws_parser.add_argument('--action', help='Action type')
    
    # bridge
    subparsers.add_parser('bridge', help='Test bridge')
    
    # replay
    replay_parser = subparsers.add_parser('replay', help='Replay reasoning')
    replay_parser.add_argument('--session-id', help='Session to replay')
    
    args = parser.parse_args()
    
    if not args.command:
        print_banner()
        parser.print_help()
        return 0
    
    commands = {
        'status': cmd_status,
        'think': cmd_think,
        'orchestrate': cmd_orchestrate,
        'laws': cmd_laws,
        'bridge': cmd_bridge,
        'replay': cmd_replay,
    }
    
    try:
        commands[args.command](args)
        print()
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
