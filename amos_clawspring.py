#!/usr/bin/env python3
"""
AMOS-ClawSpring: Brain-Enhanced Agent Runtime

This is the main entry point for running ClawSpring with full AMOS brain integration.
It wraps the standard clawspring agent with:
  - AMOS brain initialization
  - Global laws enforcement
  - Rule of 2 / Rule of 4 reasoning
  - Enhanced system prompts
  - Cognitive stack routing

Usage:
  python amos_clawspring.py [options] [prompt]

All standard clawspring options are supported.
"""
from __future__ import annotations

import sys
import os

# Ensure paths are set up
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import AMOS brain
from amos_brain.integration import get_amos_integration

# ClawSpring version reference
CLAWSPRING_VERSION = "3.05.5"
AMOS_VERSION = f"{CLAWSPRING_VERSION}+amos.brain.vInfinity"

# ANSI colors for banner
C = {
    "cyan": "\033[36m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "red": "\033[31m",
    "bold": "\033[1m",
    "reset": "\033[0m",
}


def clr(text: str, *keys: str) -> str:
    return "".join(C[k] for k in keys) + str(text) + C["reset"]


def info(msg: str):
    print(clr(msg, "cyan"))


def ok(msg: str):
    print(clr(msg, "green"))


def warn(msg: str):
    print(clr(f"Warning: {msg}", "yellow"))


def err(msg: str):
    print(clr(f"Error: {msg}", "red"), file=sys.stderr)


def print_amos_banner():
    """Print AMOS brain-enhanced banner."""
    print()
    print(clr("╔══════════════════════════════════════════════════════════╗", "cyan", "bold"))
    print(clr("║         AMOS BRAIN-ENHANCED AGENT RUNTIME                ║", "cyan", "bold"))
    print(clr("║     Unified Biological Intelligence × Cognitive OS       ║", "cyan"))
    print(clr("╠══════════════════════════════════════════════════════════╣", "cyan"))
    print(clr(f"║  Version: {AMOS_VERSION:<45} ║", "green"))
    print(clr("║  Laws: L1-Law | L2-Rule2 | L3-Rule4 | L4-Integrity     ║", "yellow"))
    print(clr("║        L5-Communication | L6-UBI Alignment             ║", "yellow"))
    print(clr("╚══════════════════════════════════════════════════════════╝", "cyan", "bold"))
    print()


def initialize_amos_brain():
    """Initialize AMOS brain and report status."""
    info("Initializing AMOS Brain...")

    try:
        amos = get_amos_integration()
        status = amos.get_status()

        if status['initialized']:
            ok(f"Brain loaded: {status['engines_count']} engines available")
            ok(f"Domains covered: {len(status['domains_covered'])} areas")
            ok(f"Laws active: {', '.join(status['laws_active'])}")
        else:
            warn("Brain initialization incomplete")

        return amos

    except Exception as e:
        err(f"Failed to initialize AMOS brain: {e}")
        return None


def run_clawspring():
    """Run clawspring as subprocess to avoid import issues."""
    import subprocess

    clawspring_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'clawspring', 'clawspring.py'
    )

    # Pass through all command line args except script name
    passthrough = list(sys.argv[1:])
    if "--amos" not in passthrough:
        passthrough.append("--amos")
    args = [sys.executable, clawspring_path] + passthrough

    try:
        result = subprocess.run(args, cwd=os.path.dirname(clawspring_path))
        return result.returncode
    except KeyboardInterrupt:
        return 0
    except Exception as e:
        err(f"Failed to run clawspring: {e}")
        return 1


def main():
    """Main entry point with AMOS brain enhancement."""
    # Print banner
    print_amos_banner()

    # Initialize brain
    amos = initialize_amos_brain()

    if amos:
        info("AMOS reasoning engine active - Rule of 2 and Rule of 4 enabled")

    # Run standard clawspring with brain context
    info("Starting agent runtime...")
    print()

    try:
        exit_code = run_clawspring()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        info("Shutting down AMOS-ClawSpring...")
        sys.exit(0)
    except Exception as e:
        err(f"Runtime error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
