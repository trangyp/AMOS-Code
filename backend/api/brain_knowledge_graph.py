"""Brain Knowledge Graph API - AMOS brain-powered knowledge management.

Provides knowledge graph operations:
- Knowledge node CRUD operations
- Relationship management
- Semantic queries
- Knowledge path finding
- Concept clustering
"""

from __future__ import annotations

import asyncio
import sys
import uuid
from collections.abc import AsyncIterator
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

UTC = timezone.utc

# Setup paths
AMOS_ROOT = Path(__file__).parent.parent.parent.resolve()
for p in [AMOS_ROOT, AMOS_ROOT / "amos_brain"]:
    if str(p) not in sys.path:

# Import brain components
try:
    from knowledge_loader import KnowledgeLoader

    from memory import BrainMemory

    _BRAIN_AVAILABLE = True
except ImportError:
    _BRAIN_AVAILABLE = False

router = APIRouter(prefix="/api/v1/brain/knowledge", tags=["Brain Knowledge Graph"])


class NodeType(str, Enum):
    """Types of knowledge nodes."""

    CONCEPT = "concept"
    ENTITY = "entity"
    EVENT = "event"
    RULE = "rule"
    PATTERN = "pattern"
    INSIGHT = "insight"


class RelationType(str, Enum):
    """Types of relationships between nodes."""

    IS_A = "is_a"
    PART_OF = "part_of"
    RELATED_TO = "related_to"
    CAUSES = "causes"
    DEPENDS_ON = "depends_on"
    SIMILAR_TO = "similar_to"
    LEADS_TO = "leads_to"
    CONTRADICTS = "contradicts"


class KnowledgeNode(BaseModel):
    """Knowledge graph node."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:12])
    label: str
    node_type: NodeType = NodeType.CONCEPT
    description: str = ""
    properties: dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)
    source: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    tags: list[str] = Field(default_factory=list)


class KnowledgeEdge(BaseModel):
    """Knowledge graph edge (relationship)."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    source_id: str
    target_id: str
    relation_type: RelationType = RelationType.RELATED_TO
    weight: float = Field(ge=0.0, le=1.0, default=1.0)
    properties: dict[str, Any] = Field(default_factory=dict)
    bidirectional: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class KnowledgeQuery(BaseModel):
    """Knowledge graph query."""

    query_text: str = Field(..., min_length=1, description="Natural language query")
    node_types: list[NodeType] = Field(default_factory=list)
    relation_types: list[RelationType] = Field(default_factory=list)
    min_confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    max_depth: int = Field(default=2, ge=1, le=5)
    limit: int = Field(default=20, ge=1, le=100)


class KnowledgePath(BaseModel):
    """Path through knowledge graph."""

    path_id: str
    nodes: list[KnowledgeNode]
    edges: list[KnowledgeEdge]
    total_weight: float
    path_length: int
    relevance_score: float


class KnowledgeCluster(BaseModel):
    """Cluster of related knowledge nodes."""

    cluster_id: str
    label: str
    nodes: list[KnowledgeNode]
    center_node: KnowledgeNode
    cohesion_score: float
    dominant_type: NodeType


class KnowledgeGraphStats(BaseModel):
    """Knowledge graph statistics."""

    total_nodes: int
    total_edges: int
    nodes_by_type: dict[str, int]
    edges_by_type: dict[str, int]
    avg_connectivity:float
    last_updated: Optional[datetime] = None


