"""AMOS Brain-Powered Smart API Gateway

Intelligent request routing and processing using BrainClient cognitive capabilities.
Analyzes request patterns, optimizes routing decisions, and provides intelligent
request transformation using the AMOS Brain.

Creator: Trang Phan
Version: 1.0.0
"""

from __future__ import annotations

import asyncio
import json
import time
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from fastapi import APIRouter, Header, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

UTC = UTC

# Import BrainClient facade
try:
    from clawspring.agents.amos_brain.facade import BrainClient
    from clawspring.agents.amos_brain.master_orchestrator import MasterOrchestrator

    _BRAIN_AVAILABLE = True
except ImportError:
    _BRAIN_AVAILABLE = False

router = APIRouter(prefix="/api/v1/brain/gateway", tags=["Brain Smart Gateway"])


class RouteRequest(BaseModel):
    """Request for intelligent routing."""

    path: str
    method: str = "GET"
    headers: dict[str, str] = Field(default_factory=dict)
    body: dict[str, Any] = Field(default_factory=dict)
    priority: int = Field(default=5, ge=1, le=10)
    context: dict[str, Any] = Field(default_factory=dict)


class RouteDecision(BaseModel):
    """Brain-powered routing decision."""

    request_id: str
    target_service: str
    confidence: float
    reasoning: str
    estimated_latency_ms: int
    cache_key: Optional[str] = None
    should_cache: bool = False
    suggested_headers: dict[str, str] = Field(default_factory=dict)
    transformations: list[str] = Field(default_factory=list)
    legality_score: float
    timestamp: str


class RequestAnalysis(BaseModel):
    """Brain analysis of request patterns."""

    request_id: str
    pattern_type: str
    complexity_score: float
    risk_assessment: str
    optimization_suggestions: list[str]
    security_flags: list[str]
    brain_recommendations: str


class GatewayStats(BaseModel):
    """Gateway performance statistics."""

    total_requests: int
    routed_requests: int
    cached_requests: int
    avg_confidence: float
    avg_latency_ms: float
    active_rules: int


