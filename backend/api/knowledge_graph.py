"""AMOS Knowledge Graph API - GraphRAG & Entity Management

Production-ready graph endpoints for knowledge representation
and graph-based retrieval with Brain v2 integration.

Owner: Trang Phan
Version: 2.0.0
"""

from __future__ import annotations


from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from backend.auth import User, get_current_user
from backend.knowledge_graph import (
    GraphNode,
    GraphQuery,
    GraphRelationship,
    KnowledgeGraphService,
    extract_entities,
    graph_retrieval,
    knowledge_graph,
)

# Brain v2 integration for intelligent graph analysis
try:
    from amos_brain.api_integration import brain_process_sync
    from amos_brain.brain_event_processor import emit_event

    _BRAIN_KG_AVAILABLE = True
except ImportError:
    _BRAIN_KG_AVAILABLE = False

router = APIRouter(prefix="/knowledge-graph", tags=["knowledge-graph"])


class NodeCreateRequest(BaseModel):
    """Request to create a graph node."""

    node_id: str = Field(..., description="Unique node identifier")
    node_type: str = Field(..., description="Node type: entity, concept, document, chunk")
    name: str = Field(..., description="Node name/label")
    properties: dict[str, Any] = Field(default_factory=dict, description="Node properties")
    vector: list[float] | None = Field(None, description="Optional embedding vector")
    source_doc: str | None = Field(None, description="Source document ID")


class RelationshipCreateRequest(BaseModel):
    """Request to create a relationship."""

    source_id: str = Field(..., description="Source node ID")
    target_id: str = Field(..., description="Target node ID")
    rel_type: str = Field(..., description="Relationship type")
    properties: dict[str, Any] = Field(default_factory=dict, description="Relationship properties")
    weight: float = Field(default=1.0, description="Relationship weight")


class EntityExtractRequest(BaseModel):
    """Request to extract entities from text."""

    text: str = Field(..., description="Text to analyze")
    doc_id: str | None = Field(None, description="Optional document ID")


class GraphRAGRequest(BaseModel):
    """Request for GraphRAG retrieval."""

    query: str = Field(..., description="Search query")
    query_vector: list[float] | None = Field(None, description="Optional query embedding")
    depth: int = Field(default=2, ge=1, le=5, description="Graph traversal depth")
    top_k: int = Field(default=10, ge=1, le=50, description="Number of results")


class NodeResponse(BaseModel):
    """Node response model."""

    node_id: str
    node_type: str
    name: str
    properties: dict[str, Any]
    source_doc: str | None
    created_at: float


class RelationshipResponse(BaseModel):
    """Relationship response model."""

    rel_id: str
    source_id: str
    target_id: str
    rel_type: str
    weight: float
    properties: dict[str, Any]


class GraphRAGResult(BaseModel):
    """GraphRAG retrieval result."""

    seed_node: NodeResponse
    context: str
    depth: int
    path_score: float


class GraphStatsResponse(BaseModel):
    """Graph statistics."""

    total_nodes: int
    total_relationships: int
    nodes_by_type: dict[str, int]
    relationships_by_type: dict[str, int]
    backend: str


def get_graph_service() -> KnowledgeGraphService:
    """Dependency injection for knowledge graph service."""
    return knowledge_graph


@router.post("/nodes", response_model=NodeResponse, status_code=status.HTTP_201_CREATED)
async def create_node(
    request: NodeCreateRequest,
    service: KnowledgeGraphService = Depends(get_graph_service),
    current_user: User = Depends(get_current_user),
) -> NodeResponse:
    """Create a new graph node."""
    node = GraphNode(
        node_id=request.node_id,
        node_type=request.node_type,
        name=request.name,
        properties=request.properties,
        vector=request.vector,
        source_doc=request.source_doc,
    )

    success = service.add_node(node)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create node (may be duplicate or validation failed)",
        )

    return NodeResponse(
        node_id=node.node_id,
        node_type=node.node_type,
        name=node.name,
        properties=node.properties,
        source_doc=node.source_doc,
        created_at=node.created_at,
    )


@router.get("/nodes/{node_id}", response_model=NodeResponse)
async def get_node(
    node_id: str,
    service: KnowledgeGraphService = Depends(get_graph_service),
    current_user: User = Depends(get_current_user),
) -> NodeResponse:
    """Get node by ID."""
    node = service.get_node(node_id)
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Node {node_id} not found"
        )

    return NodeResponse(
        node_id=node.node_id,
        node_type=node.node_type,
        name=node.name,
        properties=node.properties,
        source_doc=node.source_doc,
        created_at=node.created_at,
    )


@router.post(
    "/relationships", response_model=RelationshipResponse, status_code=status.HTTP_201_CREATED
)
async def create_relationship(
    request: RelationshipCreateRequest,
    service: KnowledgeGraphService = Depends(get_graph_service),
    current_user: User = Depends(get_current_user),
) -> RelationshipResponse:
    """Create a new relationship between nodes."""
    import hashlib

    rel_id = f"rel_{hashlib.sha256(f'{request.source_id}:{request.target_id}:{request.rel_type}'.encode()).hexdigest()[:12]}"

    rel = GraphRelationship(
        rel_id=rel_id,
        source_id=request.source_id,
        target_id=request.target_id,
        rel_type=request.rel_type,
        properties=request.properties,
        weight=request.weight,
    )

    success = service.add_relationship(rel)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create relationship (nodes may not exist)",
        )

    return RelationshipResponse(
        rel_id=rel.rel_id,
        source_id=rel.source_id,
        target_id=rel.target_id,
        rel_type=rel.rel_type,
        weight=rel.weight,
        properties=rel.properties,
    )


