#!/usr/bin/env python3
"""AMOS GODMODE - Executive Controller

Top-level executive controller that coordinates brainstack, sensors, 
executor and dashboards. This is the highest-level control interface.

Usage:
    python AMOS_GODMODE.py [--mode omega|gamma|sigma]
    ./start_godmode_full.sh
"""

from __future__ import annotations

import argparse
import signal
import sys
from pathlib import Path
from typing import Any

# Add AMOS to path
REPO_ROOT = Path(__file__).parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "AMOS_ORGANISM_OS"))


class GodmodeController:
    """Executive controller for AMOS organism.
    
    Coordinates:
    - Brainstack (cognitive engines)
    - Sensors (environment monitoring)
    - Executor (task execution)
    - Dashboard (human interface)
    """
    
    def __init__(self, mode: str = "omega"):
        self.mode = mode
        self.root = Path(__file__).parent
        self.running = False
        self.components: dict[str, Any] = {}
        
        # Mode configuration
        self.modes = {
            "omega": "Full organism mode - all subsystems online",
            "gamma": "Deep scan and repair mode",
            "sigma": "Stable synchronized state",
            "alpha": "Basic sandbox mode",
            "beta": "Development mode",
        }
        
    def initialize(self) -> bool:
        """Initialize all components."""
        print("=" * 70)
        print("AMOS GODMODE - EXECUTIVE CONTROLLER")
        print("=" * 70)
        print(f"Mode: {self.mode} - {self.modes.get(self.mode, 'Unknown')}")
        print("-" * 70)
        
        # Initialize organism
        try:
            from organism import AMOSOrganism
            self.components["organism"] = AMOSOrganism()
            print("  ✓ Organism: initialized")
        except Exception as e:
            print(f"  ✗ Organism: {e}")
            
        # Initialize runtime
        try:
            from AMOS_RUNTIME import AmosRuntime
            self.components["runtime"] = AmosRuntime(mode=self.mode)
            print("  ✓ Runtime: initialized")
        except Exception as e:
            print(f"  ✗ Runtime: {e}")
            
        # Check 6 repos
        repos = ["AMOS-Code", "AMOS-Consulting", "AMOS-Claws", 
                "Mailinhconect", "AMOS-Invest", "AMOS-UNIVERSE"]
        for repo in repos:
            repo_path = self.root / "AMOS_REPOS" / repo
            if repo_path.exists():
                print(f"  ✓ Repo: {repo}")
            else:
                print(f"  ✗ Repo: {repo} (missing)")
                
        print("=" * 70)
        return True
        
    def run(self) -> None:
        """Run the godmode loop."""
        self.running = True
        print("\n🔱 GODMODE ACTIVE - Press Ctrl+C to exit\n")
        
        try:
            while self.running:
                # Main executive loop
                pass
        except KeyboardInterrupt:
            self.shutdown()
            
    def shutdown(self) -> None:
        """Graceful shutdown."""
        print("\n🛑 GODMODE shutting down...")
        self.running = False
        
        for name, component in self.components.items():
            try:
                if hasattr(component, 'shutdown'):
                    component.shutdown()
                print(f"  ✓ {name}: shutdown")
            except Exception as e:
                print(f"  ✗ {name}: {e}")
                
        print("=" * 70)
        print("GODMODE OFFLINE")
        print("=" * 70)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="AMOS GODMODE Controller")
    parser.add_argument("--mode", choices=["omega", "gamma", "sigma", "alpha", "beta"],
                       default="omega", help="Operation mode")
    args = parser.parse_args()
    
    controller = GodmodeController(mode=args.mode)
    
    if controller.initialize():
        controller.run()
    else:
        print("❌ Initialization failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
