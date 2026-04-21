#!/usr/bin/env python3
"""AMOS 7-System Organism - Main Orchestrator

This is the main entry point for the AMOS 7-System Organism.
It wires together all subsystems according to the primary loop:

BRAIN -> SENSES -> SKELETON -> WORLD_MODEL -> QUANTUM_LAYER -> MUSCLE -> METABOLISM -> BRAIN

Usage:
    python amos_organism.py [--mode {interactive,daemon,single}]
"""

import argparse
import importlib
import json
import logging
import sys
from datetime import datetime, timezone
UTC = timezone.utc, timezone
from pathlib import Path
from typing import Any, Optional, dict

UTC = UTC
# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("amos.organism")


class AMOSOrganism:
    """The AMOS 7-System Organism orchestrates all subsystems."""

    def __init__(self, organism_root: Optional[Path] = None):
        self.root = organism_root or Path(__file__).parent
        self.state: dict[str, Any] = {
            "status": "initializing",
            "boot_time": datetime.now(timezone.utc).isoformat(),
            "active_subsystems": [],
            "cycle_count": 0,
        }

        # Subsystem references (loaded on demand)
        self._brain = None
        self._senses = None
        self._skeleton = None
        self._immune = None
        self._blood = None
        self._muscle = None
        self._metabolism = None
        self._world_model = None
        self._quantum = None
        self._learning = None
        self._canon = None
        self._ethics = None
        self._memory = None
        self._interfaces = None
        self._engine_activation = None
        self._subsystems: dict[str, Any] = {}

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
        self._init_metabolism()
        self._init_world_model()
        self._init_quantum()
        self._init_learning()
        self._init_canon()
        self._init_ethics()
        self._init_memory()
        self._init_interfaces()
        self._init_engine_activation()

        self.state["status"] = "ready"
        logger.info("AMOS Organism ready")

    def _init_brain(self):
        """Initialize the BRAIN subsystem."""
        try:
            brain_path = self.root / "01_BRAIN"

            # Clear any cached brain_kernel module
            if "brain_kernel" in sys.modules:
                del sys.modules["brain_kernel"]

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

            # Clear any cached module
            if "senses_kernel" in sys.modules:
                del sys.modules["senses_kernel"]

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

            # Clear any cached module
            if "skeleton_kernel" in sys.modules:
                del sys.modules["skeleton_kernel"]

            import skeleton_kernel

            importlib.reload(skeleton_kernel)

            self._skeleton = skeleton_kernel.SkeletonKernel(self.root)
            self._subsystems["05_SKELETON"] = self._skeleton
            self.state["active_subsystems"].append("05_SKELETON")

            # Grant permissions to key subsystems
            self._skeleton.grant_permission(
                "01_BRAIN", "all", skeleton_kernel.PermissionLevel.ADMIN, "00_ROOT"
            )
            self._skeleton.grant_permission(
                "06_MUSCLE", "filesystem", skeleton_kernel.PermissionLevel.WRITE, "00_ROOT"
            )

            logger.info("SKELETON subsystem initialized with rules and permissions")
        except Exception as e:
            logger.error(f"Failed to initialize SKELETON: {e}")

    def _init_immune(self):
        """Initialize the IMMUNE subsystem."""
        try:
            immune_path = self.root / "03_IMMUNE"

            # Clear any cached module
            if "immune_kernel" in sys.modules:
                del sys.modules["immune_kernel"]

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

            # Clear any cached module
            if "blood_kernel" in sys.modules:
                del sys.modules["blood_kernel"]

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

            # Clear any cached module
            if "muscle_kernel" in sys.modules:
                del sys.modules["muscle_kernel"]

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

    def _init_metabolism(self):
        """Initialize the METABOLISM subsystem."""
        try:
            metabolism_path = self.root / "07_METABOLISM"

            # Clear any cached module
            if "metabolism_kernel" in sys.modules:
                del sys.modules["metabolism_kernel"]

            import metabolism_kernel

            importlib.reload(metabolism_kernel)

            self._metabolism = metabolism_kernel.MetabolismKernel(self.root)
            self._subsystems["07_METABOLISM"] = self._metabolism
            self.state["active_subsystems"].append("07_METABOLISM")

            # Start monitoring
            self._metabolism.start()

            logger.info("METABOLISM subsystem initialized with monitoring")
        except Exception as e:
            logger.error(f"Failed to initialize METABOLISM: {e}")

    def _init_world_model(self):
        """Initialize the WORLD_MODEL subsystem."""
        try:
            world_path = self.root / "08_WORLD_MODEL"

            # Clear any cached module
            if "world_model_kernel" in sys.modules:
                del sys.modules["world_model_kernel"]

            import world_model_kernel

            importlib.reload(world_model_kernel)

            self._world_model = world_model_kernel.WorldModelKernel(self.root)
            self._subsystems["08_WORLD_MODEL"] = self._world_model
            self.state["active_subsystems"].append("08_WORLD_MODEL")

            logger.info("WORLD_MODEL subsystem initialized with environmental representation")
        except Exception as e:
            logger.error(f"Failed to initialize WORLD_MODEL: {e}")

    def _init_quantum(self):
        """Initialize the QUANTUM_LAYER subsystem."""
        try:
            quantum_path = self.root / "09_QUANTUM_LAYER"

            # Clear any cached module
            if "quantum_layer_kernel" in sys.modules:
                del sys.modules["quantum_layer_kernel"]

            import quantum_layer_kernel

            importlib.reload(quantum_layer_kernel)

            self._quantum = quantum_layer_kernel.QuantumLayerKernel(self.root)
            self._subsystems["09_QUANTUM_LAYER"] = self._quantum
            self.state["active_subsystems"].append("09_QUANTUM_LAYER")

            logger.info("QUANTUM_LAYER subsystem initialized with probabilistic computing")
        except Exception as e:
            logger.error(f"Failed to initialize QUANTUM_LAYER: {e}")

    def _init_learning(self):
        """Initialize the LEARNING subsystem."""
        try:
            learning_path = self.root / "10_LEARNING"

            # Clear any cached module
            if "learning_kernel" in sys.modules:
                del sys.modules["learning_kernel"]

            import learning_kernel

            importlib.reload(learning_kernel)

            self._learning = learning_kernel.LearningKernel(self.root)
            self._subsystems["10_LEARNING"] = self._learning
            self.state["active_subsystems"].append("10_LEARNING")

            logger.info("LEARNING subsystem initialized with adaptive capabilities")
        except Exception as e:
            logger.error(f"Failed to initialize LEARNING: {e}")

    def _init_canon(self):
        """Initialize the CANON_INTEGRATION subsystem."""
        try:
            canon_path = self.root / "11_CANON_INTEGRATION"

            # Clear any cached module
            if "canon_integration_kernel" in sys.modules:
                del sys.modules["canon_integration_kernel"]

            import canon_integration_kernel

            importlib.reload(canon_integration_kernel)

            self._canon = canon_integration_kernel.CanonIntegrationKernel(self.root)
            self._subsystems["11_CANON_INTEGRATION"] = self._canon
            self.state["active_subsystems"].append("11_CANON_INTEGRATION")

            logger.info("CANON_INTEGRATION subsystem initialized with protocol adapters")
        except Exception as e:
            logger.error(f"Failed to initialize CANON_INTEGRATION: {e}")

    def _init_ethics(self):
        """Initialize the ETHICS_VALIDATION subsystem."""
        try:
            ethics_path = self.root / "12_ETHICS_VALIDATION"

            # Clear any cached module
            if "ethics_validation_kernel" in sys.modules:
                del sys.modules["ethics_validation_kernel"]

            import ethics_validation_kernel

            importlib.reload(ethics_validation_kernel)

            self._ethics = ethics_validation_kernel.EthicsValidationKernel(self.root)
            self._subsystems["12_ETHICS_VALIDATION"] = self._ethics
            self.state["active_subsystems"].append("12_ETHICS_VALIDATION")

            logger.info("ETHICS_VALIDATION initialized with ethical constraints")
        except Exception as e:
            logger.error(f"Failed to initialize ETHICS_VALIDATION: {e}")

    def _init_memory(self):
        """Initialize the MEMORY_ARCHIVAL subsystem."""
        try:
            memory_path = self.root / "13_MEMORY_ARCHIVAL"

            # Clear any cached module
            if "memory_archival_kernel" in sys.modules:
                del sys.modules["memory_archival_kernel"]

            import memory_archival_kernel

            importlib.reload(memory_archival_kernel)

            self._memory = memory_archival_kernel.MemoryArchivalKernel(self.root)
            self._subsystems["13_MEMORY_ARCHIVAL"] = self._memory
            self.state["active_subsystems"].append("13_MEMORY_ARCHIVAL")

            logger.info("MEMORY_ARCHIVAL initialized with long-term storage")
        except Exception as e:
            logger.error(f"Failed to initialize MEMORY_ARCHIVAL: {e}")

    def _init_interfaces(self):
        """Initialize the INTERFACE_LAYER subsystem."""
        try:
            interfaces_path = self.root / "14_INTERFACES"

            # Clear any cached module
            if "interface_layer_kernel" in sys.modules:
                del sys.modules["interface_layer_kernel"]

            import interface_layer_kernel

            importlib.reload(interface_layer_kernel)

            self._interfaces = interface_layer_kernel.InterfaceLayerKernel(self.root, self)
            self._subsystems["14_INTERFACE_LAYER"] = self._interfaces
            self.state["active_subsystems"].append("14_INTERFACE_LAYER")

            logger.info("INTERFACE_LAYER initialized with CLI/API/Dashboard")
        except Exception as e:
            logger.error(f"Failed to initialize INTERFACE_LAYER: {e}")

    def _init_engine_activation(self):
        """Initialize the ENGINE_ACTIVATION subsystem."""
        try:
            activation_path = self.root / "15_ENGINE_ACTIVATION"

            # Clear any cached module
            if "engine_activation_kernel" in sys.modules:
                del sys.modules["engine_activation_kernel"]

            import engine_activation_kernel

            importlib.reload(engine_activation_kernel)

            self._engine_activation = engine_activation_kernel.EngineActivationKernel(
                self.root, self._brain
            )

            # Scan and activate engines
            discovery = self._engine_activation.scan_and_discover()
            logger.info(f"Engine discovery: {discovery['discovered']} engines found")

            # Activate cognitive engines by default
            activated = self._engine_activation.activate_by_category("cognitive")
            activated += self._engine_activation.activate_by_category("tech")
            activated += self._engine_activation.activate_by_category("core")

            self._subsystems["15_ENGINE_ACTIVATION"] = self._engine_activation
            self.state["active_subsystems"].append("15_ENGINE_ACTIVATION")

            logger.info(f"ENGINE_ACTIVATION initialized with {activated} engines active")
        except Exception as e:
            logger.error(f"Failed to initialize ENGINE_ACTIVATION: {e}")

    def perceive(self) -> dict[str, Any]:
        """Run the SENSES subsystem to gather environmental data."""
        if self._senses is None:
            return {"error": "SENSES not initialized"}

        perception = self._senses.sense_all()
        logger.info(f"Perception complete: {perception.get('buffered_inputs', 0)} buffered inputs")
        return perception

    def think(self, input_data: dict[str, Any], mode: str = "exploratory") -> dict[str, Any]:
        """Run the BRAIN subsystem to process input."""
        if self._brain is None:
            return {"error": "BRAIN not initialized"}

        # Get brain module from sys.modules (already loaded in _init_brain)
        brain_module = sys.modules.get("brain_kernel")
        if brain_module is None:
            return {"error": "Brain module not available"}

        mode_map = {
            "exploratory": brain_module.ReasoningMode.EXPLORATORY,
            "diagnostic": brain_module.ReasoningMode.DIAGNOSTIC,
            "design": brain_module.ReasoningMode.DESIGN,
            "audit": brain_module.ReasoningMode.AUDIT,
            "measurement": brain_module.ReasoningMode.MEASUREMENT,
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

    def act(self, decision: dict[str, Any]) -> dict[str, Any]:
        """Execute actions (MUSCLE subsystem placeholder)."""
        # TODO: Implement full MUSCLE subsystem
        action_result = {
            "status": "logged_only",
            "action": decision.get("action", "none"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Full MUSCLE subsystem not yet implemented",
        }
        logger.info(f"Action logged: {action_result['action']}")
        return action_result

    def run_cycle(self, goal: str = None) -> dict[str, Any]:
        """Run one full organism cycle through the primary loop.

        BRAIN -> SENSES -> SKELETON -> WORLD_MODEL -> QUANTUM_LAYER -> MUSCLE -> METABOLISM -> BRAIN
        """
        logger.info(f"=== Starting Organism Cycle {self.state['cycle_count'] + 1} ===")

        cycle_start = datetime.now(timezone.utc).isoformat()

        # 1. PERCEIVE (SENSES)
        perception = self.perceive()

        # 2. THINK (BRAIN)
        thought_input = {
            "goal": goal or "organism_maintenance",
            "perception": perception,
            "context": self.state,
        }
        thought = self.think(thought_input, mode="diagnostic")

        # 3. DECIDE (BRAIN integration)
        decision = {
            "action": "continue_operation",
            "priority": thought.get("results", {})
            .get("meta_logic", {})
            .get("output", {})
            .get("next_steps", ["monitor"]),
            "confidence": thought.get("results", {}).get("meta_logic", {}).get("confidence", 0.5),
        }

        # 4. ACT (MUSCLE - placeholder)
        action = self.act(decision)

        # Update state
        self.state["cycle_count"] += 1
        self.state["last_cycle"] = {
            "start": cycle_start,
            "end": datetime.now(UTC).isoformat(),
            "perception_keys": list(perception.keys()),
            "thought_thread": thought.get("thread_id"),
            "action": action["action"],
        }

        return {
            "cycle": self.state["cycle_count"],
            "perception": perception,
            "thought": thought,
            "decision": decision,
            "action": action,
            "state_summary": self.get_state_summary(),
        }

    def get_state_summary(self) -> dict[str, Any]:
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
            "muscle_state": self._muscle.get_state() if self._muscle else None,
            "metabolism_state": self._metabolism.get_state() if self._metabolism else None,
            "world_model_state": self._world_model.get_state() if self._world_model else None,
            "quantum_state": self._quantum.get_state() if self._quantum else None,
            "learning_state": self._learning.get_state() if self._learning else None,
            "canon_state": self._canon.get_state() if self._canon else None,
            "ethics_state": self._ethics.get_state() if self._ethics else None,
            "memory_state": self._memory.get_state() if self._memory else None,
            "interfaces_state": self._interfaces.get_state() if self._interfaces else None,
            "engine_activation_state": self._engine_activation.get_state()
            if self._engine_activation
            else None,
        }

    def interactive_mode(self):
        """Run in interactive mode."""
        print("\n" + "=" * 60)
        print("AMOS 7-System Organism - Interactive Mode")
        print("=" * 60)
        print(f"Identity: {self.state.get('identity', {}).get('system_name', 'AMOS')}")
        print(f"Creator: {self.state.get('identity', {}).get('creator', 'Trang Phan')}")
        print("=" * 60)
        print("\nCommands:")
        print("  cycle [goal]  - Run one organism cycle")
        print("  state         - Show organism state")
        print("  perceive      - Run senses only")
        print("  think [text]  - Run brain on text input")
        print("  quit          - Exit")
        print("-" * 60 + "\n")

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
                    result = self.think(
                        {"goal": text, "context": "interactive"}, mode="exploratory"
                    )
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
        help="Operating mode",
    )
    parser.add_argument(
        "--root", type=Path, default=None, help="Path to AMOS_ORGANISM_OS directory"
    )
    parser.add_argument("--goal", type=str, default=None, help="Goal for single cycle mode")

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
