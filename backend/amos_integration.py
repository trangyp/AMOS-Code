"""
AMOS Integration Layer

Integrates all existing AMOS Python infrastructure with the FastAPI backend:
- repo_doctor/self_evolution/engine.py
- amos_brain/unified_orchestrator_bridge.py
- repo_doctor/unified_architecture_orchestrator.py
- amos_brain/facade.py

Creator: Trang Phan
Version: 3.0.0
"""


import asyncio
import importlib.util
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from event_bus import AMOSEvent, event_bus
from evolution_bridge import evolution_bridge


class AMOSIntegrationLayer:
    """
    Central integration layer connecting all AMOS components.
    Acts as a bridge between the existing Python codebase and the new backend.
    """

    def __init__(self):
        self._components: Dict[str, Any] = {}
        self._loaded = False
        self._unified_orchestrator = None
        self._cognitive_facade = None
        self._architecture_orchestrator = None

    async def initialize(self):
        """Initialize all AMOS components."""
        print("[AMOSIntegration] Initializing...")

        # Load existing components
        await self._load_unified_orchestrator()
        await self._load_cognitive_facade()
        await self._load_architecture_orchestrator()

        self._loaded = True
        print("[AMOSIntegration] Initialization complete")

        # Emit system ready event
        await event_bus.publish(
            AMOSEvent(
                event_type="system_initialized",
                source="amos_integration",
                payload={
                    "components_loaded": list(self._components.keys()),
                    "timestamp": datetime.now(UTC).isoformat(),
                },
                timestamp=datetime.now(UTC).isoformat(),
            )
        )

    async def _load_unified_orchestrator(self):
        """Load the unified orchestrator bridge."""
        try:
            bridge_path = (
                Path(__file__).parent.parent / "amos_brain" / "unified_orchestrator_bridge.py"
            )
            if bridge_path.exists():
                spec = importlib.util.spec_from_file_location("unified_bridge", bridge_path)
                module = importlib.util.module_from_spec(spec)
                sys.modules["unified_bridge"] = module
                spec.loader.exec_module(module)

                # Try to get orchestrator instance
                if hasattr(module, "get_orchestrator"):
                    self._unified_orchestrator = module.get_orchestrator()
                    self._components["unified_orchestrator"] = True
                    print("[AMOSIntegration] Loaded unified orchestrator")
                elif hasattr(module, "UnifiedOrchestrator"):
                    self._unified_orchestrator = module.UnifiedOrchestrator()
                    self._components["unified_orchestrator"] = True
                    print("[AMOSIntegration] Loaded unified orchestrator")
        except Exception as e:
            print(f"[AMOSIntegration] Could not load unified orchestrator: {e}")
            self._components["unified_orchestrator"] = False

    async def _load_cognitive_facade(self):
        """Load the cognitive facade."""
        try:
            facade_path = Path(__file__).parent.parent / "amos_brain" / "facade.py"
            if facade_path.exists():
                spec = importlib.util.spec_from_file_location("cognitive_facade", facade_path)
                module = importlib.util.module_from_spec(spec)
                sys.modules["cognitive_facade"] = module
                spec.loader.exec_module(module)

                if hasattr(module, "CognitiveFacade"):
                    self._cognitive_facade = module.CognitiveFacade()
                    self._components["cognitive_facade"] = True
                    print("[AMOSIntegration] Loaded cognitive facade")
                elif hasattr(module, "AMOSFacade"):
                    self._cognitive_facade = module.AMOSFacade()
                    self._components["cognitive_facade"] = True
                    print("[AMOSIntegration] Loaded cognitive facade")
        except Exception as e:
            print(f"[AMOSIntegration] Could not load cognitive facade: {e}")
            self._components["cognitive_facade"] = False

    async def _load_architecture_orchestrator(self):
        """Load the architecture orchestrator."""
        try:
            arch_path = (
                Path(__file__).parent.parent
                / "repo_doctor"
                / "unified_architecture_orchestrator.py"
            )
            if arch_path.exists():
                spec = importlib.util.spec_from_file_location("arch_orchestrator", arch_path)
                module = importlib.util.module_from_spec(spec)
                sys.modules["arch_orchestrator"] = module
                spec.loader.exec_module(module)

                if hasattr(module, "UnifiedArchitectureOrchestrator"):
                    self._architecture_orchestrator = module.UnifiedArchitectureOrchestrator()
                    self._components["architecture_orchestrator"] = True
                    print("[AMOSIntegration] Loaded architecture orchestrator")
        except Exception as e:
            print(f"[AMOSIntegration] Could not load architecture orchestrator: {e}")
            self._components["architecture_orchestrator"] = False

    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status from all components."""
        status = {
            "integration_loaded": self._loaded,
            "components": self._components,
            "timestamp": datetime.now(UTC).isoformat(),
            "subsystems": {},
        }

        # Get evolution status
        status["evolution"] = evolution_bridge.get_status()

        # Get unified orchestrator status
        if self._unified_orchestrator:
            try:
                if hasattr(self._unified_orchestrator, "get_status"):
                    status["subsystems"]["orchestrator"] = self._unified_orchestrator.get_status()
            except Exception as e:
                status["subsystems"]["orchestrator"] = {"error": str(e)}

        # Get cognitive facade status
        if self._cognitive_facade:
            try:
                if hasattr(self._cognitive_facade, "get_status"):
                    status["subsystems"]["cognitive"] = self._cognitive_facade.get_status()
            except Exception as e:
                status["subsystems"]["cognitive"] = {"error": str(e)}

        return status

    async def execute_cognitive_command(
        self, command: str, parameters: Optional[dict] = None
    ) -> Dict[str, Any]:
        """
        Execute a cognitive command through the facade.

        Args:
            command: Command to execute
            parameters: Command parameters

        Returns:
            Command result
        """
        if not self._cognitive_facade:
            return {"error": "Cognitive facade not available"}

        try:
            if hasattr(self._cognitive_facade, "execute"):
                result = await asyncio.get_running_loop().run_in_executor(
                    None, self._cognitive_facade.execute, command, parameters or {}
                )
                return {"success": True, "result": result}
            else:
                return {"error": "Execute method not available"}
        except Exception as e:
            return {"error": str(e)}

    async def get_architecture_analysis(self) -> Dict[str, Any]:
        """Get architecture analysis from the orchestrator."""
        if not self._architecture_orchestrator:
            return {"error": "Architecture orchestrator not available"}

        try:
            if hasattr(self._architecture_orchestrator, "analyze"):
                result = await asyncio.get_running_loop().run_in_executor(
                    None, self._architecture_orchestrator.analyze
                )
                return {"success": True, "analysis": result}
            else:
                return {"error": "Analyze method not available"}
        except Exception as e:
            return {"error": str(e)}

    async def run_orchestrator_cycle(self) -> Dict[str, Any]:
        """Run a unified orchestrator cycle."""
        if not self._unified_orchestrator:
            return {"error": "Unified orchestrator not available"}

        try:
            if hasattr(self._unified_orchestrator, "run_cycle"):
                result = await asyncio.get_running_loop().run_in_executor(
                    None, self._unified_orchestrator.run_cycle
                )

                # Emit event
                await event_bus.publish(
                    AMOSEvent(
                        event_type="orchestra_status_updated",
                        source="unified_orchestrator",
                        payload={
                            "cycle_completed": True,
                            "result": result,
                        },
                        timestamp=datetime.now(UTC).isoformat(),
                    )
                )

                return {"success": True, "result": result}
            else:
                return {"error": "Run cycle method not available"}
        except Exception as e:
            return {"error": str(e)}

    def is_component_available(self, component_name: str) -> bool:
        """Check if a specific component is available."""
        return self._components.get(component_name, False)

    def get_available_components(self) -> List[str]:
        """Get list of available component names."""
        return [name for name, available in self._components.items() if available]


# Global integration layer instance
amos_integration = AMOSIntegrationLayer()
