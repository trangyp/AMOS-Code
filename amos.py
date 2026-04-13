#!/usr/bin/env python3
"""AMOS-powered ClawSpring - AI coding assistant with cognitive architecture.

This is the main entry point for running ClawSpring with AMOS Brain integration.
It automatically loads the AMOS cognitive architecture and enhances the agent
with Rule of 2, Rule of 4, Global Laws, and the 7 Intelligences.

Usage:
    python amos.py                    # Start with default settings
    python amos.py --model claude-... # Use specific model
    python amos.py --agent amos       # Use AMOS agent (default)
"""
from __future__ import annotations

import sys
import os

# Ensure clawspring is in path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'clawspring'))

# Import AMOS brain integration
try:
    from amos_brain import get_brain
    from amos_brain.integration import get_amos_integration
    AMOS_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] AMOS brain not available: {e}")
    AMOS_AVAILABLE = False

# Import clawspring components
try:
    import clawspring
    from clawspring.clawspring import main as clawspring_main
    from clawspring.multi_agent.subagent import get_agent_definition
    CLAWSPRING_AVAILABLE = True
except ImportError:
    CLAWSPRING_AVAILABLE = False
    # Fallback: try importing directly
    try:
        from clawspring import main as clawspring_main
        from multi_agent.subagent import get_agent_definition
        CLAWSPRING_AVAILABLE = True
    except ImportError as e:
        print(f"[ERROR] ClawSpring not available: {e}")
        sys.exit(1)


def print_amos_banner():
    """Print AMOS Brain startup banner."""
    print(r"""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   █████╗ ███╗   ███╗ ██████╗ ███████╗                            ║
║  ██╔══██╗████╗ ████║██╔═══██╗██╔════╝                            ║
║  ███████║██╔████╔██║██║   ██║███████╗                            ║
║  ██╔══██║██║╚██╔╝██║██║   ██║╚════██║                            ║
║  ██║  ██║██║ ╚═╝ ██║╚██████╔╝███████║                            ║
║  ╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚══════╝                            ║
║                                                                  ║
║   Artificial Mind Operating System + ClawSpring                  ║
║   Deterministic Cognitive Architecture for AI Coding             ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)

    if AMOS_AVAILABLE:
        try:
            amos = get_amos_integration()
            status = amos.get_status()
            print(f"[AMOS] Brain loaded: {status.get('brain_loaded', False)}")
            print(f"[AMOS] Engines: {status.get('engines_count', 0)}")
            print(f"[AMOS] Laws active: {len(status.get('laws_active', []))}")
            print()
        except Exception as e:
            print(f"[WARNING] Could not initialize AMOS: {e}")
            print()


def main():
    """Run AMOS-powered ClawSpring."""
    print_amos_banner()

    # Set default agent to AMOS if not specified
    if '--agent' not in sys.argv and '-a' not in sys.argv:
        # Check if AMOS agent is available
        amos_def = get_agent_definition('amos')
        if amos_def:
            sys.argv.extend(['--agent', 'amos'])
            print("[AMOS] Using AMOS brain-powered agent")
        else:
            print("[AMOS] Agent definition not found, using default")
    
    # Run clawspring main loop
    try:
        clawspring_main()
    except KeyboardInterrupt:
        print("\n[AMOS] Session terminated by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[AMOS] Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
