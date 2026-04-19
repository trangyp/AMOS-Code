"""
AXIOM ONE: MVP Backend Implementation
FastAPI + PostgreSQL + Neo4j + Redis
"""

import asyncio
import json
import os
import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

import asyncpg
import redis.asyncio as redis
from fastapi import Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field

# ============================================
# CONFIGURATION
# ============================================


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://localhost/axiom_one")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "password")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-secret")
    API_VERSION: str = "v1"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")


settings = Settings()

# ============================================
# DATABASE CONNECTION
# ============================================


class Database:
    def __init__(self):
        self.pool: asyncpg.Pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(settings.DATABASE_URL, min_size=5, max_size=20)

    async def disconnect(self):
        if self.pool:
            await self.pool.close()

    async def fetch_one(self, query: str, *args) -> Dict[str, Any]:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, *args)
            return dict(row) if row else None

    async def fetch_many(self, query: str, *args) -> list[dict[str, Any]]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(row) for row in rows]

    async def execute(self, query: str, *args) -> str:
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)


db = Database()

# ============================================
# REDIS CACHE
# ============================================


class Cache:
    def __init__(self):
        self.client: redis.Redis = None

    async def connect(self):
        self.client = redis.from_url(settings.REDIS_URL)

    async def disconnect(self):
        if self.client:
            await self.client.close()

    async def get(self, key: str) -> str:
        return await self.client.get(key)

    async def set(self, key: str, value: str, ttl: int = 300):
        await self.client.set(key, value, ex=ttl)

    async def delete(self, key: str):
        await self.client.delete(key)

    async def publish(self, channel: str, message: str):
        await self.client.publish(channel, message)


cache = Cache()

# ============================================
# PYDANTIC MODELS
# ============================================


