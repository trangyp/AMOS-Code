#!/usr/bin/env python3
"""
AMOS 7-System Organism - Main Orchestrator

This is the main entry point for the AMOS 7-System Organism.
It wires together all subsystems according to the primary loop:

BRAIN -> SENSES -> SKELETON -> WORLD_MODEL -> QUANTUM_LAYER -> MUSCLE -> METABOLISM -> BRAIN

Usage:
    python amos_organism.py [--mode {interactive,daemon,single}]
"""

from __future__ import annotations

import argparse
import importlib
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger("amos.organism")


class AMOSOrganism:
    """
    The AMOS 7-System Organism orchestrates all subsystems.
    """
    
    def __init__(self, organism_root: Optional[Path] = None):
        self.root = organism_root or Path(__file__).parent
        self.state: Dict[str, Any] = {
            "status": "initializing",
            "boot_time": datetime.utcnow().isoformat(),
            "active_subsystems": [],
            "cycle_count": 0
        }
        
        # Subsystem references (loaded on demand)
        self._brain = None
        self._senses = None
        self._skeleton = None
        self._immune = None
        self._blood = None
        self._muscle = None
        self._subsystems: Dict[str, Any] = {}
        
        logger.info(f"AMOS Organism initializing at {self.root}")
        self._bootstrap()
    
    def _bootstrap(self):
        """Bootstrap the organism - load ROOT manifest and initialize core subsystems."""
        # Load ROOT manifest
        root_manifest_path = self.root / "00_ROOT" / "root_manifest.json"
        if root_manifest_path.exists():
            with open(root_manifest_path) as f:
                self.root_manifest = json.load(f)
            logger.info(f"Loaded ROOT manifest: {self.root_manifest['_meta']['name']}")
            self.state["identity"] = self.root_manifest.get("identity", {})
        else:
            logger.warning("ROOT manifest not found - using defaults")
            self.root_manifest = {}
        
        # Initialize core subsystems
        self._init_brain()
        self._init_senses()
        self._init_skeleton()
        self._init_immune()
        self._init_blood()
        self._init_muscle()
        
        self.state["status"] = "ready"
        logger.info("AMOS Organism ready")
    
    def _init_brain(self):
        """Initialize the BRAIN subsystem."""
        try:
            brain_path = self.root / "01_BRAIN"
            
            # Add to path and import directly
            if str(brain_path) not in sys.path:
                sys.path.insert(0, str(brain_path))
            if str(self.root) not in sys.path:
                sys.path.insert(0, str(self.root))
            
            # Clear any cached brain_kernel module
            if 'brain_kernel' in sys.modules:
                del sys.modules['brain_kernel']
            
            import brain_kernel
            importlib.reload(brain_kernel)
            
            self._brain = brain_kernel.BrainKernel(self.root)
            self._subsystems["01_BRAIN"] = self._brain
            self.state["active_subsystems"].append("01_BRAIN")
            logger.info("BRAIN subsystem initialized")
        except Exception as e:
            logger.error(f"Failed to initialize BRAIN: {e}")
    
    def _init_senses(self):
        """Initialize the SENSES subsystem."""
        try:
            senses_path = self.root / "02_SENSES"
            
            # Add to path and import directly
            if str(senses_path) not in sys.path:
                sys.path.insert(0, str(senses_path))
            
            # Clear any cached module
            if 'senses_kernel' in sys.modules:
                del sys.modules['senses_kernel']
            
            import senses_kernel
            importlib.reload(senses_kernel)
            
            self._senses = senses_kernel.SensesKernel(self.root)
            self._subsystems["02_SENSES"] = self._senses
            self.state["active_subsystems"].append("02_SENSES")
            logger.info("SENSES subsystem initialized")
        except Exception as e:
            logger.error(f"Failed to initialize SENSES: {e}")
    
    def _init_skeleton(self):
        """Initialize the SKELETON subsystem."""
        try:
            skeleton_path = self.root / "05_SKELETON"
            
            # Add to path and import directly
            if str(skeleton_path) not in sys.path:
                sys.path.insert(0, str(skeleton_path))
            
            # Clear any cached module
            if 'skeleton_kernel' in sys.modules:
                del sys.modules['skeleton_kernel']
            
            import skeleton_kernel
            importlib.reload(skeleton_kernel)
            
            self._skeleton = skeleton_kernel.SkeletonKernel(self.root)
            self._subsystems["05_SKELETON"] = self._skeleton
            self.state["active_subsystems"].append("05_SKELETON")
            
            # Grant permissions to key subsystems
            self._skeleton.grant_permission("01_BRAIN", "all", skeleton_kernel.PermissionLevel.ADMIN, "00_ROOT")
            self._skeleton.grant_permission("06_MUSCLE", "filesystem", skeleton_kernel.PermissionLevel.WRITE, "00_ROOT")
            
            logger.info("SKELETON subsystem initialized with rules and permissions")
        except Exception as e:
            logger.error(f"Failed to initialize SKELETON: {e}")
    
    def _init_immune(self):
        """Initialize the IMMUNE subsystem."""
        try:
            immune_path = self.root / "03_IMMUNE"
            
            # Add to path and import directly
            if str(immune_path) not in sys.path:
                sys.path.insert(0, str(immune_path))
            
            # Clear any cached module
            if 'immune_kernel' in sys.modules:
                del sys.modules['immune_kernel']
            
            import immune_kernel
            importlib.reload(immune_kernel)
            
            self._immune = immune_kernel.ImmuneKernel(self.root)
            self._subsystems["03_IMMUNE"] = self._immune
            self.state["active_subsystems"].append("03_IMMUNE")
            
            logger.info("IMMUNE subsystem initialized with safety boundaries")
        except Exception as e:
            logger.error(f"Failed to initialize IMMUNE: {e}")
    
    def _init_blood(self):
        """Initialize the BLOOD subsystem."""
        try:
            blood_path = self.root / "04_BLOOD"
            
            # Add to path and import directly
            if str(blood_path) not in sys.path:
                sys.path.insert(0, str(blood_path))
            
            # Clear any cached module
            if 'blood_kernel' in sys.modules:
                del sys.modules['blood_kernel']
            
            import blood_kernel
            importlib.reload(blood_kernel)
            
            self._blood = blood_kernel.BloodKernel(self.root)
            self._subsystems["04_BLOOD"] = self._blood
            self.state["active_subsystems"].append("04_BLOOD")
            
            # Start circulation
            self._blood.start()
            
            logger.info("BLOOD subsystem initialized with circulation active")
        except Exception as e:
            logger.error(f"Failed to initialize BLOOD: {e}")
    
    def _init_muscle(self):
        """Initialize the MUSCLE subsystem."""
        try:
            muscle_path = self.root / "06_MUSCLE"
            
            # Add to path and import directly
            if str(muscle_path) not in sys.path:
                sys.path.insert(0, str(muscle_path))
            
            # Clear any cached module
            if 'muscle_kernel' in sys.modules:
                del sys.modules['muscle_kernel']
            
            import muscle_kernel
            importlib.reload(muscle_kernel)
            
            self._muscle = muscle_kernel.MuscleKernel(self.root)
            self._subsystems["06_MUSCLE"] = self._muscle
            self.state["active_subsystems"].append("06_MUSCLE")
            
            # Connect to IMMUNE for safety checks
            if self._immune:
                self._muscle.set_immune_checker(self._immune.check_safety)
            
            logger.info("MUSCLE subsystem initialized with action execution")
        except Exception as e:
            logger.error(f"Failed to initialize MUSCLE: {e}")
    
    def perceive(self) -> Dict[str, Any]:
        """Run the SENSES subsystem to gather environmental data."""
        if self._senses is None:
            return {"error": "SENSES not initialized"}
        
        perception = self._senses.sense_all()
        logger.info(f"Perception complete: {perception.get('buffered_inputs', 0)} buffered inputs")
        return perception
    
    def think(self, input_data: Dict[str, Any], mode: str = "exploratory") -> Dict[str, Any]:
        """Run the BRAIN subsystem to process input."""
        if self._brain is None:
            return {"error": "BRAIN not initialized"}
        
        # Get brain module from sys.modules (already loaded in _init_brain)
        brain_module = sys.modules.get('brain_kernel')
        if brain_module is None:
            return {"error": "Brain module not available"}
        
        mode_map = {
            "exploratory": brain_module.ReasoningMode.EXPLORATORY,
            "diagnostic": brain_module.ReasoningMode.DIAGNOSTIC,
            "design": brain_module.ReasoningMode.DESIGN,
            "audit": brain_module.ReasoningMode.AUDIT,
            "measurement": brain_module.ReasoningMode.MEASUREMENT
        }
        
        reasoning_mode = mode_map.get(mode, brain_module.ReasoningMode.EXPLORATORY)
        
        # Register default engines if not already done
        if not self._brain.engines:
            self._brain.register_engine("meta_logic", brain_module.meta_logic_engine)
            self._brain.register_engine("structural", brain_module.structural_reasoning_engine)
            self._brain.register_engine("scenario", brain_module.scenario_engine)
        
        result = self._brain.process(input_data, mode=reasoning_mode)
        logger.info(f"Thinking complete: thread {result.get('thread_id', 'unknown')}")
        return result
    
    def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Execute actions (MUSCLE subsystem placeholder)."""
        # TODO: Implement full MUSCLE subsystem
        action_result = {
            "status": "logged_only",
            "action": decision.get("action", "none"),
            "timestamp": datetime.utcnow().isoformat(),
            "note": "Full MUSCLE subsystem not yet implemented"
        }
        logger.info(f"Action logged: {action_result['action']}")
        return action_result
    
    def run_cycle(self, goal: Optional[str] = None) -> Dict[str, Any]:
        """
        Run one full organism cycle through the primary loop.
        
        BRAIN -> SENSES -> SKELETON -> WORLD_MODEL -> QUANTUM_LAYER -> MUSCLE -> METABOLISM -> BRAIN
        """
        logger.info(f"=== Starting Organism Cycle {self.state['cycle_count'] + 1} ===")
        
        cycle_start = datetime.utcnow().isoformat()
        
        # 1. PERCEIVE (SENSES)
        perception = self.perceive()
        
        # 2. THINK (BRAIN)
        thought_input = {
            "goal": goal or "organism_maintenance",
            "perception": perception,
            "context": self.state
        }
        thought = self.think(thought_input, mode="diagnostic")
        
        # 3. DECIDE (BRAIN integration)
        decision = {
            "action": "continue_operation",
            "priority": thought.get("results", {}).get("meta_logic", {}).get("output", {}).get("next_steps", ["monitor"]),
            "confidence": thought.get("results", {}).get("meta_logic", {}).get("confidence", 0.5)
        }
        
        # 4. ACT (MUSCLE - placeholder)
        action = self.act(decision)
        
        # Update state
        self.state["cycle_count"] += 1
        self.state["last_cycle"] = {
            "start": cycle_start,
            "end": datetime.utcnow().isoformat(),
            "perception_keys": list(perception.keys()),
            "thought_thread": thought.get("thread_id"),
            "action": action["action"]
        }
        
        return {
            "cycle": self.state["cycle_count"],
            "perception": perception,
            "thought": thought,
            "decision": decision,
            "action": action,
            "state_summary": self.get_state_summary()
        }
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get a summary of current organism state."""
        return {
            "status": self.state["status"],
            "boot_time": self.state["boot_time"],
            "cycles_completed": self.state["cycle_count"],
            "active_subsystems": self.state["active_subsystems"],
            "brain_state": self._brain.get_state() if self._brain else None,
            "skeleton_state": self._skeleton.get_state() if self._skeleton else None,
            "immune_state": self._immune.get_state() if self._immune else None,
            "blood_state": self._blood.get_state() if self._blood else None,
            "muscle_state": self._muscle.get_state() if self._muscle else None
        }
    
    def interactive_mode(self):
        """Run in interactive mode."""
        print("\n" + "="*60)
        print("AMOS 7-System Organism - Interactive Mode")
        print("="*60)
        print(f"Identity: {self.state.get('identity', {}).get('system_name', 'AMOS')}")
        print(f"Creator: {self.state.get('identity', {}).get('creator', 'Trang Phan')}")
        print("="*60)
        print("\nCommands:")
        print("  cycle [goal]  - Run one organism cycle")
        print("  state         - Show organism state")
        print("  perceive      - Run senses only")
        print("  think [text]  - Run brain on text input")
        print("  quit          - Exit")
        print("-"*60 + "\n")
        
        while True:
            try:
                cmd = input("AMOS> ").strip()
                
                if cmd == "quit":
                    print("Shutting down AMOS Organism...")
                    break
                elif cmd == "state":
                    print(json.dumps(self.get_state_summary(), indent=2))
                elif cmd == "perceive":
                    result = self.perceive()
                    print(json.dumps(result, indent=2, default=str))
                elif cmd.startswith("think "):
                    text = cmd[6:]
                    result = self.think({"goal": text, "context": "interactive"}, mode="exploratory")
                    print(json.dumps(result, indent=2))
                elif cmd.startswith("cycle"):
                    goal = cmd[6:] if len(cmd) > 6 else None
                    result = self.run_cycle(goal)
                    print(f"\nCycle {result['cycle']} complete")
                    print(f"Confidence: {result['decision']['confidence']:.2f}")
                    print(f"Next steps: {result['decision']['priority']}")
                else:
                    print("Unknown command. Try: cycle, state, perceive, think, quit")
                    
            except KeyboardInterrupt:
                print("\nInterrupted. Use 'quit' to exit.")
            except Exception as e:
                logger.error(f"Error in interactive mode: {e}")
    
    def daemon_mode(self):
        """Run in daemon mode (continuous cycles)."""
        logger.info("Starting daemon mode")
        try:
            while True:
                self.run_cycle(goal="system_maintenance")
                import time
                time.sleep(60)  # 1 minute between cycles
        except KeyboardInterrupt:
            logger.info("Daemon stopped")


def main():
    parser = argparse.ArgumentParser(description="AMOS 7-System Organism")
    parser.add_argument(
        "--mode",
        choices=["interactive", "daemon", "single"],
        default="interactive",
        help="Operating mode"
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Path to AMOS_ORGANISM_OS directory"
    )
    parser.add_argument(
        "--goal",
        type=str,
        default=None,
        help="Goal for single cycle mode"
    )
    
    args = parser.parse_args()
    
    # Initialize organism
    organism = AMOSOrganism(organism_root=args.root)
    
    if args.mode == "interactive":
        organism.interactive_mode()
    elif args.mode == "daemon":
        organism.daemon_mode()
    elif args.mode == "single":
        result = organism.run_cycle(goal=args.goal)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
