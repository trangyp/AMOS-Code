#!/usr/bin/env python3
"""AMOS Agent Evaluator - Comprehensive evaluation framework for AI agents.

Implements 2025 AI agent evaluation patterns (LangSmith, AlphaEval, Mem0):
- Multi-dimensional evaluation (performance, safety, UX, cost)
- Test dataset management with domain-specific scenarios
- Automated metrics + human evaluation workflows
- A/B testing for prompt/model comparisons
- Regression testing for changes
- Benchmark dataset management
- Integration with Model Registry (#70) and Prompt Registry (#73)

Component #75 - Agent Evaluation & Testing Framework
"""

import asyncio
import json
import statistics
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol


class EvalMetricType(Enum):
    """Types of evaluation metrics."""

    PERFORMANCE = "performance"  # Accuracy, completion rate, latency
    SAFETY = "safety"  # Bias, harmful content, compliance
    UX = "ux"  # User satisfaction, interaction quality
    COST = "cost"  # Token usage, resource consumption
    CUSTOM = "custom"  # User-defined metrics


class EvalResultStatus(Enum):
    """Status of an evaluation result."""

    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    PENDING = "pending"
    ERROR = "error"


@dataclass
class TestCase:
    """A single test case for agent evaluation."""

    test_id: str
    name: str
    description: str

    # Input
    input_query: str
    input_context: str = None
    variables: Dict[str, Any] = field(default_factory=dict)

    # Expected output (for automated evaluation)
    expected_output: str = None
    expected_behavior: str = None  # Description of expected behavior

    # Metadata
    domain: str = "general"  # Domain category (e.g., "customer_support", "coding")
    difficulty: str = "medium"  # easy, medium, hard
    tags: List[str] = field(default_factory=list)
    is_edge_case: bool = False

    # Evaluation criteria
    min_acceptable_score: float = 0.7
    critical: bool = False  # If True, failure blocks deployment

    created_at: float = field(default_factory=time.time)


@dataclass
class EvalMetric:
    """A single evaluation metric result."""

    metric_name: str
    metric_type: EvalMetricType
    score: float  # 0-1 or 0-100 depending on metric
    weight: float = 1.0  # Importance weight

    # Details
    raw_value: float = None  # Raw measurement
    threshold: float = None  # Pass/fail threshold
    unit: str = None  # Unit of measurement (e.g., "seconds", "tokens")

    # Status
    status: EvalResultStatus = EvalResultStatus.PENDING
    explanation: str = None

    def is_passing(self) -> bool:
        """Check if metric passes threshold."""
        if self.threshold is None:
            return True
        return self.score >= self.threshold


@dataclass
class TestResult:
    """Result of running a single test case."""

    result_id: str
    test_id: str
    run_id: str

    # Agent output
    actual_output: str
    execution_time_ms: float
    tokens_used: int
    cost: float

    # Evaluation metrics
    metrics: List[EvalMetric] = field(default_factory=list)
    overall_score: float = 0.0
    status: EvalResultStatus = EvalResultStatus.PENDING

    # Metadata
    executed_at: float = field(default_factory=time.time)
    agent_config: Dict[str, Any] = field(default_factory=dict)
    error_message: str = None

    def calculate_overall_score(self) -> float:
        """Calculate weighted overall score."""
        if not self.metrics:
            return 0.0

        total_weight = sum(m.weight for m in self.metrics)
        if total_weight == 0:
            return 0.0

        weighted_sum = sum(m.score * m.weight for m in self.metrics)
        return weighted_sum / total_weight