class BrainSmartGateway:
    """Brain-powered intelligent API gateway."""

    def __init__(self):
        self.request_history: list[dict[str, Any]] = []
        self.routing_cache: dict[str, dict[str, Any]] = {}
        self.stats = {
            "total_requests": 0,
            "routed_requests": 0,
            "cached_requests": 0,
            "confidence_sum": 0.0,
            "latency_sum": 0.0,
        }
        self._lock = asyncio.Lock()

    async def analyze_request(
        self,
        route_req: RouteRequest,
    ) -> RequestAnalysis:
        """Use brain to analyze request pattern."""
        request_id = str(uuid4())

        if not _BRAIN_AVAILABLE:
            return RequestAnalysis(
                request_id=request_id,
                pattern_type="unknown",
                complexity_score=5.0,
                risk_assessment="unknown",
                optimization_suggestions=[],
                security_flags=[],
                brain_recommendations="Brain not available",
            )

        # Build context for brain analysis
        context = {
            "path": route_req.path,
            "method": route_req.method,
            "priority": route_req.priority,
            "request_context": route_req.context,
            "analysis_type": "request_pattern",
        }

        try:
            client = BrainClient()
            brain_result = await client.think(
                thought=f"Analyze API request pattern: {route_req.method} {route_req.path}",
                context=context,
                use_legality=True,
            )

            # Extract insights from brain result
            pattern_type = self._extract_pattern_type(brain_result)
            complexity = self._calculate_complexity(route_req)
            risk = self._assess_risk(route_req, brain_result)
            suggestions = self._extract_suggestions(brain_result)

            return RequestAnalysis(
                request_id=request_id,
                pattern_type=pattern_type,
                complexity_score=complexity,
                risk_assessment=risk,
                optimization_suggestions=suggestions,
                security_flags=self._check_security_flags(route_req),
                brain_recommendations=brain_result.get("response", "No recommendations"),
            )
        except Exception as e:
            return RequestAnalysis(
                request_id=request_id,
                pattern_type="error",
                complexity_score=5.0,
                risk_assessment="unknown",
                optimization_suggestions=[],
                security_flags=[],
                brain_recommendations=f"Analysis error: {e!s}",
            )

    async def route_request(
        self,
        route_req: RouteRequest,
    ) -> RouteDecision:
        """Use brain to make intelligent routing decision."""
        request_id = str(uuid4())
        start_time = time.time()

        async with self._lock:
            self.stats["total_requests"] += 1

        if not _BRAIN_AVAILABLE:
            return RouteDecision(
                request_id=request_id,
                target_service="default",
                confidence=0.5,
                reasoning="Brain not available - using default routing",
                estimated_latency_ms=100,
                cache_key=None,
                should_cache=False,
                suggested_headers={},
                transformations=[],
                legality_score=0.5,
                timestamp=datetime.now(UTC).isoformat(),
            )

        # Check routing cache first
        cache_key = f"{route_req.method}:{route_req.path}"
        if cache_key in self.routing_cache:
            cached = self.routing_cache[cache_key]
            cached["request_id"] = request_id
            cached["timestamp"] = datetime.now(UTC).isoformat()
            async with self._lock:
                self.stats["cached_requests"] += 1
            return RouteDecision(**cached)

        try:
            client = BrainClient()
            orchestrator = MasterOrchestrator()

            # Use orchestrator for complex routing decision
            orchestration_result = await orchestrator.orchestrate_cognitive_task(
                task_type="route_optimization",
                inputs={
                    "path": route_req.path,
                    "method": route_req.method,
                    "priority": route_req.priority,
                    "context": route_req.context,
                },
            )

            # Extract routing decision from orchestration result
            target_service = self._determine_target_service(route_req, orchestration_result)
            confidence = orchestration_result.get("confidence", 0.7)
            reasoning = orchestration_result.get("reasoning", "Routed via brain orchestration")
            legality_score = orchestration_result.get("legality_score", 0.8)

            # Calculate estimated latency
            estimated_latency = self._estimate_latency(target_service, route_req)

            # Determine if result should be cached
            should_cache = route_req.method == "GET" and confidence > 0.8

            decision = RouteDecision(
                request_id=request_id,
                target_service=target_service,
                confidence=confidence,
                reasoning=reasoning,
                estimated_latency_ms=estimated_latency,
                cache_key=cache_key if should_cache else None,
                should_cache=should_cache,
                suggested_headers=self._generate_headers(route_req, orchestration_result),
                transformations=self._determine_transformations(route_req),
                legality_score=legality_score,
                timestamp=datetime.now(UTC).isoformat(),
            )

            # Cache the routing decision
            if should_cache:
                self.routing_cache[cache_key] = decision.model_dump()

            # Update stats
            latency_ms = int((time.time() - start_time) * 1000)
            async with self._lock:
                self.stats["routed_requests"] += 1
                self.stats["confidence_sum"] += confidence
                self.stats["latency_sum"] += latency_ms

            return decision

        except Exception as e:
            return RouteDecision(
                request_id=request_id,
                target_service="error_handler",
                confidence=0.0,
                reasoning=f"Routing error: {e!s}",
                estimated_latency_ms=0,
                legality_score=0.0,
                timestamp=datetime.now(UTC).isoformat(),
            )

    def _extract_pattern_type(self, brain_result: dict[str, Any]) -> str:
        """Extract pattern type from brain result."""
        response = str(brain_result.get("response", "")).lower()
        if "read" in response or "get" in response:
            return "read_operation"
        elif "write" in response or "post" in response or "put" in response:
            return "write_operation"
        elif "delete" in response:
            return "delete_operation"
        elif "query" in response or "search" in response:
            return "query_operation"
        return "generic_operation"

    def _calculate_complexity(self, route_req: RouteRequest) -> float:
        """Calculate request complexity score."""
        complexity = 5.0  # Base complexity

        # Increase for large payloads
        if route_req.body:
            body_size = len(json.dumps(route_req.body))
            if body_size > 10000:
                complexity += 2.0
            elif body_size > 1000:
                complexity += 1.0

        # Increase for high priority
        if route_req.priority >= 8:
            complexity += 1.5
        elif route_req.priority <= 3:
            complexity -= 1.0

        # Increase for complex paths
        path_depth = len([p for p in route_req.path.split("/") if p])
        complexity += path_depth * 0.5

        return min(max(complexity, 1.0), 10.0)

    def _assess_risk(
        self,
        route_req: RouteRequest,
        brain_result: dict[str, Any],
    ) -> str:
        """Assess request risk level."""
        # Check for high-risk patterns
        if route_req.method in ["DELETE", "PUT"]:
            return "high"

        if route_req.priority >= 9:
            return "elevated"

        # Use brain legality score
        legality = brain_result.get("legality_score", 1.0)
        if legality < 0.5:
            return "suspicious"

        return "low"

    def _extract_suggestions(self, brain_result: dict[str, Any]) -> list[str]:
        """Extract optimization suggestions from brain result."""
        suggestions = []
        response = brain_result.get("response", "")

        if "cache" in response.lower():
            suggestions.append("Enable response caching")
        if "rate limit" in response.lower():
            suggestions.append("Apply rate limiting")
        if "validate" in response.lower():
            suggestions.append("Add input validation")
        if "optimize" in response.lower():
            suggestions.append("Consider query optimization")

        return suggestions

    def _check_security_flags(self, route_req: RouteRequest) -> list[str]:
        """Check for security concerns."""
        flags = []

        sensitive_paths = ["/admin", "/auth", "/password", "/token", "/secret"]
        if any(route_req.path.startswith(p) for p in sensitive_paths):
            flags.append("sensitive_path")

        if route_req.method in ["POST", "PUT", "DELETE"] and not route_req.headers.get(
            "X-CSRF-Token"
        ):
            flags.append("no_csrf_token")

        return flags

    def _determine_target_service(
        self,
        route_req: RouteRequest,
        orchestration_result: dict[str, Any],
    ) -> str:
        """Determine which service should handle the request."""
        # Map paths to services
        path = route_req.path.lower()

        if "/brain" in path or "/cognitive" in path:
            return "brain_service"
        elif "/agent" in path:
            return "agent_fabric"
        elif "/simulation" in path:
            return "simulation_engine"
        elif "/memory" in path or "/cache" in path:
            return "memory_service"
        elif "/auth" in path or "/user" in path:
            return "auth_service"
        elif "/analytics" in path or "/metrics" in path:
            return "analytics_service"

        # Use orchestrator recommendation if available
        recommendation = orchestration_result.get("recommendation", {})
        if isinstance(recommendation, dict) and "service" in recommendation:
            return recommendation["service"]

        return "api_gateway"

    def _estimate_latency(self, target_service: str, route_req: RouteRequest) -> int:
        """Estimate request latency."""
        base_latencies = {
            "brain_service": 150,
            "agent_fabric": 200,
            "simulation_engine": 300,
            "memory_service": 50,
            "auth_service": 100,
            "analytics_service": 120,
            "api_gateway": 80,
            "default": 100,
        }

        base = base_latencies.get(target_service, 100)

        # Adjust for priority
        if route_req.priority >= 8:
            base = int(base * 0.8)  # High priority gets faster handling
        elif route_req.priority <= 3:
            base = int(base * 1.2)  # Low priority can wait

        return base

    def _generate_headers(
        self,
        route_req: RouteRequest,
        orchestration_result: dict[str, Any],
    ) -> dict[str, str]:
        """Generate suggested headers based on routing decision."""
        headers = {}

        # Add caching headers for GET requests
        if route_req.method == "GET":
            headers["Cache-Control"] = "max-age=300"

        # Add priority header
        headers["X-Request-Priority"] = str(route_req.priority)

        # Add correlation ID
        headers["X-Correlation-ID"] = str(uuid4())

        return headers

    def _determine_transformations(self, route_req: RouteRequest) -> list[str]:
        """Determine what request/response transformations are needed."""
        transformations = []

        if route_req.method in ["POST", "PUT"]:
            transformations.append("validate_json")
            transformations.append("sanitize_input")

        if "compress" in route_req.headers.get("Accept-Encoding", ""):
            transformations.append("compress_response")

        return transformations

    def get_stats(self) -> GatewayStats:
        """Get gateway statistics."""
        total = self.stats["total_requests"]
        routed = self.stats["routed_requests"]

        avg_confidence = self.stats["confidence_sum"] / routed if routed > 0 else 0.0
        avg_latency = self.stats["latency_sum"] / routed if routed > 0 else 0.0

        return GatewayStats(
            total_requests=total,
            routed_requests=routed,
            cached_requests=self.stats["cached_requests"],
            avg_confidence=round(avg_confidence, 2),
            avg_latency_ms=round(avg_latency, 1),
            active_rules=len(self.routing_cache),
        )


