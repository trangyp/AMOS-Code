#!/usr/bin/env python3
"""AMOS Ecosystem Integrator (Layer 20)
=====================================

Final integration layer connecting all AMOS systems:
- AMOS Brain (19 layers)
- AMOS Organism OS (14 subsystems)
- AMOSL Programming Language
- ClawSpring Agent Framework
- SDK (Python/JavaScript)

Provides unified ecosystem orchestration.

Usage:
    from amos_ecosystem_integrator import Ecosystem

    eco = Ecosystem()
    eco.activate()

    # Use any capability
    result = eco.think("Question")
    result = eco.execute("Task")
    result = eco.orchestrate("Goal")

Creator: Trang Phan
System: AMOS vInfinity - Layer 20
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class EcosystemState:
    """Complete state of the AMOS ecosystem."""

    activated_at: str = None
    brain_layers: int = 19
    organism_subsystems: int = 14
    amosl_loaded: bool = False
    clawspring_connected: bool = False
    sdk_available: bool = False
    session_id: str = None
    active_engines: list[str] = field(default_factory=list)
    law_compliance: dict[str, bool] = field(default_factory=dict)
    canon_loaded: bool = False
    canon_terms: int = 0
    canon_agents: int = 0


class Ecosystem:
    """AMOS Ecosystem Integrator - Master control for all systems.

    Integrates:
    - L1-L19: AMOS Brain Cognitive OS
    - L20: This integrator layer
    - AMOS Organism OS (14 biological subsystems)
    - AMOSL (multi-substrate language)
    - ClawSpring (agent framework)
    - SDK (Python/JavaScript clients)

    Provides single interface to 1000+ files, 400+ classes, 160+ engines.
    """

    VERSION = "20.0.0"
    LAYERS = 20

    def __init__(self):
        self.state = EcosystemState()
        self._brain = None
        self._organism = None
        self._amosl = None
        self._initialized = False
        self._canon_bridge = None

    async def _get_canon_bridge(self):
        """Lazy initialization of canon bridge."""
        if self._canon_bridge is None:
            from amos_brain.canon_bridge import get_canon_bridge

            self._canon_bridge = await get_canon_bridge()
        return self._canon_bridge

    def activate(self) -> dict[str, Any]:
        """Activate the complete AMOS ecosystem.

        Initializes all systems in dependency order:
        1. AMOS Brain (19 layers)
        2. Organism OS (14 subsystems)
        3. AMOSL runtime
        4. ClawSpring integration
        5. SDK connections

        Returns:
            Activation status with component readiness
        """
        results = {
            "status": "activating",
            "components": {},
            "timestamp": datetime.now(UTC).isoformat(),
        }

        # 1. Activate Brain (L1-L19)
        try:
            from amos_brain import get_brain, get_state_manager

            self._brain = get_brain()
            sm = get_state_manager()
            self.state.session_id = sm.start_session(goal="Ecosystem Activation", domain="unified")
            self.state.active_engines = self._brain.list_engines()
            results["components"]["brain"] = {
                "status": "active",
                "layers": 19,
                "engines": len(self.state.active_engines),
            }
        except Exception as e:
            results["components"]["brain"] = {"status": "error", "error": str(e)}

        # 2. Connect Organism OS
        try:
            from amos_brain import initialize_organism

            org_result = initialize_organism()
            if org_result["status"] == "initialized":
                self.state.organism_subsystems = org_result.get("subsystems", 14)
                results["components"]["organism"] = {
                    "status": "connected",
                    "subsystems": self.state.organism_subsystems,
                }
            else:
                results["components"]["organism"] = {
                    "status": "optional",
                    "note": "Not initialized but available",
                }
        except Exception as e:
            results["components"]["organism"] = {
                "status": "optional",
                "note": f"Module available: {e}",
            }

        # 3. Check AMOSL
        try:
            from amosl import __version__ as amosl_version

            self.state.amosl_loaded = True
            results["components"]["amosl"] = {"status": "available", "version": amosl_version}
        except Exception as e:
            results["components"]["amosl"] = {"status": "optional", "error": str(e)}

        # 4. Check SDK
        try:
            from amos_sdk import __version__ as sdk_version

            self.state.sdk_available = True
            results["components"]["sdk"] = {"status": "available", "version": sdk_version}
        except Exception as e:
            results["components"]["sdk"] = {"status": "optional", "error": str(e)}

        # 5. Check ClawSpring
        try:
            import clawspring

            self.state.clawspring_connected = True
            results["components"]["clawspring"] = {
                "status": "connected",
                "version": getattr(clawspring, "__version__", "unknown"),
            }
        except Exception as e:
            results["components"]["clawspring"] = {"status": "optional", "error": str(e)}

        # 6. Initialize Canon
        try:
            import asyncio

            from amos_canon_integration import get_canon_loader, initialize_canon

            canon_ready = asyncio.run(initialize_canon())
            if canon_ready:
                loader = get_canon_loader()
                status = loader.get_status()
                self.state.canon_loaded = True
                self.state.canon_terms = status.total_terms
                self.state.canon_agents = status.total_agents
                results["components"]["canon"] = {
                    "status": "loaded",
                    "terms": status.total_terms,
                    "agents": status.total_agents,
                    "engines": status.total_engines,
                }
            else:
                results["components"]["canon"] = {"status": "error", "note": "Failed to load"}
        except Exception as e:
            results["components"]["canon"] = {"status": "optional", "error": str(e)}

        # Final status
        self.state.activated_at = results["timestamp"]
        active_count = sum(
            1
            for c in results["components"].values()
            if c["status"] in ["active", "connected", "available"]
        )

        results["status"] = "activated" if active_count >= 2 else "partial"
        results["active_components"] = active_count
        results["total_components"] = len(results["components"])
        results["session_id"] = self.state.session_id

        self._initialized = True
        return results

    # ===== BRAIN INTERFACE (L10) =====

    async def think(self, query: str, domain: str = "general") -> dict[str, Any]:
        """Cognitive analysis via Brain L10 with Canon context."""
        if not self._initialized:
            self.activate()

        # Enrich with Canon context
        canon_context = {}
        try:
            canon = await self._get_canon_bridge()
            ctx = canon.get_context_for_domain(domain)
            query = canon.enrich_query(query, domain)
            canon_context = {
                "domain": ctx.domain,
                "terms_available": len(ctx.glossary_terms),
                "applicable_agents": ctx.applicable_agents[:3],
            }
        except Exception:
            pass

        from amos_brain.facade import BrainClient

        client = BrainClient()
        response = await client.think(query, domain=domain)

        return {
            "success": response.success,
            "reasoning": response.reasoning,
            "confidence": response.confidence,
            "law_compliant": response.law_compliant,
            "layer": "L10",
            "source": "brain",
            "canon_context": canon_context,
        }

    def decide(self, problem: str, options: list[str] = None) -> dict[str, Any]:
        """Decision making via Brain L10."""
        if not self._initialized:
            self.activate()

        from amos_brain import decide

        result = decide(problem, options or [])

        return {
            "success": True,
            "recommendation": result.recommendation,
            "confidence": result.confidence,
            "perspectives": result.perspectives,
            "layer": "L10",
            "source": "brain",
        }

    def validate(self, action: str) -> dict[str, Any]:
        """Law validation via Brain L5."""
        if not self._initialized:
            self.activate()

        from amos_brain import validate

        is_valid, issues = validate(action)

        return {"valid": is_valid, "issues": issues, "layer": "L5", "source": "brain"}

    # ===== COOKBOOK INTERFACE (L12) =====

    def architecture_decision(self, question: str) -> dict[str, Any]:
        """Architecture decision via Cookbook L12."""
        if not self._initialized:
            self.activate()

        from amos_brain import ArchitectureDecision

        result = ArchitectureDecision.analyze(question)

        return {
            "success": True,
            "recipe": result.recipe_name,
            "analysis": result.analysis,
            "recommendations": result.recommendations,
            "confidence": result.confidence,
            "layer": "L12",
            "source": "cookbook",
        }

    def code_review(self, code: str) -> dict[str, Any]:
        """Code review via Cookbook L12."""
        if not self._initialized:
            self.activate()

        from amos_brain import CodeReview

        result = CodeReview.analyze(code)

        return {
            "success": True,
            "recipe": result.recipe_name,
            "issues": result.recommendations,
            "confidence": result.confidence,
            "layer": "L12",
            "source": "cookbook",
        }

    # ===== ORGANISM INTERFACE (L18) =====

    def execute(self, task: str, domain: str = "general") -> dict[str, Any]:
        """Execute via Organism OS L18."""
        if not self._initialized:
            self.activate()

        try:
            from amos_brain import execute_organism_task

            result = execute_organism_task(task, domain)

            return {
                "success": result.get("status") == "completed",
                "task": task,
                "domain": domain,
                "result": result,
                "layer": "L18",
                "source": "organism",
            }
        except Exception as e:
            return {"success": False, "error": str(e), "task": task, "layer": "L18"}

    # ===== ORCHESTRATION INTERFACE (L8) =====

    def orchestrate(self, goal: str) -> dict[str, Any]:
        """Orchestrate via Meta-Cognitive L8."""
        if not self._initialized:
            self.activate()

        from amos_brain import get_meta_controller

        mc = get_meta_controller()
        plan = mc.orchestrate(goal, auto_execute=False)

        return {
            "success": True,
            "plan_id": plan.plan_id,
            "subtasks": plan.subtasks,
            "estimated_duration": plan.estimated_duration,
            "layer": "L8",
            "source": "meta_cognitive",
        }

    # ===== ECOSYSTEM STATUS =====

    def status(self) -> dict[str, Any]:
        """Get complete ecosystem status."""
        return {
            "version": self.VERSION,
            "layers": self.LAYERS,
            "activated": self.state.activated_at is not None,
            "activated_at": self.state.activated_at,
            "session_id": self.state.session_id,
            "components": {
                "brain": {
                    "layers": self.state.brain_layers,
                    "engines": len(self.state.active_engines),
                    "laws": 6,
                },
                "organism": {"subsystems": self.state.organism_subsystems},
                "amosl": {"loaded": self.state.amosl_loaded},
                "sdk": {"available": self.state.sdk_available},
                "clawspring": {"connected": self.state.clawspring_connected},
            },
        }

    def summary(self) -> str:
        """Get human-readable ecosystem summary."""
        status = self.status()

        lines = [
            "=" * 66,
            "AMOS ECOSYSTEM INTEGRATOR - Layer 20",
            "=" * 66,
            "",
            f"Version: {status['version']}",
            f"Layers: {status['layers']}",
            f"Activated: {status['activated']}",
            "",
            "Components:",
            f"  • Brain: {status['components']['brain']['layers']} layers, "
            f"{status['components']['brain']['engines']} engines, "
            f"{status['components']['brain']['laws']} laws",
            f"  • Organism: {status['components']['organism']['subsystems']} subsystems",
            f"  • AMOSL: {'Available' if status['components']['amosl']['loaded'] else 'Optional'}",
            f"  • SDK: {'Available' if status['components']['sdk']['available'] else 'Optional'}",
            f"  • ClawSpring: {'Connected' if status['components']['clawspring']['connected'] else 'Optional'}",
            "",
            "Usage:",
            "  eco.think('Question')           - Brain L10",
            "  eco.decide('Problem')           - Decision L10",
            "  eco.architecture_decision('Q')  - Cookbook L12",
            "  eco.execute('Task')             - Organism L18",
            "  eco.orchestrate('Goal')         - Meta L8",
            "",
            "=" * 66,
        ]

        return "\n".join(lines)


# Global instance
_ecosystem_instance: Ecosystem | None = None


def get_ecosystem() -> Ecosystem:
    """Get global ecosystem instance."""
    global _ecosystem_instance
    if _ecosystem_instance is None:
        _ecosystem_instance = Ecosystem()
        _ecosystem_instance.activate()
    return _ecosystem_instance


# Convenience exports
def think(query: str) -> dict[str, Any]:
    """Quick think via ecosystem."""
    return get_ecosystem().think(query)


def decide(problem: str, options: list[str] = None) -> dict[str, Any]:
    """Quick decide via ecosystem."""
    return get_ecosystem().decide(problem, options)


def execute(task: str, domain: str = "general") -> dict[str, Any]:
    """Quick execute via ecosystem."""
    return get_ecosystem().execute(task, domain)


if __name__ == "__main__":
    # Demo activation
    print("\nActivating AMOS Ecosystem (Layer 20)...\n")

    eco = Ecosystem()
    result = eco.activate()

    print(f"Status: {result['status']}")
    print(f"Active Components: {result['active_components']}/{result['total_components']}")
    print(f"Session: {result['session_id'][:20]}...")
    print()

    for name, component in result["components"].items():
        status_icon = "✓" if component["status"] in ["active", "connected", "available"] else "○"
        print(f"  {status_icon} {name}: {component['status']}")

    print()
    print(eco.summary())
