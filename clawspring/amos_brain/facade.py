"""AMOS Brain Facade for Axiom One Integration

Provides a simplified interface to the AMOS Brain for:
- Axiom One unified technical operating system
- Repo Autopsy cognitive analysis
- Agent plane orchestration
- Cross-domain reasoning
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

UTC = timezone.utc

UTC = timezone.utc
from typing import Any

# Try to import brain components
try:
    from .integrated_brain_api import BrainResponse, IntegratedBrainAPI

    _BRAIN_AVAILABLE = True
except ImportError:
    try:
        from integrated_brain_api import BrainResponse, IntegratedBrainAPI

        _BRAIN_AVAILABLE = True
    except ImportError:
        _BRAIN_AVAILABLE = False
        IntegratedBrainAPI = None
        BrainResponse = None


@dataclass
class CognitiveTask:
    """A cognitive task for brain processing."""

    id: str
    task_type: str
    description: str
    context: dict[str, Any] = field(default_factory=dict)
    priority: int = 5
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class CognitiveResult:
    """Result from brain cognitive processing."""

    task_id: str
    status: str
    response: str
    confidence: float
    recommendations: list[dict[str, Any]]
    processing_time_ms: float
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class BrainThinkResponse:
    """Response from brain think() method - matches axiom_one_brain_bridge expectations."""

    content: str
    confidence: float
    law_compliant: bool
    violations: list[str]
    reasoning: str
    metadata: dict[str, Any]
    success: bool = True  # For compatibility with BrainResponse interface


class BrainClient:
    """Facade for AMOS Brain - Unified interface for Axiom One.

    Usage:
        client = BrainClient()
        await client.initialize()
        result = await client.analyze_repo_issue(issue_description, context)
    """

    def __init__(self):
        self._brain: IntegratedBrainAPI | None = None
        self._initialized = False
        self._task_count = 0

    async def initialize(self) -> bool:
        """Initialize brain connection."""
        if not _BRAIN_AVAILABLE or not IntegratedBrainAPI:
            return False

        try:
            self._brain = IntegratedBrainAPI()
            # Trigger initialization
            await self._brain._ensure_initialized()
            self._initialized = True
            return True
        except Exception:
            return False

    @property
    def is_available(self) -> bool:
        """Check if brain is available."""
        return _BRAIN_AVAILABLE and self._initialized

    def think(
        self, query: str, domain: str = "software", context: dict[str, Any] = None
    ) -> BrainThinkResponse:
        """Process a thought through the brain - synchronous interface for axiom_one_brain_bridge.

        Uses amos_brain_working.think as the primary brain implementation.

        Args:
            query: The query to process
            domain: Domain for processing (software, code_review, architecture, etc.)
            context: Additional context

        Returns:
            BrainThinkResponse with content, confidence, law_compliance, etc.

        """
        try:
            # Try the working brain first (most reliable)
            from amos_brain_working import think as working_think

            result = working_think(query, context or {})

            return BrainThinkResponse(
                content=result.get("response", result.get("output", "No response")),
                confidence=result.get("confidence", result.get("sigma", 0.5)),
                law_compliant=result.get("legality", 0.5) > 0.3,
                violations=[],
                reasoning=f"Processed via {result.get('mode', 'unknown')} mode",
                metadata={
                    "components_used": result.get("components_used", ["amos_brain_working"]),
                    "latency_ms": result.get("latency_ms", 0),
                    "domain": domain,
                    "status": result.get("status"),
                    "brain_used": result.get("brain_used", False),
                },
            )
        except Exception as e:
            # Fallback to basic response
            return BrainThinkResponse(
                content=f"Query received: {query[:100]}... (Brain processing limited: {e})",
                confidence=0.3,
                law_compliant=True,
                violations=[],
                reasoning="Fallback mode - brain components unavailable",
                metadata={"error": str(e), "domain": domain},
            )

    async def think_async(
        self, query: str, domain: str = "software", context: dict[str, Any] = None
    ) -> BrainThinkResponse:
        """Async version of think() method."""
        await self.initialize()

        if not self._brain:
            return BrainThinkResponse(
                content="Brain not available",
                confidence=0.0,
                law_compliant=True,
                violations=[],
                reasoning="Brain initialization failed",
                metadata={"error": "brain_unavailable"},
            )

        try:
            brain_response = await self._brain.process(query, mode="auto", context=context)

            return BrainThinkResponse(
                content=brain_response.response,
                confidence=brain_response.confidence,
                law_compliant=True,
                violations=[],
                reasoning=f"Processed via {brain_response.mode} mode",
                metadata={
                    "components_used": brain_response.components_used,
                    "latency_ms": brain_response.latency_ms,
                    "domain": domain,
                },
            )
        except Exception as e:
            return BrainThinkResponse(
                content=f"Error: {str(e)}",
                confidence=0.0,
                law_compliant=False,
                violations=[str(e)],
                reasoning="Exception during processing",
                metadata={"error": str(e)},
            )

    async def analyze_repo_issue(
        self,
        issue_description: str,
        context: dict[str, Any] = None,
    ) -> CognitiveResult:
        """Analyze a repository issue using brain cognitive capabilities.

        Args:
            issue_description: Description of the issue
            context: Repository context (files, error logs, etc.)

        Returns:
            CognitiveResult with analysis and recommendations

        """
        if not self._brain:
            return self._fallback_result("Brain not initialized")

        self._task_count += 1
        task_id = f"repo-analysis-{self._task_count}"

        # Build query
        query = f"""Analyze this repository issue and provide recommendations:

Issue: {issue_description}

Context:
{self._format_context(context)}

