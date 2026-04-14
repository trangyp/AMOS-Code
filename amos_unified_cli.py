#!/usr/bin/env python3
"""AMOS Unified CLI - One command for all AMOS capabilities.

Intelligently routes commands to appropriate AMOS subsystems:
  amos demo          → Run capstone demonstration
  amos cycle         → Execute organism biological cycle
  amos health        → Check subsystem health
  amos self-drive    → Activate autonomous evolution
  amos think "..."   → Use brain reasoning
  amos decide "..."  → Request decision from brain

Usage:
    python amos_unified_cli.py demo
    python amos_unified_cli.py cycle
    python amos_unified_cli.py health --watch
    python amos_unified_cli.py self-drive "Evolve the system"
"""
import sys
import subprocess
from pathlib import Path
from typing import List, Optional

COMMANDS = {
    "demo": {
        "script": "amos_demo.py",
        "desc": "Run 3-layer capstone demonstration",
    },
    "cycle": {
        "script": "amos_organism_cycle.py",
        "desc": "Execute biological circulation cycle",
    },
    "health": {
        "script": "amos_organism_health.py",
        "desc": "Check subsystem health status",
    },
    "self-drive": {
        "script": "amos_activate_self_driving.py",
        "desc": "Activate autonomous evolution",
    },
    "demo-all": {
        "script": "amos_demo_all.py",
        "desc": "Run all demonstrations",
    },
}


def print_banner():
    print("=" * 70)
    print("  🧠 AMOS UNIFIED CLI")
    print("  One Command • All Capabilities")
    print("=" * 70)


def print_help():
    print_banner()
    print("\n  Commands:")
    for cmd, info in COMMANDS.items():
        print(f"    {cmd:<12} → {info['desc']}")
    print("\n  Brain Direct:")
    print("    think <query>    → Brain analysis with Rule of 2/4")
    print("    decide <q> <o1> <o2> ... → Brain decision making")
    print("\n  Usage:")
    print("    python amos_unified_cli.py demo")
    print("    python amos_unified_cli.py health --watch")
    print("    python amos_unified_cli.py think \"Analyze this code\"")
    print("=" * 70)


def run_script(script_name: str, args: List[str]) -> int:
    """Run a demo script with arguments."""
    root = Path(__file__).parent
    script_path = root / script_name
    
    if not script_path.exists():
        print(f"Error: {script_name} not found")
        return 1
    
    cmd = ["python3", str(script_path)] + args
    result = subprocess.run(cmd, cwd=str(root))
    return result.returncode


def brain_think(query: str):
    """Direct brain think command."""
    sys.path.insert(0, str(Path(__file__).parent))
    from amos_brain import get_amos_integration
    
    print_banner()
    print(f"\n  🧠 Brain Thinking: {query[:50]}...")
    
    amos = get_amos_integration()
    result = amos.analyze_with_rules(query)
    
    print(f"\n  Confidence: {result['rule_of_two']['confidence']:.2f}")
    print(f"  Recommendation: {result['rule_of_two']['recommendation']}")
    print("\n  Top Actions:")
    for i, rec in enumerate(result['recommendations'][:3], 1):
        print(f"    {i}. {rec}")


def brain_decide(question: str, options: List[str]):
    """Direct brain decide command."""
    sys.path.insert(0, str(Path(__file__).parent))
    from amos_brain import get_amos_integration
    
    print_banner()
    print(f"\n  ⚖️  Brain Deciding: {question}")
    print(f"  Options: {', '.join(options)}")
    
    amos = get_amos_integration()
    decision = amos.decide(question, options)
    
    print(f"\n  Decision: {decision.get('recommendation', 'Analyze')}")
    print(f"  Confidence: {decision.get('confidence', 0):.2f}")


def main():
    if len(sys.argv) < 2:
        print_help()
        return 0
    
    command = sys.argv[1]
    args = sys.argv[2:]
    
    if command in COMMANDS:
        return run_script(COMMANDS[command]["script"], args)
    
    elif command == "think":
        if not args:
            print("Usage: python amos_unified_cli.py think <query>")
            return 1
        brain_think(" ".join(args))
        return 0
    
    elif command == "decide":
        if len(args) < 2:
            print("Usage: python amos_unified_cli.py decide <question> <option1> <option2> ...")
            return 1
        brain_decide(args[0], args[1:])
        return 0
    
    elif command in ("help", "--help", "-h"):
        print_help()
        return 0
    
    else:
        print(f"Unknown command: {command}")
        print("\nAvailable commands:")
        for cmd in COMMANDS.keys():
            print(f"  {cmd}")
        print("  think, decide, help")
        return 1


if __name__ == "__main__":
    sys.exit(main())
