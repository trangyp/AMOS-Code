#!/usr/bin/env python3
"""AMOS Brain Demonstration CLI - Showcase cognitive capabilities."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime

from amos_brain import (
    get_brain,
    process_task,
    KernelRouter,
    GlobalLaws,
    RuleOfTwo,
    RuleOfFour,
    BrainTaskProcessor,
)


def show_banner():
    """Display AMOS brain banner."""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                    AMOS BRAIN COGNITIVE CORE                     ║
║           Deterministic Reasoning • Global Laws • UBI           ║
║                   Creator: Trang Phan | vInfinity               ║
╚══════════════════════════════════════════════════════════════════╝
""")


def cmd_status(args):
    """Show brain status and configuration."""
    brain = get_brain()
    laws = GlobalLaws()
    
    print("\n📊 BRAIN STATUS")
    print("─" * 60)
    print(f"System: {brain._config.name if brain._config else 'Unknown'}")
    print(f"Version: {brain._config.version if brain._config else 'Unknown'}")
    print(f"Engines Available: {len(brain.list_engines())}")
    print(f"Global Laws: {len(brain._config.global_laws) if brain._config else 0}")
    print(f"Domains: {len(brain._config.domains) if brain._config else 0}")
    
    if args.verbose:
        print("\n🔧 Available Engines:")
        for engine in brain.list_engines()[:10]:
            print(f"  • {engine}")
        if len(brain.list_engines()) > 10:
            print(f"  ... and {len(brain.list_engines()) - 10} more")
    
    print("\n⚖️  Global Laws:")
    for law_id in sorted(laws.LAWS.keys()):
        law = laws.LAWS[law_id]
        print(f"  [{law_id}] {law.name}")
        if args.verbose:
            print(f"       {law.description[:60]}...")


def cmd_process(args):
    """Process a task through the AMOS brain."""
    task = args.task or input("Enter task to process: ")
    
    print(f"\n🧠 PROCESSING TASK")
    print("─" * 60)
    print(f"Task: {task}")
    print()
    
    # Process through brain
    result = process_task(task)
    
    # Display routing info
    router = KernelRouter(get_brain())
    print(router.explain_routing(task))
    print()
    
    # Display compliance
    print("✅ COMPLIANCE CHECKS")
    print("─" * 60)
    
    # Rule of 2
    ro2 = result.rule_of_two_check
    print(f"Rule of 2 (Dual Perspective):")
    print(f"  Perspectives: {ro2['perspectives_checked']}/2")
    print(f"  Views: {', '.join(ro2['perspectives'])}")
    print(f"  Status: {'✓ COMPLIANT' if ro2['compliant'] else '✗ NON-COMPLIANT'}")
    print()
    
    # Rule of 4
    ro4 = result.rule_of_four_check
    print(f"Rule of 4 (Quadrant Analysis):")
    print(f"  Quadrants: {ro4['coverage']}/4")
    print(f"  Checked: {', '.join(ro4['quadrants_checked'])}")
    print(f"  Status: {'✓ COMPLIANT' if ro4['compliant'] else '✗ NON-COMPLIANT'}")
    print()
    
    # Output
    print("📋 OUTPUT")
    print("─" * 60)
    print(result.output)
    print()
    
    print(f"⏱️  Processing Time: {result.processing_time_ms}ms")
    print(f"🎯 Confidence: {result.confidence.upper()}")
    
    # Save if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump({
                'task': task,
                'result': {
                    'task_id': result.task_id,
                    'output': result.output,
                    'reasoning_steps': result.reasoning_steps,
                    'kernels_used': result.kernels_used,
                    'rule_of_two': result.rule_of_two_check,
                    'rule_of_four': result.rule_of_four_check,
                    'confidence': result.confidence,
                    'processing_time_ms': result.processing_time_ms,
                }
            }, f, indent=2)
        print(f"\n💾 Saved to: {args.output}")


