"""AMOS Agent Reasoning & Planning System.

Implements ReAct (Reasoning + Acting) pattern and other reasoning strategies
for AI agents with chain-of-thought, planning, and decision-making capabilities.

Features:
- ReAct pattern implementation (Reasoning + Acting)
- Chain-of-Thought reasoning
- Plan-and-Execute workflow
- Tool selection and orchestration
- Self-reflection and correction
- Multi-step planning

Research Sources:
- ReAct Paper (Reasoning + Acting in Language Models)
- Building Effective AI Agents (Anthropic 2026)
- Planning and Reasoning in AI Agents (AIToolKit 2026)

Creator: Trang Phan
Version: 3.0.0
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timezone
from enum import Enum
from typing import Any, Optional

UTC = UTC


class ReasoningStrategy(Enum):
    """Available reasoning strategies."""

    REACT = "react"  # Reasoning + Acting
    CHAIN_OF_THOUGHT = "cot"  # Step-by-step reasoning
    PLAN_AND_EXECUTE = "plan_execute"  # Plan first, then execute
    TREE_OF_THOUGHTS = "tot"  # Explore multiple reasoning paths
    DIRECT = "direct"  # Direct response


class ThoughtType(Enum):
    """Types of thoughts in reasoning chain."""

    REASONING = "reasoning"
    ACTION = "action"
    OBSERVATION = "observation"
    PLAN = "plan"
    REFLECTION = "reflection"
    CONCLUSION = "conclusion"


@dataclass
class Thought:
    """Represents a single thought in reasoning chain."""

    thought_type: str
    content: str
    step_number: int
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ReasoningChain:
    """Complete reasoning chain for a task."""

    chain_id: str
    agent_id: str
    task: str
    strategy: str
    thoughts: list[Thought] = field(default_factory=list)
    final_answer: str = None
    completed: bool = False
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolCall:
    """Represents a tool call in agent workflow."""

    tool_name: str
    parameters: dict[str, Any]
    call_id: str
    result: Optional[Any] = None
    executed: bool = False
    error: str = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class AgentReasoningEngine:
    """Core reasoning engine for AMOS agents."""

    def __init__(self):
        self.reasoning_chains: dict[str, ReasoningChain] = {}
        self.tool_registry: dict[str, Callable] = {}
        self.max_iterations = 10

    def register_tool(self, name: str, tool_func: Callable) -> bool:
        """Register a tool for agent use."""
        self.tool_registry[name] = tool_func
        return True

    def create_chain(
        self, agent_id: str, task: str, strategy: ReasoningStrategy = ReasoningStrategy.REACT
    ) -> ReasoningChain:
        """Create a new reasoning chain."""
        import uuid

        chain = ReasoningChain(
            chain_id=str(uuid.uuid4())[:8], agent_id=agent_id, task=task, strategy=strategy.value
        )
        self.reasoning_chains[chain.chain_id] = chain
        return chain

    async def execute_react(
        self, chain: ReasoningChain, llm_call: Callable[[str], str], max_iterations: int = 10
    ) -> str:
        """Execute ReAct reasoning pattern.

        ReAct pattern: Thought -> Action -> Observation -> ... -> Answer
        """
        iteration = 0
        current_input = chain.task

        # Add initial thought
        self._add_thought(chain, ThoughtType.REASONING, f"Starting task: {chain.task}", 0)

        while iteration < max_iterations:
            iteration += 1

            # Generate thought
            thought_prompt = self._build_react_prompt(chain, current_input)
            response = await llm_call(thought_prompt)

            # Parse response for action
            if "Action:" in response:
                parts = response.split("Action:")
                thought_content = parts[0].replace("Thought:", "").strip()
                action_content = parts[1].strip()

                # Add reasoning thought
                self._add_thought(chain, ThoughtType.REASONING, thought_content, iteration)

                # Execute action
                action_result = await self._execute_action(action_content)

                # Add action and observation
                self._add_thought(chain, ThoughtType.ACTION, action_content, iteration)
                self._add_thought(chain, ThoughtType.OBSERVATION, str(action_result), iteration)

                # Update input for next iteration
                current_input = f"Observation: {action_result}"

            elif "Final Answer:" in response:
                # Extract final answer
                answer = response.split("Final Answer:")[1].strip()
                self._add_thought(chain, ThoughtType.CONCLUSION, answer, iteration)
                chain.final_answer = answer
                chain.completed = True
                return answer

            else:
                # No clear action or answer, treat as reasoning
                self._add_thought(chain, ThoughtType.REASONING, response, iteration)

        # Max iterations reached
        return chain.final_answer or "Max iterations reached without answer"

    async def execute_chain_of_thought(
        self, chain: ReasoningChain, llm_call: Callable[[str], str]
    ) -> str:
        """Execute Chain-of-Thought reasoning."""

        # Add planning thought
        self._add_thought(chain, ThoughtType.PLAN, "Breaking down problem into steps", 0)

        # Prompt for step-by-step reasoning
        cot_prompt = f"""Solve the following problem step by step.
Show your reasoning clearly.

Problem: {chain.task}

