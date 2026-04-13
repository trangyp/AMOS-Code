#!/usr/bin/env python3
"""
AMOS Brain-Organism Execution Bridge

Connects the standalone amos_brain (cognition) to AMOS Organism OS (execution).

Flow:
    Brain Decision → Bridge Translation → Organism Execution → Result Feedback

Subsystems Connected:
    - BRAIN (amos_brain package) → Analysis, reasoning, decisions
    - MUSCLE → Code execution, commands, deployment
    - BLOOD → Resource allocation, budgeting
    - METABOLISM → Data processing, transformations
    - IMMUNE → Safety checks, compliance
    - SENSES → Environment scanning, input gathering

Usage:
    bridge = BrainOrganismBridge()
    result = bridge.execute_decision("Refactor the auth module")
"""
from __future__ import annotations

import sys
import os
import json
from pathlib import Path
from typing import Any
from dataclasses import dataclass, field

# Add organism to path
sys.path.insert(0, str(Path(__file__).parent / "AMOS_ORGANISM_OS"))

# Import standalone brain
sys.path.insert(0, str(Path(__file__).parent))
from amos_brain import get_amos_integration
from amos_brain.cookbook import ArchitectureDecision, ProjectPlanner, ProblemDiagnosis

# Import organism subsystems (with fallback stubs)
try:
    from organism import AmosOrganism
    _organism_available = True
except ImportError:
    _organism_available = False
    print("[Bridge] Organism OS not fully available, using execution stub")


@dataclass
class ExecutionResult:
    """Result from executing a brain decision through organism."""
    decision: str
    brain_analysis: dict
    organism_action: str
    status: str  # "success", "failed", "blocked"
    output: str
    resources_used: dict = field(default_factory=dict)
    execution_time_ms: int = 0


class BrainOrganismBridge:
    """
    Bridge between amos_brain (cognition) and organism (execution).
    
    Translates cognitive decisions into organism actions and executes them.
    """
    
    def __init__(self):
        self.amos = get_amos_integration()
        self.organism = None
        
        if _organism_available:
            try:
                self.organism = AmosOrganism()
                print("[Bridge] Connected to AMOS Organism OS")
            except Exception as e:
                print(f"[Bridge] Organism init failed: {e}")
    
    def analyze_and_execute(self, task: str, context: dict | None = None) -> ExecutionResult:
        """
        Full pipeline: Brain analysis → Organism execution.
        
        Args:
            task: Task description
            context: Optional context (files, constraints, etc.)
            
        Returns:
            ExecutionResult with analysis and execution details
        """
        # Step 1: Brain analysis
        print(f"[Bridge] Analyzing: {task[:50]}...")
        analysis = self.amos.analyze_with_rules(task)
        
        # Step 2: Route to appropriate execution
        action_type = self._classify_action(task, analysis)
        print(f"[Bridge] Classified as: {action_type}")
        
        # Step 3: Execute through organism
        if action_type == "code_execution":
            result = self._execute_code_task(task, analysis, context)
        elif action_type == "architecture_decision":
            result = self._execute_architecture_task(task, analysis, context)
        elif action_type == "diagnosis":
            result = self._execute_diagnosis_task(task, analysis, context)
        else:
            result = self._execute_generic_task(task, analysis, context)
        
        return result
    
    def _classify_action(self, task: str, analysis: dict) -> str:
        """Classify task type for routing to appropriate subsystem."""
        task_lower = task.lower()
        
        # Check task patterns
        if any(kw in task_lower for kw in ["refactor", "implement", "write code", "create function"]):
            return "code_execution"
        
        if any(kw in task_lower for kw in ["should we", "architecture", "design", "choose"]):
            return "architecture_decision"
        
        if any(kw in task_lower for kw in ["debug", "fix", "error", "issue", "problem"]):
            return "diagnosis"
        
        if any(kw in task_lower for kw in ["analyze", "review", "assess"]):
            return "analysis"
        
        return "generic"
    
    def _execute_code_task(self, task: str, analysis: dict, context: dict | None) -> ExecutionResult:
        """Execute code-related task through MUSCLE subsystem."""
        print("[Bridge] Routing to MUSCLE (code execution)...")
        
        # Extract code recommendations from analysis
        recommendations = analysis.get("recommendations", [])
        code_action = recommendations[0] if recommendations else "No specific action"
        
        # Simulate execution (would call MUSCLE.code_runner in full implementation)
        output = f"Code execution simulated:\n  Action: {code_action[:100]}...\n  Files modified: 0 (stub)"
        
        return ExecutionResult(
            decision=task,
            brain_analysis=analysis,
            organism_action="MUSCLE.execute_code",
            status="success",
            output=output,
            resources_used={"compute": "medium", "time": "2min"}
        )
    
    def _execute_architecture_task(self, task: str, analysis: dict, context: dict | None) -> ExecutionResult:
        """Execute architecture decision through full cognitive workflow."""
        print("[Bridge] Running ArchitectureDecision workflow...")
        
        # Use cookbook workflow
        result = ArchitectureDecision.run(task, context)
        
        output = f"Architecture analysis complete:\n"
        output += f"  Confidence: {result.confidence:.0%}\n"
        output += f"  Recommendations: {len(result.recommendations)}\n"
        for i, rec in enumerate(result.recommendations[:3], 1):
            output += f"    {i}. {rec[:80]}...\n"
        
        return ExecutionResult(
            decision=task,
            brain_analysis=analysis,
            organism_action="BRAIN.cookbook.ArchitectureDecision",
            status="success",
            output=output,
            resources_used={"compute": "high", "time": "5min"}
        )
    
    def _execute_diagnosis_task(self, task: str, analysis: dict, context: dict | None) -> ExecutionResult:
        """Execute diagnosis through SENSES + BRAIN."""
        print("[Bridge] Running ProblemDiagnosis workflow...")
        
        # Use cookbook workflow
        symptoms = context.get("symptoms", []) if context else []
        result = ProblemDiagnosis.run(task, symptoms=symptoms)
        
        output = f"Diagnosis complete:\n"
        output += f"  Findings: {len(result.recommendations)}\n"
        for rec in result.recommendations[:3]:
            output += f"    - {rec[:80]}...\n"
        
        return ExecutionResult(
            decision=task,
            brain_analysis=analysis,
            organism_action="SENSES.scan + BRAIN.diagnose",
            status="success",
            output=output
        )
    
    def _execute_generic_task(self, task: str, analysis: dict, context: dict | None) -> ExecutionResult:
        """Execute generic task through default pipeline."""
        print("[Bridge] Executing generic task...")
        
        # Format analysis output
        output = f"Analysis Results:\n"
        
        if "rule_of_two" in analysis:
            r2 = analysis["rule_of_two"]
            output += f"\nRule of 2 (Dual Perspective):\n"
            output += f"  Confidence: {r2.get('confidence', 0):.0%}\n"
        
        if "rule_of_four" in analysis:
            r4 = analysis["rule_of_four"]
            output += f"\nRule of 4 (Four Quadrants):\n"
            output += f"  Coverage: {r4.get('completeness_score', 0):.0%}\n"
        
        output += f"\nRecommendations:\n"
        for rec in analysis.get("recommendations", [])[:3]:
            output += f"  • {rec[:80]}...\n"
        
        return ExecutionResult(
            decision=task,
            brain_analysis=analysis,
            organism_action="BRAIN.analyze",
            status="success",
            output=output
        )
    
    def get_system_status(self) -> dict:
        """Get combined brain + organism status."""
        brain_status = self.amos.get_status()
        
        return {
            "brain": {
                "initialized": brain_status.get("initialized"),
                "engines": brain_status.get("engines_count"),
                "laws": len(brain_status.get("laws_active", [])),
            },
            "organism": {
                "connected": self.organism is not None,
                "subsystems": 14 if self.organism else 0,
            },
            "bridge": {
                "status": "active",
                "version": "3.05.5",
            }
        }


