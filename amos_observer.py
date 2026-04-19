#!/usr/bin/env python3
"""AMOS Brain Observer
====================
Real-time visualization of AMOS cognitive processes.

Usage:
    python amos_observer.py [command]

Commands:
    status      Show current brain status
    engines     List active cognitive engines
    laws        Check global laws compliance
    trace       Trace a thought process
    dashboard   Run interactive dashboard
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Add paths
sys.path.insert(0, str(Path(__file__).parent / "clawspring"))
sys.path.insert(0, str(Path(__file__).parent))


class AMOSObserver:
    """Observe and visualize AMOS Brain activity."""

    def __init__(self):
        self.brain = None
        self.integration = None

    def _load_brain(self):
        """Lazy load brain components."""
        if self.integration is None:
            from amos_brain import get_amos_integration

            self.integration = get_amos_integration()
        return self.integration

    def show_status(self) -> Dict[str, Any]:
        """Show comprehensive brain status."""
        integration = self._load_brain()
        status = integration.get_status()

        print("=" * 60)
        print("AMOS BRAIN STATUS")
        print("=" * 60)
        print(f"Initialized: {'Yes' if status.get('initialized') else 'No'}")
        print(f"Engines: {status.get('engines_count', 0)}")
        print(f"Active Laws: {len(status.get('laws_active', []))}")
        print(f"UBI Aligned: {'Yes' if status.get('ubi_aligned') else 'No'}")

        if "timestamp" in status:
            print(f"Last Updated: {status['timestamp']}")

        return status

    def show_engines(self) -> List[dict]:
        """Show all cognitive engines."""
        integration = self._load_brain()

        print("=" * 60)
        print("COGNITIVE ENGINES")
        print("=" * 60)

        engines = []
        stack = integration.cognitive_stack
        if stack:
            for name, engine in stack.engines.items():
                engine_info = {
                    "name": name,
                    "active": getattr(engine, "active", False),
                    "type": getattr(engine, "type", "unknown"),
                }
                engines.append(engine_info)
                status = "Active" if engine_info["active"] else "Inactive"
                print(f"  {name}: {status}")

        print(f"\nTotal: {len(engines)} engines")
        return engines

    def show_laws(self) -> Dict[str, Any]:
        """Show global laws and compliance."""
        integration = self._load_brain()

        print("=" * 60)
        print("GLOBAL LAWS (L1-L6)")
        print("=" * 60)

        laws_info = {}
        laws = integration.laws
        if laws:
            for law_id, law in laws.LAWS.items():
                laws_info[law_id] = {
                    "name": law.name,
                    "priority": law.priority,
                    "description": law.description[:60] + "...",
                }
                print(f"\n{law_id}: {law.name} (P{law.priority})")
                print(f"  {law.description[:80]}...")

        return laws_info

    def trace_thought(self, problem: str) -> Dict[str, Any]:
        """Trace AMOS reasoning on a problem."""
        integration = self._load_brain()

        print("=" * 60)
        print(f"THOUGHT TRACE: {problem[:50]}...")
        print("=" * 60)

        trace = {"timestamp": datetime.now().isoformat(), "problem": problem, "stages": []}

        # Stage 1: Pre-processing
        print("\n[Stage 1] Pre-processing...")
        pre = integration.pre_process(problem)
        trace["stages"].append({"stage": "pre_process", "result": pre})
        print(f"  Laws check: {pre.get('laws_check', 'N/A')}")
        print(f"  Engines suggested: {pre.get('engines_suggested', [])}")

        # Stage 2: Reasoning
        print("\n[Stage 2] Reasoning...")
        reasoning = integration.reasoning
        if reasoning:
            analysis = reasoning.full_analysis(problem)
            trace["stages"].append({"stage": "reasoning", "result": analysis})
            print(
                f"  Rule of 2: {analysis.get('rule_of_two', {}).get('confidence', 'N/A')} confidence"
            )
            print(
                f"  Rule of 4: {len(analysis.get('rule_of_four', {}).get('quadrants', {}))} quadrants"
            )

        # Stage 3: Cognitive Stack
        print("\n[Stage 3] Cognitive Stack...")
        stack = integration.cognitive_stack
        if stack:
            result = stack.execute(problem)
            trace["stages"].append({"stage": "cognitive_stack", "result": result})
            print(f"  Engines used: {result.get('engines_used', [])}")

        # Stage 4: Post-processing
        print("\n[Stage 4] Post-processing...")
        post = integration.post_process("Sample response", problem)
        trace["stages"].append({"stage": "post_process", "result": post})
        print(f"  L4 compliance: {post.get('l4_compliant', 'N/A')}")

        return trace

    def run_dashboard(self):
        """Run interactive status dashboard."""
        print("=" * 60)
        print("AMOS BRAIN DASHBOARD")
        print("=" * 60)
        print("\nRefreshing every 5 seconds (Ctrl+C to exit)\n")

        try:
            while True:
                self._clear_screen()
                self.show_status()
                print("\n")
                self.show_engines()
                print("\n")
                self.show_laws()
                print("\n" + "=" * 60)
                print(f"Last refresh: {datetime.now().strftime('%H:%M:%S')}")
                print("=" * 60)
                import time

                time.sleep(5)
        except KeyboardInterrupt:
            print("\n\nDashboard stopped.")

    def _clear_screen(self):
        """Clear terminal screen."""
        import os

        os.system("clear" if os.name == "posix" else "cls")

    def export_trace(self, trace: dict, filename: str):
        """Export thought trace to JSON."""
        with open(filename, "w") as f:
            json.dump(trace, f, indent=2, default=str)
        print(f"\nTrace exported to: {filename}")


def main():
    parser = argparse.ArgumentParser(description="AMOS Brain Observer")
    parser.add_argument(
        "command",
        nargs="?",
        default="status",
        choices=["status", "engines", "laws", "trace", "dashboard"],
        help="Observation command",
    )
    parser.add_argument(
        "--problem",
        default="Analyze a complex software architecture decision",
        help="Problem for trace command",
    )
    parser.add_argument("--export", help="Export trace to JSON file")
    args = parser.parse_args()

    observer = AMOSObserver()

    try:
        if args.command == "status":
            observer.show_status()
        elif args.command == "engines":
            observer.show_engines()
        elif args.command == "laws":
            observer.show_laws()
        elif args.command == "trace":
            trace = observer.trace_thought(args.problem)
            if args.export:
                observer.export_trace(trace, args.export)
        elif args.command == "dashboard":
            observer.run_dashboard()
    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
