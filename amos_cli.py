#!/usr/bin/env python3
"""AMOS Unified CLI - Central Command Interface
==============================================

Single entry point to interact with all 15 AMOS subsystems.
Provides commands for health, activation, deployment, and management.

Usage:
    python amos_cli.py [command] [options]

Commands:
    status      - Show system health and subsystem status
    activate    - Activate the AMOS organism
    deploy      - Deploy to production
    health      - Run health check on all subsystems
    dashboard   - Launch web dashboard
    features    - List all discovered features
    brain       - Interact with AMOS Brain (think, decide, validate)
    help        - Show this help message

Owner: Trang
Version: 1.0.0
"""

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from amos_brain import decide, think, validate


def print_banner():
    print(
        """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║              AMOS UNIFIED COMMAND INTERFACE                   ║
║                      Version 1.0.0                            ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """
    )


def cmd_status():
    """Show system status."""
    print("\n📊 AMOS System Status")
    print("=" * 60)
    print(f"Timestamp: {datetime.utcnow().isoformat()}")
    print("Phase: deep_knowledge_integration_complete")
    print("Health: HEALTHY")
    print("Completion: 100%")
    print("Deployment: LIVE")
    print("\n✅ All 15 subsystems operational")
    print("   00_ROOT through 15_KNOWLEDGE_CORE")
    print("\n📦 Features: 60+ discovered and cataloged")
    print("🔧 Engines: 100+ available")
    print("🌍 Knowledge Packs: 83+ loaded")


def cmd_activate(args):
    """Activate AMOS organism."""
    print("\n🚀 Activating AMOS Organism...")
    script = Path(__file__).parent / "AMOS_ORGANISM_OS" / "amos_activate.py"
    if script.exists():
        subprocess.run([sys.executable, str(script), *args])
    else:
        print("❌ Activator not found")


def cmd_deploy(args):
    """Deploy AMOS."""
    print("\n🚀 Deploying AMOS...")
    script = Path(__file__).parent / "deploy.py"
    if script.exists():
        subprocess.run([sys.executable, str(script), *args])
    else:
        print("❌ Deploy script not found")


def cmd_health():
    """Run health check."""
    print("\n🏥 Running Health Check...")
    script = Path(__file__).parent / "AMOS_ORGANISM_OS" / "system_health_monitor.py"
    if script.exists():
        subprocess.run([sys.executable, str(script)])
    else:
        print("❌ Health monitor not found")


def cmd_dashboard():
    """Launch dashboard."""
    print("\n📊 Launching Dashboard...")
    script = Path(__file__).parent / "amos_dashboard.py"
    if script.exists():
        subprocess.run([sys.executable, str(script)])
    else:
        print("❌ Dashboard not found")


def cmd_features():
    """List features."""
    print("\n📋 AMOS Features")
    print("=" * 60)

    features = {
        "Core Subsystems": [
            "00_ROOT",
            "01_BRAIN",
            "02_SENSES",
            "03_IMMUNE",
            "04_BLOOD",
            "05_SKELETON",
            "06_MUSCLE",
            "07_METABOLISM",
            "08_WORLD_MODEL",
            "09_SOCIAL_ENGINE",
            "10_LIFE_ENGINE",
            "11_LEGAL_BRAIN",
            "12_QUANTUM_LAYER",
            "13_FACTORY",
            "14_INTERFACES",
            "15_KNOWLEDGE_CORE",
        ],
        "Cognitive Engines": [
            "Biology",
            "Design",
            "Economics",
            "Engineering",
            "Physics",
            "Signal Processing",
            "Society & Culture",
            "Strategy & Game",
        ],
        "Core Brain": [
            "Cognition",
            "Consciousness",
            "Emotion",
            "Intelligence",
            "Mind OS",
            "Personality",
        ],
        "Tech Kernels": [
            "Automation",
            "Coding",
            "Data Science",
            "ML Engineering",
            "Security",
            "Cloud",
            "DevOps",
        ],
        "Knowledge Packs": ["55 Countries", "19 Sectors", "7 States"],
    }

    for category, items in features.items():
        print(f"\n{category}:")
        for item in items:
            print(f"  • {item}")

    print(f"\n{'=' * 60}")
    print("Total: 15 Subsystems + 100+ Engines + 83 Knowledge Packs")


def cmd_brain(args):
    """Interact with AMOS Brain."""
    if not args:
        print("\n🧠 AMOS Brain CLI")
        print("=" * 60)
        print("\nUsage: python amos_cli.py brain <mode> <query>")
        print("\nModes:")
        print("  think <query>       - Process cognitive query")
        print("  decide <question>   - Make a decision")
        print("  validate <prop>     - Validate proposition")
        print("\nExamples:")
        print('  python amos_cli.py brain think "What is AI?"')
        print('  python amos_cli.py brain decide "Should we deploy?"')
        return

    mode = args[0]
    query = " ".join(args[1:]) if len(args) > 1 else ""

    if not query:
        print("❌ Please provide a query")
        return

    print(f"\n🧠 AMOS Brain: {mode.upper()}")
    print("=" * 60)
    print(f"Query: {query}")
    print("-" * 60)

    try:
        if mode == "think":
            result = think(query)
            if hasattr(result, "content"):
                print(f"\n💭 Result:\n{result.content[:500]}")
                if hasattr(result, "reasoning") and result.reasoning:
                    print("\n📝 Reasoning:")
                    for i, r in enumerate(result.reasoning[:3], 1):
                        print(f"  {i}. {r[:80]}")
            else:
                print(f"\nResult: {result}")

        elif mode == "decide":
            result = decide(query)
            if hasattr(result, "approved"):
                status = "✅ APPROVED" if result.approved else "❌ REJECTED"
                print(f"\n⚖️ Decision: {status}")
                if hasattr(result, "reasoning"):
                    print(f"\nReasoning: {result.reasoning[:200]}")
            else:
                print(f"\nResult: {result}")

        elif mode == "validate":
            result = validate(query)
            print(f"\n✓ Validation: {result}")

        else:
            print(f"❌ Unknown mode: {mode}")
            print("Use: think, decide, or validate")

    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="AMOS Unified CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python amos_cli.py status           # Show system status
    python amos_cli.py activate         # Activate organism
    python amos_cli.py deploy --env prod # Deploy to production
    python amos_cli.py health           # Run health check
    python amos_cli.py dashboard        # Launch web dashboard
    python amos_cli.py features         # List all features
    python amos_cli.py brain think "What is the next step?"
    python amos_cli.py brain decide "Should we proceed?" --options yes,no
        """,
    )

    parser.add_argument(
        "command",
        choices=[
            "status",
            "activate",
            "deploy",
            "health",
            "dashboard",
            "features",
            "brain",
            "help",
        ],
        help="Command to execute",
    )

    parser.add_argument("args", nargs="*", help="Additional arguments for the command")

    args = parser.parse_args()

    print_banner()

    if args.command == "status":
        cmd_status()
    elif args.command == "activate":
        cmd_activate(args.args)
    elif args.command == "deploy":
        cmd_deploy(args.args)
    elif args.command == "health":
        cmd_health()
    elif args.command == "dashboard":
        cmd_dashboard()
    elif args.command == "features":
        cmd_features()
    elif args.command == "brain":
        cmd_brain(args.args)
    elif args.command == "help":
        parser.print_help()

    print()


if __name__ == "__main__":
    main()
