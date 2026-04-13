"""
Brain-Muscle Bridge (06_MUSCLE Integration)
=============================================

Connects the AMOS cognitive runtime (01_BRAIN) to the execution engine (06_MUSCLE).
Enables intelligent task execution with 6-layer cognitive processing.

Owner: Trang
Version: 1.0.0
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from amos_worker_engine import (
    AmosWorkerEngine,
    WorkerResult,
    get_worker_engine,
    CodeWorker,
    FileWorker,
)


@dataclass
class CognitiveTask:
    """A task with cognitive processing requirements."""
    id: str
    description: str
    cognitive_mode: str  # exploratory_mapping, diagnostic_analysis, etc.
    execution_plan: Dict[str, Any]
    context: Dict[str, Any]
    immune_validated: bool = False


@dataclass
class CognitiveExecutionResult:
    """Result of cognitively-enhanced execution."""
    task_id: str
    success: bool
    cognitive_analysis: str
    execution_output: str
    artifacts: List[Path]
    law_compliance: Dict[str, Any]
    metadata: Dict[str, Any]


class BrainMuscleBridge:
    """
    Bridge between BRAIN (cognitive runtime) and MUSCLE (execution).
    
    This enables the organism to:
    1. Analyze tasks using 6-layer cognitive architecture
    2. Generate execution plans with quality checks
    3. Execute plans via the muscle subsystem
    4. Validate results against global laws
    """
    
    def __init__(self, organism_root: Optional[Path] = None):
        if organism_root is None:
            organism_root = Path(__file__).parent.parent
        
        self.root = organism_root
        self.worker = get_worker_engine(organism_root)
        self.code_worker = CodeWorker(self.worker)
        self.file_worker = FileWorker(self.worker)
        
        # Check cognitive runtime availability
        self.cognitive_available = self.worker.runtime is not None
    
    def execute_with_cognition(
        self,
        task_description: str,
        mode: str = "diagnostic_analysis",
        context: Optional[Dict] = None
    ) -> CognitiveExecutionResult:
        """
        Execute a task with full cognitive processing.
        
        Flow:
        1. Analyze task using cognitive runtime (BRAIN)
        2. Generate execution plan
        3. Execute via muscle (MUSCLE)
        4. Validate and return results
        """
        if not self.cognitive_available:
            return self._fallback_execution(task_description, context)
        
        # Step 1: Cognitive analysis
        analysis = self.worker.runtime.think(task_description, mode)
        synthesis = analysis.get("synthesis", {})
        
        # Step 2: Extract recommendations as execution plan
        plan = self._convert_analysis_to_plan(analysis, task_description)
        
        # Step 3: Execute the plan
        worker_result = self.worker.execute_plan(plan, context)
        
        # Step 4: Build result with cognitive metadata
        return CognitiveExecutionResult(
            task_id=plan.get("task_id", "unknown"),
            success=worker_result.success,
            cognitive_analysis=analysis.get("explanation", ""),
            execution_output=worker_result.output,
            artifacts=worker_result.artifacts,
            law_compliance={
                "meta_logic_compliant": synthesis.get("meta_logic_compliant", False),
                "structural_integrity": synthesis.get("structural_integrity", {}),
            },
            metadata={
                "cognitive_mode": mode,
                "has_runtime": True,
                **worker_result.metadata
            }
        )
    
    def _convert_analysis_to_plan(
        self,
        analysis: Dict[str, Any],
        original_task: str
    ) -> Dict[str, Any]:
        """Convert cognitive analysis to executable plan."""
        synthesis = analysis.get("synthesis", {})
        
        # Extract domain and recommendations
        problem = synthesis.get("problem_structure", {})
        domain = problem.get("domain", "general")
        
        # Build steps based on domain
        steps = []
        
        if domain == "engineering":
            steps = [
                {"action": "analyze", "topic": original_task},
                {"action": "generate_code", "prompt": original_task},
            ]
        elif domain == "biology":
            steps = [
                {"action": "analyze", "topic": original_task},
                {"action": "audit", "target": original_task},
            ]
        else:
            steps = [
                {"action": "analyze", "topic": original_task},
            ]
        
        return {
            "task_id": analysis.get("working_memory_id", "task_001"),
            "steps": steps,
            "domain": domain,
        }
    
    def _fallback_execution(
        self,
        task_description: str,
        context: Optional[Dict]
    ) -> CognitiveExecutionResult:
        """Execute without cognitive runtime (fallback)."""
        # Direct execution via file worker
        result = self.file_worker.write(
            f"# Task: {task_description}\n# Executed without cognitive runtime\n",
            "output/fallback_task.txt"
        )
        
        return CognitiveExecutionResult(
            task_id="fallback_001",
            success=result.success,
            cognitive_analysis="Cognitive runtime not available - fallback mode",
            execution_output=result.output,
            artifacts=result.artifacts,
            law_compliance={},
            metadata={"fallback": True}
        )
    
    def generate_architecture(
        self,
        requirements: str,
        target_file: Optional[str] = None
    ) -> CognitiveExecutionResult:
        """
        Generate system architecture using cognitive design mode.
        
        Uses the full 6-layer cognitive architecture:
        - Meta-logic validation
        - Structural reasoning
        - UBI alignment check
        - Quality validation
        """
        if not self.cognitive_available:
            return self._fallback_execution(requirements, {})
        
        # Use design_and_architecture mode
        analysis = self.worker.runtime.think(
            requirements,
            "design_and_architecture"
        )
        
        synthesis = analysis.get("synthesis", {})
        
        # Generate code/architecture
        if target_file:
            code_result = self.code_worker.generate(requirements, target_file)
            artifacts = code_result.artifacts
            success = code_result.success
        else:
            artifacts = []
            success = True
        
        return CognitiveExecutionResult(
            task_id=f"arch_{hash(requirements) % 10000:04d}",
            success=success,
            cognitive_analysis=analysis.get("explanation", ""),
            execution_output="Architecture generated",
            artifacts=artifacts,
            law_compliance={
                "meta_logic_compliant": synthesis.get("meta_logic_compliant"),
                "structural_integrity": synthesis.get("structural_integrity"),
            },
            metadata={
                "mode": "design_and_architecture",
                "domain": synthesis.get("problem_structure", {}).get("domain"),
            }
        )
    
    def audit_and_execute(
        self,
        decision: str,
        rationale: str,
        action: Optional[Dict] = None
    ) -> CognitiveExecutionResult:
        """
        Audit a decision before executing.
        
        Uses audit_and_critique mode to validate against global laws,
        then optionally executes if validation passes.
        """
        if not self.cognitive_available:
            return self._fallback_execution(decision, {})
        
        # Audit first
        analysis = self.worker.runtime.think(
            f"Decision: {decision}\nRationale: {rationale}",
            "audit_and_critique"
        )
        
        synthesis = analysis.get("synthesis", {})
        compliance = synthesis.get("structural_integrity", {})
        
        # Check if we should proceed
        meta_compliant = synthesis.get("meta_logic_compliant", False)
        
        if not meta_compliant:
            return CognitiveExecutionResult(
                task_id=f"audit_{hash(decision) % 10000:04d}",
                success=False,
                cognitive_analysis=analysis.get("explanation", ""),
                execution_output="Execution blocked: failed law compliance check",
                artifacts=[],
                law_compliance={
                    "meta_logic_compliant": False,
                    "structural_integrity": compliance,
                },
                metadata={"blocked_by_audit": True}
            )
        
        # Execute if action provided and audit passed
        if action:
            plan = {"steps": [action]}
            exec_result = self.worker.execute_plan(plan)
            success = exec_result.success
            output = exec_result.output
            artifacts = exec_result.artifacts
        else:
            success = True
            output = "Audit passed, no action executed"
            artifacts = []
        
        return CognitiveExecutionResult(
            task_id=f"audit_{hash(decision) % 10000:04d}",
            success=success,
            cognitive_analysis=analysis.get("explanation", ""),
            execution_output=output,
            artifacts=artifacts,
            law_compliance={
                "meta_logic_compliant": True,
                "structural_integrity": compliance,
            },
            metadata={"audit_passed": True}
        )


# Global bridge instance
_BRIDGE: Optional[BrainMuscleBridge] = None


def get_brain_muscle_bridge(
    organism_root: Optional[Path] = None
) -> BrainMuscleBridge:
    """Get or create global brain-muscle bridge instance."""
    global _BRIDGE
    if _BRIDGE is None:
        _BRIDGE = BrainMuscleBridge(organism_root)
    return _BRIDGE


if __name__ == "__main__":
    print("Brain-Muscle Bridge (06_MUSCLE Integration)")
    print("=" * 50)
    
    bridge = get_brain_muscle_bridge()
    
    print(f"Cognitive runtime available: {bridge.cognitive_available}")
    
    # Test execution with cognition
    if bridge.cognitive_available:
        print("\n[TEST] Executing with cognition...")
        result = bridge.execute_with_cognition(
            "Analyze the codebase structure and suggest improvements",
            "diagnostic_analysis"
        )
        print(f"Success: {result.success}")
        print(f"Artifacts: {result.artifacts}")
        print(f"Law compliance: {result.law_compliance}")
    else:
        print("\n[Cognitive runtime not available - skipping test]")
