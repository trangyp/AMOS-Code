"""AMOS Brain Agent Execution Bridge - Bidirectional brain-agent integration."""

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from functools import lru_cache
from typing import Any, Dict, List, Optional

from .canon_bridge import get_canon_bridge
from .laws import GlobalLaws, UBILaws
from .loader import get_brain
from .reasoning import RuleOfFour, RuleOfTwo
from .task_processor import BrainTaskProcessor


@dataclass
class ToolDecision:
    """Record of a tool execution decision."""

    timestamp: str
    tool_name: str
    arguments: dict
    reasoning_chain: List[str]
    law_violations: List[dict]
    approved: bool
    alternatives: List[str] = field(default_factory=list)


@dataclass
class ExecutionContext:
    """Context for agent execution with brain oversight."""

    task_id: str
    active_kernels: List[str]
    reasoning_steps: List[str]
    quadrant_analysis: dict
    law_compliance: dict


class AMOSAgentBridge:
    """Bridge connecting AMOS brain to agent execution runtime.

    Provides:
    - Pre-tool law validation (block unsafe operations)
    - Post-tool reasoning audit (verify outputs)
    - Decision logging with reasoning chain
    - Law violation alerts with alternatives
    """

    # Risk categories for tools
    RISK_CATEGORIES = {
        "high": [
            "Bash",
            "Write",
            "Edit",  # Destructive file operations
        ],
        "medium": [
            "WebFetch",
            "WebSearch",  # External data
        ],
        "low": [
            "Read",
            "Grep",
            "Glob",  # Read-only operations
        ],
    }

    def __init__(self):
        self.brain = get_brain()
        self.processor = BrainTaskProcessor()
        self.global_laws = GlobalLaws()
        self.ubi_laws = UBILaws()
        self.rule_of_two = RuleOfTwo()
        self.rule_of_four = RuleOfFour()
        self._decision_log: List[ToolDecision] = []
        self._hooks: Dict[str, list[Callable]] = {
            "pre_tool": [],
            "post_tool": [],
            "law_violation": [],
        }
        self._canon_bridge = None

    async def _get_canon_bridge(self):
        """Lazy initialization of canon bridge."""
        if self._canon_bridge is None:
            self._canon_bridge = await get_canon_bridge()
        return self._canon_bridge

    def validate_tool_call(
        self,
        tool_name: str,
        arguments: dict,
        context: Optional[ExecutionContext] = None,
    ) -> dict:
        """Validate a tool call against AMOS global laws.

        Returns:
            dict with keys: approved, reason, violations, alternatives, risk_level
        """
        result: Dict[str, Any] = {
            "approved": True,
            "reason": "No violations detected",
            "violations": [],
            "alternatives": [],
            "risk_level": self._get_risk_level(tool_name),
        }

        # L1: Law of Law - Check operational scope
        l1_ok, msg = self.global_laws.check_l1_constraint(f"tool_{tool_name}")
        if not l1_ok:
            result["approved"] = False
            result["reason"] = msg
            result["violations"].append({"law": "L1", "message": msg})

        # Check for high-risk tool patterns
        if tool_name in ["Bash", "Write", "Edit"]:
            # Check for dangerous patterns
            args_str = str(arguments).lower()
            dangerous_patterns = [
                "rm -rf /",
                "rm -rf *",
                "mkfs",
                "dd if=/dev/zero",
                "> /dev/sda",
                "format c:",
                "del /f /s /q",
            ]
            for pattern in dangerous_patterns:
                if pattern in args_str:
                    result["approved"] = False
                    result["reason"] = f"L1: Dangerous pattern detected: {pattern}"
                    result["violations"].append(
                        {"law": "L1", "message": f"Operation exceeds safe scope: {pattern}"}
                    )
                    result["alternatives"].append(f"Use safer alternative to: {pattern}")

        # L5: Post-Theory Communication - Check for prohibited terms
        args_str = str(arguments)
        l5_ok, violations = self.global_laws.l5_communication_check(args_str)
        if not l5_ok:
            result["violations"].extend([{"law": "L5", "message": v} for v in violations])

        # If violations found but not critical, flag as warning
        if result["violations"] and result["approved"]:
            result["reason"] = f"Warnings: {len(result['violations'])} law considerations"

        # Log the decision
        decision = ToolDecision(
            timestamp=datetime.now().isoformat(),
            tool_name=tool_name,
            arguments=arguments,
            reasoning_chain=[
                f"Risk level: {result['risk_level']}",
                f"L1 check: {'pass' if l1_ok else 'fail'}",
                f"L5 check: {'pass' if l5_ok else 'fail'}",
            ],
            law_violations=result["violations"],
            approved=result["approved"],
            alternatives=result["alternatives"],
        )
        self._decision_log.append(decision)

        # Trigger hooks
        self._trigger_hooks("pre_tool", tool_name, arguments, result)
        if result["violations"]:
            self._trigger_hooks("law_violation", tool_name, result["violations"])

        return result

    def audit_tool_result(
        self,
        tool_name: str,
        arguments: dict,
        result: Any,
        context: Optional[ExecutionContext] = None,
    ) -> dict:
        """Post-execution audit of tool result.

        Returns:
            dict with keys: valid, issues, recommendations
        """
        audit: Dict[str, Any] = {
            "valid": True,
            "issues": [],
            "recommendations": [],
        }

        # Check result size (economic consideration)
        result_str = str(result)
        if len(result_str) > 100000:  # 100KB
            audit["issues"].append("Large result may impact performance")
            audit["recommendations"].append("Consider pagination or filtering")

        # Check for errors in result
        if isinstance(result, dict) and "error" in result:
            audit["valid"] = False
            audit["issues"].append(f"Tool returned error: {result['error']}")

        # Structural integrity check
        if isinstance(result, str):
            # Check for contradictions in text output
            statements = [s.strip() for s in result.split(".") if s.strip()]
            if len(statements) > 1:
                ok, contradictions = self.global_laws.check_l4_integrity(statements[:20])
                if not ok:
                    audit["issues"].extend(contradictions[:3])

        self._trigger_hooks("post_tool", tool_name, result, audit)

        return audit

    async def analyze_task(self, task: str, domain: str = "general") -> dict:
        """Analyze a task using brain cognitive architecture with Canon context.

        Returns structured analysis with reasoning.
        """
        # Get Canon context for domain
        canon_context = {}
        try:
            canon = await self._get_canon_bridge()
            ctx = canon.get_context_for_domain(domain)
            canon_context = {
                "domain": ctx.domain,
                "terms_available": len(ctx.glossary_terms),
                "applicable_agents": ctx.applicable_agents[:3],
            }
            # Enrich task with Canon context
            task = canon.enrich_query(task, domain)
        except Exception:
            pass

        full_question = f"Analyze this {domain} task: {task}"
        result = self.processor.process(full_question)

        return {
            "analysis": result.output,
            "reasoning": result.reasoning_steps,
            "confidence": result.confidence,
            "kernels_used": result.kernels_used,
            "law_compliant": len(result.law_violations) == 0,
            "canon_context": canon_context,
        }

    def enhance_prompt_for_task(self, task: str, base_prompt: str) -> str:
        """Enhance system prompt with brain context for specific task."""
        # Process task to get reasoning context
        result = self.processor.process(task)

        enhancement = f"""
# AMOS BRAIN COGNITIVE CONTEXT

Active Kernels: {", ".join(result.kernels_used[:3])}
Reasoning Compliance:
- Rule of 2: {"✓" if result.rule_of_two_check["compliant"] else "○"} ({result.rule_of_two_check["perspectives_checked"]} perspectives)
- Rule of 4: {"✓" if result.rule_of_four_check["compliant"] else "○"} ({result.rule_of_four_check["coverage"]} quadrants)
- Confidence: {result.confidence}

## Reasoning Chain
{chr(10).join(["- " + step for step in result.reasoning_steps[:5]])}

## Global Laws Active
L1: Law of Law - Obey highest applicable constraints
L2: Rule of 2 - Check two contrasting perspectives
L3: Rule of 4 - Consider four quadrants (technical, biological, economic, environmental)
L4: Absolute Structural Integrity - Maintain logical consistency
L5: Post-Theory Communication - Clear, grounded language
L6: UBI Alignment - Respect biological intelligence

Execute with AMOS cognitive discipline.
---
"""

        return enhancement + base_prompt

    def get_execution_report(self) -> dict:
        """Generate report of all tool decisions."""
        total = len(self._decision_log)
        approved = sum(1 for d in self._decision_log if d.approved)
        blocked = total - approved

        violations_by_law: Dict[str, int] = {}
        for decision in self._decision_log:
            for v in decision.law_violations:
                law = v["law"]
                violations_by_law[law] = violations_by_law.get(law, 0) + 1

        return {
            "total_decisions": total,
            "approved": approved,
            "blocked": blocked,
            "block_rate": blocked / total if total > 0 else 0,
            "violations_by_law": violations_by_law,
            "recent_decisions": [
                {
                    "tool": d.tool_name,
                    "approved": d.approved,
                    "timestamp": d.timestamp,
                }
                for d in self._decision_log[-10:]
            ],
        }

    def register_hook(self, event: str, callback: Callable):
        """Register callback for bridge events."""
        if event in self._hooks:
            self._hooks[event].append(callback)

    def _get_risk_level(self, tool_name: str) -> str:
        """Determine risk level for a tool."""
        for level, tools in self.RISK_CATEGORIES.items():
            if tool_name in tools:
                return level
        return "unknown"

    def _trigger_hooks(self, event: str, *args):
        """Trigger registered hooks for an event."""
        for hook in self._hooks.get(event, []):
            try:
                hook(*args)
            except Exception as e:
                # Log hook error but don't break execution
                import logging

                logging.getLogger(__name__).warning(f"Hook failed for event '{event}': {e}")


@lru_cache(maxsize=1)
def get_agent_bridge() -> AMOSAgentBridge:
    """Get or create global agent bridge instance (singleton)."""
    return AMOSAgentBridge()