Step 1:"""

        response = await llm_call(cot_prompt)

        # Parse steps
        steps = response.split("\n")
        for i, step in enumerate(steps):
            if step.strip():
                self._add_thought(chain, ThoughtType.REASONING, step.strip(), i + 1)

        # Extract final answer (last few lines)
        if steps:
            chain.final_answer = steps[-1] if len(steps) > 1 else response
            chain.completed = True

        return chain.final_answer or "No answer generated"

    async def execute_plan_and_execute(
        self, chain: ReasoningChain, llm_call: Callable[[str], str]
    ) -> str:
        """Execute Plan-and-Execute strategy."""

        # Phase 1: Planning
        plan_prompt = f"""Create a step-by-step plan to solve this task:

Task: {chain.task}

Provide a numbered list of steps to complete this task."""

        plan_response = await llm_call(plan_prompt)

        self._add_thought(chain, ThoughtType.PLAN, f"Plan created:\n{plan_response}", 0)

        # Phase 2: Execution
        execution_prompt = f"""Execute the following plan step by step:

Task: {chain.task}
Plan:
{plan_response}

Execute each step and provide the final result."""

        result = await llm_call(execution_prompt)

        self._add_thought(chain, ThoughtType.CONCLUSION, result, 1)
        chain.final_answer = result
        chain.completed = True

        return result

    async def _execute_action(self, action_str: str) -> Any:
        """Execute an action from the action string."""
        # Parse action string (e.g., "search[query]" or "calculate[2+2]")
        try:
            if "[" in action_str and "]" in action_str:
                tool_name = action_str.split("[")[0].strip()
                params_str = action_str.split("[")[1].split("]")[0]

                if tool_name in self.tool_registry:
                    tool = self.tool_registry[tool_name]
                    result = await tool(params_str)
                    return result
                else:
                    return f"Tool '{tool_name}' not found"
            else:
                return "Invalid action format"

        except Exception as e:
            return f"Error executing action: {str(e)}"

    def _build_react_prompt(self, chain: ReasoningChain, current_input: str) -> str:
        """Build ReAct prompt from chain history."""
        prompt_parts = [
            "You are an AI agent that reasons and acts to solve tasks.",
            "",
            f"Task: {chain.task}",
            "",
            "History:",
        ]

        for thought in chain.thoughts[-5:]:  # Last 5 thoughts
            prompt_parts.append(f"{thought.thought_type}: {thought.content}")

        prompt_parts.extend(
            [
                "",
                f"Current Input: {current_input}",
                "",
                "Respond with either:",
                "1. Thought: [your reasoning]\nAction: [tool_name][parameters]",
                "2. Thought: [your reasoning]\nFinal Answer: [your answer]",
            ]
        )

        return "\n".join(prompt_parts)

    def _add_thought(
        self, chain: ReasoningChain, thought_type: ThoughtType, content: str, step_number: int
    ):
        """Add a thought to the reasoning chain."""
        thought = Thought(thought_type=thought_type.value, content=content, step_number=step_number)
        chain.thoughts.append(thought)

    def get_chain(self, chain_id: str) -> Optional[ReasoningChain]:
        """Get reasoning chain by ID."""
        return self.reasoning_chains.get(chain_id)

    def get_chain_summary(self, chain_id: str) -> dict[str, Any]:
        """Get summary of reasoning chain."""
        chain = self.reasoning_chains.get(chain_id)
        if not chain:
            return {"error": "Chain not found"}

        return {
            "chain_id": chain.chain_id,
            "agent_id": chain.agent_id,
            "task": chain.task,
            "strategy": chain.strategy,
            "thought_count": len(chain.thoughts),
            "completed": chain.completed,
            "final_answer": chain.final_answer,
            "thoughts": [
                {
                    "type": t.thought_type,
                    "content": t.content[:100] + "..." if len(t.content) > 100 else t.content,
                    "step": t.step_number,
                }
                for t in chain.thoughts
            ],
        }

    def get_all_chains(self) -> list[dict[str, Any]]:
        """Get all reasoning chains."""
        return [
            {
                "chain_id": c.chain_id,
                "agent_id": c.agent_id,
                "task": c.task[:50] + "..." if len(c.task) > 50 else c.task,
                "strategy": c.strategy,
                "completed": c.completed,
                "thought_count": len(c.thoughts),
            }
            for c in self.reasoning_chains.values()
        ]


# Global reasoning engine
reasoning_engine = AgentReasoningEngine()


# Convenience functions
async def reason_with_react(agent_id: str, task: str, llm_call: Callable[[str], str]) -> str:
    """Execute ReAct reasoning for a task."""
    chain = reasoning_engine.create_chain(agent_id, task, ReasoningStrategy.REACT)
    return await reasoning_engine.execute_react(chain, llm_call)


async def reason_step_by_step(agent_id: str, task: str, llm_call: Callable[[str], str]) -> str:
    """Execute Chain-of-Thought reasoning."""
    chain = reasoning_engine.create_chain(agent_id, task, ReasoningStrategy.CHAIN_OF_THOUGHT)
    return await reasoning_engine.execute_chain_of_thought(chain, llm_call)


async def plan_and_solve(agent_id: str, task: str, llm_call: Callable[[str], str]) -> str:
    """Execute Plan-and-Execute strategy."""
    chain = reasoning_engine.create_chain(agent_id, task, ReasoningStrategy.PLAN_AND_EXECUTE)
    return await reasoning_engine.execute_plan_and_execute(chain, llm_call)


def register_tool(name: str, func: Callable) -> bool:
    """Register a tool for agent use."""
    return reasoning_engine.register_tool(name, func)
