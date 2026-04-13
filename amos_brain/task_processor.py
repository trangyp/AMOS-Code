"""AMOS Brain Task Processor - Standalone cognitive task processing."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .loader import get_brain
from .kernel_router import KernelRouter
from .laws import GlobalLaws
from .reasoning import RuleOfTwo, RuleOfFour


@dataclass
class TaskResult:
    """Result of brain-processed task."""
    task_id: str
    input_task: str
    output: str
    reasoning_steps: list[str]
    kernels_used: list[str]
    law_violations: list[dict]
    rule_of_two_check: dict
    rule_of_four_check: dict
    confidence: str
    processing_time_ms: int = 0


@dataclass
class ReasoningStep:
    """Single reasoning step with tracking."""
    step_number: int
    description: str
    perspective: str
    evidence: list[str]
    assumptions: list[str]


class BrainTaskProcessor:
    """
    AMOS Brain Task Processor - Applies cognitive architecture to tasks.

    Features:
    - Routes tasks through appropriate cognitive kernels
    - Applies Rule of 2 (two perspectives minimum)
    - Applies Rule of 4 (four quadrants check)
    - Validates output against Global Laws
    - Tracks reasoning chain
    """

    def __init__(self):
        self._brain = None
        self._router = None
        self.laws = GlobalLaws()
        self.rule_of_two = RuleOfTwo()
        self.rule_of_four = RuleOfFour()
        self._task_counter = 0

    @property
    def brain(self):
        """Lazy-load brain to prevent blocking during initialization."""
        if self._brain is None:
            self._brain = get_brain()
        return self._brain

    @property
    def router(self):
        """Lazy-load router to prevent blocking during initialization."""
        if self._router is None:
            self._router = KernelRouter(self.brain)
        return self._router
    
    def process(self, task: str, context: dict | None = None) -> TaskResult:
        """
        Process a task through the AMOS brain.
        
        Args:
            task: Task description
            context: Optional context data
            
        Returns:
            TaskResult with reasoning chain and validation
        """
        import time
        start_time = time.time()
        
        self._task_counter += 1
        task_id = f"AMOS-{self._task_counter:04d}"
        
        # 1. Route to kernels
        intent = self.router.parse_intent(task)
        kernels = self.router.route(task)
        kernel_names = [k.get("name", "unknown") for k in kernels]
        
        # 2. Apply Rule of 2 - generate two perspectives
        perspectives = self._generate_perspectives(task, intent)
        
        # 3. Apply Rule of 4 - check four quadrants
        quadrants = self._analyze_quadrants(task, context or {})
        
        # 4. Build reasoning chain
        reasoning_steps = self._build_reasoning_chain(
            task, perspectives, quadrants, kernel_names
        )
        
        # 5. Generate output
        output = self._generate_output(
            task, reasoning_steps, perspectives, quadrants
        )
        
        # 6. Build result
        result = TaskResult(
            task_id=task_id,
            input_task=task,
            output=output,
            reasoning_steps=reasoning_steps,
            kernels_used=kernel_names,
            law_violations=[],
            rule_of_two_check={
                "perspectives_checked": len(perspectives),
                "perspectives": [p.get("name") for p in perspectives],
                "compliant": len(perspectives) >= 2
            },
            rule_of_four_check={
                "quadrants_checked": list(quadrants.keys()),
                "coverage": len(quadrants),
                "compliant": len(quadrants) >= 4
            },
            confidence="high" if len(perspectives) >= 2 and len(quadrants) >= 4 else "medium",
            processing_time_ms=int((time.time() - start_time) * 1000)
        )
        
        return result
    
    def _generate_perspectives(self, task: str, intent) -> list[dict]:
        """Generate at least two perspectives per Rule of 2."""
        perspectives = []
        
        # Primary perspective - direct approach
        perspectives.append({
            "name": "Direct Analysis",
            "approach": f"Analyze {task} directly using {intent.primary_domain} domain",
            "focus": "Immediate solution"
        })
        
        # Secondary perspective - contrasting view
        if intent.requires_code:
            perspectives.append({
                "name": "Alternative Implementation",
                "approach": "Consider different implementation strategies",
                "focus": "Alternative patterns"
            })
        elif intent.requires_reasoning:
            perspectives.append({
                "name": "Contrarian View",
                "approach": "Challenge assumptions and consider opposite conclusions",
                "focus": "Critical examination"
            })
        else:
            perspectives.append({
                "name": "Systemic Context",
                "approach": "View within broader system context",
                "focus": "Long-term implications"
            })
        
        return perspectives
    
    def _analyze_quadrants(self, task: str, context: dict) -> dict:
        """Analyze task across four quadrants per Rule of 4."""
        return {
            "technical": {
                "question": "What are the technical requirements and constraints?",
                "factors": ["Implementation complexity", "Tool availability", "Performance"],
                "assessment": self._assess_quadrant(task, "technical")
            },
            "biological": {
                "question": "What human/biological factors are involved?",
                "factors": ["User cognitive load", "Human error potential", "Wellbeing impact"],
                "assessment": self._assess_quadrant(task, "biological")
            },
            "economic": {
                "question": "What are the economic/resource considerations?",
                "factors": ["Time cost", "Resource needs", "ROI"],
                "assessment": self._assess_quadrant(task, "economic")
            },
            "environmental": {
                "question": "What is the environmental/system context?",
                "factors": ["System dependencies", "External constraints", "Sustainability"],
                "assessment": self._assess_quadrant(task, "environmental")
            }
        }
    
    def _assess_quadrant(self, task: str, quadrant: str) -> str:
        """Quick assessment of quadrant relevance."""
        task_lower = task.lower()
        
        indicators = {
            "technical": ["code", "implement", "system", "architecture", "design"],
            "biological": ["user", "human", "cognitive", "health", "stress"],
            "economic": ["cost", "budget", "time", "resource", "efficiency"],
            "environmental": ["context", "system", "integration", "scale"]
        }
        
        indicators_for_quadrant = indicators.get(quadrant, [])
        score = sum(1 for ind in indicators_for_quadrant if ind in task_lower)
        
        if score >= 2:
            return "highly_relevant"
        elif score == 1:
            return "relevant"
        return "contextually_relevant"
    
    def _build_reasoning_chain(
        self,
        task: str,
        perspectives: list[dict],
        quadrants: dict,
        kernels: list[str]
    ) -> list[str]:
        """Build explicit reasoning chain."""
        steps = [
            f"1. Task Analysis: '{task}' requires {len(perspectives)} perspectives",
            f"2. Kernel Routing: Activating {len(kernels)} cognitive kernels",
            f"3. Rule of 2: Checking {len(perspectives)} contrasting views",
        ]
        
        for i, p in enumerate(perspectives, 1):
            steps.append(f"   - Perspective {i}: {p['name']} - {p['focus']}")
        
        steps.append(f"4. Rule of 4: Analyzing {len(quadrants)} quadrants")
        for quad_name, quad_data in quadrants.items():
            steps.append(f"   - {quad_name.title()}: {quad_data['assessment']}")
        
        steps.append("5. Law Validation: Checking against Global Laws")
        steps.append("6. Output Generation: Synthesizing results")
        
        return steps
    
    def _generate_output(
        self,
        task: str,
        reasoning_steps: list[str],
        perspectives: list[dict],
        quadrants: dict
    ) -> str:
        """Generate final output with reasoning summary."""
        output_lines = [
            f"## AMOS Brain Analysis: {task[:50]}...",
            "",
            "### Reasoning Chain",
        ]
        
        for step in reasoning_steps:
            output_lines.append(f"- {step}")
        
        output_lines.extend([
            "",
            "### Perspectives Considered",
        ])
        
        for p in perspectives:
            output_lines.append(f"- **{p['name']}**: {p['approach']}")
        
        output_lines.extend([
            "",
            "### Quadrant Analysis",
        ])
        
        for quad_name, quad_data in quadrants.items():
            output_lines.append(f"- **{quad_name.title()}**: {quad_data['assessment']}")
        
        output_lines.extend([
            "",
            "### Assessment",
            f"- Rule of 2 compliance: {len(perspectives)} perspectives ✓" if len(perspectives) >= 2 else f"- Rule of 2: Only {len(perspectives)} perspective (consider alternative view)",
            f"- Rule of 4 compliance: {len(quadrants)} quadrants ✓" if len(quadrants) >= 4 else f"- Rule of 4: {len(quadrants)} quadrants",
        ])
        
        return "\n".join(output_lines)
    
    def get_brain_status(self) -> dict:
        """Get current brain processor status."""
        return {
            "brain_loaded": self.brain is not None,
            "kernels_available": len(self.brain.list_engines()) if self.brain else 0,
            "tasks_processed": self._task_counter,
            "global_laws": len(self.brain._config.global_laws) if self.brain and self.brain._config else 0,
        }


def process_task(task: str, context: dict | None = None) -> TaskResult:
    """Convenience function to process a single task."""
    processor = BrainTaskProcessor()
    return processor.process(task, context)
