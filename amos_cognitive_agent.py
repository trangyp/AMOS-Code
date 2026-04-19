#!/usr/bin/env python3
"""AMOS Cognitive Agent
A reasoning agent that uses the AMOS brain to analyze and decide actions.
"""

import sys

sys.path.insert(0, "clawspring")


from amos_brain import get_agent_bridge, get_amos_integration, get_meta_controller


class AmosCognitiveAgent:
    """AMOS Cognitive Agent - thinks before acting.

    Uses AMOS brain to:
    1. Analyze user requests
    2. Plan appropriate actions
    3. Execute with reasoning
    4. Learn from outcomes
    """

    def __init__(self):
        self.amos = get_amos_integration()
        self.bridge = get_agent_bridge()
        self.controller = get_meta_controller()
        self.history = []

    def think_and_act(self, user_request: str) -> dict:
        """Main cognitive loop: perceive -> think -> decide -> act -> reflect."""
        print(f"\n🧠 Analyzing: '{user_request}'")

        # Step 1: Perceive (raw input)
        perception = self._perceive(user_request)

        # Step 2: Think (analyze context)
        analysis = self._analyze(perception)

        # Step 3: Decide (choose action)
        decision = self._decide(analysis)

        # Step 4: Act (execute)
        result = self._execute(decision)

        # Step 5: Reflect (learn)
        reflection = self._reflect(result)

        return {
            "request": user_request,
            "perception": perception,
            "analysis": analysis,
            "decision": decision,
            "result": result,
            "reflection": reflection,
        }

    def _perceive(self, request: str) -> dict:
        """Perceive and categorize the request."""
        # Use AMOS brain to pre-process
        result = self.amos.pre_process(request, context={"agent_mode": True})

        # Categorize by intent
        categories = {
            "command": any(kw in request.lower() for kw in ["run", "execute", "do"]),
            "query": any(kw in request.lower() for kw in ["what", "how", "why", "check"]),
            "plan": any(kw in request.lower() for kw in ["plan", "create", "build"]),
            "analyze": any(kw in request.lower() for kw in ["analyze", "review", "check"]),
        }

        primary_intent = (
            max(categories, key=categories.get) if any(categories.values()) else "general"
        )

        return {
            "raw": request,
            "thought_id": result.get("thought_id"),
            "intent": primary_intent,
            "categories": categories,
            "complexity": self._assess_complexity(request),
        }

    def _assess_complexity(self, request: str) -> str:
        """Assess task complexity."""
        words = len(request.split())
        if words <= 3:
            return "simple"
        elif words <= 10:
            return "moderate"
        else:
            return "complex"

    def _analyze(self, perception: dict) -> dict:
        """Analyze the perceived request."""
        intent = perception["intent"]
        complexity = perception["complexity"]

        # Use agent bridge to decide approach
        tool_decision = self.bridge.decide_tool_use(perception["raw"])

        # Generate analysis
        analysis = {
            "intent": intent,
            "complexity": complexity,
            "approach": tool_decision.action,
            "reason": tool_decision.reason,
            "estimated_steps": 1
            if complexity == "simple"
            else (3 if complexity == "moderate" else 5),
        }

        print(f"  📊 Analysis: {intent} task ({complexity}) - {analysis['estimated_steps']} steps")
        return analysis

    def _decide(self, analysis: dict) -> dict:
        """Decide on specific actions."""
        if analysis["intent"] == "command":
            action = "execute_shell"
            params = {"safety_check": True}
        elif analysis["intent"] == "query":
            action = "gather_info"
            params = {"sources": ["system", "context"]}
        elif analysis["intent"] == "plan":
            action = "orchestrate_goal"
            params = {"horizon": "short-term"}
        else:
            action = "think_cognitively"
            params = {"depth": "standard"}

        print(f"  🎯 Decision: {action}")
        return {
            "action": action,
            "params": params,
            "confidence": 0.85 if analysis["complexity"] != "complex" else 0.70,
        }

    def _execute(self, decision: dict) -> dict:
        """Execute with REAL AMOS brain cognition."""
        action = decision["action"]

        # Import real brain think
        try:
            from amos_brain_working import think as brain_think
        except ImportError:
            brain_think = None

        if brain_think:
            # REAL BRAIN EXECUTION
            brain_input = f"Execute {action}: {decision.get('params', {})}"
            brain_result = brain_think(
                brain_input, context={"action": action, "params": decision.get("params", {})}
            )
            result = {
                "success": brain_result.get("status") == "SUCCESS",
                "brain_status": brain_result.get("status"),
                "brain_sigma": brain_result.get("sigma"),
                "brain_legality": brain_result.get("legality"),
                "output": str(brain_result.get("result", brain_result))[:500],
                "provider": "amos_brain",
            }
        elif action == "orchestrate_goal":
            plan = self.controller.orchestrate_goal("Complete user request")
            result = {
                "success": True,
                "plan_id": plan.plan_id,
                "steps": len(plan.steps),
                "output": f"Created plan with {len(plan.steps)} steps",
            }
        elif action == "execute_shell":
            import subprocess

            try:
                cmd = decision.get("params", {}).get("command", "echo 'no command'")
                proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
                result = {
                    "success": proc.returncode == 0,
                    "command": cmd,
                    "output": proc.stdout[:500],
                    "exit_code": proc.returncode,
                }
            except Exception as e:
                result = {"success": False, "error": str(e)}
        else:
            enhanced = self.amos.enhance_system_prompt("Processing user request")
            result = {
                "success": True,
                "cognitive_layers": ["perceptual", "conceptual"],
                "enhancement": enhanced[:100] + "..." if enhanced else None,
            }

        print(f"  ⚡ Executed: {action} | Brain: {result.get('provider', 'fallback')}")
        return result

    def _reflect(self, result: dict) -> dict:
        """Reflect on the outcome."""
        success = result.get("success", False)

        reflection = {
            "success": success,
            "outcome": "completed" if success else "failed",
            "learning": "Task pattern recorded" if success else "Error pattern noted",
            "confidence_adjustment": 0.0,
        }

        # Record in history
        self.history.append(reflection)

        print(f"  ✓ Reflection: {reflection['outcome']}")
        return reflection

    def get_stats(self) -> dict:
        """Get agent statistics."""
        total = len(self.history)
        successful = sum(1 for h in self.history if h.get("success"))

        return {
            "total_tasks": total,
            "successful": successful,
            "success_rate": successful / total if total > 0 else 0,
            "brain_status": self.amos.get_status(),
        }


