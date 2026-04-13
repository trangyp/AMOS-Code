#!/usr/bin/env python3
"""AMOS Brain CLI - Command line interface to the AMOS cognitive architecture."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from amos_brain import BrainLoader, KernelRouter, SystemPromptBuilder, GlobalLaws


def cmd_info(args):
    """Display AMOS brain information."""
    loader = BrainLoader(args.brain_path)
    loader.load()
    
    print("=" * 60)
    print(f"AMOS BRAIN INFORMATION")
    print("=" * 60)
    print(f"System: {loader.system_name}")
    print(f"Creator: {loader.creator_name}")
    print(f"Kernels loaded: {len(loader.kernels)}")
    print(f"Routing rules: {len(loader.routing_rules)}")
    print(f"Global laws: {len(loader.global_laws)}")
    print()
    
    print("GLOBAL LAWS:")
    for law in loader.global_laws[:6]:
        print(f"  [{law.id}] {law.name}")
        print(f"       {law.description[:70]}...")
    print()
    
    print("REQUIRED KERNELS:")
    for k in loader.get_required_kernels():
        print(f"  - {k.name} ({k.id})")
    print()


def cmd_route(args):
    """Route a task through the kernel system."""
    loader = BrainLoader(args.brain_path)
    loader.load()
    router = KernelRouter(loader)
    
    print("=" * 60)
    print(f"TASK ROUTING ANALYSIS")
    print("=" * 60)
    print(f"Task: {args.task}")
    print()
    
    print(router.explain_routing(args.task))
    print()
    
    # Show full kernel details
    if args.verbose:
        print("KERNEL DETAILS:")
        kernels = router.route(args.task)
        for k in kernels:
            print(f"\n  {k.id}:")
            print(f"    Name: {k.name}")
            print(f"    Domains: {', '.join(k.domains)}")
            print(f"    Modes: {', '.join(k.modes)}")
            if k.dependencies:
                print(f"    Dependencies: {', '.join(k.dependencies)}")


def cmd_prompt(args):
    """Generate system prompt."""
    loader = BrainLoader(args.brain_path)
    loader.load()
    router = KernelRouter(loader)
    builder = SystemPromptBuilder(loader, router)
    
    if args.task:
        prompt = builder.build_task_prompt(args.task)
    elif args.compact:
        prompt = builder.build_compact_prompt()
    else:
        prompt = builder.build_base_prompt()
    
    print(prompt)


def cmd_laws(args):
    """Check text for law violations."""
    laws = GlobalLaws()
    
    if args.file:
        text = open(args.file).read()
    else:
        text = args.text or sys.stdin.read()
    
    violations = laws.check_output(text)
    
    if violations:
        print("LAW VIOLATIONS DETECTED:")
        for v in violations:
            print(f"\n[{v.severity.upper()}] {v.law_id}: {v.law_name}")
            print(f"  Issue: {v.message}")
            print(f"  Suggestion: {v.suggestion}")
    else:
        print("No law violations detected.")
    
    if args.audit:
        # Split by paragraphs for reasoning audit
        steps = [p for p in text.split('\n\n') if p.strip()]
        audit = laws.audit_reasoning(steps)
        if audit:
            print("\nREASONING AUDIT:")
            for v in audit:
                print(f"\n[{v.severity.upper()}] {v.law_id}: {v.law_name}")
                print(f"  {v.message}")


def cmd_kernels(args):
    """List all available kernels."""
    loader = BrainLoader(args.brain_path)
    loader.load()
    
    print("=" * 60)
    print("AMOS KERNEL REGISTRY")
    print("=" * 60)
    
    # Group by priority
    by_priority = {}
    for k in loader.kernels:
        p = k.priority
        if p not in by_priority:
            by_priority[p] = []
        by_priority[p].append(k)
    
    for priority in sorted(by_priority.keys(), reverse=True):
        print(f"\nPriority {priority}:")
        for k in by_priority[priority]:
            req = " [R]" if k.required else ""
            print(f"  - {k.id}: {k.name}{req}")
            if args.verbose:
                print(f"    Domains: {', '.join(k.domains)}")
                print(f"    Modes: {', '.join(k.modes)}")


def main():
    parser = argparse.ArgumentParser(
        description="AMOS Brain CLI - Cognitive architecture interface"
    )
    parser.add_argument(
        "--brain-path",
        type=Path,
        default=None,
        help="Path to AMOS brain directory"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # info command
    subparsers.add_parser("info", help="Show brain information")
    
    # route command
    route_parser = subparsers.add_parser("route", help="Route a task")
    route_parser.add_argument("task", help="Task description")
    route_parser.add_argument("-v", "--verbose", action="store_true")
    
    # prompt command
    prompt_parser = subparsers.add_parser("prompt", help="Generate system prompt")
    prompt_parser.add_argument("--task", help="Task for context-aware prompt")
    prompt_parser.add_argument("--compact", action="store_true", help="Compact version")
    
    # laws command
    laws_parser = subparsers.add_parser("laws", help="Check text for law violations")
    laws_parser.add_argument("--text", help="Text to check")
    laws_parser.add_argument("--file", help="File to check")
    laws_parser.add_argument("--audit", action="store_true", help="Audit reasoning")
    
    # kernels command
    kernels_parser = subparsers.add_parser("kernels", help="List kernels")
    kernels_parser.add_argument("-v", "--verbose", action="store_true")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    commands = {
        "info": cmd_info,
        "route": cmd_route,
        "prompt": cmd_prompt,
        "laws": cmd_laws,
        "kernels": cmd_kernels,
    }
    
    try:
        commands[args.command](args)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