# Global gateway instance
gateway = BrainSmartGateway()


@router.post("/analyze", response_model=RequestAnalysis)
async def analyze_request(route_req: RouteRequest) -> RequestAnalysis:
    """Analyze a request using brain cognitive capabilities."""
    return await gateway.analyze_request(route_req)


@router.post("/route", response_model=RouteDecision)
async def route_request(route_req: RouteRequest) -> RouteDecision:
    """Get intelligent routing decision from brain."""
    return await gateway.route_request(route_req)


@router.get("/stats", response_model=GatewayStats)
async def get_gateway_stats() -> GatewayStats:
    """Get gateway performance statistics."""
    return gateway.get_stats()


@router.post("/process")
async def process_request(
    request: Request,
    x_priority: int = Header(default=5),
) -> Response:
    """Process a request through the brain-powered gateway."""
    try:
        body = await request.body()
        body_json = json.loads(body) if body else {}

        route_req = RouteRequest(
            path=str(request.url.path),
            method=request.method,
            headers=dict(request.headers),
            body=body_json,
            priority=x_priority,
            context={"source_ip": request.client.host if request.client else "unknown"},
        )

        # Get routing decision
        decision = await gateway.route_request(route_req)

        # If legality score is too low, reject request
        if decision.legality_score < 0.3:
            raise HTTPException(
                status_code=403,
                detail="Request blocked by brain legality check",
            )

        # Return routing decision as response
        return JSONResponse(
            content=decision.model_dump(),
            headers=decision.suggested_headers,
        )

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON body")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gateway error: {e!s}")


@router.get("/health")
async def gateway_health() -> dict[str, Any]:
    """Check gateway health and brain connectivity."""
    return {
        "status": "healthy",
        "brain_available": _BRAIN_AVAILABLE,
        "timestamp": datetime.now(UTC).isoformat(),
        "gateway_stats": gateway.get_stats().model_dump(),
    }