class KnowledgeGraphEngine:
    """Knowledge graph engine using AMOS brain."""

    def __init__(self) -> None:
        self._nodes: dict[str, KnowledgeNode] = {}
        self._edges: dict[str, KnowledgeEdge] = {}
        self._adjacency: dict[str, list[str]] = {}  # node_id -> list of edge_ids
        self._knowledge_loader: Any = None
        self._memory: Any = None
        self._lock = asyncio.Lock()

    async def _get_knowledge_loader(self) -> Any:
        """Get knowledge loader."""
        if _BRAIN_AVAILABLE and self._knowledge_loader is None:
            try:
                self._knowledge_loader = KnowledgeLoader()
            except Exception:
                pass
        return self._knowledge_loader

    async def _get_memory(self) -> Any:
        """Get brain memory."""
        if _BRAIN_AVAILABLE and self._memory is None:
            try:
                self._memory = BrainMemory()
            except Exception:
                pass
        return self._memory

    async def create_node(self, node: KnowledgeNode) -> KnowledgeNode:
        """Create a knowledge node."""
        async with self._lock:
            # Check for duplicate labels
            existing = [n for n in self._nodes.values() if n.label.lower() == node.label.lower()]
            if existing:
                raise HTTPException(
                    status_code=409, detail=f"Node with label '{node.label}' already exists"
                )

            self._nodes[node.id] = node
            self._adjacency[node.id] = []

            # Save to memory if available
            memory = await self._get_memory()
            if memory and hasattr(memory, "save_reasoning"):
                try:
                    memory.save_reasoning(
                        problem=f"Knowledge node: {node.label}",
                        analysis=node.model_dump(),
                        tags=["knowledge_graph", node.node_type.value],
                    )
                except Exception:
                    pass

            return node

    async def get_node(self, node_id: str) -> Optional[KnowledgeNode]:
        """Get a knowledge node by ID."""
        return self._nodes.get(node_id)

    async def update_node(self, node_id: str, updates: dict[str, Any]) -> KnowledgeNode:
        """Update a knowledge node."""
        async with self._lock:
            if node_id not in self._nodes:
                raise HTTPException(status_code=404, detail=f"Node {node_id} not found")

            node = self._nodes[node_id]

            # Apply updates
            for key, value in updates.items():
                if hasattr(node, key) and key != "id":
                    setattr(node, key, value)

            node.updated_at = datetime.now(UTC)

            return node

    async def delete_node(self, node_id: str) -> bool:
        """Delete a knowledge node and its edges."""
        async with self._lock:
            if node_id not in self._nodes:
                return False

            # Remove connected edges
            edge_ids = self._adjacency.get(node_id, [])
            for edge_id in edge_ids:
                if edge_id in self._edges:
                    del self._edges[edge_id]

            # Remove from adjacency lists
            del self._adjacency[node_id]
            for edges in self._adjacency.values():
                if edge_id in edges:
                    edges.remove(edge_id)

            del self._nodes[node_id]
            return True

    async def create_edge(self, edge: KnowledgeEdge) -> KnowledgeEdge:
        """Create a relationship between nodes."""
        async with self._lock:
            # Validate nodes exist
            if edge.source_id not in self._nodes:
                raise HTTPException(
                    status_code=404, detail=f"Source node {edge.source_id} not found"
                )
            if edge.target_id not in self._nodes:
                raise HTTPException(
                    status_code=404, detail=f"Target node {edge.target_id} not found"
                )

            self._edges[edge.id] = edge

            # Update adjacency
            if edge.source_id not in self._adjacency:
                self._adjacency[edge.source_id] = []
            self._adjacency[edge.source_id].append(edge.id)

            if edge.bidirectional:
                if edge.target_id not in self._adjacency:
                    self._adjacency[edge.target_id] = []
                self._adjacency[edge.target_id].append(edge.id)

            return edge

    async def query_knowledge(self, query: KnowledgeQuery) -> list[KnowledgeNode]:
        """Query knowledge graph."""
        results: list[KnowledgeNode] = []

        # Simple text-based search
        query_lower = query.query_text.lower()

        for node in self._nodes.values():
            # Check confidence
            if node.confidence < query.min_confidence:
                continue

            # Check node type filter
            if query.node_types and node.node_type not in query.node_types:
                continue

            # Text matching
            score = 0.0
            if query_lower in node.label.lower():
                score += 1.0
            if node.description and query_lower in node.description.lower():
                score += 0.5
            if any(query_lower in tag.lower() for tag in node.tags):
                score += 0.3

            if score > 0:
                results.append(node)

        # Sort by relevance (simplified)
        results.sort(key=lambda n: n.confidence, reverse=True)

        return results[: query.limit]

    async def find_paths(
        self, source_id: str, target_id: str, max_depth: int = 3
    ) -> list[KnowledgePath]:
        """Find paths between two nodes."""
        if source_id not in self._nodes:
            raise HTTPException(status_code=404, detail=f"Source {source_id} not found")
        if target_id not in self._nodes:
            raise HTTPException(status_code=404, detail=f"Target {target_id} not found")

        paths: list[KnowledgePath] = []

        # Simple BFS for paths
        visited: set[str] = set()
        queue: list[tuple[str, list[str], list[str], float]] = [(source_id, [source_id], [], 0.0)]

        while queue and len(paths) < 10:
            current_id, node_path, edge_path, weight = queue.pop(0)

            if current_id == target_id and len(node_path) > 1:
                nodes = [self._nodes[nid] for nid in node_path]
                edges = [self._edges[eid] for eid in edge_path]
                paths.append(
                    KnowledgePath(
                        path_id=str(uuid.uuid4())[:8],
                        nodes=nodes,
                        edges=edges,
                        total_weight=weight,
                        path_length=len(edges),
                        relevance_score=1.0 / len(edges) if edges else 0,
                    )
                )
                continue

            if len(node_path) >= max_depth:
                continue

            # Explore neighbors
            for edge_id in self._adjacency.get(current_id, []):
                edge = self._edges.get(edge_id)
                if not edge:
                    continue

                next_id = edge.target_id if edge.source_id == current_id else edge.source_id

                if next_id not in visited or next_id == target_id:
                    new_visited = visited | {next_id}
                    queue.append(
                        (
                            next_id,
                            node_path + [next_id],
                            edge_path + [edge_id],
                            weight + edge.weight,
                        )
                    )

        return paths

    async def get_clusters(self) -> list[KnowledgeCluster]:
        """Get knowledge clusters."""
        clusters: list[KnowledgeCluster] = []

        # Group by node type as simple clustering
        by_type: dict[NodeType, list[KnowledgeNode]] = {}
        for node in self._nodes.values():
            if node.node_type not in by_type:
                by_type[node.node_type] = []
            by_type[node.node_type].append(node)

        for node_type, nodes in by_type.items():
            if len(nodes) >= 2:
                center = max(nodes, key=lambda n: len(self._adjacency.get(n.id, [])))
                clusters.append(
                    KnowledgeCluster(
                        cluster_id=str(uuid.uuid4())[:8],
                        label=f"{node_type.value.capitalize()} Cluster",
                        nodes=nodes,
                        center_node=center,
                        cohesion_score=len(nodes) / len(self._nodes) if self._nodes else 0,
                        dominant_type=node_type,
                    )
                )

        return clusters

    async def get_stats(self) -> KnowledgeGraphStats:
        """Get knowledge graph statistics."""
        nodes_by_type: dict[str, int] = {}
        for node in self._nodes.values():
            t = node.node_type.value
            nodes_by_type[t] = nodes_by_type.get(t, 0) + 1

        edges_by_type: dict[str, int] = {}
        for edge in self._edges.values():
            t = edge.relation_type.value
            edges_by_type[t] = edges_by_type.get(t, 0) + 1

        # Calculate average connectivity
        total_connections = sum(len(edges) for edges in self._adjacency.values())
        avg_connectivity = total_connections / len(self._nodes) if self._nodes else 0.0

        return KnowledgeGraphStats(
            total_nodes=len(self._nodes),
            total_edges=len(self._edges),
            nodes_by_type=nodes_by_type,
            edges_by_type=edges_by_type,
            avg_connectivity=avg_connectivity,
            last_updated=datetime.now(UTC) if self._nodes else None,
        )

    async def stream_nodes(self) -> AsyncIterator[KnowledgeNode]:
        """Stream all nodes."""
        for node in self._nodes.values():
            yield node