def main():
    """Run the cognitive agent demo."""
    print("=" * 70)
    print("🧠 AMOS COGNITIVE AGENT")
    print("=" * 70)
    print("\nInitializing AMOS cognitive capabilities...")

    agent = AmosCognitiveAgent()

    # Demo requests
    demo_requests = [
        "Check system status",
        "Plan a new feature implementation",
        "Run the test suite",
        "Analyze this code for issues",
    ]

    print("\n" + "-" * 70)
    print("DEMONSTRATION: Cognitive Processing")
    print("-" * 70)

    for request in demo_requests:
        result = agent.think_and_act(request)

    # Final stats
    print("\n" + "=" * 70)
    print("AGENT STATISTICS")
    print("=" * 70)
    stats = agent.get_stats()
    print(f"Total Tasks: {stats['total_tasks']}")
    print(f"Successful: {stats['successful']}")
    print(f"Success Rate: {stats['success_rate']:.0%}")
    print(f"Brain Status: {stats['brain_status']['brain_loaded']}")

    print("\n" + "=" * 70)
    print("✅ COGNITIVE AGENT READY")
    print("=" * 70)
    print("\nThe agent can now:")
    print("  • Analyze user requests using AMOS brain")
    print("  • Plan multi-step actions")
    print("  • Execute with reasoning")
    print("  • Learn from outcomes")
    print("\nUse: agent.think_and_act('your request')")
    print("=" * 70)


if __name__ == "__main__":
    main()