@dataclass
class EvalRun:
    """A complete evaluation run."""

    run_id: str
    name: str
    description: str

    # What is being evaluated
    target_type: str  # "prompt", "model", "agent", "workflow"
    target_id: str
    target_version: str

    # Test cases
    test_case_ids: List[str]

    # Results
    results: List[TestResult] = field(default_factory=list)

    # Status
    status: str = "running"  # running, completed, failed
    started_at: float = field(default_factory=time.time)
    completed_at: float = None

    # Agent configuration used for this run
    agent_config: Dict[str, Any] = field(default_factory=dict)

    # Summary (computed)
    overall_score: float = 0.0
    pass_rate: float = 0.0
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    warning_tests: int = 0

    def compute_summary(self) -> None:
        """Compute summary statistics."""
        self.total_tests = len(self.results)
        self.passed_tests = sum(1 for r in self.results if r.status == EvalResultStatus.PASS)
        self.failed_tests = sum(1 for r in self.results if r.status == EvalResultStatus.FAIL)
        self.warning_tests = sum(1 for r in self.results if r.status == EvalResultStatus.WARNING)

        if self.total_tests > 0:
            self.pass_rate = self.passed_tests / self.total_tests
            self.overall_score = statistics.mean(r.overall_score for r in self.results)


@dataclass
class ABTest:
    """A/B test configuration for comparing variants."""

    test_id: str
    name: str
    description: str

    # Variants
    control_config: Dict[str, Any]  # Baseline configuration
    variant_configs: List[dict[str, Any]]  # Test configurations

    # Test parameters
    test_case_ids: List[str]
    sample_size: int = 100
    confidence_level: float = 0.95

    # Results
    control_results: List[TestResult] = field(default_factory=list)
    variant_results: List[list[TestResult]] = field(default_factory=list)

    # Analysis
    winner: str = None
    improvement_pct: float = None
    statistical_significance: bool = False

    status: str = "pending"  # pending, running, completed
    started_at: float = field(default_factory=time.time)
    completed_at: float = None


@dataclass
class BenchmarkDataset:
    """A benchmark dataset for evaluation."""

    dataset_id: str
    name: str
    description: str
    domain: str

    # Test cases
    test_case_ids: List[str]

    # Metadata
    version: str = "1.0.0"
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    tags: List[str] = field(default_factory=list)

    # Statistics
    total_tests: int = 0
    easy_tests: int = 0
    medium_tests: int = 0
    hard_tests: int = 0
    edge_cases: int = 0

    def compute_stats(self) -> None:
        """Compute dataset statistics."""
        self.total_tests = len(self.test_case_ids)


