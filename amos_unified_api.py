#!/usr/bin/env python3
"""AMOS Unified API (Layer 19)
============================

Single entry point for all 17+ AMOS Brain layers.
Provides clean, consistent interface to the entire cognitive system.

Usage:
    from amos_unified_api import AMOS

    # Initialize
    amos = AMOS()

    # Think with brain
    result = amos.think("Should we use microservices?")

    # Use cookbook recipes
    adr = amos.architecture_decision("Database choice", options=["SQL", "NoSQL"])

    # Execute with organism
    result = amos.execute("Deploy to production", domain="devops")

Creator: Trang Phan
System: AMOS vInfinity
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class AMOSResult:
    """Standard result wrapper for all AMOS operations."""

    success: bool
    data: Any
    law_compliant: bool
    confidence: str
    reasoning: List[str]
    layer: str  # Which layer handled this
    session_id: str = None


class AMOS:
    """Unified AMOS Brain API - Access all 17+ layers through one interface.

    Layers exposed:
    - L1: Brain Loader (26 engines)
    - L4: Task Processor (Rule 2/4)
    - L5: Global Laws (L1-L6)
    - L6: Agent Bridge
    - L7: State Manager
    - L8: Meta-Cognitive Controller
    - L10: Cognitive Facade (think, decide, validate)
    - L11: Cognitive Config
    - L12: Cognitive Cookbook (6 recipes)
    - L14: ClawSpring Integration
    - L18: Organism Bridge (14 subsystems)
    """

    def __init__(self):
        self.session_id = None
        self._brain = None
        self._state_manager = None
        self._initialized = False

    def initialize(self) -> AMOSResult:
        """Initialize all AMOS layers."""
        try:
            from amos_brain import get_brain, get_state_manager

            self._brain = get_brain()
            self._state_manager = get_state_manager()
            self.session_id = self._state_manager.start_session(
                goal="AMOS Unified API Session", domain="general"
            )
            self._initialized = True

            return AMOSResult(
                success=True,
                data={"engines": len(self._brain.list_engines()), "layers": 17},
                law_compliant=True,
                confidence="high",
                reasoning=["Brain loaded", "State manager ready", "Session created"],
                layer="L1-L7",
                session_id=self.session_id,
            )
        except Exception as e:
            return AMOSResult(
                success=False,
                data={"error": str(e)},
                law_compliant=False,
                confidence="low",
                reasoning=[f"Initialization failed: {e}"],
                layer="INIT",
            )

    # ===== LAYER 10: COGNITIVE FACADE =====

    def think(self, query: str, domain: str = "general") -> AMOSResult:
        """Cognitive analysis with Rule 2/4."""
        if not self._initialized:
            self.initialize()

        from amos_brain import think

        response = think(query)

        return AMOSResult(
            success=response.success,
            data={
                "reasoning": response.reasoning,
                "kernels_used": response.kernels_used,
                "metadata": response.metadata,
            },
            law_compliant=response.law_compliant,
            confidence=response.confidence,
            reasoning=response.reasoning[:3],
            layer="L10",
            session_id=self.session_id,
        )

    def decide(self, problem: str, options: list[str] = None) -> AMOSResult:
        """Decision making with analysis."""
        if not self._initialized:
            self.initialize()

        from amos_brain import decide

        result = decide(problem, options or [])

        return AMOSResult(
            success=True,
            data={
                "recommendation": result.recommendation,
                "perspectives": result.perspectives,
                "confidence": result.confidence,
            },
            law_compliant=True,
            confidence=result.confidence,
            reasoning=[f"Decision: {result.recommendation}"],
            layer="L10",
            session_id=self.session_id,
        )

    def validate(self, action: str) -> AMOSResult:
        """Validate action against Global Laws L1-L6."""
        if not self._initialized:
            self.initialize()

        from amos_brain import validate

        is_valid, issues = validate(action)

        return AMOSResult(
            success=is_valid,
            data={"valid": is_valid, "issues": issues},
            law_compliant=is_valid,
            confidence="high" if is_valid else "low",
            reasoning=["Law validation complete"] + issues,
            layer="L5-L10",
            session_id=self.session_id,
        )

    # ===== LAYER 12: COGNITIVE COOKBOOK =====

    def architecture_decision(
        self, question: str, context: dict = None, options: list[str] = None
    ) -> AMOSResult:
        """Architecture Decision Record workflow."""
        if not self._initialized:
            self.initialize()

        from amos_brain import ArchitectureDecision

        result = ArchitectureDecision.analyze(question)

        return AMOSResult(
            success=True,
            data={
                "recipe": result.recipe_name,
                "analysis": result.analysis,
                "recommendations": result.recommendations,
            },
            law_compliant=result.law_compliant,
            confidence=result.confidence,
            reasoning=result.recommendations[:3],
            layer="L12",
            session_id=self.session_id,
        )

    def code_review(self, code: str, language: str = "python") -> AMOSResult:
        """Code review with cognitive analysis."""
        if not self._initialized:
            self.initialize()

        from amos_brain import CodeReview

        result = CodeReview.analyze(code)

        return AMOSResult(
            success=True,
            data={
                "recipe": result.recipe_name,
                "analysis": result.analysis,
                "issues": result.recommendations,
            },
            law_compliant=result.law_compliant,
            confidence=result.confidence,
            reasoning=[f"Code review: {len(result.recommendations)} issues"],
            layer="L12",
            session_id=self.session_id,
        )

    def security_audit(self, system_description: str) -> AMOSResult:
        """Security audit workflow."""
        if not self._initialized:
            self.initialize()

        from amos_brain import SecurityAudit

        result = SecurityAudit.analyze(system_description)

        return AMOSResult(
            success=True,
            data={
                "recipe": result.recipe_name,
                "threats": result.recommendations,
                "analysis": result.analysis,
            },
            law_compliant=result.law_compliant,
            confidence=result.confidence,
            reasoning=["Security audit complete"],
            layer="L12",
            session_id=self.session_id,
        )

    # ===== LAYER 18: ORGANISM BRIDGE =====

    def execute(self, task: str, domain: str = "general") -> AMOSResult:
        """Execute task through Organism OS with brain guidance."""
        if not self._initialized:
            self.initialize()

        try:
            from amos_brain import execute_organism_task

            result = execute_organism_task(task, domain)

            return AMOSResult(
                success=result["status"] == "completed",
                data=result,
                law_compliant=result.get("law_compliant", True),
                confidence="high",
                reasoning=[
                    f"Task '{task}' executed via Organism OS",
                    f"Status: {result['status']}",
                ],
                layer="L18",
                session_id=self.session_id,
            )
        except Exception as e:
            return AMOSResult(
                success=False,
                data={"error": str(e)},
                law_compliant=False,
                confidence="low",
                reasoning=[f"Execution failed: {e}"],
                layer="L18",
                session_id=self.session_id,
            )

    # ===== NEW: UNIFIED FEATURE INTEGRATION (22 Advanced Features) =====

    def scan_system(self, scan_type: str = "quick") -> AMOSResult:
        """Execute deep system scan using amos_deep_system_scanner.

        Features:
        - Full drive scanning
        - Security analysis
        - File inventory
        - Storage optimization
        """
        if not self._initialized:
            self.initialize()

        try:
            from amos_deep_system_scanner import DeepSystemScanner

            scanner = DeepSystemScanner()
            result = (
                scanner.scan_workspace(".") if scan_type == "quick" else scanner.scan_full_system()
            )

            return AMOSResult(
                success=True,
                data={
                    "files_scanned": result.get("files", 0),
                    "directories": result.get("directories", 0),
                    "security_findings": result.get("security_findings", []),
                    "storage_usage": result.get("storage", {}),
                },
                law_compliant=True,
                confidence="high",
                reasoning=[f"System scan complete: {result.get('files', 0)} files analyzed"],
                layer="DEEP_SCANNER",
                session_id=self.session_id,
            )
        except Exception as e:
            return AMOSResult(
                success=False,
                data={"error": str(e)},
                law_compliant=False,
                confidence="low",
                reasoning=[f"Scan failed: {e}"],
                layer="DEEP_SCANNER",
            )

    def health_check(self) -> AMOSResult:
        """Check health of all 14 AMOS subsystems.

        Features:
        - 14 subsystem health checks
        - Integration verification
        - Performance metrics
        """
        if not self._initialized:
            self.initialize()

        try:
            from AMOS_ORGANISM_OS.system_health_monitor import SystemHealthMonitor

            monitor = SystemHealthMonitor()
            report = monitor.check_all()

            return AMOSResult(
                success=report.overall_status == "HEALTHY",
                data={
                    "overall_status": report.overall_status,
                    "subsystems": report.subsystems,
                    "healthy_count": report.healthy_count,
                    "total_subsystems": 14,
                },
                law_compliant=True,
                confidence="high",
                reasoning=[f"Health check: {report.healthy_count}/14 subsystems healthy"],
                layer="HEALTH_MONITOR",
                session_id=self.session_id,
            )
        except Exception as e:
            return AMOSResult(
                success=False,
                data={"error": str(e)},
                law_compliant=False,
                confidence="low",
                reasoning=[f"Health check failed: {e}"],
                layer="HEALTH_MONITOR",
            )

    def quantum_analysis(self, problem: str) -> AMOSResult:
        """Quantum computing analysis using quantum engine.

        Features:
        - Quantum circuit simulation
        - Qubit operations
        - Superposition analysis
        """
        if not self._initialized:
            self.initialize()

        try:
            # Import from clawspring quantum engine
            import sys

            sys.path.insert(0, "clawspring")
            from amos_tech_quantum_engine import QuantumEngine

            engine = QuantumEngine()
            result = engine.analyze(problem)

            return AMOSResult(
                success=True,
                data={
                    "quantum_solution": result.get("solution"),
                    "qubits_used": result.get("qubits", 0),
                    "algorithm": result.get("algorithm"),
                },
                law_compliant=True,
                confidence="high",
                reasoning=["Quantum analysis complete"],
                layer="QUANTUM_ENGINE",
                session_id=self.session_id,
            )
        except Exception as e:
            return AMOSResult(
                success=False,
                data={"error": str(e)},
                law_compliant=False,
                confidence="low",
                reasoning=[f"Quantum analysis unavailable: {e}"],
                layer="QUANTUM_ENGINE",
            )

    def legal_compliance_check(self, document: str, jurisdiction: str = "VN") -> AMOSResult:
        """Check legal compliance using VN legal engine.

        Features:
        - Vietnam legal compliance
        - Regulatory validation
        - Document analysis
        """
        if not self._initialized:
            self.initialize()

        try:
            import sys

            sys.path.insert(0, "clawspring")
            from amos_vn_legal_engine import LegalEngine

            engine = LegalEngine()
            result = engine.check_compliance(document, jurisdiction)

            return AMOSResult(
                success=True,
                data={
                    "compliant": result.get("compliant", False),
                    "violations": result.get("violations", []),
                    "recommendations": result.get("recommendations", []),
                    "jurisdiction": jurisdiction,
                },
                law_compliant=result.get("compliant", False),
                confidence="high",
                reasoning=[f"Legal check: {len(result.get('violations', []))} violations found"],
                layer="LEGAL_ENGINE",
                session_id=self.session_id,
            )
        except Exception as e:
            return AMOSResult(
                success=False,
                data={"error": str(e)},
                law_compliant=False,
                confidence="low",
                reasoning=[f"Legal engine unavailable: {e}"],
                layer="LEGAL_ENGINE",
            )

    def deploy_production(self, config: dict) -> AMOSResult:
        """Deploy using production orchestrator.

        Features:
        - Kubernetes deployment
        - Docker orchestration
        - Health monitoring
        """
        if not self._initialized:
            self.initialize()

        try:
            from amos_production_orchestrator import ProductionOrchestrator

            orchestrator = ProductionOrchestrator()
            result = orchestrator.deploy(config)

            return AMOSResult(
                success=result.get("success", False),
                data={
                    "deployment_id": result.get("deployment_id"),
                    "status": result.get("status"),
                    "endpoints": result.get("endpoints", []),
                },
                law_compliant=True,
                confidence="high" if result.get("success") else "low",
                reasoning=[f"Deployment: {result.get('status', 'unknown')}"],
                layer="PRODUCTION_ORCHESTRATOR",
                session_id=self.session_id,
            )
        except Exception as e:
            return AMOSResult(
                success=False,
                data={"error": str(e)},
                law_compliant=False,
                confidence="low",
                reasoning=[f"Deployment failed: {e}"],
                layer="PRODUCTION_ORCHESTRATOR",
            )

    def discover_modules(self) -> AMOSResult:
        """Discover all AMOS modules using unified integrator.

        Features:
        - Module discovery
        - Dependency graph
        - Tier classification
        """
        if not self._initialized:
            self.initialize()

        try:
            from pathlib import Path

            from amos_unified_system_integrator import AMOSModuleDiscovery

            discovery = AMOSModuleDiscovery(Path("."))
            modules = discovery.discover_all()

            return AMOSResult(
                success=True,
                data={
                    "modules_discovered": len(modules),
                    "by_tier": {
                        "CRITICAL": len([m for m in modules.values() if m.tier.name == "CRITICAL"]),
                        "ESSENTIAL": len(
                            [m for m in modules.values() if m.tier.name == "ESSENTIAL"]
                        ),
                        "IMPORTANT": len(
                            [m for m in modules.values() if m.tier.name == "IMPORTANT"]
                        ),
                    },
                },
                law_compliant=True,
                confidence="high",
                reasoning=[f"Discovered {len(modules)} modules"],
                layer="UNIFIED_INTEGRATOR",
                session_id=self.session_id,
            )
        except Exception as e:
            return AMOSResult(
                success=False,
                data={"error": str(e)},
                law_compliant=False,
                confidence="low",
                reasoning=[f"Module discovery failed: {e}"],
                layer="UNIFIED_INTEGRATOR",
            )

    def list_all_features(self) -> dict:
        """List all 22 integrated features."""
        return {
            "core_features": [
                "think",
                "decide",
                "validate",
                "execute",
                "architecture_decision",
                "code_review",
                "security_audit",
            ],
            "advanced_features": [
                "scan_system",
                "health_check",
                "quantum_analysis",
                "legal_compliance_check",
                "deploy_production",
                "discover_modules",
            ],
            "subsystem_integrations": [
                "Brain",
                "Senses",
                "Immune",
                "Blood",
                "Skeleton",
                "Muscle",
                "Metabolism",
                "World Model",
                "Social Engine",
                "Life Engine",
                "Legal Brain",
                "Quantum Layer",
                "Factory",
                "Interfaces",
            ],
            "total_features": 22,
        }

    # ===== LAYER 8: META-COGNITIVE =====

    def orchestrate(self, goal: str, auto_execute: bool = False) -> AMOSResult:
        """Orchestrate multi-step workflow."""
        if not self._initialized:
            self.initialize()

        from amos_brain import get_meta_controller

        mc = get_meta_controller()
        plan = mc.orchestrate(goal, auto_execute=auto_execute)

        return AMOSResult(
            success=True,
            data={
                "plan_id": plan.plan_id,
                "subtasks": plan.subtasks,
                "estimated_duration": plan.estimated_duration,
            },
            law_compliant=True,
            confidence="high",
            reasoning=[f"Created plan with {len(plan.subtasks)} subtasks"],
            layer="L8",
            session_id=self.session_id,
        )

    # ===== UTILITY =====

    def status(self) -> Dict[str, Any]:
        """Get full system status."""
        if not self._initialized:
            return {"status": "not_initialized", "layers": 0}

        return {
            "status": "operational",
            "layers": 17,
            "engines": 26,
            "laws": 6,
            "recipes": 6,
            "session_id": self.session_id,
            "version": "14.0.0",
        }


# Global instance
_amos_instance: Optional[AMOS] = None


def get_amos() -> AMOS:
    """Get global AMOS instance."""
    global _amos_instance
    if _amos_instance is None:
        _amos_instance = AMOS()
        _amos_instance.initialize()
    return _amos_instance


# Convenience functions for direct usage
def think(query: str, domain: str = "general") -> AMOSResult:
    """Quick think function."""
    return get_amos().think(query, domain)


def decide(problem: str, options: list[str] = None) -> AMOSResult:
    """Quick decide function."""
    return get_amos().decide(problem, options)


def validate(action: str) -> AMOSResult:
    """Quick validate function."""
    return get_amos().validate(action)


if __name__ == "__main__":
    # Demo
    print("=" * 70)
    print("AMOS Unified API Demo")
    print("=" * 70)
    print()

    amos = AMOS()

    # Initialize
    print("1. Initializing AMOS...")
    result = amos.initialize()
    print(f"   Status: {result.success}")
    print(f"   Engines: {result.data.get('engines', 0)}")
    print(f"   Layers: {result.data.get('layers', 0)}")
    print()

    # Think
    print("2. Brain thinking...")
    result = amos.think("Should we implement caching?")
    print(f"   Success: {result.success}")
    print(f"   Law compliant: {result.law_compliant}")
    print(f"   Confidence: {result.confidence}")
    print()

    # Architecture decision
    print("3. Architecture decision...")
    result = amos.architecture_decision("Cache strategy")
    print(f"   Recipe: {result.data.get('recipe', 'N/A')}")
    print(f"   Recommendations: {len(result.data.get('recommendations', []))}")
    print()

    # Status
    print("4. System status...")
    status = amos.status()
    print(f"   Status: {status['status']}")
    print(f"   Version: {status['version']}")
    print()

    print("=" * 70)
    print("AMOS Unified API - Ready for production")
    print("=" * 70)
