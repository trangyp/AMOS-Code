#!/usr/bin/env python3
"""
AMOS Unified API (Layer 19)
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
from __future__ import annotations

from typing import Any, Optional, List, Dict
from dataclasses import dataclass


@dataclass
class AMOSResult:
    """Standard result wrapper for all AMOS operations."""
    success: bool
    data: Any
    law_compliant: bool
    confidence: str
    reasoning: List[str]
    layer: str  # Which layer handled this
    session_id: Optional[str] = None


class AMOS:
    """
    Unified AMOS Brain API - Access all 17+ layers through one interface.
    
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
                goal="AMOS Unified API Session",
                domain="general"
            )
            self._initialized = True
            
            return AMOSResult(
                success=True,
                data={"engines": len(self._brain.list_engines()), "layers": 17},
                law_compliant=True,
                confidence="high",
                reasoning=["Brain loaded", "State manager ready", "Session created"],
                layer="L1-L7",
                session_id=self.session_id
            )
        except Exception as e:
            return AMOSResult(
                success=False,
                data={"error": str(e)},
                law_compliant=False,
                confidence="low",
                reasoning=[f"Initialization failed: {e}"],
                layer="INIT"
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
                "metadata": response.metadata
            },
            law_compliant=response.law_compliant,
            confidence=response.confidence,
            reasoning=response.reasoning[:3],
            layer="L10",
            session_id=self.session_id
        )
    
    def decide(self, problem: str, options: Optional[List[str]] = None) -> AMOSResult:
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
                "confidence": result.confidence
            },
            law_compliant=True,
            confidence=result.confidence,
            reasoning=[f"Decision: {result.recommendation}"],
            layer="L10",
            session_id=self.session_id
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
            session_id=self.session_id
        )
    
    # ===== LAYER 12: COGNITIVE COOKBOOK =====
    
    def architecture_decision(
        self,
        question: str,
        context: Optional[Dict] = None,
        options: Optional[List[str]] = None
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
                "recommendations": result.recommendations
            },
            law_compliant=result.law_compliant,
            confidence=result.confidence,
            reasoning=result.recommendations[:3],
            layer="L12",
            session_id=self.session_id
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
                "issues": result.recommendations
            },
            law_compliant=result.law_compliant,
            confidence=result.confidence,
            reasoning=[f"Code review: {len(result.recommendations)} issues"],
            layer="L12",
            session_id=self.session_id
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
                "analysis": result.analysis
            },
            law_compliant=result.law_compliant,
            confidence=result.confidence,
            reasoning=["Security audit complete"],
            layer="L12",
            session_id=self.session_id
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
                reasoning=[f"Executed via {result.get('subsystem_result', {}).get('subsystem', 'unknown')}"],
                layer="L18",
                session_id=self.session_id
            )
        except Exception as e:
            return AMOSResult(
                success=False,
                data={"error": str(e)},
                law_compliant=False,
                confidence="low",
                reasoning=[f"Execution error: {e}"],
                layer="L18",
                session_id=self.session_id
            )
    
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
                "estimated_duration": plan.estimated_duration
            },
            law_compliant=True,
            confidence="high",
            reasoning=[f"Created plan with {len(plan.subtasks)} subtasks"],
            layer="L8",
            session_id=self.session_id
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
            "version": "14.0.0"
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


def decide(problem: str, options: Optional[List[str]] = None) -> AMOSResult:
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