#Global engine
_graph_engine: Optional[KnowledgeGraphEngine] = None


def get_graph_engine() -> KnowledgeGraphEngine:
    """Get or create knowledge graph engine."""
    global _graph_engine
    if _graph_engine is None:
        _graph_engine = KnowledgeGraphEngine()
    return _graph_engine


@router.post("/nodes", response_model=KnowledgeNode)
async def create_node(node: KnowledgeNode) -> KnowledgeNode:
    """Create a knowledge node."""
    engine = get_graph_engine()
    return await engine.create_node(node)


@router.get("/nodes/{node_id}", response_model=KnowledgeNode)
async def get_node(node_id: str) -> KnowledgeNode:
    """Get a knowledge node by ID."""
    engine = get_graph_engine()
    node = await engine.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
    return node


@router.get("/nodes")
async def list_nodes(node_type: Optional[NodeType] =None,
    tag: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=200),
) -> list[KnowledgeNode]:
    """List knowledge nodes with optional filtering."""
    engine = get_graph_engine()
    nodes = list(engine._nodes.values())

    if node_type:
        nodes = [n for n in nodes if n.node_type == node_type]

    if tag:
        nodes = [n for n in nodes if tag in n.tags]

    return nodes[:limit]


@router.patch("/nodes/{node_id}")
async def update_node(node_id: str, updates: dict[str, Any]) -> KnowledgeNode:
    """Update a knowledge node."""
    engine = get_graph_engine()
    return await engine.update_node(node_id, updates)