class UUIDModel(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    modified_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Tenant(UUIDModel):
    name: str
    slug: str
    plan: str = "free"
    settings: dict = Field(default_factory=dict)


class Person(UUIDModel):
    tenant_id: uuid.UUID
    email: str
    name: str
    avatar_url: str = None
    timezone: str = "UTC"
    theme: str = "system"


class Team(UUIDModel):
    tenant_id: uuid.UUID
    name: str
    slug: str
    description: str = None
    cost_center: str = None


class Repository(UUIDModel):
    tenant_id: uuid.UUID
    team_id: uuid.UUID = None
    name: str
    full_name: str
    url: str
    provider: str
    provider_id: str = None
    default_branch: str = "main"
    language: str = None
    languages: dict = Field(default_factory=dict)
    health_score: float = None
    last_activity_at: datetime = None
    open_issues: int = 0
    open_prs: int = 0


class Symbol(UUIDModel):
    tenant_id: uuid.UUID
    repository_id: uuid.UUID
    file_id: uuid.UUID
    name: str
    symbol_type: str
    fully_qualified_name: str
    line_start: int
    line_end: int
    column_start: int = None
    column_end: int = None
    signature: str = None
    docstring: str = None


class Service(UUIDModel):
    tenant_id: uuid.UUID
    team_id: uuid.UUID
    repository_id: uuid.UUID = None
    name: str
    slug: str
    description: str = None
    service_type: str
    current_availability: float = None
    current_latency_p99: int = None
    monthly_cost_cents: int = None


class Endpoint(UUIDModel):
    tenant_id: uuid.UUID
    service_id: uuid.UUID
    symbol_id: uuid.UUID = None
    path: str
    method: str
    request_schema: dict = None
    response_schema: dict = None
    request_rate: float = None
    error_rate: float = None
    latency_p50: int = None
    latency_p99: int = None


class Environment(UUIDModel):
    tenant_id: uuid.UUID
    name: str
    slug: str
    environment_type: str
    region: str
    status: str = "healthy"
    health_score: float = None
    require_approval: bool = True


class Deployment(UUIDModel):
    tenant_id: uuid.UUID
    service_id: uuid.UUID
    environment_id: uuid.UUID
    commit_sha: str
    image: str = None
    image_digest: str = None
    deployed_by_id: uuid.UUID
    deployed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    status: str = "pending"
    replicas: int = 0
    healthy_replicas: int = 0
    hourly_cost_cents: int = None


class Incident(UUIDModel):
    tenant_id: uuid.UUID
    title: str
    description: str = None
    severity: str
    status: str = "open"
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    detected_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    mitigated_at: datetime = None
    resolved_at: datetime = None
    detected_by_id: uuid.UUID = None
    commander_id: uuid.UUID = None
    root_cause: str = None
    affected_customers: int = None
    estimated_revenue_impact_cents: int = None


class Alert(UUIDModel):
    tenant_id: uuid.UUID
    service_id: uuid.UUID = None
    title: str
    description: str = None
    severity: str
    status: str = "firing"
    first_fired_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_fired_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    resolved_at: datetime = None
    acknowledged_by_id: uuid.UUID = None


class Agent(UUIDModel):
    tenant_id: uuid.UUID
    name: str
    role: str
    description: str = None
    permitted_tools: List[str] = Field(default_factory=list)
    forbidden_paths: List[str] = Field(default_factory=list)
    budget_tokens_per_day: int = None
    approval_threshold: str = "risky"
    status: str = "idle"
    execution_count: int = 0
    success_rate: float = None
    last_execution_at: datetime = None


class AgentExecution(UUIDModel):
    tenant_id: uuid.UUID
    agent_id: uuid.UUID
    triggered_by_id: uuid.UUID
    goal: str
    observation: str = None
    plan: dict = None
    steps_executed: List[dict] = None
    status: str = "observing"
    result: dict = None
    evidence_hash: str = None
    rollback_available: bool = False
    tokens_used: int = 0
    cost_cents: int = None
    duration_ms: int = None


class RepoAutopsyJob(UUIDModel):
    tenant_id: uuid.UUID
    repository_id: uuid.UUID
    status: str = "pending"
    started_at: datetime = None
    completed_at: datetime = None
    total_issues: int = 0
    fixable_issues: int = 0
    report: dict = None


# ============================================
# REQUEST/RESPONSE MODELS
# ============================================


class CreateTenantRequest(BaseModel):
    name: str
    slug: str


class CreatePersonRequest(BaseModel):
    email: str
    name: str
    avatar_url: str = None


class ImportRepositoryRequest(BaseModel):
    url: str
    provider: str = "github"
    team_id: uuid.UUID = None


class CreateServiceRequest(BaseModel):
    name: str
    slug: str
    description: str = None
    service_type: str
    team_id: uuid.UUID
    repository_id: uuid.UUID = None


class CreateEnvironmentRequest(BaseModel):
    name: str
    slug: str
    environment_type: str
    region: str


class DeployRequest(BaseModel):
    service_id: uuid.UUID
    environment_id: uuid.UUID
    commit_sha: str
    image: str = None


class CreateIncidentRequest(BaseModel):
    title: str
    description: str = None
    severity: str
    affected_service_ids: list[uuid.UUID] = Field(default_factory=list)


class TriggerAgentRequest(BaseModel):
    agent_id: uuid.UUID
    goal: str
    context: dict = Field(default_factory=dict)


class RepoAutopsyRequest(BaseModel):
    repository_id: uuid.UUID


class CommandRequest(BaseModel):
    command: str
    args: dict = Field(default_factory=dict)


# ============================================
# REPOSITORY LAYER
# ============================================


class Repository:
    """Data access layer"""

    @staticmethod
    async def create_tenant(data: CreateTenantRequest) -> Dict[str, Any]:
        query = """
            INSERT INTO tenants (name, slug, plan, settings)
            VALUES ($1, $2, $3, $4)
            RETURNING *
        """
        return await db.fetch_one(query, data.name, data.slug, "free", "{}")

    @staticmethod
    async def get_tenant(id: uuid.UUID) -> Dict[str, Any]:
        return await db.fetch_one("SELECT * FROM tenants WHERE id = $1", id)

    @staticmethod
    async def create_person(tenant_id: uuid.UUID, data: CreatePersonRequest) -> Dict[str, Any]:
        query = """
            INSERT INTO people (tenant_id, email, name, avatar_url, timezone, theme)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING *
        """
        return await db.fetch_one(
            query, tenant_id, data.email, data.name, data.avatar_url, "UTC", "system"
        )

    @staticmethod
    async def get_person(id: uuid.UUID) -> Dict[str, Any]:
        return await db.fetch_one("SELECT * FROM people WHERE id = $1", id)

    @staticmethod
    async def list_people(
        tenant_id: uuid.UUID, limit: int = 20, offset: int = 0
    ) -> list[dict[str, Any]]:
        return await db.fetch_many(
            "SELECT * FROM people WHERE tenant_id = $1 ORDER BY created_at DESC LIMIT $2 OFFSET $3",
            tenant_id,
            limit,
            offset,
        )

    @staticmethod
    async def create_repository(
        tenant_id: uuid.UUID, data: ImportRepositoryRequest
    ) -> Dict[str, Any]:
        # Extract name from URL
        name = data.url.split("/")[-1].replace(".git", "")
        full_name = data.url.split("github.com/")[-1].replace(".git", "")

        query = """
            INSERT INTO repositories
                (tenant_id, team_id, name, full_name, url, provider, default_branch, open_issues, open_prs)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING *
        """
        return await db.fetch_one(
            query, tenant_id, data.team_id, name, full_name, data.url, data.provider, "main", 0, 0
        )

    @staticmethod
    async def get_repository(id: uuid.UUID) -> Dict[str, Any]:
        return await db.fetch_one("SELECT * FROM repositories WHERE id = $1", id)

    @staticmethod
    async def list_repositories(
        tenant_id: uuid.UUID, limit: int = 20, offset: int = 0
    ) -> list[dict[str, Any]]:
        return await db.fetch_many(
            "SELECT * FROM repositories WHERE tenant_id = $1 ORDER BY created_at DESC LIMIT $2 OFFSET $3",
            tenant_id,
            limit,
            offset,
        )

    @staticmethod
    async def create_service(tenant_id: uuid.UUID, data: CreateServiceRequest) -> Dict[str, Any]:
        query = """
            INSERT INTO services
                (tenant_id, team_id, repository_id, name, slug, description, service_type, open_issues, open_prs)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING *
        """
        return await db.fetch_one(
            query,
            tenant_id,
            data.team_id,
            data.repository_id,
            data.name,
            data.slug,
            data.description,
            data.service_type,
            0,
            0,
        )

    @staticmethod
    async def get_service(id: uuid.UUID) -> Dict[str, Any]:
        return await db.fetch_one("SELECT * FROM services WHERE id = $1", id)

    @staticmethod
    async def list_services(
        tenant_id: uuid.UUID, limit: int = 20, offset: int = 0
    ) -> list[dict[str, Any]]:
        return await db.fetch_many(
            "SELECT * FROM services WHERE tenant_id = $1 ORDER BY created_at DESC LIMIT $2 OFFSET $3",
            tenant_id,
            limit,
            offset,
        )

    @staticmethod
    async def create_environment(
        tenant_id: uuid.UUID, data: CreateEnvironmentRequest
    ) -> Dict[str, Any]:
        query = """
            INSERT INTO environments
                (tenant_id, name, slug, environment_type, region, status, require_approval)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING *
        """
        return await db.fetch_one(
            query,
            tenant_id,
            data.name,
            data.slug,
            data.environment_type,
            data.region,
            "healthy",
            True,
        )

    @staticmethod
    async def get_environment(id: uuid.UUID) -> Dict[str, Any]:
        return await db.fetch_one("SELECT * FROM environments WHERE id = $1", id)

    @staticmethod
    async def create_deployment(
        tenant_id: uuid.UUID, deployed_by_id: uuid.UUID, data: DeployRequest
    ) -> Dict[str, Any]:
        query = """
            INSERT INTO deployments
                (tenant_id, service_id, environment_id, commit_sha, image, deployed_by_id,
                 deployed_at, status, replicas, healthy_replicas)
            VALUES ($1, $2, $3, $4, $5, $6, NOW(), $7, $8, $9)
            RETURNING *
        """
        return await db.fetch_one(
            query,
            tenant_id,
            data.service_id,
            data.environment_id,
            data.commit_sha,
            data.image,
            deployed_by_id,
            "pending",
            0,
            0,
        )

    @staticmethod
    async def get_deployment(id: uuid.UUID) -> Dict[str, Any]:
        return await db.fetch_one("SELECT * FROM deployments WHERE id = $1", id)

    @staticmethod
    async def create_incident(tenant_id: uuid.UUID, data: CreateIncidentRequest) -> Dict[str, Any]:
        query = """
            INSERT INTO incidents
                (tenant_id, title, description, severity, status, started_at, detected_at,
                 affected_customers)
            VALUES ($1, $2, $3, $4, $5, NOW(), NOW(), $6)
            RETURNING *
        """
        incident = await db.fetch_one(
            query, tenant_id, data.title, data.description, data.severity, "open", 0
        )

        # Link services
        for service_id in data.affected_service_ids:
            await db.execute(
                "INSERT INTO incident_services (incident_id, service_id) VALUES ($1, $2)",
                incident["id"],
                service_id,
            )

        return incident

    @staticmethod
    async def get_incident(id: uuid.UUID) -> Dict[str, Any]:
        incident = await db.fetch_one("SELECT * FROM incidents WHERE id = $1", id)
        if incident:
            services = await db.fetch_many(
                """
                    SELECT s.* FROM services s
                    JOIN incident_services ins ON s.id = ins.service_id
                    WHERE ins.incident_id = $1
                """,
                id,
            )
            incident["affected_services"] = services
        return incident

    @staticmethod
    async def list_incidents(
        tenant_id: uuid.UUID, limit: int = 20, offset: int = 0
    ) -> list[dict[str, Any]]:
        return await db.fetch_many(
            "SELECT * FROM incidents WHERE tenant_id = $1 ORDER BY started_at DESC LIMIT $2 OFFSET $3",
            tenant_id,
            limit,
            offset,
        )

    @staticmethod
    async def list_alerts(
        tenant_id: uuid.UUID, limit: int = 20, offset: int = 0
    ) -> list[dict[str, Any]]:
        return await db.fetch_many(
            "SELECT * FROM alerts WHERE tenant_id = $1 ORDER BY first_fired_at DESC LIMIT $2 OFFSET $3",
            tenant_id,
            limit,
            offset,
        )

    @staticmethod
    async def create_agent(tenant_id: uuid.UUID, data: Dict[str, Any]) -> Dict[str, Any]:
        query = """
            INSERT INTO agents
                (tenant_id, name, role, description, permitted_tools, forbidden_paths,
                 budget_tokens_per_day, approval_threshold, status, execution_count)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            RETURNING *
        """
        return await db.fetch_one(
            query,
            tenant_id,
            data["name"],
            data["role"],
            data.get("description"),
            json.dumps(data.get("permitted_tools", [])),
            json.dumps(data.get("forbidden_paths", [])),
            data.get("budget_tokens_per_day"),
            data.get("approval_threshold", "risky"),
            "idle",
            0,
        )

    @staticmethod
    async def get_agent(id: uuid.UUID) -> Dict[str, Any]:
        return await db.fetch_one("SELECT * FROM agents WHERE id = $1", id)

    @staticmethod
    async def list_agents(
        tenant_id: uuid.UUID, limit: int = 20, offset: int = 0
    ) -> list[dict[str, Any]]:
        return await db.fetch_many(
            "SELECT * FROM agents WHERE tenant_id = $1 ORDER BY created_at DESC LIMIT $2 OFFSET $3",
            tenant_id,
            limit,
            offset,
        )

    @staticmethod
    async def create_agent_execution(
        tenant_id: uuid.UUID, data: TriggerAgentRequest, triggered_by_id: uuid.UUID
    ) -> Dict[str, Any]:
        query = """
            INSERT INTO agent_executions
                (tenant_id, agent_id, triggered_by_id, goal, status, tokens_used, rollback_available)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING *
        """
        return await db.fetch_one(
            query, tenant_id, data.agent_id, triggered_by_id, data.goal, "observing", 0, False
        )

    @staticmethod
    async def get_agent_execution(id: uuid.UUID) -> Dict[str, Any]:
        return await db.fetch_one("SELECT * FROM agent_executions WHERE id = $1", id)

    @staticmethod
    async def create_repo_autopsy_job(
        tenant_id: uuid.UUID, repository_id: uuid.UUID
    ) -> Dict[str, Any]:
        query = """
            INSERT INTO repo_autopsy_jobs (tenant_id, repository_id, status, total_issues, fixable_issues)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING *
        """
        return await db.fetch_one(query, tenant_id, repository_id, "pending", 0, 0)

    @staticmethod
    async def get_repo_autopsy_job(id: uuid.UUID) -> Dict[str, Any]:
        return await db.fetch_one("SELECT * FROM repo_autopsy_jobs WHERE id = $1", id)

    @staticmethod
    async def update_repo_autopsy_job(id: uuid.UUID, updates: Dict[str, Any]) -> Dict[str, Any]:
        # Build dynamic update query
        fields = []
        values = []
        for key, value in updates.items():
            fields.append(f"{key} = ${len(values) + 1}")
            values.append(value)
        values.append(id)

        query = f"""
            UPDATE repo_autopsy_jobs
            SET {', '.join(fields)}, modified_at = NOW()
            WHERE id = ${len(values)}
            RETURNING *
        """
        return await db.fetch_one(query, *values)


repo = Repository()

# ============================================
# BUSINESS LOGIC LAYER
# ============================================


class RepoAutopsyEngine:
    """Static analysis engine for repo debugging"""

    @staticmethod
    async def analyze_repository(repository_id: uuid.UUID, tenant_id: uuid.UUID) -> Dict[str, Any]:
        """Run full repo autopsy analysis"""
        # Get repository
        repo_data = await repo.get_repository(repository_id)
        if not repo_data:
            raise HTTPException(status_code=404, detail="Repository not found")

        # Create job
        job = await repo.create_repo_autopsy_job(tenant_id, repository_id)

        # Start analysis (async)
        asyncio.create_task(RepoAutopsyEngine._run_analysis(job["id"], repo_data))

        return job

    @staticmethod
    async def _run_analysis(job_id: uuid.UUID, repo_data: Dict[str, Any]):
        """Background analysis task"""
        try:
            # Update status to running
            await repo.update_repo_autopsy_job(
                job_id, {"status": "running", "started_at": datetime.now(UTC)}
            )

            issues = []

            # Clone and analyze (simplified)
            # In production, this would:
            # 1. Clone repo to temp location
            # 2. Run tree-sitter parsing
            # 3. Check packaging configs
            # 4. Validate imports
            # 5. Check for common issues

            # Simulate findings for MVP
            issues.extend(
                [
                    {
                        "id": str(uuid.uuid4()),
                        "severity": "medium",
                        "category": "packaging",
                        "title": "Missing __init__.py in utils/",
                        "description": "Package directory lacks __init__.py file",
                        "file_path": "utils/",
                        "line_number": None,
                        "fix_available": True,
                        "fix_diff": "+ touch utils/__init__.py",
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "severity": "high",
                        "category": "imports",
                        "title": "Unresolved import: old_module",
                        "description": "Import references non-existent module",
                        "file_path": "src/main.py",
                        "line_number": 42,
                        "fix_available": False,
                    },
                ]
            )

            # Update job with results
            report = {
                "repository": repo_data["full_name"],
                "issues_found": len(issues),
                "by_severity": {
                    "critical": len([i for i in issues if i["severity"] == "critical"]),
                    "high": len([i for i in issues if i["severity"] == "high"]),
                    "medium": len([i for i in issues if i["severity"] == "medium"]),
                    "low": len([i for i in issues if i["severity"] == "low"]),
                },
                "by_category": {},
                "issues": issues,
            }

            fixable = len([i for i in issues if i.get("fix_available")])

            await repo.update_repo_autopsy_job(
                job_id,
                {
                    "status": "completed",
                    "completed_at": datetime.now(UTC),
                    "total_issues": len(issues),
                    "fixable_issues": fixable,
                    "report": json.dumps(report),
                },
            )

            # Cache results
            await cache.set(f"autopsy:{job_id}", json.dumps(report), ttl=3600)

        except Exception as e:
            await repo.update_repo_autopsy_job(
                job_id,
                {
                    "status": "failed",
                    "completed_at": datetime.now(UTC),
                    "report": json.dumps({"error": str(e)}),
                },
            )


class AgentRuntime:
    """AI agent execution runtime"""

    @staticmethod
    async def trigger_agent(
        agent_id: uuid.UUID,
        goal: str,
        context: dict,
        triggered_by_id: uuid.UUID,
        tenant_id: uuid.UUID,
    ) -> Dict[str, Any]:
        """Trigger an AI agent to perform work"""
        # Get agent
        agent_data = await repo.get_agent(agent_id)
        if not agent_data:
            raise HTTPException(status_code=404, detail="Agent not found")

        # Create execution
        execution = await repo.create_agent_execution(
            tenant_id,
            TriggerAgentRequest(agent_id=agent_id, goal=goal, context=context),
            triggered_by_id,
        )

        # Start execution (async)
        asyncio.create_task(AgentRuntime._run_execution(execution["id"], agent_data, goal, context))

        return execution

    @staticmethod
    async def _run_execution(execution_id: uuid.UUID, agent_data: dict, goal: str, context: dict):
        """Background agent execution"""
        try:
            # Update status
            await db.execute(
                "UPDATE agent_executions SET status = $1, modified_at = NOW() WHERE id = $2",
                "observing",
                execution_id,
            )

            # Simulate observation phase
            await asyncio.sleep(1)

            # Planning phase
            await db.execute(
                "UPDATE agent_executions SET status = $1, plan = $2, modified_at = NOW() WHERE id = $3",
                "planning",
                json.dumps({"steps": ["Analyze goal", "Gather context", "Generate solution"]}),
                execution_id,
            )

            await asyncio.sleep(1)

            # Execution phase
            await db.execute(
                """UPDATE agent_executions
                    SET status = $1,
                        steps_executed = $2,
                        result = $3,
                        tokens_used = $4,
                        duration_ms = $5,
                        modified_at = NOW()
                    WHERE id = $6""",
                "completed",
                json.dumps([{"step": 1, "action": "Analyzed", "status": "success"}]),
                json.dumps({"output": f"Completed: {goal}"}),
                150,  # simulated tokens
                2500,  # simulated ms
                execution_id,
            )

            # Update agent stats
            await db.execute(
                """UPDATE agents
                    SET execution_count = execution_count + 1,
                        last_execution_at = NOW(),
                        modified_at = NOW()
                    WHERE id = $1""",
                agent_data["id"],
            )

        except Exception as e:
            await db.execute(
                """UPDATE agent_executions
                    SET status = $1,
                        result = $2,
                        modified_at = NOW()
                    WHERE id = $3""",
                "failed",
                json.dumps({"error": str(e)}),
                execution_id,
            )


class CommandProcessor:
    """Universal command processor"""

    @staticmethod
    async def execute_command(
        command: str, args: dict, tenant_id: uuid.UUID, user_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Execute a universal command"""

        handlers = {
            "inspect": CommandProcessor._handle_inspect,
            "run": CommandProcessor._handle_run,
            "explain": CommandProcessor._handle_explain,
            "patch": CommandProcessor._handle_patch,
        }

        handler = handlers.get(command)
        if not handler:
            return {"error": f"Unknown command: {command}"}

        return await handler(args, tenant_id, user_id)

    @staticmethod
    async def _handle_inspect(
        args: dict, tenant_id: uuid.UUID, user_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Handle /inspect command"""
        object_type = args.get("type")
        object_id = args.get("id")

        # Route to appropriate query
        if object_type == "repository":
            data = await repo.get_repository(uuid.UUID(object_id))
        elif object_type == "service":
            data = await repo.get_service(uuid.UUID(object_id))
        elif object_type == "incident":
            data = await repo.get_incident(uuid.UUID(object_id))
        else:
            return {"error": f"Unknown object type: {object_type}"}

        if not data:
            return {"error": "Object not found"}

        return {
            "command": "inspect",
            "object": data,
            "related": await CommandProcessor._get_related_objects(
                object_type, object_id, tenant_id
            ),
        }

    @staticmethod
    async def _handle_run(args: dict, tenant_id: uuid.UUID, user_id: uuid.UUID) -> Dict[str, Any]:
        """Handle /run command"""
        test_type = args.get("type")
        target = args.get("target")

        # Trigger test execution
        return {
            "command": "run",
            "status": "started",
            "test_type": test_type,
            "target": target,
            "execution_id": str(uuid.uuid4()),
        }

    @staticmethod
    async def _handle_explain(
        args: dict, tenant_id: uuid.UUID, user_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Handle /explain command"""
        target = args.get("target")

        # Generate explanation (would use LLM in production)
        return {
            "command": "explain",
            "target": target,
            "explanation": f"Explanation for {target} would be generated here using the canonical object graph.",
        }

    @staticmethod
    async def _handle_patch(args: dict, tenant_id: uuid.UUID, user_id: uuid.UUID) -> Dict[str, Any]:
        """Handle /patch command"""
        issue_id = args.get("issue_id")

        return {
            "command": "patch",
            "issue_id": issue_id,
            "status": "patch would be generated and applied",
            "requires_approval": True,
        }

    @staticmethod
    async def _get_related_objects(
        object_type: str, object_id: str, tenant_id: uuid.UUID
    ) -> dict[str, list]:
        """Get related objects from graph"""
        # Simplified - would query Neo4j in production
        return {"depends_on": [], "depended_by": [], "owned_by": [], "monitored_by": []}


# ============================================
# FASTAPI APP
# ============================================

security = HTTPBearer()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup
    await db.connect()
    await cache.connect()
    yield
    # Shutdown
    await db.disconnect()
    await cache.disconnect()


app = FastAPI(
    title="AXIOM ONE API",
    description="Unified Technical Operating System",
    version="1.0.0-mvp",
    lifespan=lifespan,
)

# Middleware
app.add_middleware(GZipMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.ENVIRONMENT == "development" else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# DEPENDENCIES
# ============================================


async def get_current_user(request: Request) -> Dict[str, Any]:
    """Extract current user from JWT (simplified for MVP)"""
    # In production: validate JWT, extract claims
    auth_header = request.headers.get("authorization")
    if not auth_header:
        return {"id": uuid.uuid4(), "tenant_id": uuid.uuid4(), "email": "demo@axiom.one"}

    # Parse Bearer token
    try:
        token = auth_header.replace("Bearer ", "")
        # Validate JWT here
        # For MVP, return demo user
        return {"id": uuid.uuid4(), "tenant_id": uuid.uuid4(), "email": "demo@axiom.one"}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication"
        )


async def get_tenant(user: dict = Depends(get_current_user)) -> uuid.UUID:
    """Get current tenant ID from user"""
    return user.get("tenant_id", uuid.uuid4())


# ============================================
# HEALTH ENDPOINTS
# ============================================


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0-mvp", "timestamp": datetime.now(UTC).isoformat()}


@app.get("/ready")
async def readiness_check():
    """Readiness check"""
    try:
        # Check database
        await db.fetch_one("SELECT 1")
        # Check cache
        await cache.get("health-check")
        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


# ============================================
# IDENTITY ENDPOINTS
# ============================================


@app.post("/api/v1/tenants", response_model=dict)
async def create_tenant(data: CreateTenantRequest):
    """Create a new tenant"""
    result = await repo.create_tenant(data)
    return result


@app.get("/api/v1/tenants/{tenant_id}")
async def get_tenant(tenant_id: uuid.UUID):
    """Get tenant by ID"""
    result = await repo.get_tenant(tenant_id)
    if not result:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return result


@app.post("/api/v1/people")
async def create_person(data: CreatePersonRequest, tenant_id: uuid.UUID = Depends(get_tenant)):
    """Create a new person"""
    result = await repo.create_person(tenant_id, data)
    return result


@app.get("/api/v1/people")
async def list_people(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    tenant_id: uuid.UUID = Depends(get_tenant),
):
    """List people in tenant"""
    results = await repo.list_people(tenant_id, limit, offset)
    return {"data": results, "count": len(results)}


# ============================================
# CODE ENDPOINTS
# ============================================


@app.post("/api/v1/repositories")
async def import_repository(
    data: ImportRepositoryRequest, tenant_id: uuid.UUID = Depends(get_tenant)
):
    """Import a repository"""
    result = await repo.create_repository(tenant_id, data)
    return result


@app.get("/api/v1/repositories")
async def list_repositories(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    tenant_id: uuid.UUID = Depends(get_tenant),
):
    """List repositories"""
    results = await repo.list_repositories(tenant_id, limit, offset)
    return {"data": results, "count": len(results)}


@app.get("/api/v1/repositories/{repo_id}")
async def get_repository(repo_id: uuid.UUID):
    """Get repository details"""
    result = await repo.get_repository(repo_id)
    if not result:
        raise HTTPException(status_code=404, detail="Repository not found")
    return result


# ============================================
# SERVICE ENDPOINTS
# ============================================


@app.post("/api/v1/services")
async def create_service(data: CreateServiceRequest, tenant_id: uuid.UUID = Depends(get_tenant)):
    """Create a new service"""
    result = await repo.create_service(tenant_id, data)
    return result


@app.get("/api/v1/services")
async def list_services(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    tenant_id: uuid.UUID = Depends(get_tenant),
):
    """List services"""
    results = await repo.list_services(tenant_id, limit, offset)
    return {"data": results, "count": len(results)}


@app.get("/api/v1/services/{service_id}")
async def get_service(service_id: uuid.UUID):
    """Get service details"""
    result = await repo.get_service(service_id)
    if not result:
        raise HTTPException(status_code=404, detail="Service not found")
    return result


# ============================================
# RUNTIME ENDPOINTS
# ============================================


@app.post("/api/v1/environments")
async def create_environment(
    data: CreateEnvironmentRequest, tenant_id: uuid.UUID = Depends(get_tenant)
):
    """Create a new environment"""
    result = await repo.create_environment(tenant_id, data)
    return result


@app.get("/api/v1/environments/{env_id}")
async def get_environment(env_id: uuid.UUID):
    """Get environment details"""
    result = await repo.get_environment(env_id)
    if not result:
        raise HTTPException(status_code=404, detail="Environment not found")
    return result


@app.post("/api/v1/deployments")
async def create_deployment(
    data: DeployRequest,
    user: dict = Depends(get_current_user),
    tenant_id: uuid.UUID = Depends(get_tenant),
):
    """Create a new deployment"""
    result = await repo.create_deployment(tenant_id, user["id"], data)
    return result


@app.get("/api/v1/deployments/{deployment_id}")
async def get_deployment(deployment_id: uuid.UUID):
    """Get deployment details"""
    result = await repo.get_deployment(deployment_id)
    if not result:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return result


# ============================================
# OPERATIONS ENDPOINTS
# ============================================


@app.post("/api/v1/incidents")
async def create_incident(data: CreateIncidentRequest, tenant_id: uuid.UUID = Depends(get_tenant)):
    """Create a new incident"""
    result = await repo.create_incident(tenant_id, data)
    return result


@app.get("/api/v1/incidents")
async def list_incidents(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    tenant_id: uuid.UUID = Depends(get_tenant),
):
    """List incidents"""
    results = await repo.list_incidents(tenant_id, limit, offset)
    return {"data": results, "count": len(results)}


@app.get("/api/v1/incidents/{incident_id}")
async def get_incident(incident_id: uuid.UUID):
    """Get incident details"""
    result = await repo.get_incident(incident_id)
    if not result:
        raise HTTPException(status_code=404, detail="Incident not found")
    return result


@app.get("/api/v1/alerts")
async def list_alerts(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    tenant_id: uuid.UUID = Depends(get_tenant),
):
    """List alerts"""
    results = await repo.list_alerts(tenant_id, limit, offset)
    return {"data": results, "count": len(results)}


# ============================================
# AI AGENT ENDPOINTS
# ============================================


@app.post("/api/v1/agents")
async def create_agent(data: dict, tenant_id: uuid.UUID = Depends(get_tenant)):
    """Create a new AI agent"""
    result = await repo.create_agent(tenant_id, data)
    return result


@app.get("/api/v1/agents")
async def list_agents(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    tenant_id: uuid.UUID = Depends(get_tenant),
):
    """List agents"""
    results = await repo.list_agents(tenant_id, limit, offset)
    return {"data": results, "count": len(results)}


@app.get("/api/v1/agents/{agent_id}")
async def get_agent(agent_id: uuid.UUID):
    """Get agent details"""
    result = await repo.get_agent(agent_id)
    if not result:
        raise HTTPException(status_code=404, detail="Agent not found")
    return result


@app.post("/api/v1/agent-executions")
async def trigger_agent(
    data: TriggerAgentRequest,
    user: dict = Depends(get_current_user),
    tenant_id: uuid.UUID = Depends(get_tenant),
):
    """Trigger an AI agent"""
    result = await AgentRuntime.trigger_agent(
        data.agent_id, data.goal, data.context, user["id"], tenant_id
    )
    return result


@app.get("/api/v1/agent-executions/{execution_id}")
async def get_agent_execution(execution_id: uuid.UUID):
    """Get agent execution status"""
    result = await repo.get_agent_execution(execution_id)
    if not result:
        raise HTTPException(status_code=404, detail="Execution not found")
    return result


# ============================================
# REPO AUTOPSY ENDPOINTS
# ============================================


@app.post("/api/v1/repo-autopsy")
async def run_repo_autopsy(data: RepoAutopsyRequest, tenant_id: uuid.UUID = Depends(get_tenant)):
    """Start a repo autopsy analysis"""
    result = await RepoAutopsyEngine.analyze_repository(data.repository_id, tenant_id)
    return result


@app.get("/api/v1/repo-autopsy/{job_id}")
async def get_repo_autopsy_status(job_id: uuid.UUID):
    """Get repo autopsy job status"""
    result = await repo.get_repo_autopsy_job(job_id)
    if not result:
        raise HTTPException(status_code=404, detail="Job not found")
    return result


@app.post("/api/v1/repo-autopsy/{job_id}/apply-fix")
async def apply_autofix(job_id: uuid.UUID, issue_id: str):
    """Apply an autofix from autopsy"""
    return {
        "job_id": job_id,
        "issue_id": issue_id,
        "status": "fix_applied",
        "pr_url": f"https://github.com/axiom-one/demo/pull/{uuid.uuid4().hex[:8]}",
    }


# ============================================
# COMMAND ENDPOINTS
# ============================================


@app.post("/api/v1/commands/execute")
async def execute_command(
    data: CommandRequest,
    user: dict = Depends(get_current_user),
    tenant_id: uuid.UUID = Depends(get_tenant),
):
    """Execute a universal command"""
    result = await CommandProcessor.execute_command(data.command, data.args, tenant_id, user["id"])
    return result


@app.get("/api/v1/commands")
async def list_commands():
    """List available commands"""
    return {
        "commands": [
            {
                "name": "inspect",
                "description": "Inspect any object in the system",
                "args": ["type", "id"],
                "example": "/inspect repository abc-123",
            },
            {
                "name": "run",
                "description": "Run tests or benchmarks",
                "args": ["type", "target"],
                "example": "/run tests payment-service",
            },
            {
                "name": "explain",
                "description": "Get AI explanation of any object",
                "args": ["target"],
                "example": "/explain service:payment-gateway",
            },
            {
                "name": "patch",
                "description": "Generate and apply patches",
                "args": ["issue_id"],
                "example": "/patch issue-123",
            },
        ]
    }


# ============================================
# SEARCH ENDPOINTS
# ============================================


@app.get("/api/v1/search")
async def search(
    q: str = Query(..., min_length=1),
    type: str = None,
    limit: int = Query(20, ge=1, le=100),
    tenant_id: uuid.UUID = Depends(get_tenant),
):
    """Universal search across all objects"""
    # Simplified - would use Elasticsearch in production
    results = []

    # Search repositories
    repos = await db.fetch_many(
        "SELECT * FROM repositories WHERE tenant_id = $1 AND (name ILIKE $2 OR full_name ILIKE $2) LIMIT $3",
        tenant_id,
        f"%{q}%",
        limit,
    )
    results.extend([{**r, "_type": "repository"} for r in repos])

    # Search services
    services = await db.fetch_many(
        "SELECT * FROM services WHERE tenant_id = $1 AND (name ILIKE $2 OR slug ILIKE $2) LIMIT $3",
        tenant_id,
        f"%{q}%",
        limit,
    )
    results.extend([{**s, "_type": "service"} for s in services])

    return {"query": q, "results": results[:limit], "total": len(results)}


# ============================================
# ERROR HANDLERS
# ============================================


@app.exception_handler(asyncpg.PostgresError)
async def database_error_handler(request: Request, exc: asyncpg.PostgresError):
    return JSONResponse(status_code=500, content={"error": "Database error", "detail": str(exc)})


@app.exception_handler(Exception)
async def general_error_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"error": "Internal error", "detail": str(exc)})


# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "AXIOM_ONE_MVP_BACKEND:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_level="info",
    )
