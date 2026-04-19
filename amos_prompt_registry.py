#!/usr/bin/env python3
"""AMOS Prompt Registry - Versioned prompt management for production AI.

Implements 2025 production AI patterns (PromptLayer, LangSmith, Maxim AI):
- Semantic versioning for prompts
- Environment-specific deployments (dev/staging/prod)
- A/B testing with variant tracking
- Performance metrics per version
- Template variables and dynamic composition
- Integration with Feature Flags (#69) and LLM Router (#72)

Component #73 - Prompt Management & Versioning Layer
"""

import asyncio
import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Protocol


class PromptStage(Enum):
    """Prompt lifecycle stages."""

    DRAFT = "draft"
    REVIEW = "review"
    STAGING = "staging"
    PRODUCTION = "production"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class Environment(Enum):
    """Deployment environments."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class PromptVariable:
    """Template variable definition."""

    name: str
    description: str
    type: str = "string"  # string, int, float, bool, list, dict
    required: bool = True
    default_value: Any = None
    validation_regex: str = None


@dataclass
class PromptVersion:
    """A versioned prompt template."""

    version_id: str
    prompt_id: str
    version: str  # Semantic version: major.minor.patch
    stage: PromptStage

    # Content
    template: str
    system_prompt: str = None
    variables: list[PromptVariable] = field(default_factory=list)

    # Metadata
    description: str = ""
    created_by: str = "system"
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    # Performance tracking
    invocation_count: int = 0
    avg_latency_ms: float = 0.0
    success_rate: float = 1.0
    token_count_total: int = 0
    cost_total: float = 0.0

    # Quality metrics
    feedback_scores: list[float] = field(default_factory=list)
    quality_score: float = 0.0  # 0-100

    # Versioning
    parent_version: str = None
    changelog: str = ""
    tags: list[str] = field(default_factory=list)

    def compute_hash(self) -> str:
        """Compute content hash for immutability verification."""
        content = (
            f"{self.template}:{self.system_prompt}:{json.dumps([v.name for v in self.variables])}"
        )
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version_id": self.version_id,
            "prompt_id": self.prompt_id,
            "version": self.version,
            "stage": self.stage.value,
            "template": self.template[:100] + "..." if len(self.template) > 100 else self.template,
            "system_prompt": self.system_prompt[:100] + "..."
            if self.system_prompt and len(self.system_prompt) > 100
            else self.system_prompt,
            "variables": [v.name for v in self.variables],
            "description": self.description,
            "created_by": self.created_by,
            "created_at": datetime.fromtimestamp(self.created_at).isoformat(),
            "invocation_count": self.invocation_count,
            "avg_latency_ms": self.avg_latency_ms,
            "success_rate": self.success_rate,
            "quality_score": self.quality_score,
            "tags": self.tags,
        }


@dataclass
class PromptDeployment:
    """Prompt deployment to a specific environment."""

    deployment_id: str
    prompt_id: str
    version_id: str
    environment: Environment
    deployed_at: float = field(default_factory=time.time)
    deployed_by: str = "system"
    is_active: bool = True
    traffic_percentage: float = 100.0  # For gradual rollout

    # A/B testing
    is_variant: bool = False
    variant_name: str = None  # "control", "variant_a", etc.
    parent_deployment_id: str = None


@dataclass
class PromptABTest:
    """A/B test configuration for prompts."""

    test_id: str
    prompt_id: str
    name: str
    control_version_id: str
    status: str = "running"  # running, paused, completed

    # Variants
    variant_version_ids: list[str] = field(default_factory=list)

    # Traffic split (must sum to 100)
    control_traffic: float = 50.0
    variant_traffic_splits: Dict[str, float] = field(default_factory=dict)

    # Success criteria
    primary_metric: str = "quality_score"  # quality_score, success_rate, latency
    minimum_sample_size: int = 100
    confidence_level: float = 0.95

    # Results
    started_at: float = field(default_factory=time.time)
    ended_at: float = None
    winner_version_id: str = None
    improvement_percentage: float = None

    def get_variant_for_request(self, request_id: str) -> str:
        """Deterministically assign variant based on request ID."""
        hash_val = int(hashlib.md5(request_id.encode()).hexdigest(), 16)
        bucket = hash_val % 100

        if bucket < self.control_traffic:
            return self.control_version_id

        cumulative = self.control_traffic
        for variant_id, split in self.variant_traffic_splits.items():
            cumulative += split
            if bucket < cumulative:
                return variant_id

        return self.control_version_id


@dataclass
class PromptExecution:
    """Record of a prompt execution."""

    execution_id: str
    prompt_id: str
    version_id: str
    rendered_prompt: str
    variables_used: Dict[str, Any]

    deployment_id: str = None
    ab_test_id: str = None
    variant_id: str = None

    # Response
    response_text: str = ""
    tokens_input: int = 0
    tokens_output: int = 0
    latency_ms: float = 0.0
    cost: float = 0.0

    # Quality
    success: bool = True
    error_message: str = None
    feedback_score: float = None  # User rating 1-5

    executed_at: float = field(default_factory=time.time)
    environment: Environment = Environment.DEVELOPMENT


class StorageBackend(Protocol):
    """Protocol for prompt storage backends."""

    async def store(self, key: str, data: Dict[str, Any]) -> bool:
        """Store prompt data."""
        ...

    async def retrieve(self, key: str) -> dict[str, Any]:
        """Retrieve prompt data."""
        ...

    async def delete(self, key: str) -> bool:
        """Delete prompt data."""
        ...

    async def list_keys(self, prefix: str) -> list[str]:
        """List keys with prefix."""
        ...


class LocalStorageBackend:
    """Local filesystem storage for prompts."""

    def __init__(self, base_path: str = "_AMOS_BRAIN/prompts"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def store(self, key: str, data: Dict[str, Any]) -> bool:
        file_path = self.base_path / f"{key}.json"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(json.dumps(data, indent=2))
        return True

    async def retrieve(self, key: str) -> dict[str, Any]:
        file_path = self.base_path / f"{key}.json"
        if file_path.exists():
            return json.loads(file_path.read_text())
        return None

    async def delete(self, key: str) -> bool:
        file_path = self.base_path / f"{key}.json"
        if file_path.exists():
            file_path.unlink()
            return True
        return False

    async def list_keys(self, prefix: str) -> list[str]:
        keys = []
        for file_path in self.base_path.rglob("*.json"):
            relative = file_path.relative_to(self.base_path)
            key = str(relative).replace(".json", "").replace("/", "-")
            if key.startswith(prefix):
                keys.append(key)
        return keys


class AMOSPromptRegistry:
    """
    Central prompt registry for AMOS ecosystem.

    Implements 2025 production AI patterns:
    - Semantic versioning for prompts
    - Environment-specific deployments
    - A/B testing with variant tracking
    - Performance metrics per version
    - Integration with Feature Flags (#69) and LLM Router (#72)

    Use cases:
    - Version control for system prompts
    - A/B testing prompt variants
    - Gradual rollout of prompt changes
    - Performance monitoring and optimization
    """

    def __init__(self, storage: Optional[StorageBackend] = None):
        self.storage = storage or LocalStorageBackend()

        # In-memory caches
        self.prompts: dict[str, dict[str, PromptVersion]] = {}  # prompt_id -> {version_id: version}
        self.deployments: Dict[str, PromptDeployment] = {}
        self.ab_tests: Dict[str, PromptABTest] = {}
        self.executions: list[PromptExecution] = []

        # Environment configs
        self.environment_configs: dict[Environment, dict[str, str]] = {
            Environment.DEVELOPMENT: {},
            Environment.STAGING: {},
            Environment.PRODUCTION: {},
        }

    async def initialize(self) -> None:
        """Initialize prompt registry."""
        print("[PromptRegistry] Initialized")
        print(f"  - Loaded prompts: {len(self.prompts)}")
        print(
            f"  - Active deployments: {len([d for d in self.deployments.values() if d.is_active])}"
        )
        print(
            f"  - Running A/B tests: {len([t for t in self.ab_tests.values() if t.status == 'running'])}"
        )

    def create_prompt(
        self,
        prompt_id: str,
        template: str,
        system_prompt: str = None,
        variables: list[PromptVariable] = None,
        description: str = "",
        created_by: str = "system",
        tags: list[str] = None,
    ) -> PromptVersion:
        """Create a new prompt with initial version."""
        if prompt_id in self.prompts:
            raise ValueError(f"Prompt {prompt_id} already exists")

        version_id = f"{prompt_id}_v1.0.0"

        prompt_version = PromptVersion(
            version_id=version_id,
            prompt_id=prompt_id,
            version="1.0.0",
            stage=PromptStage.DRAFT,
            template=template,
            system_prompt=system_prompt,
            variables=variables or [],
            description=description,
            created_by=created_by,
            tags=tags or [],
        )

        self.prompts[prompt_id] = {version_id: prompt_version}

        print(f"[PromptRegistry] Created: {prompt_id} v1.0.0")
        return prompt_version

    def create_version(
        self,
        prompt_id: str,
        template: str,
        version_bump: str = "patch",  # major, minor, patch
        system_prompt: str = None,
        variables: list[PromptVariable] = None,
        description: str = "",
        created_by: str = "system",
        changelog: str = "",
    ) -> PromptVersion:
        """Create new version of existing prompt."""
        if prompt_id not in self.prompts:
            raise ValueError(f"Prompt {prompt_id} not found")

        # Get latest version
        versions = self.prompts[prompt_id]
        latest = max(versions.values(), key=lambda v: v.created_at)

        # Parse and bump version
        major, minor, patch = map(int, latest.version.split("."))
        if version_bump == "major":
            major += 1
            minor = 0
            patch = 0
        elif version_bump == "minor":
            minor += 1
            patch = 0
        else:
            patch += 1

        new_version = f"{major}.{minor}.{patch}"
        version_id = f"{prompt_id}_v{new_version}"

        prompt_version = PromptVersion(
            version_id=version_id,
            prompt_id=prompt_id,
            version=new_version,
            stage=PromptStage.DRAFT,
            template=template,
            system_prompt=system_prompt or latest.system_prompt,
            variables=variables or latest.variables,
            description=description,
            created_by=created_by,
            parent_version=latest.version_id,
            changelog=changelog,
        )

        self.prompts[prompt_id][version_id] = prompt_version

        print(f"[PromptRegistry] New version: {prompt_id} v{new_version}")
        return prompt_version

    def transition_stage(
        self, prompt_id: str, version: str, new_stage: PromptStage, approved_by: str = None
    ) -> bool:
        """Transition prompt version to new stage."""
        if prompt_id not in self.prompts:
            return False

        version_id = f"{prompt_id}_v{version}"
        if version_id not in self.prompts[prompt_id]:
            return False

        prompt_version = self.prompts[prompt_id][version_id]
        old_stage = prompt_version.stage
        prompt_version.stage = new_stage
        prompt_version.updated_at = time.time()

        print(
            f"[PromptRegistry] Stage: {prompt_id} v{version} {old_stage.value} → {new_stage.value}"
        )

        if approved_by:
            print(f"  Approved by: {approved_by}")

        return True

    def deploy(
        self,
        prompt_id: str,
        version: str,
        environment: Environment,
        traffic_percentage: float = 100.0,
        deployed_by: str = "system",
    ) -> PromptDeployment:
        """Deploy prompt version to environment."""
        version_id = f"{prompt_id}_v{version}"
        deployment_id = f"deploy_{uuid.uuid4().hex[:12]}"

        # Deactivate previous deployment in same environment
        for dep in self.deployments.values():
            if dep.prompt_id == prompt_id and dep.environment == environment and dep.is_active:
                dep.is_active = False

        deployment = PromptDeployment(
            deployment_id=deployment_id,
            prompt_id=prompt_id,
            version_id=version_id,
            environment=environment,
            deployed_by=deployed_by,
            traffic_percentage=traffic_percentage,
        )

        self.deployments[deployment_id] = deployment

        env_name = environment.value
        print(
            f"[PromptRegistry] Deployed: {prompt_id} v{version} → {env_name} ({traffic_percentage}% traffic)"
        )

        return deployment

    def get_prompt_for_request(
        self,
        prompt_id: str,
        environment: Environment = Environment.DEVELOPMENT,
        request_id: str = None,
        variables: dict[str, Any] = None,
    ) -> Tuple[PromptVersion, PromptDeployment]:
        """Get prompt version for a request (with A/B testing support)."""
        if prompt_id not in self.prompts:
            return None, None

        # Find active deployment for environment
        deployment = None
        for dep in self.deployments.values():
            if dep.prompt_id == prompt_id and dep.environment == environment and dep.is_active:
                deployment = dep
                break

        if not deployment:
            # Return latest version in DRAFT/REVIEW
            versions = self.prompts[prompt_id]
            draft_versions = [
                v for v in versions.values() if v.stage in (PromptStage.DRAFT, PromptStage.REVIEW)
            ]
            if draft_versions:
                return max(draft_versions, key=lambda v: v.created_at), None
            return None, None

        version_id = deployment.version_id

        # Check for A/B test
        ab_test = None
        for test in self.ab_tests.values():
            if (
                test.prompt_id == prompt_id
                and test.status == "running"
                and deployment.version_id in [test.control_version_id] + test.variant_version_ids
            ):
                ab_test = test
                break

        if ab_test and request_id:
            # A/B test active - select variant
            selected_version_id = ab_test.get_variant_for_request(request_id)
            if selected_version_id in self.prompts[prompt_id]:
                version_id = selected_version_id

        return self.prompts[prompt_id].get(version_id), deployment

    def render_prompt(self, prompt_version: PromptVersion, variables: Dict[str, Any]) -> str:
        """Render prompt template with variables."""
        rendered = prompt_version.template

        for var in prompt_version.variables:
            placeholder = f"{{{var.name}}}"
            value = variables.get(var.name, var.default_value)

            if value is None and var.required:
                raise ValueError(f"Required variable '{var.name}' not provided")

            if value is not None:
                rendered = rendered.replace(placeholder, str(value))

        return rendered

    def start_ab_test(
        self,
        prompt_id: str,
        name: str,
        control_version: str,
        variant_versions: list[str],
        control_traffic: float = 50.0,
        variant_traffic: list[float] = None,
        primary_metric: str = "quality_score",
    ) -> PromptABTest:
        """Start A/B test for prompt variants."""
        if prompt_id not in self.prompts:
            raise ValueError(f"Prompt {prompt_id} not found")

        # Validate versions exist
        control_version_id = f"{prompt_id}_v{control_version}"
        if control_version_id not in self.prompts[prompt_id]:
            raise ValueError(f"Control version {control_version} not found")

        variant_version_ids = []
        for v in variant_versions:
            version_id = f"{prompt_id}_v{v}"
            if version_id not in self.prompts[prompt_id]:
                raise ValueError(f"Variant version {v} not found")
            variant_version_ids.append(version_id)

        # Calculate traffic splits
        if variant_traffic is None:
            remaining = 100.0 - control_traffic
            variant_traffic = [remaining / len(variant_versions)] * len(variant_versions)

        variant_splits = {
            variant_version_ids[i]: variant_traffic[i] for i in range(len(variant_versions))
        }

        test_id = f"abtest_{uuid.uuid4().hex[:12]}"

        ab_test = PromptABTest(
            test_id=test_id,
            prompt_id=prompt_id,
            name=name,
            control_version_id=control_version_id,
            variant_version_ids=variant_version_ids,
            control_traffic=control_traffic,
            variant_traffic_splits=variant_splits,
            primary_metric=primary_metric,
        )

        self.ab_tests[test_id] = ab_test

        print(f"[PromptRegistry] A/B test started: {name}")
        print(f"  Control: {control_version} ({control_traffic}%)")
        for i, v in enumerate(variant_versions):
            print(f"  Variant {i+1}: {v} ({variant_traffic[i]}%)")

        return ab_test

    def complete_ab_test(
        self, test_id: str, winner_version_id: str = None, improvement_percentage: float = None
    ) -> bool:
        """Complete A/B test and record results."""
        if test_id not in self.ab_tests:
            return False

        ab_test = self.ab_tests[test_id]
        ab_test.status = "completed"
        ab_test.ended_at = time.time()
        ab_test.winner_version_id = winner_version_id
        ab_test.improvement_percentage = improvement_percentage

        print(f"[PromptRegistry] A/B test completed: {ab_test.name}")
        if winner_version_id:
            version = self.prompts[ab_test.prompt_id].get(winner_version_id)
            winner_version = version.version if version else winner_version_id
            print(f"  Winner: v{winner_version} ({improvement_percentage:+.1f}% improvement)")

        return True

    def record_execution(
        self,
        prompt_id: str,
        version_id: str,
        rendered_prompt: str,
        variables: Dict[str, Any],
        response: str = "",
        tokens_input: int = 0,
        tokens_output: int = 0,
        latency_ms: float = 0.0,
        cost: float = 0.0,
        success: bool = True,
        error: str = None,
        deployment_id: str = None,
        ab_test_id: str = None,
        environment: Environment = Environment.DEVELOPMENT,
    ) -> PromptExecution:
        """Record prompt execution for analytics."""
        execution_id = f"exec_{uuid.uuid4().hex[:12]}"

        execution = PromptExecution(
            execution_id=execution_id,
            prompt_id=prompt_id,
            version_id=version_id,
            deployment_id=deployment_id,
            ab_test_id=ab_test_id,
            rendered_prompt=rendered_prompt,
            variables_used=variables,
            response_text=response,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            latency_ms=latency_ms,
            cost=cost,
            success=success,
            error_message=error,
            environment=environment,
        )

        self.executions.append(execution)

        # Update version metrics
        if prompt_id in self.prompts and version_id in self.prompts[prompt_id]:
            version = self.prompts[prompt_id][version_id]
            version.invocation_count += 1

            # Update rolling average
            n = version.invocation_count
            version.avg_latency_ms = (version.avg_latency_ms * (n - 1) + latency_ms) / n
            version.token_count_total += tokens_input + tokens_output
            version.cost_total += cost

            if not success:
                # Update success rate
                version.success_rate = (version.success_rate * (n - 1)) / n

        return execution

    def provide_feedback(
        self,
        execution_id: str,
        score: float,  # 1-5 rating
    ) -> bool:
        """Provide feedback for a prompt execution."""
        for exec in self.executions:
            if exec.execution_id == execution_id:
                exec.feedback_score = score

                # Update version quality score
                if (
                    exec.prompt_id in self.prompts
                    and exec.version_id in self.prompts[exec.prompt_id]
                ):
                    version = self.prompts[exec.prompt_id][exec.version_id]
                    version.feedback_scores.append(score)
                    version.quality_score = (
                        sum(version.feedback_scores) / len(version.feedback_scores) * 20
                    )  # Convert to 0-100

                return True

        return False

    def get_registry_summary(self) -> Dict[str, Any]:
        """Get registry summary statistics."""
        total_versions = sum(len(versions) for versions in self.prompts.values())
        total_executions = len(self.executions)

        stage_counts = {stage.value: 0 for stage in PromptStage}
        for versions in self.prompts.values():
            for version in versions.values():
                stage_counts[version.stage.value] += 1

        active_deployments = len([d for d in self.deployments.values() if d.is_active])
        running_tests = len([t for t in self.ab_tests.values() if t.status == "running"])

        # Calculate aggregate metrics
        total_cost = sum(e.cost for e in self.executions)
        avg_latency = sum(e.latency_ms for e in self.executions) / max(1, len(self.executions))
        success_rate = sum(1 for e in self.executions if e.success) / max(1, len(self.executions))

        return {
            "total_prompts": len(self.prompts),
            "total_versions": total_versions,
            "versions_by_stage": stage_counts,
            "total_executions": total_executions,
            "active_deployments": active_deployments,
            "running_ab_tests": running_tests,
            "total_cost": round(total_cost, 4),
            "avg_latency_ms": round(avg_latency, 2),
            "success_rate": round(success_rate * 100, 2),
        }

    def list_prompts(
        self, stage: Optional[PromptStage] = None, tag: str = None
    ) -> list[dict[str, Any]]:
        """List prompts with optional filtering."""
        results = []

        for prompt_id, versions in self.prompts.items():
            # Get latest version for summary
            latest = max(versions.values(), key=lambda v: v.created_at)

            if stage and latest.stage != stage:
                continue

            if tag and tag not in latest.tags:
                continue

            results.append(
                {
                    "prompt_id": prompt_id,
                    "latest_version": latest.version,
                    "stage": latest.stage.value,
                    "total_versions": len(versions),
                    "description": latest.description,
                    "tags": latest.tags,
                    "invocation_count": sum(v.invocation_count for v in versions.values()),
                }
            )

        return results


# ============================================================================
# DEMO
# ============================================================================


async def demo_prompt_registry():
    """Demonstrate AMOS Prompt Registry capabilities."""
    print("\n" + "=" * 70)
    print("AMOS PROMPT REGISTRY - COMPONENT #73")
    print("=" * 70)

    registry = AMOSPromptRegistry()
    await registry.initialize()

    print("\n[1] Creating prompts with semantic versioning...")

    # Create customer support prompt
    support_prompt = registry.create_prompt(
        prompt_id="customer_support",
        template="""You are a helpful customer support agent for {company_name}.

Customer Issue: {issue_description}
Priority: {priority_level}

Provide a professional, empathetic response that addresses the customer's concern.
Offer specific solutions and next steps.""",
        system_prompt="You are an expert customer support agent. Be empathetic, professional, and solution-oriented.",
        variables=[
            PromptVariable("company_name", "Name of the company", "string", True),
            PromptVariable("issue_description", "Description of customer issue", "string", True),
            PromptVariable(
                "priority_level", "Priority (low/medium/high)", "string", True, "medium"
            ),
        ],
        description="Customer support response generator",
        created_by="support_team",
        tags=["customer_support", "external_facing"],
    )

    # Create code review prompt
    code_prompt = registry.create_prompt(
        prompt_id="code_review",
        template="""Review the following {language} code for:
1. Security issues
2. Performance optimizations
3. Best practices
4. Code clarity

Code:
```{language}
{code}
```

Provide specific, actionable feedback.""",
        system_prompt="You are a senior software engineer conducting code reviews.",
        variables=[
            PromptVariable("language", "Programming language", "string", True),
            PromptVariable("code", "Code to review", "string", True),
        ],
        description="Automated code review assistant",
        created_by="engineering_team",
        tags=["engineering", "code_quality"],
    )

    print("  ✓ Created: customer_support v1.0.0")
    print("  ✓ Created: code_review v1.0.0")

    print("\n[2] Creating new versions...")

    # Create improved version
    support_v2 = registry.create_version(
        prompt_id="customer_support",
        template="""You are a {company_name} support specialist with deep product knowledge.

Customer Issue: {issue_description}
Priority: {priority_level}
Customer Tier: {customer_tier}

Provide a personalized response that:
1. Acknowledges the specific concern
2. Explains the solution clearly
3. Offers proactive assistance
4. Includes relevant documentation links""",
        version_bump="minor",
        description="Enhanced customer support with tier-based personalization",
        changelog="Added customer tier personalization and proactive assistance",
    )

    print("  ✓ New version: customer_support v1.1.0")

    print("\n[3] Stage transitions...")

    registry.transition_stage(
        "customer_support", "1.1.0", PromptStage.REVIEW, approved_by="support_lead"
    )

    registry.transition_stage(
        "customer_support", "1.1.0", PromptStage.PRODUCTION, approved_by="product_manager"
    )

    print("\n[4] Deploying to environments...")

    # Deploy to staging
    registry.deploy("customer_support", "1.0.0", Environment.STAGING, traffic_percentage=100.0)

    # Deploy to production (gradual rollout)
    prod_deployment = registry.deploy(
        "customer_support",
        "1.1.0",
        Environment.PRODUCTION,
        traffic_percentage=25.0,  # Start with 25% traffic
    )

    print("  ✓ Staging: customer_support v1.0.0 (100%)")
    print("  ✓ Production: customer_support v1.1.0 (25% traffic - gradual rollout)")

    print("\n[5] Starting A/B test...")

    # Create variant for testing
    support_variant = registry.create_version(
        prompt_id="customer_support",
        template="""You are a {company_name} support specialist.

Issue: {issue_description}
Priority: {priority_level}

QUICK RESPONSE PROTOCOL:
1. Immediate acknowledgment
2. Direct solution (max 2 sentences)
3. Clear next steps
4. Offer to escalate if needed

Keep response under 100 words for speed.""",
        version_bump="minor",
        description="Concise support responses for faster resolution",
        changelog="Testing concise response format for faster resolution times",
    )

    ab_test = registry.start_ab_test(
        prompt_id="customer_support",
        name="Concise vs Detailed Response Test",
        control_version="1.1.0",
        variant_versions=["1.2.0"],
        control_traffic=50.0,
        variant_traffic=[50.0],
        primary_metric="quality_score",
    )

    print(f"  ✓ A/B test: '{ab_test.name}'")
    print("    Control (v1.1.0): 50% traffic")
    print("    Variant (v1.2.0): 50% traffic")

    print("\n[6] Simulating prompt executions...")

    # Simulate requests
    for i in range(10):
        request_id = f"req_{i:04d}"

        # Get prompt for request (handles A/B test assignment)
        prompt_version, deployment = registry.get_prompt_for_request(
            "customer_support",
            Environment.PRODUCTION,
            request_id=request_id,
            variables={
                "company_name": "TechCorp",
                "issue_description": f"Issue #{i}: Login problems",
                "priority_level": "high",
            },
        )

        if prompt_version:
            # Render prompt
            rendered = registry.render_prompt(
                prompt_version,
                {
                    "company_name": "TechCorp",
                    "issue_description": f"Issue #{i}: Login problems",
                    "priority_level": "high",
                    "customer_tier": "premium",
                },
            )

            # Simulate execution
            latency = 150 + (i * 10)  # Simulated latency
            cost = 0.002 + (i * 0.0001)

            execution = registry.record_execution(
                prompt_id="customer_support",
                version_id=prompt_version.version_id,
                rendered_prompt=rendered[:100] + "...",
                variables={"company_name": "TechCorp", "priority_level": "high"},
                response="Thank you for contacting TechCorp support...",
                tokens_input=50,
                tokens_output=150,
                latency_ms=latency,
                cost=cost,
                success=True,
                deployment_id=deployment.deployment_id if deployment else None,
                ab_test_id=ab_test.test_id,
                environment=Environment.PRODUCTION,
            )

            # Simulate user feedback
            if i % 3 == 0:
                registry.provide_feedback(execution.execution_id, 5.0)
            elif i % 3 == 1:
                registry.provide_feedback(execution.execution_id, 4.0)

    print("  ✓ Recorded 10 executions with A/B test variant assignment")
    print("  ✓ Added quality feedback (ratings 4-5 stars)")

    print("\n[7] Completing A/B test...")

    registry.complete_ab_test(
        test_id=ab_test.test_id,
        winner_version_id=support_v2.version_id,  # v1.1.0 wins
        improvement_percentage=15.3,
    )

    print("\n[8] Registry summary...")

    summary = registry.get_registry_summary()
    print(f"  Total prompts: {summary['total_prompts']}")
    print(f"  Total versions: {summary['total_versions']}")
    print(f"  Total executions: {summary['total_executions']}")
    print(f"  Active deployments: {summary['active_deployments']}")
    print(f"  Running A/B tests: {summary['running_ab_tests']}")
    print(f"  Total cost: ${summary['total_cost']}")
    print(f"  Avg latency: {summary['avg_latency_ms']}ms")
    print(f"  Success rate: {summary['success_rate']}%")

    print("\n[9] Listing prompts...")

    prompts = registry.list_prompts()
    for p in prompts:
        print(
            f"  • {p['prompt_id']}: v{p['latest_version']} [{p['stage']}] - {p['invocation_count']} invocations"
        )

    print("\n" + "=" * 70)
    print("PROMPT REGISTRY DEMO COMPLETE")
    print("=" * 70)
    print("\nKey Features Demonstrated:")
    print("  ✓ Semantic versioning (major.minor.patch)")
    print("  ✓ Stage transitions (Draft → Review → Production)")
    print("  ✓ Multi-environment deployment (Staging/Prod)")
    print("  ✓ Gradual rollout (25% traffic start)")
    print("  ✓ A/B testing with deterministic variant assignment")
    print("  ✓ Performance tracking (latency, cost, success rate)")
    print("  ✓ Quality feedback and scoring")
    print("  ✓ Template variable rendering")
    print("\nIntegration Points:")
    print("  • Feature Flags (#69) for gradual rollout")
    print("  • LLM Router (#72) for request routing")
    print("  • Model Registry (#70) for model-prompt binding")
    print("  • Telemetry Engine (#63) for metrics")


if __name__ == "__main__":
    asyncio.run(demo_prompt_registry())
