"""AMOS Graph API Endpoints.

REST API for equation graph and knowledge graph operations.

Author: AMOS Graph Team
Version: 2.0.0
"""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from graph.neo4j_client import EquationGraph, GraphEquation

router = APIRouter(prefix="/graph", tags=["Graph"])


# Pydantic Models
class EquationNode(BaseModel):
    """Equation node for graph."""

    id: str
    name: str
    formula: str
    category: str = "general"
    difficulty: int = Field(default=1, ge=1, le=10)


class ConceptNode(BaseModel):
    """Concept node for graph."""

    id: str
    name: str
    concept_type: str = "mathematical"


class RelationshipCreate(BaseModel):
    """Create relationship request."""

    source_id: str
    target_id: str
    rel_type: str = Field(..., regex="^(DERIVES_FROM|PREREQUISITE_FOR|RELATED_TO|USES|EXAMPLE_OF)$")
    properties: Dict[str, Any] = {}


class RelatedEquation(BaseModel):
    """Related equation response."""

    id: str
    name: str
    formula: str
    category: str
    difficulty: int
    distance: int = None


class LearningPathResponse(BaseModel):
    """Learning path response."""

    start: str
    end: str
    nodes: List[dict[str, Any]]
    steps: int
    path_found: bool


class Recommendation(BaseModel):
    """Equation recommendation."""

    id: str
    name: str
    formula: str
    relevance: int


class GraphStats(BaseModel):
    """Knowledge graph statistics."""

    equations: int
    concepts: int
    relationships: int
    categories: int


# Dependency injection
def get_graph() -> EquationGraph:
    """Get graph database instance."""
    from config import settings

    return EquationGraph(
        uri=settings.NEO4J_URI or "bolt://localhost:7687",
        user=settings.NEO4J_USER or "neo4j",
        password=settings.NEO4J_PASSWORD or "password",
    )


# API Endpoints
@router.post("/equations", status_code=201)
async def create_equation_node(
    equation: EquationNode,
    graph: EquationGraph = Depends(get_graph),
) -> Dict[str, str]:
    """Create equation node in graph."""
    await graph.create_equation_node(
        GraphEquation(
            id=equation.id,
            name=equation.name,
            formula=equation.formula,
            category=equation.category,
            difficulty=equation.difficulty,
        )
    )
    return {"status": "created", "id": equation.id}


@router.post("/concepts", status_code=201)
async def create_concept_node(
    concept: ConceptNode,
    graph: EquationGraph = Depends(get_graph),
) -> Dict[str, str]:
    """Create concept node in graph."""
    await graph.create_concept_node(
        concept_id=concept.id,
        name=concept.name,
        concept_type=concept.concept_type,
    )
    return {"status": "created", "id": concept.id}


@router.post("/relationships", status_code=201)
async def create_relationship(
    rel: RelationshipCreate,
    graph: EquationGraph = Depends(get_graph),
) -> Dict[str, str]:
    """Create relationship between nodes."""
    await graph.create_relationship(
        source_id=rel.source_id,
        target_id=rel.target_id,
        rel_type=rel.rel_type,
        properties=rel.properties,
    )
    return {
        "status": "created",
        "relationship": f"{rel.source_id}-[:{rel.rel_type}]->{rel.target_id}",
    }


@router.get("/equations/{equation_id}/related", response_model=list[RelatedEquation])
async def get_related_equations(
    equation_id: str,
    rel_type: str = Query(None, description="Filter by relationship type"),
    depth: int = Query(default=1, ge=1, le=3),
    graph: EquationGraph = Depends(get_graph),
) -> List[RelatedEquation]:
    """Get equations related to given equation."""
    related = await graph.get_related_equations(equation_id, rel_type, depth)
    return [
        RelatedEquation(
            id=r["id"],
            name=r["name"],
            formula=r["formula"],
            category=r["category"],
            difficulty=r["difficulty"],
            distance=r.get("distance"),
        )
        for r in related
    ]


@router.get("/equations/{equation_id}/prerequisites")
async def get_prerequisites(
    equation_id: str,
    graph: EquationGraph = Depends(get_graph),
) -> List[dict[str, Any]]:
    """Get prerequisite equations/concepts."""
    return await graph.get_prerequisites(equation_id)


@router.get("/equations/{equation_id}/derivatives")
async def get_derivatives(
    equation_id: str,
    graph: EquationGraph = Depends(get_graph),
) -> List[dict[str, Any]]:
    """Get equations derived from this equation."""
    return await graph.get_derivatives(equation_id)


@router.get("/path", response_model=LearningPathResponse)
async def find_learning_path(
    start: str = Query(..., description="Starting concept/equation ID"),
    end: str = Query(..., description="Target concept/equation ID"),
    max_depth: int = Query(default=5, ge=1, le=10),
    graph: EquationGraph = Depends(get_graph),
) -> LearningPathResponse:
    """Find learning path between concepts."""
    path = await graph.find_learning_path(start, end, max_depth)

    if not path:
        return LearningPathResponse(
            start=start,
            end=end,
            nodes=[],
            steps=0,
            path_found=False,
        )

    return LearningPathResponse(
        start=start,
        end=end,
        nodes=path.nodes,
        steps=path.length,
        path_found=True,
    )


@router.get("/recommendations/{user_id}", response_model=list[Recommendation])
async def get_recommendations(
    user_id: str,
    known: List[str] = Query(default=[], description="Known equation IDs"),
    limit: int = Query(default=10, ge=1, le=50),
    graph: EquationGraph = Depends(get_graph),
) -> List[Recommendation]:
    """Get equation recommendations for user."""
    recs = await graph.recommend_for_user(user_id, known, limit)
    return [
        Recommendation(
            id=r["id"],
            name=r["name"],
            formula=r["formula"],
            relevance=r["relevance"],
        )
        for r in recs
    ]


@router.get("/search")
async def search_concepts(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(default=20, ge=1, le=100),
    graph: EquationGraph = Depends(get_graph),
) -> Dict[str, Any]:
    """Search concepts and equations."""
    results = await graph.search_concepts(q, limit)
    return {"query": q, "results": results, "count": len(results)}


@router.get("/stats", response_model=GraphStats)
async def get_graph_stats(
    graph: EquationGraph = Depends(get_graph),
) -> GraphStats:
    """Get knowledge graph statistics."""
    stats = await graph.get_knowledge_graph_stats()
    return GraphStats(**stats)


@router.get("/centrality")
async def get_central_equations(
    limit: int = Query(default=10, ge=1, le=50),
    graph: EquationGraph = Depends(get_graph),
) -> List[dict[str, Any]]:
    """Get most central equations by connection count."""
    from graph.neo4j_client import GraphAnalytics

    analytics = GraphAnalytics(graph)
    return await analytics.get_central_equations(limit)


@router.delete("/equations/{equation_id}")
async def delete_equation(
    equation_id: str,
    graph: EquationGraph = Depends(get_graph),
) -> Dict[str, str]:
    """Delete equation from graph."""
    await graph.delete_equation(equation_id)
    return {"status": "deleted", "id": equation_id}


@router.get("/admin/health")
async def graph_health(
    graph: EquationGraph = Depends(get_graph),
) -> Dict[str, Any]:
    """Check graph database health."""
    return await graph.health_check()


@router.post("/admin/indexes")
async def create_indexes(
    graph: EquationGraph = Depends(get_graph),
) -> Dict[str, str]:
    """Create database indexes."""
    await graph.create_indexes()
    return {"status": "indexes_created"}
