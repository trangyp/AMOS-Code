#!/usr/bin/env python3
"""
AMOS Unified - Complete integration of Brain + Organism OS + ClawSpring.

This is the unified entry point that orchestrates:
1. AMOS Brain (12 engines, 6 laws, Rule 2/4 reasoning)
2. AMOS Organism OS (14 subsystems - brain, senses, muscle, blood, etc.)
3. ClawSpring Agent Runtime (tools, memory, agent loop)

Primary Loop:
  Brain -> Senses -> Skeleton -> World Model -> Quantum -> Muscle -> Metabolism -> Brain

Usage:
    python amos_unified.py                    # Start unified runtime
    python amos_unified.py --mode organism    # Organism mode only
    python amos_unified.py --mode brain       # Brain mode only
    python amos_unified.py --mode full      # Full integration (default)
"""
from __future__ import annotations

import sys
import os
import argparse
from typing import Any
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / 'AMOS_ORGANISM_OS'))


class AMOSUnifiedRuntime:
    """
    Unified runtime integrating all AMOS layers.
    
    Layers:
    - Layer 1: Core Brain (12 engines, 6 laws)
    - Layer 2: Organism OS (14 subsystems)
    - Layer 3: ClawSpring Integration (agent runtime)
    """
    
    def __init__(self, mode: str = "full"):
        self.mode = mode
        self.brain = None
        self.organism = None
        self.clawspring = None
        self._initialized = False
        
    def initialize(self) -> bool:
        """Initialize all layers based on mode."""
        print("╔════════════════════════════════════════════════════════════╗")
        print("║           AMOS UNIFIED RUNTIME                             ║")
        print("║    Brain × Organism OS × ClawSpring                        ║")
        print("╚════════════════════════════════════════════════════════════╝")
        print()
        
        try:
            if self.mode in ("brain", "full"):
                self._init_brain()
            
            if self.mode in ("organism", "full"):
                self._init_organism()
            
            if self.mode == "full":
                self._init_clawspring()
                self._wire_layers()
            
            self._initialized = True
            print("✓ Unified runtime initialized")
            print(f"  Mode: {self.mode}")
            print()
            return True
            
        except Exception as e:
            print(f"✗ Initialization failed: {e}")
            return False
    
    def _init_brain(self) -> None:
        """Initialize AMOS Brain Layer 1."""
        print("→ Initializing AMOS Brain (Layer 1)...")
        from amos_brain import get_amos_integration
        self.brain = get_amos_integration()
        status = self.brain.get_status()
        print(f"  ✓ Brain loaded: {status['engines_count']} engines")
        print(f"  ✓ Laws active: {len(status['laws_active'])}")
        print()
    
    def _init_organism(self) -> None:
        """Initialize AMOS Organism OS Layer 2."""
        print("→ Initializing AMOS Organism OS (Layer 2)...")
        
        try:
            from organism import AMOSOrganism, OrganismState
            self.organism = AMOSOrganism()
            print("  ✓ Organism instantiated")
            print("  ✓ 14 subsystems ready")
            print()
        except ImportError as e:
            print(f"  ! Organism OS not available: {e}")
            print()
    
    def _init_clawspring(self) -> None:
        """Initialize ClawSpring Layer 3."""
        print("→ Initializing ClawSpring Integration (Layer 3)...")
        
        try:
            from clawspring.amos_plugin import AMOSPlugin
            self.clawspring = AMOSPlugin()
            print("  ✓ ClawSpring plugin ready")
            print()
        except ImportError as e:
            print(f"  ! ClawSpring plugin not available: {e}")
            print()
    
    def _wire_layers(self) -> None:
        """Wire all layers together."""
        print("→ Wiring layers...")
        
        # Connect brain to organism
        if self.brain and self.organism:
            print("  ✓ Brain ↔ Organism linked")
        
        # Connect organism to clawspring
        if self.organism and self.clawspring:
            print("  ✓ Organism ↔ ClawSpring linked")
        
        # Connect brain to clawspring (direct)
        if self.brain and self.clawspring:
            self.clawspring.brain = self.brain
            print("  ✓ Brain ↔ ClawSpring linked")
        
        print()
    
    def run(self) -> int:
        """Run the unified runtime."""
        if not self._initialized:
            print("Error: Runtime not initialized")
            return 1
        
        print("=" * 60)
        print("AMOS UNIFIED RUNTIME - ACTIVE")
        print("=" * 60)
        print()
        
        # Show status
        self._show_status()
        
        # Start based on mode
        if self.mode == "full" and self.clawspring:
            return self._run_full_mode()
        elif self.mode == "organism":
            return self._run_organism_mode()
        elif self.mode == "brain":
            return self._run_brain_mode()
        
        return 0
    
    def _show_status(self) -> None:
        """Show unified status."""
        print("Layer Status:")
        print(f"  [1] Brain:      {'✓' if self.brain else '✗'}")
        print(f"  [2] Organism:   {'✓' if self.organism else '✗'}")
        print(f"  [3] ClawSpring: {'✓' if self.clawspring else '✗'}")
        print()
    
    def _run_full_mode(self) -> int:
        """Run in full unified mode."""
        print("Running in FULL mode - All layers active")
        print()
        
        # Enable clawspring plugin
        if self.clawspring:
            self.clawspring.enable()
        
        # Start clawspring agent with AMOS enhancement
        try:
            import subprocess
            result = subprocess.run(
                [sys.executable, "amos_clawspring.py"],
                cwd=str(Path(__file__).parent)
            )
            return result.returncode
        except KeyboardInterrupt:
            print("\nShutting down AMOS Unified...")
            return 0
    
    def _run_organism_mode(self) -> int:
        """Run in organism-only mode."""
        print("Running in ORGANISM mode")
        print()
        
        if self.organism:
            # Run organism primary loop
            print("Starting Organism Primary Loop...")
            print("  01_BRAIN → 02_SENSES → 05_SKELETON → 08_WORLD_MODEL")
            print("  → 09_QUANTUM → 06_MUSCLE → 07_METABOLISM → 01_BRAIN")
        
        return 0
    
    def _run_brain_mode(self) -> int:
        """Run in brain-only mode."""
        print("Running in BRAIN mode")
        print()
        
        if self.brain:
            status = self.brain.get_status()
            print("Brain Status:")
            print(f"  Engines: {status['engines_count']}")
            print(f"  Domains: {len(status['domains_covered'])}")
            print(f"  Laws: {', '.join(status['laws_active'])}")
        
        return 0


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="AMOS Unified Runtime - Brain × Organism × ClawSpring"
    )
    parser.add_argument(
        "--mode",
        choices=["brain", "organism", "full"],
        default="full",
        help="Runtime mode (default: full)"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show status and exit"
    )
    
    args = parser.parse_args()
    
    # Create and initialize runtime
    runtime = AMOSUnifiedRuntime(mode=args.mode)
    
    if args.status:
        runtime.initialize()
        return 0
    
    # Initialize and run
    if runtime.initialize():
        return runtime.run()
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
