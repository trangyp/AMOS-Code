#!/usr/bin/env python3
"""
AMOS Brain Launcher - Unified menu for all brain features.

Discover and launch all AMOS Brain components from one place:
  - Tutorial: Learn brain features interactively
  - CLI: Daily brain command interface
  - Tests: Run integration test suite
  - Demos: See cookbook workflows in action
  - Dashboard: View analytics (no CLI needed)
  - Docs: Open usage guide

Usage:
    python amos_brain_launcher.py
"""
from __future__ import annotations

import sys
import os
import subprocess

# Setup paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from amos_brain import get_amos_integration
from amos_brain.dashboard import print_dashboard


# ANSI colors
C = {
    "cyan": "\033[36m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "red": "\033[31m",
    "magenta": "\033[35m",
    "bold": "\033[1m",
    "reset": "\033[0m",
}


def clr(text: str, *keys: str) -> str:
    return "".join(C[k] for k in keys) + str(text) + C["reset"]


def print_banner():
    """Print launcher banner."""
    print()
    print(clr("╔══════════════════════════════════════════════════════════╗", "cyan", "bold"))
    print(clr("║              AMOS BRAIN LAUNCHER                         ║", "cyan", "bold"))
    print(clr("║     Unified Interface for All Brain Features             ║", "cyan"))
    print(clr("╚══════════════════════════════════════════════════════════╝", "cyan", "bold"))
    print()


def print_menu():
    """Print main menu."""
    print(clr("Available Features:", "bold"))
    print()
    print(f"  {clr('1', 'cyan', 'bold')}. {clr('Tutorial', 'green')}     - Learn brain features interactively")
    print(f"  {clr('2', 'cyan', 'bold')}. {clr('CLI', 'green')}          - Brain command interface (/decide, /analyze)")
    print(f"  {clr('3', 'cyan', 'bold')}. {clr('Tests', 'green')}        - Run integration test suite (32 tests)")
    print(f"  {clr('4', 'cyan', 'bold')}. {clr('Cookbook', 'green')}     - Demo workflow examples")
    print(f"  {clr('5', 'cyan', 'bold')}. {clr('Dashboard', 'green')}    - View reasoning analytics")
    print(f"  {clr('6', 'cyan', 'bold')}. {clr('Status', 'green')}       - Show brain status")
    print(f"  {clr('7', 'cyan', 'bold')}. {clr('Guide', 'yellow')}       - Open usage guide")
    print(f"  {clr('0', 'red', 'bold')}. {clr('Exit', 'red')}         - Quit launcher")
    print()


def run_tutorial():
    """Launch interactive tutorial."""
    print(clr("\n[Launching Tutorial...]", "cyan"))
    print()
    subprocess.run([sys.executable, "amos_brain_tutorial.py"])
    print()
    input(clr("[Press Enter to return to menu...]", "yellow"))


def run_cli():
    """Launch brain CLI."""
    print(clr("\n[Launching AMOS interactive shell...]", "cyan"))
    print()
    subprocess.run([sys.executable, os.path.join("clawspring", "clawspring.py"), "--amos"])
    print()
    input(clr("[Press Enter to return to menu...]", "yellow"))


def run_tests():
    """Run integration tests."""
    print(clr("\n[Running Integration Tests...]", "cyan"))
    print()
    result = subprocess.run([sys.executable, "-m", "pytest", "tests/test_amos_brain.py", "-v"])
    print()

    if result.returncode == 0:
        print(clr("✓ All tests passed!", "green"))
    else:
        print(clr("✗ Some tests failed", "red"))

    print()
    input(clr("[Press Enter to return to menu...]", "yellow"))


def run_cookbook_demo():
    """Launch cookbook workflow demos."""
    print(clr("\n[Launching Cookbook Demos...]", "cyan"))
    print()
    subprocess.run([sys.executable, "demo_cookbook.py"])
    print()
    input(clr("[Press Enter to return to menu...]", "yellow"))


def run_dashboard():
    """Show dashboard analytics."""
    print(clr("\n[Generating Dashboard...]", "cyan"))
    print()
    print_dashboard(days=30)
    print()
    input(clr("[Press Enter to return to menu...]", "yellow"))


def show_status():
    """Show brain status."""
    print(clr("\n[Loading Brain Status...]", "cyan"))
    print()

    amos = get_amos_integration()
    status = amos.get_status()

    print(clr("┌─ AMOS Brain Status ─", "bold"))
    print(f"│ Initialized: {status.get('initialized', False)}")
    print(f"│ Brain Loaded: {status.get('brain_loaded', False)}")
    print(f"│ Engines: {status.get('engines_count', 0)} domain engines")
    print(f"│ Laws: {len(status.get('laws_active', []))} global laws active")
    print(f"│ Domains: {len(status.get('domains_covered', []))} areas covered")
    print(clr("└─────────────────────", "bold"))

    # Show laws
    print()
    print(clr("Active Laws:", "bold"))
    for law in status.get('laws_active', []):
        print(f"  • {law}")

    # Show domains
    print()
    print(clr("Covered Domains:", "bold"))
    for domain in status.get('domains_covered', [])[:6]:
        print(f"  • {domain}")
    if len(status.get('domains_covered', [])) > 6:
        print(f"  ... and {len(status.get('domains_covered', [])) - 6} more")

    print()
    input(clr("[Press Enter to return to menu...]", "yellow"))


def open_guide():
    """Open usage guide."""
    guide_path = "AMOS_BRAIN_GUIDE.md"

    if os.path.exists(guide_path):
        print(clr(f"\n[Opening {guide_path}...]", "cyan"))

        # Try to open with different methods
        try:
            if sys.platform == "darwin":  # macOS
                subprocess.run(["open", guide_path])
            elif sys.platform == "linux":
                subprocess.run(["xdg-open", guide_path])
            else:  # Windows or fallback
                print(f"Guide location: {os.path.abspath(guide_path)}")
                print("Please open manually in your preferred editor.")
        except Exception as e:
            print(f"Could not auto-open: {e}")
            print(f"Guide location: {os.path.abspath(guide_path)}")
    else:
        print(clr(f"\nGuide not found at {guide_path}", "red"))

    print()
    input(clr("[Press Enter to return to menu...]", "yellow"))


def main():
    """Main launcher loop."""
    print_banner()

    # Initialize brain
    print("Initializing AMOS Brain...")
    amos = get_amos_integration()
    status = amos.get_status()

    if status.get('initialized'):
        print(clr("✓ Brain ready", "green"))
        print(
            f"  {status.get('engines_count', 0)} engines | "
            f"{len(status.get('laws_active', []))} laws | "
            f"{len(status.get('domains_covered', []))} domains"
        )
    else:
        print(clr("✗ Brain initialization failed", "red"))
        return 1

    print()

    # Menu loop
    while True:
        print_menu()

        try:
            choice = input(clr("Select option (0-7): ", "cyan", "bold")).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if choice == "0":
            print()
            print(clr("Exiting AMOS Brain Launcher...", "cyan"))
            break
        elif choice == "1":
            run_tutorial()
        elif choice == "2":
            run_cli()
        elif choice == "3":
            run_tests()
        elif choice == "4":
            run_cookbook_demo()
        elif choice == "5":
            run_dashboard()
        elif choice == "6":
            show_status()
        elif choice == "7":
            open_guide()
        else:
            print()
            print(clr("Invalid option. Please select 0-7.", "red"))
            print()

    print()
    print(clr("AMOS Brain Launcher terminated.", "cyan"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