def demo_bridge():
    """Demonstrate brain-organism bridge functionality."""
    print("=" * 70)
    print("AMOS BRAIN-ORGANISM BRIDGE DEMONSTRATION")
    print("=" * 70)
    
    bridge = BrainOrganismBridge()
    
    # Show system status
    print("\n[System Status]")
    status = bridge.get_system_status()
    print(f"  Brain: {status['brain']['engines']} engines, {status['brain']['laws']} laws")
    print(f"  Organism: {'Connected' if status['organism']['connected'] else 'Stub mode'}")
    print(f"  Bridge: {status['bridge']['status']}")
    
    # Demo 1: Architecture decision
    print("\n" + "-" * 70)
    print("DEMO 1: Architecture Decision")
    print("-" * 70)
    result = bridge.analyze_and_execute(
        "Should we migrate from monolith to microservices?",
        context={"current_stack": "Django monolith", "team_size": 12}
    )
    print(f"\nStatus: {result.status}")
    print(f"Action: {result.organism_action}")
    print(f"Output:\n{result.output}")
    
    # Demo 2: Problem diagnosis
    print("\n" + "-" * 70)
    print("DEMO 2: Problem Diagnosis")
    print("-" * 70)
    result = bridge.analyze_and_execute(
        "Database connection pool exhaustion",
        context={"symptoms": ["500 errors", "high latency"]}
    )
    print(f"\nStatus: {result.status}")
    print(f"Action: {result.organism_action}")
    print(f"Output:\n{result.output}")
    
    # Demo 3: Code execution
    print("\n" + "-" * 70)
    print("DEMO 3: Code Task")
    print("-" * 70)
    result = bridge.analyze_and_execute(
        "Refactor the authentication module to use JWT tokens"
    )
    print(f"\nStatus: {result.status}")
    print(f"Action: {result.organism_action}")
    print(f"Output:\n{result.output}")
    
    print("\n" + "=" * 70)
    print("BRIDGE DEMONSTRATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    demo_bridge()
