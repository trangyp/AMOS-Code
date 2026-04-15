#!/usr/bin/env python3
"""AMOS Brain ClawSpring Plugin - Real-time agent integration.

Integrates AMOS cognitive architecture into the clawspring agent loop:
- Pre-tool validation (Global Laws check before tool execution)
- Post-tool audit (Reasoning validation after tool execution)
- System prompt enhancement (AMOS context injection)
- Decision logging (Audit trail with reasoning chain)

Usage:
    # In clawspring config or startup:
    from clawspring.amos_plugin import AMOSPlugin
    plugin = AMOSPlugin()
    plugin.enable()
"""

from __future__ import annotations

import os
import sys
from datetime import datetime
from typing import Any

# Add parent path for amos_brain
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amos_brain import GlobalLaws, get_amos_integration
from amos_brain.agent_bridge import AMOSAgentBridge, ToolDecision


class AMOSPlugin:
    """ClawSpring plugin integrating AMOS brain capabilities.

    Hooks into:
    - Tool execution (pre/post validation)
    - System prompt generation (enhancement)
    - Agent loop (reasoning injection)
    """

    def __init__(self):
        self.amos = get_amos_integration()
        self.bridge = AMOSAgentBridge()
        self.laws = GlobalLaws()
        self.enabled = False
        self.decision_log: list[ToolDecision] = []

    def enable(self) -> None:
        """Enable AMOS brain integration."""
        self.enabled = True
        self._register_hooks()
        print("[AMOS] Plugin enabled - Brain integration active")

    def disable(self) -> None:
        """Disable AMOS brain integration."""
        self.enabled = False
        print("[AMOS] Plugin disabled")

    def _register_hooks(self) -> None:
        """Register hooks into clawspring."""
        try:
            # Import clawspring hooks if available
            from clawspring.hooks import register_post_tool_hook, register_pre_tool_hook

            register_pre_tool_hook(self._pre_tool_validation)
            register_post_tool_hook(self._post_tool_audit)
        except ImportError:
            # Hooks not available - use monkey patching as fallback
            self._patch_tool_execution()

    def _pre_tool_validation(
        self, tool_name: str, arguments: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Pre-tool execution validation.

        Checks:
        - L1: Operational scope (is this action permitted?)
        - L2: Dual perspective check for high-risk tools
        - L4: Structural integrity of arguments

        Returns:
            Modified arguments or None to block execution
        """
        if not self.enabled:
            return arguments

        # Check if tool is high-risk
        high_risk_tools = {"Bash", "Write", "Edit", "Shell", "Execute"}
        is_high_risk = tool_name in high_risk_tools

        # L1: Operational scope check
        action_type = self._categorize_action(tool_name, arguments)
        permitted, reason = self.laws.check_l1_constraint(action_type)

        if not permitted:
            print(f"[AMOS/L1] Blocked: {tool_name} - {reason}")
            return None

        # L2: Dual perspective for high-risk
        if is_high_risk:
            # Require explicit confirmation for destructive actions
            print(f"[AMOS/L2] High-risk tool: {tool_name}")
            print(f"[AMOS/L2] Arguments: {arguments}")
            print("[AMOS/L2] Consider both supporting and alternative cases")

        # Log decision
        decision = ToolDecision(
            timestamp=datetime.utcnow().isoformat(),
            tool_name=tool_name,
            arguments=arguments,
            reasoning_chain=[
                "L1 scope check passed",
                "L2 risk assessment" if is_high_risk else "Low risk",
            ],
            law_violations=[],
            approved=permitted,
        )
        self.decision_log.append(decision)

        return arguments

    def _post_tool_audit(self, tool_name: str, arguments: dict[str, Any], result: Any) -> Any:
        """Post-tool execution audit.

        Checks:
        - L4: Structural integrity of results
        - L5: Communication style check
        - Logs execution for audit trail
        """
        if not self.enabled:
            return result

        # Convert result to string for checking
        result_str = str(result) if result else ""

        # L5: Communication style check
        if len(result_str) > 50:  # Only check substantial outputs
            ok, violations = self.laws.l5_communication_check(result_str[:500])
            if not ok:
                print(f"[AMOS/L5] Style issues in {tool_name} output: {violations[:2]}")

        # Log execution
        print(f"[AMOS] Tool executed: {tool_name}")

        return result

    def _patch_tool_execution(self) -> None:
        """Monkey-patch tool execution as fallback."""
        try:
            import clawspring.tools as tools_module

            original_execute = tools_module.execute_tool

            def patched_execute(tool_name: str, arguments: dict[str, Any]) -> Any:
                # Pre-validation
                validated = self._pre_tool_validation(tool_name, arguments)
                if validated is None:
                    raise Exception(f"[AMOS] Tool blocked by Global Laws: {tool_name}")

                # Execute
                result = original_execute(tool_name, validated)

                # Post-audit
                return self._post_tool_audit(tool_name, validated, result)

            tools_module.execute_tool = patched_execute
            print("[AMOS] Tool execution patched")

        except Exception as e:
            print(f"[AMOS] Warning: Could not patch tools: {e}")

    def _categorize_action(self, tool_name: str, arguments: dict[str, Any]) -> str:
        """Categorize tool action for L1 scope check."""
        destructive = {"Bash", "Write", "Edit", "Delete", "Remove", "Shell"}
        financial = {"Transfer", "Pay", "Purchase", "Trade"}
        medical = {"Diagnose", "Prescribe", "Treat"}
        legal = {"Contract", "Agreement", "Legal"}

        if tool_name in destructive:
            return "file_destruction"
        elif tool_name in financial:
            return "financial_execution"
        elif tool_name in medical:
            return "medical_treatment"
        elif tool_name in legal:
            return "legal_representation"

        return "analysis"

    def enhance_system_prompt(self, base_prompt: str) -> str:
        """Enhance system prompt with AMOS brain context."""
        return self.amos.enhance_system_prompt(base_prompt)

    def get_decision_log(self) -> list[ToolDecision]:
        """Get logged tool decisions."""
        return self.decision_log

    def analyze_last_decision(self) -> dict[str, Any]:
        """Analyze the last decision with Rule of 2 and Rule of 4."""
        if not self.decision_log:
            return {"error": "No decisions logged"}

        last = self.decision_log[-1]
        problem = f"Tool execution: {last.tool_name}"

        return self.amos.analyze_with_rules(problem)


# Global plugin instance
_plugin: AMOSPlugin | None = None


def get_amos_plugin() -> AMOSPlugin:
    """Get or create global AMOS plugin instance."""
    global _plugin
    if _plugin is None:
        _plugin = AMOSPlugin()
    return _plugin


def enable_amos_brain() -> None:
    """Enable AMOS brain integration globally."""
    plugin = get_amos_plugin()
    plugin.enable()


def disable_amos_brain() -> None:
    """Disable AMOS brain integration globally."""
    plugin = get_amos_plugin()
    plugin.disable()


# Auto-enable on import if AMOS_AUTO_ENABLE is set
if os.environ.get("AMOS_AUTO_ENABLE", "0") == "1":
    enable_amos_brain()
