"""
Axiom One - Unified Graph Schema

The canonical model of reality for the Axiom One platform.
Extends the repository graph to include runtime, business, and governance objects.

Core Objects:
- Human: user, team, org, workspace, role
- Planning: mission, product, initiative, epic, issue, task
- Code: repo, branch, commit, PR, package, module, symbol
- Runtime: service, container, deployment, endpoint, job
- Data: database, schema, table, stream, cache, index
- AI: model, prompt, tool, agent, memory, trace
- Business: customer, tenant, subscription, revenue
- Governance: policy, audit, risk, compliance, approval

G_axiom = (V, E, Φ, Τ, Λ)
Where:
    V: vertices (50+ node types across 8 domains)
    E: edges (30+ relationship types)
    Φ: properties (domain-specific attributes)
    Τ: temporal versioning (time-indexed graph state)
    Λ: lineage (data provenance tracking)
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, Optional

import neo4j
from neo4j import AsyncGraphDatabase

# =============================================================================
# NODE TYPES - 8 Domains, 50+ Object Types
# =============================================================================


class DomainType(Enum):
    """The 8 domains of the Axiom One unified graph."""

    HUMAN = auto()  # Identity and organization
    PLANNING = auto()  # Work tracking and roadmaps
    CODE = auto()  # Software artifacts
    RUNTIME = auto()  # Execution environment
    DATA = auto()  # Stateful systems
    AI = auto()  # AI/ML systems
    BUSINESS = auto()  # Commercial entities
    GOVERNANCE = auto()  # Compliance and policy


class NodeType(Enum):
    """All node types in the unified graph."""

    # HUMAN Domain
    USER = "user"
    TEAM = "team"
    ORG = "organization"
    WORKSPACE = "workspace"
    ROLE = "role"
    APPROVAL_GROUP = "approval_group"
    COST_CENTER = "cost_center"

    # PLANNING Domain
    MISSION = "mission"
    PRODUCT = "product"
    INITIATIVE = "initiative"
    ROADMAP_ITEM = "roadmap_item"
    EPIC = "epic"
    ISSUE = "issue"
    BUG = "bug"
    INCIDENT = "incident"
    TASK = "task"
    MILESTONE = "milestone"
    SLA = "sla"
    SLO = "slo"

    # CODE Domain
    REPO = "repo"
    BRANCH = "branch"
    COMMIT = "commit"
    PR = "pull_request"
    TAG = "tag"
    RELEASE = "release"
    PACKAGE = "package"
    MODULE = "module"
    FILE = "file"
    CLASS = "class"
    FUNCTION = "function"
    SYMBOL = "symbol"
    CONFIG_FILE = "config_file"
    ENV_VAR = "env_var"
    SECRET = "secret"
    MIGRATION = "migration"
    TEST = "test"
    BENCHMARK = "benchmark"

    # RUNTIME Domain
    SERVICE = "service"
    CONTAINER = "container"
    IMAGE = "image"
    JOB = "job"
    WORKER = "worker"
    QUEUE = "queue"
    EVENT_BUS = "event_bus"
    FUNCTION_DEPLOYMENT = "function_deployment"
    ENDPOINT = "endpoint"
    API_ROUTE = "api_route"
    CRON = "cron"
    FEATURE_FLAG = "feature_flag"
    DEPLOYMENT = "deployment"
    REGION = "region"
    CLUSTER = "cluster"
    NODE = "node"
    EDGE_LOCATION = "edge_location"

    # DATA Domain
    DATABASE = "database"
    SCHEMA = "schema"
    TABLE = "table"
    COLUMN = "column"
    ROW_POLICY = "row_policy"
    WAREHOUSE = "warehouse"
    STREAM = "stream"
    CACHE = "cache"
    BLOB_STORE = "blob_store"
    SEARCH_INDEX = "search_index"
    VECTOR_INDEX = "vector_index"
    BACKUP = "backup"
    DATASET = "dataset"
    REPORT = "report"

    # AI Domain
    MODEL = "model"
    PROVIDER = "provider"
    PROMPT = "prompt"
    TOOL = "tool"
    AGENT = "agent"
    MEMORY_STORE = "memory_store"
    EVALUATION_SUITE = "evaluation_suite"
    SAFETY_POLICY = "safety_policy"
    TRACE = "trace"
    INFERENCE_ENDPOINT = "inference_endpoint"
    FINETUNE = "finetune"
    RAG_SOURCE = "rag_source"
    GUARDRAIL = "guardrail"

    # BUSINESS Domain
    CUSTOMER = "customer"
    TENANT = "tenant"
    SUBSCRIPTION = "subscription"
    INVOICE = "invoice"
    CONTRACT = "contract"
    REVENUE_STREAM = "revenue_stream"
    SUPPORT_CASE = "support_case"
    USAGE_METER = "usage_meter"

    # GOVERNANCE Domain
    POLICY = "policy"
    RISK = "risk"
    AUDIT_EVENT = "audit_event"
    EXCEPTION = "exception"
    EVIDENCE = "evidence"
    COMPLIANCE_CONTROL = "compliance_control"
    ACCESS_GRANT = "access_grant"
    RETENTION_RULE = "retention_rule"
    CLASSIFICATION = "classification"
    APPROVAL_RECORD = "approval_record"


# =============================================================================
# EDGE TYPES - Cross-Domain Relationships
# =============================================================================


class EdgeType(Enum):
    """Relationship types connecting the unified graph."""

    # Identity relationships
    OWNS = "OWNS"
    MEMBER_OF = "MEMBER_OF"
    BELONGS_TO = "BELONGS_TO"
    REPORTS_TO = "REPORTS_TO"
    HAS_ROLE = "HAS_ROLE"

    # Planning relationships
    DEPENDS_ON = "DEPENDS_ON"
    BLOCKS = "BLOCKS"
    FIXES = "FIXES"
    RELATES_TO = "RELATES_TO"
    PART_OF = "PART_OF"

    # Code relationships
    IMPORTS = "IMPORTS"
    CALLS = "CALLS"
    CONTAINS = "CONTAINS"
    DEFINES = "DEFINES"
    EXPORTS = "EXPORTS"
    TESTS = "TESTS"
    DOCUMENTS = "DOCUMENTS"
    COMMITTED_IN = "COMMITTED_IN"
    BRANCH_OF = "BRANCH_OF"
    MERGED_AS = "MERGED_AS"
    DEPLOYS = "DEPLOYS"

    # Runtime relationships
    RUNS_ON = "RUNS_ON"
    COMMUNICATES_WITH = "COMMUNICATES_WITH"
    PRODUCES = "PRODUCES"
    CONSUMES = "CONSUMES"
    TRIGGERS = "TRIGGERS"

    # Data relationships
    STORES_IN = "STORES_IN"
    QUERIES = "QUERIES"
    MIGRATES_TO = "MIGRATES_TO"
    BACKS_UP_TO = "BACKS_UP_TO"
    DERIVES_FROM = "DERIVES_FROM"

    # AI relationships
    USES_MODEL = "USES_MODEL"
    INVOKES_TOOL = "INVOKES_TOOL"
    DEPENDS_ON_MEMORY = "DEPENDS_ON_MEMORY"
    ENFORCED_BY = "ENFORCED_BY"

    # Business relationships
    BILLS_TO = "BILLS_TO"
    GENERATES_REVENUE = "GENERATES_REVENUE"
    SUPPORTS = "SUPPORTS"

    # Governance relationships
    GOVERNED_BY = "GOVERNED_BY"
    COMPLIES_WITH = "COMPLIES_WITH"
    REQUIRES_APPROVAL = "REQUIRES_APPROVAL"
    AUDITED_IN = "AUDITED_IN"
    HAS_ACCESS_TO = "HAS_ACCESS_TO"

    # Cross-domain (the key insight)
    CODE_IMPLEMENTS_FEATURE = "CODE_IMPLEMENTS_FEATURE"
    FEATURE_GENERATES_REVENUE = "FEATURE_GENERATES_REVENUE"
    INCIDENT_AFFECTS_SERVICE = "INCIDENT_AFFECTS_SERVICE"
    SERVICE_COSTS_BUDGET = "SERVICE_COSTS_BUDGET"
    AGENT_MODIFIES_CODE = "AGENT_MODIFIES_CODE"
    POLICY_CONTROLS_AGENT = "POLICY_CONTROLS_AGENT"


# =============================================================================
# CORE DATA STRUCTURES
# =============================================================================


@dataclass
class AxiomNode:
    """
    A node in the Axiom One unified graph.

    Every object in the platform is an AxiomNode with:
    - Unique ID (canonical hash)
    - Domain and type classification
    - Human-readable name
    - Source location (where it originates)
    - Properties (domain-specific attributes)
    - Temporal metadata (creation, modification, validity)
    """

    id: str
    domain: DomainType
    node_type: NodeType
    name: str
    properties: dict[str, Any] = field(default_factory=dict)
    source_location: dict[str, Any] = None  # file, line, url, etc.
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    modified_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    valid_from: str = None  # Temporal versioning
    valid_until: str = None

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AxiomNode):
            return NotImplemented
        return self.id == other.id

    @property
    def is_current(self) -> bool:
        """Check if node is currently valid (not deleted/archived)."""
        if self.valid_until:
            return datetime.now(UTC).isoformat() < self.valid_until
        return True

    def to_neo4j_dict(self) -> dict[str, Any]:
        """Convert to Neo4j-compatible dictionary."""
        return {
            "id": self.id,
            "domain": self.domain.name,
            "type": self.node_type.value,
            "name": self.name,
            "properties": json.dumps(self.properties),
            "created_at": self.created_at,
            "modified_at": self.modified_at,
            "valid_from": self.valid_from,
            "valid_until": self.valid_until,
        }

    @classmethod
    def from_neo4j_record(cls, record: neo4j.Record) -> AxiomNode:
        """Create from Neo4j record."""
        node = record["n"]
        return cls(
            id=node["id"],
            domain=DomainType[node["domain"]],
            node_type=NodeType(node["type"]),
            name=node["name"],
            properties=json.loads(node.get("properties", "{}")),
            created_at=node.get("created_at"),
            modified_at=node.get("modified_at"),
            valid_from=node.get("valid_from"),
            valid_until=node.get("valid_until"),
        )


@dataclass
class AxiomEdge:
    """
    An edge in the Axiom One unified graph.

    Represents relationships between objects with:
    - Source and target node IDs
    - Relationship type
    - Properties (context-specific attributes)
    - Weight (for graph algorithms)
    - Temporal validity (for time-travel queries)
    """

    source: str
    target: str
    edge_type: EdgeType
    properties: dict[str, Any] = field(default_factory=dict)
    weight: float = 1.0
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    valid_from: str = None
    valid_until: str = None

    def to_neo4j_dict(self) -> dict[str, Any]:
        """Convert to Neo4j-compatible dictionary."""
        return {
            "source": self.source,
            "target": self.target,
            "type": self.edge_type.value,
            "properties": json.dumps(self.properties),
            "weight": self.weight,
            "created_at": self.created_at,
            "valid_from": self.valid_from,
            "valid_until": self.valid_until,
        }


# =============================================================================
# UNIFIED GRAPH
# =============================================================================


class AxiomGraph:
    """
    The Axiom One unified graph G_axiom = (V, E, Φ, Τ, Λ).

    This is the canonical model of reality for the platform.
    All objects, relationships, and state are stored here.

    Features:
    - Multi-domain node types (8 domains, 50+ types)
    - Cross-domain edges (connecting code→runtime→business→governance)
    - Temporal versioning (time-travel queries)
    - Lineage tracking (data provenance)
    - Neo4j backend for graph queries
    """

    def __init__(self, neo4j_uri: str = None, neo4j_auth: tuple[str, str] = None):
        self.neo4j_uri = neo4j_uri or "bolt://localhost:7687"
        self.neo4j_auth = neo4j_auth or ("neo4j", "password")
        self._driver: Optional[AsyncGraphDatabase] = None
        self._local_nodes: dict[str, AxiomNode] = {}  # Cache for local operations
        self._local_edges: list[AxiomEdge] = []

    async def connect(self) -> bool:
        """Connect to Neo4j database."""
        try:
            self._driver = AsyncGraphDatabase.driver(self.neo4j_uri, auth=self.neo4j_auth)
            await self._driver.verify_connectivity()
            return True
        except Exception:
            return False

    async def initialize_schema(self) -> None:
        """Create Neo4j constraints and indexes."""
        if not self._driver:
            return

        async with self._driver.session() as session:
            # Constraints for uniqueness
            await session.run(
                "CREATE CONSTRAINT node_id IF NOT EXISTS FOR (n:AxiomNode) REQUIRE n.id IS UNIQUE"
            )

            # Indexes for performance
            await session.run(
                "CREATE INDEX node_type_idx IF NOT EXISTS FOR (n:AxiomNode) ON (n.type)"
            )
            await session.run(
                "CREATE INDEX node_domain_idx IF NOT EXISTS FOR (n:AxiomNode) ON (n.domain)"
            )
            await session.run(
                "CREATE INDEX node_name_idx IF NOT EXISTS FOR (n:AxiomNode) ON (n.name)"
            )
            await session.run(
                "CREATE INDEX edge_type_idx IF NOT EXISTS FOR ()-[r:RELATES]-() ON (r.type)"
            )

    async def add_node(self, node: AxiomNode) -> bool:
        """Add a node to the graph."""
        self._local_nodes[node.id] = node

        if not self._driver:
            return True

        async with self._driver.session() as session:
            try:
                await session.run(
                    """
                    MERGE (n:AxiomNode {id: $id})
                    SET n.domain = $domain,
                        n.type = $type,
                        n.name = $name,
                        n.properties = $properties,
                        n.created_at = $created_at,
                        n.modified_at = $modified_at,
                        n.valid_from = $valid_from,
                        n.valid_until = $valid_until
                    """,
                    **node.to_neo4j_dict(),
                )
                return True
            except Exception:
                return False

    async def add_edge(self, edge: AxiomEdge) -> bool:
        """Add an edge to the graph."""
        self._local_edges.append(edge)

        if not self._driver:
            return True

        async with self._driver.session() as session:
            try:
                await session.run(
                    """
                    MATCH (source:AxiomNode {id: $source})
                    MATCH (target:AxiomNode {id: $target})
                    MERGE (source)-[r:RELATES {type: $type}]->(target)
                    SET r.properties = $properties,
                        r.weight = $weight,
                        r.created_at = $created_at
                    """,
                    **edge.to_neo4j_dict(),
                )
                return True
            except Exception:
                return False

    async def get_node(self, node_id: str) -> Optional[AxiomNode]:
        """Get a node by ID."""
        # Check local cache first
        if node_id in self._local_nodes:
            return self._local_nodes[node_id]

        if not self._driver:
            return None

        async with self._driver.session() as session:
            result = await session.run("MATCH (n:AxiomNode {id: $id}) RETURN n", id=node_id)
            record = await result.single()
            if record:
                return AxiomNode.from_neo4j_record(record)
            return None

    async def get_neighbors(
        self,
        node_id: str,
        edge_type: Optional[EdgeType] = None,
        direction: str = "out",  # out, in, both
    ) -> list[AxiomNode]:
        """Get neighboring nodes."""
        if not self._driver:
            return []

        async with self._driver.session() as session:
            if edge_type:
                if direction == "out":
                    query = """
                        MATCH (n:AxiomNode {id: $id})-[r:RELATES {type: $type}]->(m)
                        RETURN m
                    """
                elif direction == "in":
                    query = """
                        MATCH (n:AxiomNode {id: $id})<-[r:RELATES {type: $type}]-(m)
                        RETURN m
                    """
                else:
                    query = """
                        MATCH (n:AxiomNode {id: $id})-[r:RELATES {type: $type}]-(m)
                        RETURN m
                    """
                result = await session.run(query, id=node_id, type=edge_type.value)
            else:
                if direction == "out":
                    query = "MATCH (n:AxiomNode {id: $id})-->(m) RETURN m"
                elif direction == "in":
                    query = "MATCH (n:AxiomNode {id: $id})<--(m) RETURN m"
                else:
                    query = "MATCH (n:AxiomNode {id: $id})--(m) RETURN m"
                result = await session.run(query, id=node_id)

            records = await result.data()
            return [AxiomNode.from_neo4j_record(r) for r in records]

    async def find_path(
        self,
        source: str,
        target: str,
        max_depth: int = 10,
        allowed_edge_types: list[EdgeType] = None,
    ) -> list[AxiomEdge]:
        """Find path between two nodes using BFS."""
        if not self._driver:
            return None

        async with self._driver.session() as session:
            if allowed_edge_types:
                types_str = "|".join([t.value for t in allowed_edge_types])
                query = f"""
                    MATCH path = shortestPath(
                        (source:AxiomNode {{id: $source}})-[:RELATES*1..{max_depth}]->(target:AxiomNode {{id: $target}})
                    )
                    WHERE ALL(r IN relationships(path) WHERE r.type IN $types)
                    RETURN path
                """
                result = await session.run(
                    query, source=source, target=target, types=types_str.split("|")
                )
            else:
                query = f"""
                    MATCH path = shortestPath(
                        (source:AxiomNode {{id: $source}})-[:RELATES*1..{max_depth}]->(target:AxiomNode {{id: $target}})
                    )
                    RETURN path
                """
                result = await session.run(query, source=source, target=target)

            record = await result.single()
            if record:
                # Convert path to list of edges
                path = record["path"]
                edges = []
                for rel in path.relationships:
                    edges.append(
                        AxiomEdge(
                            source=rel.start_node["id"],
                            target=rel.end_node["id"],
                            edge_type=EdgeType(rel["type"]),
                            properties=json.loads(rel.get("properties", "{}")),
                            weight=rel.get("weight", 1.0),
                        )
                    )
                return edges
            return None

    async def query_cross_domain(
        self, start_domain: DomainType, target_domain: DomainType, start_node_id: str
    ) -> list[dict[str, Any]]:
        """
        Query across domains - the key Axiom One capability.

        Example: Given a code file, find which customer features it affects,
        which revenue streams it generates, and which incidents touched it.
        """
        if not self._driver:
            return []

        async with self._driver.session() as session:
            # Find all paths from start node to any node in target domain
            query = """
                MATCH path = (start:AxiomNode {id: $start_id})-[:RELATES*1..10]->(target)
                WHERE target.domain = $target_domain
                RETURN path, target
                LIMIT 100
            """
            result = await session.run(
                query, start_id=start_node_id, target_domain=target_domain.name
            )

            paths = []
            async for record in result:
                path_data = {
                    "target": AxiomNode.from_neo4j_record({"n": record["target"]}),
                    "path_length": len(record["path"].relationships),
                    "relationships": [r["type"] for r in record["path"].relationships],
                }
                paths.append(path_data)

            return paths

    async def get_impact_analysis(self, node_id: str) -> dict[str, Any]:
        """
        Analyze impact of a node across all domains.

        Returns a map of affected objects by domain.
        """
        if not self._driver:
            return {}

        async with self._driver.session() as session:
            # Query all reachable nodes grouped by domain
            query = """
                MATCH (n:AxiomNode {id: $id})-[:RELATES*1..10]->(target)
                RETURN target.domain as domain, count(*) as count,
                       collect(target.name)[0..10] as examples
            """
            result = await session.run(query, id=node_id)

            impact = {}
            async for record in result:
                domain = record["domain"]
                impact[domain] = {"count": record["count"], "examples": record["examples"]}

            return impact

    async def close(self) -> None:
        """Close Neo4j connection."""
        if self._driver:
            await self._driver.close()


# =============================================================================
# NODE ID GENERATION
# =============================================================================


def generate_node_id(domain: DomainType, node_type: NodeType, name: str, context: str = "") -> str:
    """Generate canonical node ID."""
    content = f"{domain.name}:{node_type.value}:{name}:{context}"
    hash_val = hashlib.sha256(content.encode()).hexdigest()[:16]
    return f"{domain.name.lower()}:{node_type.value}:{hash_val}"


def generate_repo_file_node_id(repo_path: str, file_path: str) -> str:
    """Generate node ID for a file in a repo."""
    return generate_node_id(DomainType.CODE, NodeType.FILE, file_path, repo_path)


def generate_service_node_id(service_name: str, environment: str) -> str:
    """Generate node ID for a runtime service."""
    return generate_node_id(DomainType.RUNTIME, NodeType.SERVICE, service_name, environment)


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================


def create_user_node(user_id: str, email: str, name: str, org_id: str = None) -> AxiomNode:
    """Create a user node."""
    return AxiomNode(
        id=generate_node_id(DomainType.HUMAN, NodeType.USER, user_id),
        domain=DomainType.HUMAN,
        node_type=NodeType.USER,
        name=name,
        properties={
            "user_id": user_id,
            "email": email,
            "org_id": org_id,
        },
    )


def create_repo_node(repo_path: str, name: str, owner_id: str) -> AxiomNode:
    """Create a repository node."""
    return AxiomNode(
        id=generate_node_id(DomainType.CODE, NodeType.REPO, name, repo_path),
        domain=DomainType.CODE,
        node_type=NodeType.REPO,
        name=name,
        properties={
            "path": repo_path,
            "owner_id": owner_id,
        },
    )


def create_service_node(service_name: str, environment: str, repo_id: str = None) -> AxiomNode:
    """Create a runtime service node."""
    return AxiomNode(
        id=generate_service_node_id(service_name, environment),
        domain=DomainType.RUNTIME,
        node_type=NodeType.SERVICE,
        name=service_name,
        properties={
            "environment": environment,
            "repo_id": repo_id,
        },
    )


def create_agent_node(agent_name: str, agent_type: str, scope: list[str]) -> AxiomNode:
    """Create an AI agent node."""
    return AxiomNode(
        id=generate_node_id(DomainType.AI, NodeType.AGENT, agent_name),
        domain=DomainType.AI,
        node_type=NodeType.AGENT,
        name=agent_name,
        properties={
            "agent_type": agent_type,
            "scope": scope,
            "status": "inactive",
        },
    )