@router.delete("/nodes/{node_id}")
async def delete_node(node_id: str) -> dict[str, Any]:
    """Delete a knowledge node."""
    engine = get_graph_engine()
    success = await engine.delete_node(node_id)
    return {"deleted": success, "node_id": node_id}


@router.post("/edges", response_model=KnowledgeEdge)
async def create_edge(edge: KnowledgeEdge) -> KnowledgeEdge:
    """Create a relationship between nodes."""
    engine = get_graph_engine()
    return await engine.create_edge(edge)


@router.post("/query", response_model=list[KnowledgeNode])
async def query_knowledge(query: KnowledgeQuery) -> list[KnowledgeNode]:
    """Query knowledge graph."""
    engine = get_graph_engine()
    return await engine.query_knowledge(query)


@router.get("/paths")
async def find_paths(
    source_id: str, target_id: str, max_depth: int = Query(default=3, ge=1, le=5)
) -> list[KnowledgePath]:
    """Find paths between two knowledge nodes."""
    engine = get_graph_engine()
    return await engine.find_paths(source_id, target_id, max_depth)


@router.get("/clusters", response_model=list[KnowledgeCluster])
async def get_clusters() -> list[KnowledgeCluster]:
    """Get knowledge clusters."""
    engine = get_graph_engine()
    return await engine.get_clusters()


@router.get("/stats", response_model=KnowledgeGraphStats)
async def get_stats() -> KnowledgeGraphStats:
    """Get knowledge graph statistics."""
    engine = get_graph_engine()
    return await engine.get_stats()


@router.get("/stream")
async def stream_nodes() -> StreamingResponse:
    """Stream all knowledge nodes."""
    engine = get_graph_engine()

    async def event_generator():
        async for node in engine.stream_nodes():
            yield f"data: {node.model_dump_json()}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/health")
async def health_check() -> dict[str, Any]:
    """Health check for knowledge graph."""
    engine = get_graph_engine()
    stats = await engine.get_stats()

    return {
        "status": "healthy",
        "brain_available": _BRAIN_AVAILABLE,
        "total_nodes": stats.total_nodes,
        "total_edges": stats.total_edges,
        "engine": "active",
    }
