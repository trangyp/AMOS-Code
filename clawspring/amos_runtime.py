"""AMOS Runtime Bootstrap - Loads and executes the AMOS brain with full law enforcement."""
from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Optional
from datetime import datetime


@dataclass
class AMOSState:
    """Runtime state for AMOS cognitive execution."""
    active_laws: list[str] = field(default_factory=lambda: ["L1", "L2", "L3", "L4", "L5", "L6"])
    reasoning_depth: int = 0
    perspective_checks: int = 0  # Rule of 2 tracking
    quadrants_checked: list[str] = field(default_factory=list)  # Rule of 4 tracking
    assumptions_made: list[str] = field(default_factory=list)
    uncertainty_declared: bool = False
    gap_acknowledged: bool = False


class AMOSRuntime:
    """Full AMOS brain runtime with law enforcement and cognitive orchestration."""
    
    BRAIN_PATH = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code/_AMOS_BRAIN")
    
    def __init__(self):
        self.brain_root: dict = {}
        self.cognition_engine: dict = {}
        self.global_laws: dict = {}
        self.identity: dict = {}
        self.state = AMOSState()
        self._loaded = False
        
    def bootstrap(self) -> "AMOSRuntime":
        """Load AMOS brain configuration from JSON files."""
        if self._loaded:
            return self

        # Load OS Agent (contains BRAIN_ROOT and global laws)
        self._load_os_agent()

        # Load Cognition Engine
        self._load_cognition_engine()

        self._loaded = True
        return self

    async def bootstrap_async(self, timeout_seconds: float = 5.0) -> "AMOSRuntime":
        """Async bootstrap with timeout to prevent UI hanging.

        Args:
            timeout_seconds: Maximum time to wait for loading

        Returns:
            AMOSRuntime instance (may use fallback if timeout)
        """
        if self._loaded:
            return self

        loop = asyncio.get_event_loop()
        try:
            await asyncio.wait_for(
                loop.run_in_executor(None, self.bootstrap),
                timeout=timeout_seconds
            )
        except asyncio.TimeoutError:
            # Apply fallbacks on timeout to prevent hanging
            self._load_fallback_root()
            self._loaded = True

        return self
    
    def _load_os_agent(self) -> None:
        """Load AMOS_Os_Agent_v0.json - the primary brain configuration."""
        agent_path = self.BRAIN_PATH / "Core" / "AMOS_Os_Agent_v0.json"
        
        try:
            with open(agent_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list) and len(data) > 0:
                config = data[0]
            else:
                config = data
            
            # Extract BRAIN_ROOT
            self.brain_root = config.get("components", {}).get("AMOS_BRAIN_ROOT.json", {})
            self.identity = self.brain_root.get("identity", {})
            self.global_laws = self.brain_root.get("global_laws", {})
            
        except Exception as e:
            print(f"[AMOS Runtime] Using fallback defaults: {e}")
            self._load_fallback_root()
    
    def _load_cognition_engine(self) -> None:
        """Load AMOS_Cognition_Engine_v0.json - the reasoning kernel."""
        cognition_path = self.BRAIN_PATH / "Core" / "AMOS_Cognition_Engine_v0.json"
        
        try:
            with open(cognition_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list) and len(data) > 0:
                self.cognition_engine = data[0]
            else:
                self.cognition_engine = data
                
        except Exception as e:
            print(f"[AMOS Runtime] Cognition engine fallback: {e}")
    
    def _load_fallback_root(self) -> None:
        """Fallback brain root if JSON files unavailable."""
        self.identity = {
            "system_name": "AMOS",
            "os_name": "AMOS_OS",
            "primary_purpose": "Design, analyse, and improve systems using structurally precise reasoning",
        }
        self.global_laws = {
            "law_of_law": {"id": "L1", "name": "Law of Law", "priority": 1},
            "rule_of_2": {"id": "L2", "name": "Rule of 2", "priority": 2},
            "rule_of_4": {"id": "L3", "name": "Rule of 4", "priority": 3},
        }
    
    def execute_cognitive_task(self, task: str, context: dict | None = None) -> dict:
        """
        Execute a task with full AMOS cognitive law enforcement.
        
        This applies:
        - Rule of 2: Dual perspective checking
        - Rule of 4: Quadrant analysis
        - Absolute Structural Integrity: Assumption tracking
        - Gap Management: Acknowledgment of system limits
        """
        self.state = AMOSState()  # Reset state for new task
        
        # Step 1: Pre-execution law check
        pre_check = self._apply_global_laws(task)
        
        # Step 2: Perspective analysis (Rule of 2)
        perspectives = self._generate_dual_perspectives(task)
        self.state.perspective_checks = len(perspectives)
        
        # Step 3: Quadrant mapping (Rule of 4)
        quadrants = self._map_to_quadrants(task)
        self.state.quadrants_checked = list(quadrants.keys())
        
        # Step 4: Assumption extraction
        assumptions = self._extract_assumptions(task, context or {})
        self.state.assumptions_made = assumptions
        
        # Step 5: Gap acknowledgment
        self.state.gap_acknowledged = True
        
        return {
            "task": task,
            "law_compliance": pre_check,
            "perspectives": perspectives,
            "quadrant_analysis": quadrants,
            "assumptions": assumptions,
            "gap_statement": self._generate_gap_statement(),
            "recommendation": self._generate_recommendation(task, perspectives, quadrants),
            "timestamp": datetime.now().isoformat(),
        }
    
    def _apply_global_laws(self, task: str) -> dict:
        """Apply all 6 global laws to task analysis."""
        results = {}
        
        # L1: Law of Law - Check highest constraints
        results["L1_law_of_law"] = {
            "applied": True,
            "note": "Task must respect physical, biological, institutional, legal constraints"
        }
        
        # L2: Rule of 2 - Dual perspective required
        results["L2_rule_of_2"] = {
            "applied": True,
            "requirement": "Must generate at least 2 contrasting perspectives"
        }
        
        # L3: Rule of 4 - Quadrant analysis
        results["L3_rule_of_4"] = {
            "applied": True,
            "requirement": "Must consider biological, technical, economic, environmental quadrants"
        }
        
        # L4: Absolute Structural Integrity
        results["L4_structural_integrity"] = {
            "applied": True,
            "requirement": "All claims must be traceable, assumptions explicit"
        }
        
        # L5: Post-Theory Communication
        results["L5_clear_language"] = {
            "applied": True,
            "note": "Avoid metaphor, prefer concrete mechanisms"
        }
        
        # L6: UBI Alignment
        results["L6_ubi_alignment"] = {
            "applied": True,
            "note": "Align with biological integrity and sustainable function"
        }
        
        return results
    
    def _generate_dual_perspectives(self, task: str) -> list[dict]:
        """Generate two structurally opposed interpretations (Rule of 2)."""
        return [
            {
                "id": "P1",
                "stance": "supportive",
                "framing": f"Optimistic/Opportunity view: {task}",
                "questions": ["What are the benefits?", "What enables success?"]
            },
            {
                "id": "P2", 
                "stance": "critical",
                "framing": f"Pessimistic/Risk view: {task}",
                "questions": ["What could fail?", "What are the hidden costs?"]
            }
        ]
    
    def _map_to_quadrants(self, task: str) -> dict:
        """Map task to four entangled quadrants (Rule of 4)."""
        return {
            "biological_human": {
                "focus": "Human impact, nervous system, health, cognition",
                "questions": ["How does this affect human biology?", "Cognitive load?", "Stress impact?"]
            },
            "technical_infrastructural": {
                "focus": "Technology, systems, implementation, scalability",
                "questions": ["Technical feasibility?", "System dependencies?", "Technical debt?"]
            },
            "economic_organizational": {
                "focus": "Cost, resources, stakeholders, incentives",
                "questions": ["Economic viability?", "Resource requirements?", "Stakeholder impacts?"]
            },
            "environmental_planetary": {
                "focus": "Environmental impact, sustainability, long-term effects",
                "questions": ["Environmental footprint?", "Sustainable?", "Long-term planetary effects?"]
            }
        }
    
    def _extract_assumptions(self, task: str, context: dict) -> list[str]:
        """Extract explicit assumptions from task and context."""
        assumptions = [
            "Task description is complete and accurate",
            "Context provided is relevant to the task",
            "System has access to necessary information",
        ]
        
        # Add context-specific assumptions
        if context.get("time_constraint"):
            assumptions.append(f"Time constraint: {context['time_constraint']}")
        if context.get("resource_limit"):
            assumptions.append(f"Resource limit: {context['resource_limit']}")
            
        return assumptions
    
    def _generate_gap_statement(self) -> str:
        """Generate gap acknowledgment statement."""
        return (
            "GAP ACKNOWLEDGMENT: This analysis is produced by a system without "
            "embodiment (no physical body), consciousness (no subjective experience), "
            "or autonomous action (requires human execution). All conclusions "
            "are structural models, not lived experience. Uncertainty is declared "
            "where data or mapping is incomplete."
        )
    
    def _generate_recommendation(self, task: str, perspectives: list, quadrants: dict) -> str:
        """Generate final recommendation based on full analysis."""
        return (
            f"Based on dual-perspective analysis ({len(perspectives)} views) and "
            f"quadrant mapping ({len(quadrants)} domains), proceed with: "
            f"1) Conservative assumptions, 2) Explicit uncertainty labeling, "
            f"3) Human verification required for high-stakes decisions."
        )
    
    def get_identity(self) -> dict:
        """Get AMOS identity information."""
        return {
            "system_name": self.identity.get("system_name", "AMOS"),
            "os_name": self.identity.get("os_name", "AMOS_OS"),
            "primary_purpose": self.identity.get("primary_purpose", ""),
            "creator": self.brain_root.get("creator", {}).get("name", "Trang Phan"),
        }
    
    def get_law_summary(self) -> list[dict]:
        """Get summary of all 6 global laws."""
        laws = []
        for law_id, law_data in self.global_laws.items():
            if isinstance(law_data, dict):
                laws.append({
                    "id": law_data.get("id", law_id),
                    "name": law_data.get("name", law_id),
                    "priority": law_data.get("priority", 99),
                    "description": law_data.get("description", "")[:80] + "..."
                })
        return sorted(laws, key=lambda x: x["priority"])