Provide:
1. Root cause analysis
2. Suggested fix approach
3. Files that need modification
4. Risk assessment"""

        try:
            brain_response = await self._brain.process(
                query,
                mode="reflect",  # Use reflective mode for deep analysis
                context=context,
            )

            return CognitiveResult(
                task_id=task_id,
                status="success",
                response=brain_response.response,
                confidence=brain_response.confidence,
                recommendations=self._extract_recommendations(brain_response),
                processing_time_ms=brain_response.latency_ms,
            )
        except Exception as e:
            return self._fallback_result(str(e))

    async def suggest_fix_strategy(
        self,
        issue_type: str,
        affected_files: list[str],
        repo_context: dict[str, Any] = None,
    ) -> CognitiveResult:
        """Suggest a fix strategy for an issue type.

        Args:
            issue_type: Type of issue (packaging, imports, tests, etc.)
            affected_files: List of files affected
            repo_context: Repository context

        Returns:
            CognitiveResult with fix strategy

        """
        if not self._brain:
            return self._fallback_result("Brain not initialized")

        self._task_count += 1
        task_id = f"fix-strategy-{self._task_count}"

        query = f"""Suggest fix strategy for this repository issue:

Issue Type: {issue_type}
Affected Files: {", ".join(affected_files)}

Provide:
1. Recommended fix approach
2. Step-by-step implementation
3. Blast radius assessment
4. Testing strategy"""

        try:
            brain_response = await self._brain.process(
                query,
                mode="react",  # Use ReAct for actionable strategy
                context=repo_context,
            )

            return CognitiveResult(
                task_id=task_id,
                status="success",
                response=brain_response.response,
                confidence=brain_response.confidence,
                recommendations=self._extract_recommendations(brain_response),
                processing_time_ms=brain_response.latency_ms,
            )
        except Exception as e:
            return self._fallback_result(str(e))

    async def evaluate_impact(
        self,
        change_description: str,
        affected_domains: list[str],
    ) -> CognitiveResult:
        """Evaluate cross-domain impact of a change.

        Args:
            change_description: Description of the proposed change
            affected_domains: List of affected domains

        Returns:
            CognitiveResult with impact analysis

        """
        if not self._brain:
            return self._fallback_result("Brain not initialized")

        self._task_count += 1
        task_id = f"impact-eval-{self._task_count}"

        query = f"""Evaluate cross-domain impact of this change:

Change: {change_description}
Affected Domains: {", ".join(affected_domains)}

Provide:
1. Impact severity per domain
2. Hidden dependencies
3. Risk assessment
4. Mitigation strategies"""

        try:
            brain_response = await self._brain.process(
                query,
                mode="reflect",
            )

            return CognitiveResult(
                task_id=task_id,
                status="success",
                response=brain_response.response,
                confidence=brain_response.confidence,
                recommendations=self._extract_recommendations(brain_response),
                processing_time_ms=brain_response.latency_ms,
            )
        except Exception as e:
            return self._fallback_result(str(e))

    async def plan_agent_execution(
        self,
        goal: str,
        available_tools: list[str],
        constraints: dict[str, Any] = None,
    ) -> CognitiveResult:
        """Plan an agent execution strategy.

        Args:
            goal: The agent's goal
            available_tools: List of available tools
            constraints: Execution constraints

        Returns:
            CognitiveResult with execution plan

        """
        if not self._brain:
            return self._fallback_result("Brain not initialized")

        self._task_count += 1
        task_id = f"agent-plan-{self._task_count}"

        query = f"""Plan agent execution for this goal:

Goal: {goal}
Available Tools: {", ".join(available_tools)}

Provide:
1. Step-by-step execution plan
2. Tool selection rationale
3. Risk points
4. Success criteria"""

        try:
            brain_response = await self._brain.process(
                query,
                mode="react",
                context=constraints,
            )

            return CognitiveResult(
                task_id=task_id,
                status="success",
                response=brain_response.response,
                confidence=brain_response.confidence,
                recommendations=self._extract_recommendations(brain_response),
                processing_time_ms=brain_response.latency_ms,
            )
        except Exception as e:
            return self._fallback_result(str(e))

    def _format_context(self, context: dict[str, Any]) -> str:
        """Format context for brain query."""
        if not context:
            return "No additional context"

        lines = []
        for key, value in context.items():
            if isinstance(value, list):
                lines.append(f"- {key}: {', '.join(str(v) for v in value)}")
            else:
                lines.append(f"- {key}: {value}")
        return "\n".join(lines)

    def _extract_recommendations(self, brain_response: Any) -> list[dict[str, Any]]:
        """Extract recommendations from brain response."""
        recommendations = []

        # Parse response for structured recommendations
        response_text = getattr(brain_response, "response", "")

        # Simple extraction - look for numbered lists or bullet points
        lines = response_text.split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith(("1.", "2.", "3.", "4.", "5.", "-", "*")):
                recommendations.append(
                    {
                        "type": "suggestion",
                        "description": line.lstrip("123456789.-* "),
                        "confidence": getattr(brain_response, "confidence", 0.5),
                    }
                )

        return recommendations

    def _fallback_result(self, error_message: str) -> CognitiveResult:
        """Create fallback result when brain is unavailable."""
        return CognitiveResult(
            task_id=f"fallback-{self._task_count}",
            status="brain_unavailable",
            response=f"Brain not available: {error_message}",
            confidence=0.0,
            recommendations=[],
            processing_time_ms=0.0,
        )


# Singleton instance
_brain_client_instance: BrainClient | None = None


def get_brain_client() -> BrainClient:
    """Get or create singleton brain client instance."""
    global _brain_client_instance
    if _brain_client_instance is None:
        _brain_client_instance = BrainClient()
    return _brain_client_instance


async def initialize_brain() -> bool:
    """Initialize brain globally."""
    client = get_brain_client()
    return await client.initialize()