@router.post("/extract", response_model=dict[str, Any])
async def extract_entities_endpoint(
    request: EntityExtractRequest,
    service: KnowledgeGraphService = Depends(get_graph_service),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Extract entities and relationships from text.

    Automatically creates nodes and relationships in the graph.
    """
    nodes, relationships = extract_entities(request.text, request.doc_id)

    # Add extracted entities to graph
    created_nodes = []
    created_rels = []

    for node in nodes:
        if service.add_node(node):
            created_nodes.append(node.node_id)

    for rel in relationships:
        if service.add_relationship(rel):
            created_rels.append(rel.rel_id)

    return {
        "extracted_nodes": len(nodes),
        "extracted_relationships": len(relationships),
        "created_nodes": len(created_nodes),
        "created_relationships": len(created_rels),
        "node_ids": created_nodes,
        "relationship_ids": created_rels,
    }


@router.post("/retrieve", response_model=list[GraphRAGResult])
async def graph_rag_retrieve(
    request: GraphRAGRequest,
    service: KnowledgeGraphService = Depends(get_graph_service),
    current_user: User = Depends(get_current_user),
) -> list[GraphRAGResult]:
    """GraphRAG retrieval - combines vector similarity with graph traversal.

    Provides more contextual and accurate retrieval than vector-only RAG.
    """
    results = graph_retrieval(
        query=request.query,
        query_vector=request.query_vector,
        depth=request.depth,
        top_k=request.top_k,
    )

    return [
        GraphRAGResult(
            seed_node=NodeResponse(
                node_id=r["seed_node"].node_id,
                node_type=r["seed_node"].node_type,
                name=r["seed_node"].name,
                properties=r["seed_node"].properties,
                source_doc=r["seed_node"].source_doc,
                created_at=r["seed_node"].created_at,
            ),
            context=r["context"],
            depth=r["depth"],
            path_score=r["path_score"],
        )
        for r in results
    ]


@router.get("/stats", response_model=GraphStatsResponse)
async def get_graph_stats(
    service: KnowledgeGraphService = Depends(get_graph_service),
    current_user: User = Depends(get_current_user),
) -> GraphStatsResponse:
    """Get graph statistics."""
    stats = service.get_stats()
    return GraphStatsResponse(
        total_nodes=stats["total_nodes"],
        total_relationships=stats["total_relationships"],
        nodes_by_type=stats["nodes_by_type"],
        relationships_by_type=stats["relationships_by_type"],
        backend=stats["backend"],
    )


@router.get("/query")
async def query_graph(
    node_types: str | None = Query(None, description="Comma-separated node types"),
    rel_types: str | None = Query(None, description="Comma-separated relationship types"),
    start_node: str | None = Query(None, description="Starting node for traversal"),
    depth: int = Query(default=2, ge=1, le=5),
    limit: int = Query(default=100, ge=1, le=1000),
    service: KnowledgeGraphService = Depends(get_graph_service),
    current_user: User = Depends(get_current_user),
) -> list[dict[str, Any]]:
    """Query the knowledge graph with filters."""
    query = GraphQuery(
        node_types=node_types.split(",") if node_types else None,
        rel_types=rel_types.split(",") if rel_types else None,
        start_node=start_node,
        depth=depth,
        limit=limit,
    )

    results = service.query(query)
    return [
        {
            "node": {
                "node_id": r["node"].node_id,
                "name": r["node"].name,
                "type": r["node"].node_type,
            },
            "relationships": [
                {"type": rel.rel_type, "weight": rel.weight} for rel in r["relationships"]
            ],
            "connected_nodes": [
                {"node_id": n.node_id, "name": n.name} for n in r["connected_nodes"] if n
            ],
        }
        for r in results
    ]


@router.post("/brain-analyze")
async def brain_analyze_graph(
    focus: str | None = Query(None, description="Analysis focus"),
    service: KnowledgeGraphService = Depends(get_graph_service),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Brain-powered knowledge graph analysis."""
    if not _BRAIN_KG_AVAILABLE:
        return {"analysis": "brain_not_available"}

    stats = service.get_stats()

    try:
        emit_event("knowledge_graph.analysis_requested", {"focus": focus})

        result = brain_process_sync(
            "Analyze knowledge graph structure and suggest improvements",
            {
                "stats": stats,
                "focus": focus or "general analysis",
            },
        )

        return {
            "analysis": result.get("analysis", {}),
            "recommendations": result.get("recommendations", []),
            "insights": result.get("insights", []),
            "brain_processed": True,
        }
    except Exception as e:
        return {"analysis": "error", "error": str(e), "brain_processed": False}