def cmd_demo(args):
    """Run a demonstration of brain capabilities."""
    demo_tasks = [
        "Design a secure authentication system",
        "Analyze the trade-offs of microservices vs monoliths",
        "Plan a sustainable data architecture",
        "Evaluate ethical implications of AI recommendations",
    ]
    
    print("\n🎬 AMOS BRAIN DEMONSTRATION")
    print("=" * 60)
    
    processor = BrainTaskProcessor()
    
    for i, task in enumerate(demo_tasks, 1):
        print(f"\n{'─' * 60}")
        print(f"Demo {i}/{len(demo_tasks)}: {task}")
        print('─' * 60)
        
        result = processor.process(task)
        
        print(f"Kernels: {', '.join(result.kernels_used[:2])}")
        print(f"Rule of 2: {'✓' if result.rule_of_two_check['compliant'] else '✗'} " +
              f"({result.rule_of_two_check['perspectives_checked']} perspectives)")
        print(f"Rule of 4: {'✓' if result.rule_of_four_check['compliant'] else '✗'} " +
              f"({result.rule_of_four_check['coverage']} quadrants)")
        print(f"Confidence: {result.confidence}")
        
        if args.verbose:
            print("\nOutput preview:")
            lines = result.output.split('\n')[:8]
            for line in lines:
                print(f"  {line}")
            print("  ...")


def cmd_laws(args):
    """Check text against AMOS global laws."""
    text = args.text or input("Enter text to validate: ")
    
    print("\n⚖️  LAW VALIDATION")
    print("─" * 60)
    
    laws = GlobalLaws()
    
    # Check each law
    print("Checking against Global Laws...")
    print()
    
    # L1: Law of Law
    ok, msg = laws.check_l1_constraint(args.action if args.action else "analysis")
    print(f"[L1] Law of Law: {'✓' if ok else '✗'} {msg}")
    
    # L2: Rule of 2
    ok, msg = laws.enforce_l2_dual_check(text, args.counter or "Alternative view: None provided")
    print(f"[L2] Rule of 2: {'✓' if ok else '✗'} {msg}")
    
    # L3: Rule of 4
    quadrants = {'technical', 'biological', 'economic', 'environmental'}
    if args.quadrants:
        quadrants = set(args.quadrants.split(','))
    ok, missing = laws.enforce_l3_quadrants(quadrants)
    print(f"[L3] Rule of 4: {'✓' if ok else '✗'} " +
          (f"Missing: {', '.join(missing)}" if missing else "All quadrants present"))
    
    # L4: Structural Integrity
    statements = [s.strip() for s in text.split('.') if s.strip()]
    ok, contradictions = laws.check_l4_integrity(statements)
    print(f"[L4] Structural Integrity: {'✓' if ok else '✗'} " +
          (f"Contradictions found: {len(contradictions)}" if contradictions else "No contradictions"))
    
    # L5: Communication
    ok, violations = laws.l5_communication_check(text)
    print(f"[L5] Communication: {'✓' if ok else '✗'} " +
          (f"Issues: {', '.join(violations[:3])}" if violations else "Clear communication"))


def main():
    parser = argparse.ArgumentParser(
        description="AMOS Brain Demonstration CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s status                    # Show brain status
  %(prog)s process "Design API"      # Process a task
  %(prog)s demo                      # Run demonstration
  %(prog)s laws --text "statement"   # Check against laws
        """
    )
    
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    
    subparsers = parser.add_subparsers(dest='command', help='Command')
    
    # status
    status_parser = subparsers.add_parser('status', help='Show brain status')
    
    # process
    process_parser = subparsers.add_parser('process', help='Process a task')
    process_parser.add_argument('task', nargs='?', help='Task to process')
    process_parser.add_argument('-o', '--output', help='Save result to JSON file')
    
    # demo
    demo_parser = subparsers.add_parser('demo', help='Run demonstration')
    
    # laws
    laws_parser = subparsers.add_parser('laws', help='Check against global laws')
    laws_parser.add_argument('--text', help='Text to validate')
    laws_parser.add_argument('--action', help='Action type for L1 check')
    laws_parser.add_argument('--counter', help='Counter-perspective for L2')
    laws_parser.add_argument('--quadrants', help='Comma-separated quadrants for L3')
    
    args = parser.parse_args()
    
    show_banner()
    
    if not args.command:
        parser.print_help()
        return 1
    
    commands = {
        'status': cmd_status,
        'process': cmd_process,
        'demo': cmd_demo,
        'laws': cmd_laws,
    }
    
    try:
        commands[args.command](args)
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