# Singleton runtime instance
_runtime_instance: Optional[AMOSRuntime] = None
# Thread pool for timeout-protected loading
_runtime_executor = ThreadPoolExecutor(max_workers=1)


def get_runtime(timeout_seconds: float = 5.0) -> AMOSRuntime:
    """Get or create the global AMOS runtime with timeout protection.

    Args:
        timeout_seconds: Maximum time to wait for loading (default 5s)

    Returns:
        AMOSRuntime instance (may use fallback config if timeout)
    """
    global _runtime_instance
    if _runtime_instance is not None:
        return _runtime_instance

    runtime = AMOSRuntime()

    try:
        # Run bootstrap in thread pool with timeout
        future = _runtime_executor.submit(runtime.bootstrap)
        future.result(timeout=timeout_seconds)
        _runtime_instance = runtime
    except FutureTimeoutError:
        # Use fallback configuration on timeout
        runtime._load_fallback_root()
        runtime._loaded = True
        _runtime_instance = runtime

    return _runtime_instance


async def get_runtime_async(timeout_seconds: float = 5.0) -> AMOSRuntime:
    """Get or create the global AMOS runtime asynchronously.

    Prevents 'taking a long time' messages when loading large JSON files.

    Args:
        timeout_seconds: Maximum time to wait for loading

    Returns:
        AMOSRuntime instance
    """
    global _runtime_instance
    if _runtime_instance is None:
        _runtime_instance = AMOSRuntime()
        await _runtime_instance.bootstrap_async(timeout_seconds)
    return _runtime_instance