class AgentRunner(Protocol):
    """Protocol for running an agent against a test case."""

    async def run(
        self, query: str, context: str, variables: Dict[str, Any], config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run agent and return output with metadata."""
        ...


class MockAgentRunner:
    """Mock agent runner for testing."""

    async def run(
        self, query: str, context: str, variables: Dict[str, Any], config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Simulate agent execution."""
        # Simulate processing time
        await asyncio.sleep(0.1)

        # Generate mock response based on query
        response = f"Response to: {query[:50]}..."

        return {
            "output": response,
            "execution_time_ms": 150.0,
            "tokens_input": len(query.split()),
            "tokens_output": len(response.split()),
            "cost": 0.002,
            "metadata": {},
        }


class AMOSAgentEvaluator:
    """
    Comprehensive evaluation framework for AMOS agents.

    Implements 2025 AI evaluation patterns:
    - Multi-dimensional metrics (performance, safety, UX, cost)
    - Automated + human evaluation workflows
    - A/B testing for variant comparison
    - Regression testing for changes
    - Benchmark dataset management

    Use cases:
    - Evaluate prompt versions before deployment
    - Compare model performance
    - Regression test after changes
    - Benchmark against competitors
    - Validate safety and compliance

    Integration Points:
    - #70 Model Registry: Evaluate model versions
    - #73 Prompt Registry: Evaluate prompt versions
    - #63 Telemetry Engine: Collect runtime metrics
    """

    def __init__(self, agent_runner: Optional[AgentRunner] = None):
        self.agent_runner = agent_runner or MockAgentRunner()

        # Storage
        self.test_cases: Dict[str, TestCase] = {}
        self.eval_runs: Dict[str, EvalRun] = {}
        self.ab_tests: Dict[str, ABTest] = {}
        self.benchmarks: Dict[str, BenchmarkDataset] = {}
        self.results: Dict[str, TestResult] = {}

        # Metric evaluators
        self.metric_evaluators: Dict[str, Callable] = {
            "exact_match": self._eval_exact_match,
            "contains": self._eval_contains,
            "similarity": self._eval_similarity,
            "latency": self._eval_latency,
            "token_efficiency": self._eval_token_efficiency,
            "cost_efficiency": self._eval_cost_efficiency,
            "safety_check": self._eval_safety,
            "format_compliance": self._eval_format,
        }

    async def initialize(self) -> None:
        """Initialize evaluator."""
        print("[AgentEvaluator] Initialized")
        print(f"  - Metric evaluators: {len(self.metric_evaluators)}")
        print(f"  - Test cases: {len(self.test_cases)}")
        print(f"  - Benchmarks: {len(self.benchmarks)}")

    def create_test_case(
        self,
        name: str,
        description: str,
        input_query: str,
        expected_output: str = None,
        expected_behavior: str = None,
        domain: str = "general",
        difficulty: str = "medium",
        tags: List[str] = None,
        is_edge_case: bool = False,
        min_acceptable_score: float = 0.7,
        critical: bool = False,
        variables: Dict[str, Any] = None,
    ) -> TestCase:
        """Create a new test case."""
        test_id = f"test_{uuid.uuid4().hex[:12]}"

        test_case = TestCase(
            test_id=test_id,
            name=name,
            description=description,
            input_query=input_query,
            expected_output=expected_output,
            expected_behavior=expected_behavior,
            domain=domain,
            difficulty=difficulty,
            tags=tags or [],
            is_edge_case=is_edge_case,
            min_acceptable_score=min_acceptable_score,
            critical=critical,
            variables=variables or {},
        )

        self.test_cases[test_id] = test_case
        print(f"[AgentEvaluator] Created test case: {name} ({test_id})")

        return test_case

    def create_benchmark_dataset(
        self,
        name: str,
        description: str,
        domain: str,
        test_case_ids: List[str],
        tags: List[str] = None,
    ) -> BenchmarkDataset:
        """Create a benchmark dataset."""
        dataset_id = f"bench_{uuid.uuid4().hex[:12]}"

        # Validate test cases exist
        valid_ids = [tid for tid in test_case_ids if tid in self.test_cases]

        benchmark = BenchmarkDataset(
            dataset_id=dataset_id,
            name=name,
            description=description,
            domain=domain,
            test_case_ids=valid_ids,
            tags=tags or [],
        )

        benchmark.compute_stats()
        self.benchmarks[dataset_id] = benchmark

        print(f"[AgentEvaluator] Created benchmark: {name} ({len(valid_ids)} tests)")

        return benchmark

    async def run_evaluation(
        self,
        name: str,
        description: str,
        target_type: str,
        target_id: str,
        target_version: str,
        test_case_ids: List[str],
        agent_config: Dict[str, Any] = None,
    ) -> EvalRun:
        """Run a complete evaluation."""
        run_id = f"run_{uuid.uuid4().hex[:12]}"

        eval_run = EvalRun(
            run_id=run_id,
            name=name,
            description=description,
            target_type=target_type,
            target_id=target_id,
            target_version=target_version,
            test_case_ids=test_case_ids,
            agent_config=agent_config or {},
        )

        self.eval_runs[run_id] = eval_run

        print(f"[AgentEvaluator] Starting evaluation run: {name}")
        print(f"  Target: {target_type} {target_id} v{target_version}")
        print(f"  Tests: {len(test_case_ids)}")

        # Run each test case
        for test_id in test_case_ids:
            if test_id not in self.test_cases:
                print(f"  ⚠ Skipping unknown test: {test_id}")
                continue

            test_case = self.test_cases[test_id]
            result = await self._run_single_test(test_case, eval_run)
            eval_run.results.append(result)

            # Store result
            self.results[result.result_id] = result

        # Compute summary
        eval_run.compute_summary()
        eval_run.status = "completed"
        eval_run.completed_at = time.time()

        print(f"[AgentEvaluator] Evaluation complete: {eval_run.pass_rate:.1%} pass rate")

        return eval_run

    async def _run_single_test(self, test_case: TestCase, eval_run: EvalRun) -> TestResult:
        """Run a single test case."""
        result_id = f"result_{uuid.uuid4().hex[:16]}"

        start_time = time.time()

        try:
            # Run agent
            agent_output = await self.agent_runner.run(
                query=test_case.input_query,
                context=test_case.input_context,
                variables=test_case.variables,
                config=eval_run.agent_config,
            )

            execution_time = (time.time() - start_time) * 1000

            # Create result
            result = TestResult(
                result_id=result_id,
                test_id=test_case.test_id,
                run_id=eval_run.run_id,
                actual_output=agent_output["output"],
                execution_time_ms=execution_time,
                tokens_used=agent_output.get("tokens_input", 0)
                + agent_output.get("tokens_output", 0),
                cost=agent_output.get("cost", 0.0),
                agent_config=eval_run.agent_config,
            )

            # Evaluate metrics
            metrics = self._evaluate_test(test_case, result, agent_output)
            result.metrics = metrics
            result.overall_score = result.calculate_overall_score()

            # Determine status
            if result.overall_score >= test_case.min_acceptable_score:
                result.status = EvalResultStatus.PASS
            elif result.overall_score >= test_case.min_acceptable_score * 0.8:
                result.status = EvalResultStatus.WARNING
            else:
                result.status = EvalResultStatus.FAIL

        except Exception as e:  # noqa: BLE001
            result = TestResult(
                result_id=result_id,
                test_id=test_case.test_id,
                run_id=eval_run.run_id,
                actual_output="",
                execution_time_ms=(time.time() - start_time) * 1000,
                tokens_used=0,
                cost=0.0,
                status=EvalResultStatus.ERROR,
                error_message=str(e),
            )

        return result

    def _evaluate_test(
        self, test_case: TestCase, result: TestResult, agent_output: Dict[str, Any]
    ) -> List[EvalMetric]:
        """Evaluate all metrics for a test result."""
        metrics = []

        # Performance metrics
        if test_case.expected_output:
            # Exact match
            exact_score = self._eval_exact_match(result.actual_output, test_case.expected_output)
            metrics.append(
                EvalMetric(
                    metric_name="exact_match",
                    metric_type=EvalMetricType.PERFORMANCE,
                    score=exact_score,
                    weight=2.0 if test_case.critical else 1.0,
                    threshold=0.9,
                    explanation="Exact string match accuracy",
                )
            )

            # Contains check
            contains_score = self._eval_contains(result.actual_output, test_case.expected_output)
            metrics.append(
                EvalMetric(
                    metric_name="content_similarity",
                    metric_type=EvalMetricType.PERFORMANCE,
                    score=contains_score,
                    weight=1.0,
                    threshold=0.7,
                    explanation="Content overlap similarity",
                )
            )

        # Latency metric
        latency_score = self._eval_latency(result.execution_time_ms)
        metrics.append(
            EvalMetric(
                metric_name="latency",
                metric_type=EvalMetricType.PERFORMANCE,
                score=latency_score,
                raw_value=result.execution_time_ms,
                unit="ms",
                weight=1.0,
                threshold=0.8,
                explanation=f"Response time: {result.execution_time_ms:.0f}ms",
            )
        )

        # Token efficiency
        token_score = self._eval_token_efficiency(result.tokens_used)
        metrics.append(
            EvalMetric(
                metric_name="token_efficiency",
                metric_type=EvalMetricType.COST,
                score=token_score,
                raw_value=result.tokens_used,
                unit="tokens",
                weight=0.5,
                threshold=0.6,
                explanation=f"Token usage: {result.tokens_used}",
            )
        )

        # Cost efficiency
        cost_score = self._eval_cost_efficiency(result.cost)
        metrics.append(
            EvalMetric(
                metric_name="cost_efficiency",
                metric_type=EvalMetricType.COST,
                score=cost_score,
                raw_value=result.cost,
                unit="USD",
                weight=0.5,
                threshold=0.7,
                explanation=f"Cost: ${result.cost:.4f}",
            )
        )

        # Safety check
        safety_score = self._eval_safety(result.actual_output)
        metrics.append(
            EvalMetric(
                metric_name="safety",
                metric_type=EvalMetricType.SAFETY,
                score=safety_score,
                weight=3.0,  # High weight for safety
                threshold=0.95,
                explanation="Content safety check",
            )
        )

        return metrics

    def _eval_exact_match(self, actual: str, expected: str) -> float:
        """Evaluate exact string match."""
        return 1.0 if actual.strip() == expected.strip() else 0.0

    def _eval_contains(self, actual: str, expected: str) -> float:
        """Evaluate if expected content is contained in actual."""
        expected_words = set(expected.lower().split())
        actual_words = set(actual.lower().split())

        if not expected_words:
            return 1.0

        overlap = len(expected_words & actual_words)
        return overlap / len(expected_words)

    def _eval_similarity(self, actual: str, expected: str) -> float:
        """Evaluate semantic similarity (simplified)."""
        # In production, this would use embeddings
        return self._eval_contains(actual, expected)

    def _eval_latency(self, latency_ms: float) -> float:
        """Score latency (lower is better)."""
        # Score: 1000ms = 1.0, 5000ms = 0.0
        if latency_ms <= 1000:
            return 1.0
        elif latency_ms >= 5000:
            return 0.0
        else:
            return 1.0 - (latency_ms - 1000) / 4000

    def _eval_token_efficiency(self, tokens: int) -> float:
        """Score token usage efficiency."""
        # Score: 500 tokens = 1.0, 4000 tokens = 0.0
        if tokens <= 500:
            return 1.0
        elif tokens >= 4000:
            return 0.0
        else:
            return 1.0 - (tokens - 500) / 3500

    def _eval_cost_efficiency(self, cost: float) -> float:
        """Score cost efficiency."""
        # Score: $0.001 = 1.0, $0.05 = 0.0
        if cost <= 0.001:
            return 1.0
        elif cost >= 0.05:
            return 0.0
        else:
            return 1.0 - (cost - 0.001) / 0.049

    def _eval_safety(self, output: str) -> float:
        """Basic safety check (simplified)."""
        # Check for common problematic patterns
        problematic_patterns = [
            "I cannot help",
            "I can't assist",
            "inappropriate",
            "harmful",
            "dangerous",
        ]

        output_lower = output.lower()
        for pattern in problematic_patterns:
            if pattern in output_lower:
                return 0.5  # Warning

        return 1.0  # Pass

    def _eval_format(self, output: str, expected_format: str = None) -> float:
        """Evaluate format compliance."""
        if expected_format is None:
            return 1.0

        # Check for format indicators (JSON, markdown, etc.)
        if expected_format == "json":
            try:
                json.loads(output)
                return 1.0
            except Exception:
                return 0.0

        return 1.0

    async def run_ab_test(
        self,
        name: str,
        description: str,
        control_config: Dict[str, Any],
        variant_configs: List[dict[str, Any]],
        test_case_ids: List[str],
        sample_size: int = 100,
    ) -> ABTest:
        """Run an A/B test comparing configurations."""
        test_id = f"abtest_{uuid.uuid4().hex[:12]}"

        ab_test = ABTest(
            test_id=test_id,
            name=name,
            description=description,
            control_config=control_config,
            variant_configs=variant_configs,
            test_case_ids=test_case_ids,
            sample_size=sample_size,
        )

        self.ab_tests[test_id] = ab_test
        ab_test.status = "running"

        print(f"[AgentEvaluator] Starting A/B test: {name}")
        print(f"  Variants: 1 control + {len(variant_configs)} test variants")
        print(f"  Tests per variant: {len(test_case_ids)}")

        # Run control
        control_run = await self.run_evaluation(
            name=f"{name} - Control",
            description="Control baseline",
            target_type=control_config.get("type", "agent"),
            target_id=control_config.get("id", "control"),
            target_version=control_config.get("version", "1.0.0"),
            test_case_ids=test_case_ids,
            agent_config=control_config,
        )
        ab_test.control_results = control_run.results

        # Run variants
        for i, variant_config in enumerate(variant_configs):
            variant_run = await self.run_evaluation(
                name=f"{name} - Variant {i+1}",
                description=f"Test variant {i+1}",
                target_type=variant_config.get("type", "agent"),
                target_id=variant_config.get("id", f"variant_{i+1}"),
                target_version=variant_config.get("version", "1.0.0"),
                test_case_ids=test_case_ids,
                agent_config=variant_config,
            )
            ab_test.variant_results.append(variant_run.results)

        # Analyze results
        self._analyze_ab_test(ab_test)

        ab_test.status = "completed"
        ab_test.completed_at = time.time()

        print(f"[AgentEvaluator] A/B test complete: {ab_test.winner} wins")

        return ab_test

    def _analyze_ab_test(self, ab_test: ABTest) -> None:
        """Analyze A/B test results and determine winner."""
        if not ab_test.control_results:
            return

        control_scores = [r.overall_score for r in ab_test.control_results]
        control_avg = statistics.mean(control_scores) if control_scores else 0

        best_variant = None
        best_improvement = 0

        for i, variant_results in enumerate(ab_test.variant_results):
            variant_scores = [r.overall_score for r in variant_results]
            variant_avg = statistics.mean(variant_scores) if variant_scores else 0

            improvement = (variant_avg - control_avg) / control_avg if control_avg > 0 else 0

            if improvement > best_improvement:
                best_improvement = improvement
                best_variant = f"Variant {i+1}"

        if best_variant and best_improvement > 0.05:  # 5% improvement threshold
            ab_test.winner = best_variant
            ab_test.improvement_pct = best_improvement * 100
            ab_test.statistical_significance = best_improvement > 0.1  # 10% = significant

    def compare_eval_runs(self, baseline_run_id: str, new_run_id: str) -> Dict[str, Any]:
        """Compare two evaluation runs (for regression testing)."""
        if baseline_run_id not in self.eval_runs or new_run_id not in self.eval_runs:
            return {"error": "Run not found"}

        baseline = self.eval_runs[baseline_run_id]
        new = self.eval_runs[new_run_id]

        comparison = {
            "baseline_run": baseline_run_id,
            "new_run": new_run_id,
            "baseline_score": baseline.overall_score,
            "new_score": new.overall_score,
            "score_delta": new.overall_score - baseline.overall_score,
            "score_delta_pct": (
                (new.overall_score - baseline.overall_score) / baseline.overall_score * 100
            )
            if baseline.overall_score > 0
            else 0,
            "baseline_pass_rate": baseline.pass_rate,
            "new_pass_rate": new.pass_rate,
            "regression_detected": new.overall_score < baseline.overall_score * 0.95,
            "improvement_detected": new.overall_score > baseline.overall_score * 1.05,
        }

        return comparison

    def get_eval_summary(self, run_id: str) -> Dict[str, Any]:
        """Get summary of an evaluation run."""
        if run_id not in self.eval_runs:
            return {"error": "Run not found"}

        eval_run = self.eval_runs[run_id]

        # Metric breakdown
        metric_scores: Dict[str, list[float]] = {}
        for result in eval_run.results:
            for metric in result.metrics:
                if metric.metric_name not in metric_scores:
                    metric_scores[metric.metric_name] = []
                metric_scores[metric.metric_name].append(metric.score)

        metric_summary = {
            name: {"avg": statistics.mean(scores), "min": min(scores), "max": max(scores)}
            for name, scores in metric_scores.items()
        }

        return {
            "run_id": run_id,
            "name": eval_run.name,
            "target": f"{eval_run.target_type} {eval_run.target_id} v{eval_run.target_version}",
            "status": eval_run.status,
            "overall_score": eval_run.overall_score,
            "pass_rate": eval_run.pass_rate,
            "total_tests": eval_run.total_tests,
            "passed": eval_run.passed_tests,
            "failed": eval_run.failed_tests,
            "warnings": eval_run.warning_tests,
            "metrics": metric_summary,
            "duration_seconds": (eval_run.completed_at or time.time()) - eval_run.started_at,
        }


# ============================================================================
# DEMO
# ============================================================================


async def demo_agent_evaluator():
    """Demonstrate AMOS Agent Evaluator capabilities."""
    print("\n" + "=" * 70)
    print("AMOS AGENT EVALUATOR - COMPONENT #75")
    print("=" * 70)

    evaluator = AMOSAgentEvaluator()
    await evaluator.initialize()

    print("\n[1] Creating test cases...")

    # Create test cases for customer support domain
    test1 = evaluator.create_test_case(
        name="Password Reset Request",
        description="User requests password reset",
        input_query="I forgot my password, can you help me reset it?",
        expected_output="I can help you reset your password",
        expected_behavior="Agent should offer to reset password and verify identity",
        domain="customer_support",
        difficulty="easy",
        tags=["password", "account", "support"],
        min_acceptable_score=0.8,
    )

    test2 = evaluator.create_test_case(
        name="Technical Support - API Error",
        description="User reports API error",
        input_query="I'm getting a 500 error when calling your API endpoint",
        expected_output=" troubleshooting steps",
        expected_behavior="Agent should provide troubleshooting steps and ask for error details",
        domain="technical_support",
        difficulty="medium",
        tags=["api", "error", "technical"],
        min_acceptable_score=0.75,
    )

    test3 = evaluator.create_test_case(
        name="Billing Inquiry",
        description="User questions charge on account",
        input_query="Why was I charged $49.99 yesterday?",
        expected_output="billing",
        expected_behavior="Agent should look up transaction and explain charge",
        domain="billing",
        difficulty="medium",
        tags=["billing", "payment", "account"],
        critical=True,
        min_acceptable_score=0.9,
    )

    test4 = evaluator.create_test_case(
        name="Edge Case - Ambiguous Request",
        description="Vague user request requiring clarification",
        input_query="It's not working",
        expected_behavior="Agent should ask clarifying questions",
        domain="general",
        difficulty="hard",
        tags=["edge_case", "ambiguous"],
        is_edge_case=True,
        min_acceptable_score=0.6,
    )

    print(f"  ✓ Created {len(evaluator.test_cases)} test cases")

    print("\n[2] Creating benchmark dataset...")

    benchmark = evaluator.create_benchmark_dataset(
        name="Customer Support Suite v1",
        description="Comprehensive customer support evaluation tests",
        domain="customer_support",
        test_case_ids=list(evaluator.test_cases.keys()),
        tags=["production", "customer_facing"],
    )

    print(f"  ✓ Benchmark: {benchmark.name} ({benchmark.total_tests} tests)")

    print("\n[3] Running evaluation on baseline configuration...")

    baseline_run = await evaluator.run_evaluation(
        name="Baseline Agent v1.0.0",
        description="Evaluation of current production agent",
        target_type="agent",
        target_id="support_agent",
        target_version="1.0.0",
        test_case_ids=benchmark.test_case_ids,
        agent_config={"model": "gpt-4", "temperature": 0.7, "max_tokens": 500},
    )

    print(
        f"  ✓ Baseline: {baseline_run.pass_rate:.1%} pass rate, score: {baseline_run.overall_score:.2f}"
    )

    print("\n[4] Running evaluation on new configuration...")

    new_run = await evaluator.run_evaluation(
        name="Improved Agent v1.1.0",
        description="Evaluation with improved prompts",
        target_type="agent",
        target_id="support_agent",
        target_version="1.1.0",
        test_case_ids=benchmark.test_case_ids,
        agent_config={
            "model": "gpt-4-turbo",
            "temperature": 0.5,  # More deterministic
            "max_tokens": 750,
        },
    )

    print(f"  ✓ New version: {new_run.pass_rate:.1%} pass rate, score: {new_run.overall_score:.2f}")

    print("\n[5] Regression testing - comparing runs...")

    comparison = evaluator.compare_eval_runs(baseline_run.run_id, new_run.run_id)

    print(
        f"  Score delta: {comparison['score_delta']:+.3f} ({comparison['score_delta_pct']:+.1f}%)"
    )
    print(
        f"  Pass rate: {comparison['baseline_pass_rate']:.1%} → {comparison['new_pass_rate']:.1%}"
    )

    if comparison["regression_detected"]:
        print("  ⚠ REGRESSION DETECTED - Do not deploy!")
    elif comparison["improvement_detected"]:
        print("  ✓ IMPROVEMENT DETECTED - Safe to deploy")
    else:
        print("  → No significant change")

    print("\n[6] Running A/B test...")

    ab_test = await evaluator.run_ab_test(
        name="Model Comparison: GPT-4 vs GPT-3.5",
        description="Compare performance between model versions",
        control_config={
            "type": "agent",
            "id": "gpt4_agent",
            "version": "1.0",
            "model": "gpt-4",
            "temperature": 0.7,
        },
        variant_configs=[
            {
                "type": "agent",
                "id": "gpt35_agent",
                "version": "1.0",
                "model": "gpt-3.5-turbo",
                "temperature": 0.7,
            }
        ],
        test_case_ids=[test1.test_id, test2.test_id, test3.test_id],
        sample_size=50,
    )

    print("  ✓ A/B test complete")
    print(f"    Winner: {ab_test.winner or 'No clear winner'}")
    if ab_test.improvement_pct:
        print(f"    Improvement: {ab_test.improvement_pct:.1f}%")
    print(f"    Significant: {'Yes' if ab_test.statistical_significance else 'No'}")

    print("\n[7] Evaluation summary...")

    summary = evaluator.get_eval_summary(new_run.run_id)

    print(f"  Run: {summary['name']}")
    print(f"  Target: {summary['target']}")
    print(f"  Overall Score: {summary['overall_score']:.2f}")
    print(f"  Pass Rate: {summary['pass_rate']:.1%}")
    print(
        f"  Tests: {summary['passed']} passed, {summary['failed']} failed, {summary['warnings']} warnings"
    )

    print("\n  Metric Breakdown:")
    for metric_name, stats in summary["metrics"].items():
        print(
            f"    {metric_name}: avg={stats['avg']:.2f}, min={stats['min']:.2f}, max={stats['max']:.2f}"
        )

    print("\n[8] Evaluation statistics...")

    print(f"  Total test cases: {len(evaluator.test_cases)}")
    print(f"  Total eval runs: {len(evaluator.eval_runs)}")
    print(f"  A/B tests: {len(evaluator.ab_tests)}")
    print(f"  Benchmark datasets: {len(evaluator.benchmarks)}")

    print("\n" + "=" * 70)
    print("AGENT EVALUATOR DEMO COMPLETE")
    print("=" * 70)
    print("\nKey Features Demonstrated:")
    print("  ✓ Test case creation with expected outputs")
    print("  ✓ Multi-dimensional metrics (performance, safety, cost)")
    print("  ✓ Automated evaluation with scoring")
    print("  ✓ Regression testing between versions")
    print("  ✓ A/B testing for configuration comparison")
    print("  ✓ Benchmark dataset management")
    print("  ✓ Pass/fail/warning status tracking")
    print("  ✓ Metric aggregation and reporting")
    print("\nIntegration Points:")
    print("  • #70 Model Registry: Evaluate model versions")
    print("  • #73 Prompt Registry: Test prompt variants")
    print("  • #63 Telemetry Engine: Production metrics")
    print("  • #69 Feature Flags: Gate deployments on eval results")


if __name__ == "__main__":
    asyncio.run(demo_agent_evaluator())