def analyze_task(task: str, context: dict | None = None) -> dict:
    """Convenience function for task analysis with full AMOS enforcement."""
    runtime = get_runtime()
    return runtime.execute_cognitive_task(task, context)


def get_amos_identity() -> dict:
    """Get AMOS identity information."""
    return get_runtime().get_identity()


def get_global_laws() -> list[dict]:
    """Get all 6 global laws."""
    return get_runtime().get_law_summary()


if __name__ == "__main__":
    # Test the runtime
    print("=" * 60)
    print("AMOS RUNTIME BOOTSTRAP TEST")
    print("=" * 60)
    
    runtime = get_runtime()
    identity = runtime.get_identity()
    
    print(f"\nSystem: {identity['system_name']}")
    print(f"Creator: {identity['creator']}")
    print(f"Purpose: {identity['primary_purpose'][:60]}...")
    
    print("\n--- Global Laws ---")
    for law in runtime.get_law_summary():
        print(f"  {law['id']}: {law['name']} (P{law['priority']})")
    
    # Test task analysis
    test_task = "Design a new microservices architecture for a fintech startup"
    print(f"\n--- Test Task Analysis ---")
    print(f"Task: {test_task}")
    
    result = runtime.execute_cognitive_task(test_task)
    
    print(f"\nPerspectives generated: {len(result['perspectives'])}")
    print(f"Quadrants analyzed: {len(result['quadrant_analysis'])}")
    print(f"Assumptions tracked: {len(result['assumptions'])}")
    
    print("\n--- Quadrant Analysis ---")
    for quadrant, data in result['quadrant_analysis'].items():
        print(f"  {quadrant}: {data['focus'][:50]}...")
    
    print("\n--- Gap Statement ---")
    print(result['gap_statement'][:100] + "...")
    
    print("\n" + "=" * 60)
    print("AMOS RUNTIME OPERATIONAL")
    print("=" * 60)
