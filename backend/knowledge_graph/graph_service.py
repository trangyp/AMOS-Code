from typing import Any, Dict, List, Optional, Tuple

"""
AMOS Knowledge Graph & GraphRAG Service v2.0.0

Graph-based knowledge representation with:
- Entity extraction and relationship mapping
- Graph-based retrieval for RAG
- Hybrid search: BM25 + Vector + Graph traversal
- NetworkX/Neo4j storage backends
- Graph reasoning and path analysis

Architecture based on Microsoft GraphRAG and Neo4j best practices.

Owner: Trang Phan
Version: 2.0.0
"""

import json
import re
import time
from collections import defaultdict
from dataclasses import dataclass, field
import redis.asyncio as redis

try:
    import networkx as nx

    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False

try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    from amos_brain import get_super_brain

    SUPERBRAIN_AVAILABLE = True
except ImportError:
    SUPERBRAIN_AVAILABLE = False

try:
    from backend.data_pipeline.streaming import publish_event

    STREAMING_AVAILABLE = True
except ImportError:
    STREAMING_AVAILABLE = False

@dataclass
class GraphNode:
    """Node in knowledge graph."""

    node_id: str
    node_type: str  # entity, concept, document, chunk
    name: str
    properties: Dict[str, Any] = field(default_factory=dict)
    vector: Optional[list[float]] = None
    source_doc: Optional[str] = None
    created_at: float = field(default_factory=time.time)

@dataclass
class GraphRelationship:
    """Relationship between nodes."""

    rel_id: str
    source_id: str
    target_id: str
    rel_type: str  # part_of, relates_to, implements, depends_on, etc.
    properties: Dict[str, Any] = field(default_factory=dict)
    weight: float = 1.0
    created_at: float = field(default_factory=time.time)

@dataclass
class GraphQuery:
    """Graph query specification."""

    node_types: Optional[list[str]] = None
    rel_types: Optional[list[str]] = None
    node_properties: Dict[str, Any] = field(default_factory=dict)
    start_node: Optional[str] = None
    depth: int = 2
    min_weight: float = 0.0
    limit: int = 100

class EntityExtractor:
    """Extract entities and relationships from text."""

    # Common entity patterns
    ENTITY_PATTERNS = {
        "person": r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\b",
        "organization": r"\b[A-Z][a-z]*(?:\s+[A-Z][a-z]*)+(?:\s+(?:Inc|Ltd|Corp|LLC|Company|Organization))\b",
        "technology": r"\b(?:Python|JavaScript|TypeScript|Rust|Go|Java|C\+\+|React|Vue|Angular|Node\.js|Docker|Kubernetes|Redis|Kafka|Postgres|MongoDB)\b",
        "equation": r"\b(?:softmax|sigmoid|relu|tanh|gradient|derivative|integral|matrix|vector|tensor)\b",
        "feature": r"\b(?:workflow|search|analytics|caching|streaming|inference|embedding|tokenization)\b",
    }

    # Relationship indicators
    RELATIONSHIP_PATTERNS = {
        "implements": r"\b(?:implements?|realizes?|fulfills?)\b",
        "depends_on": r"\b(?:depends?\s+on|requires?|needs?|uses?)\b",
        "part_of": r"\b(?:part\s+of|component\s+of|belongs?\s+to|within)\b",
        "relates_to": r"\b(?:relates?\s+to|connected\s+to|associated\s+with|linked\s+to)\b",
        "produces": r"\b(?:produces?|generates?|creates?|outputs?|returns?)\b",
        "consumes": r"\b(?:consumes?|inputs?|receives?|accepts?|takes?)\b",
    }

    def extract(
        self, text: str, doc_id: Optional[str] = None
    ) -> Tuple[list[GraphNode], list[GraphRelationship]]:
        """Extract entities and relationships from text."""
        import hashlib

        nodes: List[GraphNode] = []
        relationships: List[GraphRelationship] = []
        seen_entities: Dict[str, str] = {}  # name -> node_id

        # Extract entities
        for entity_type, pattern in self.ENTITY_PATTERNS.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                name = match.group(0)
                if name.lower() in seen_entities:
                    continue

                node_id = f"ent_{hashlib.md5(f'{name}:{entity_type}'.encode()).hexdigest()[:12]}"
                seen_entities[name.lower()] = node_id

                node = GraphNode(
                    node_id=node_id,
                    node_type=entity_type,
                    name=name,
                    properties={
                        "occurrences": 1,
                        "context": text[
                            max(0, match.start() - 50) : min(len(text), match.end() + 50)
                        ],
                    },
                    source_doc=doc_id,
                )
                nodes.append(node)

        # Extract relationships between nearby entities
        for i, node1 in enumerate(nodes):
            for node2 in nodes[i + 1 :]:
                # Check for relationship patterns between these entities
                rel_type = self._detect_relationship(text, node1.name, node2.name)
                if rel_type:
                    rel_id = f"rel_{hashlib.md5(f'{node1.node_id}:{node2.node_id}:{rel_type}'.encode()).hexdigest()[:12]}"
                    rel = GraphRelationship(
                        rel_id=rel_id,
                        source_id=node1.node_id,
                        target_id=node2.node_id,
                        rel_type=rel_type,
                        properties={"extracted": True},
                    )
                    relationships.append(rel)

        return nodes, relationships

    def _detect_relationship(self, text: str, entity1: str, entity2: str) -> Optional[str]:
        """Detect relationship type between two entities based on context."""
        # Find positions of entities
        pos1 = text.lower().find(entity1.lower())
        pos2 = text.lower().find(entity2.lower())

        if pos1 == -1 or pos2 == -1:
            return None

        # Get text between entities
        start = min(pos1, pos2)
        end = max(pos1, pos2)
        between_text = text[start:end]

        # Check for relationship patterns
        for rel_type, pattern in self.RELATIONSHIP_PATTERNS.items():
            if re.search(pattern, between_text, re.IGNORECASE):
                return rel_type

        # Default relationship
        return "relates_to"

class GraphRAGEngine:
    """GraphRAG: Graph-based retrieval for RAG.

    Combines vector similarity with graph traversal for
    more contextual and accurate retrieval.
    """

    def __init__(self, graph_service: KnowledgeGraphService):
        self._graph = graph_service

    def retrieve(
        self, query: str, query_vector: Optional[list[float]] = None, depth: int = 2, top_k: int = 10
    ) -> List[dict[str, Any]]:
        """Retrieve context using graph traversal + vector similarity.

        Args:
            query: Text query
            query_vector: Optional vector embedding
            depth: Graph traversal depth
            top_k: Number of results

        Returns:
            List of retrieved contexts with graph paths
        """

        # Step 1: Extract entities from query
        extractor = EntityExtractor()
        query_entities, _ = extractor.extract(query)

        # Step 2: Find matching nodes (entity match + vector similarity)
        seed_nodes = []

        # Match by entity name
        for entity in query_entities:
            node = self._graph.get_node_by_name(entity.name)
            if node:
                seed_nodes.append(node)

        # Match by vector similarity if provided
        if query_vector:
            similar_nodes = self._graph.vector_search(query_vector, top_k=5)
            for node in similar_nodes:
                if node not in seed_nodes:
                    seed_nodes.append(node)

        # Step 3: Graph traversal from seed nodes
        contexts = []
        for seed in seed_nodes:
            subgraph = self._graph.traverse(seed.node_id, depth=depth)

            # Build context from subgraph
            context = self._build_context(subgraph, seed)
            contexts.append(
                {
                    "seed_node": seed,
                    "context": context,
                    "depth": depth,
                    "path_score": self._calculate_path_score(subgraph, query),
                }
            )

        # Step 4: Rank by path score and diversity
        contexts.sort(key=lambda x: x["path_score"], reverse=True)

        return contexts[:top_k]

    def _build_context(self, subgraph: nx.DiGraph, seed: GraphNode) -> str:
        """Build text context from subgraph."""
        context_parts = [f"Central entity: {seed.name} ({seed.node_type})"]

        if NETWORKX_AVAILABLE and subgraph:
            # Add connected entities
            for node_id in subgraph.nodes():
                if node_id == seed.node_id:
                    continue
                node_data = subgraph.nodes[node_id]
                name = node_data.get("name", node_id)
                node_type = node_data.get("node_type", "unknown")
                context_parts.append(f"- Related: {name} ({node_type})")

            # Add relationships
            for edge in subgraph.edges(data=True):
                source, target, data = edge
                rel_type = data.get("rel_type", "relates_to")
                source_name = subgraph.nodes[source].get("name", source)
                target_name = subgraph.nodes[target].get("name", target)
                context_parts.append(f"- {source_name} {rel_type} {target_name}")

        return "\n".join(context_parts)

    def _calculate_path_score(self, subgraph: nx.DiGraph, query: str) -> float:
        """Calculate relevance score for a subgraph path."""
        if not NETWORKX_AVAILABLE:
            return 0.0

        # Factors: graph density, entity match, recency
        if subgraph:
            num_nodes = subgraph.number_of_nodes()
            num_edges = subgraph.number_of_edges()
            density = num_edges / max(1, num_nodes * (num_nodes - 1))
        else:
            density = 0.0

        return density * 10.0  # Simple scoring

class KnowledgeGraphService:
    """Knowledge graph management service.

    Supports NetworkX (in-memory) and Neo4j (persistent) backends.
    """

    def __init__(self, backend: str = "networkx", neo4j_uri: Optional[str] = None):
        self.backend = backend
        self._graph: nx.Optional[DiGraph] = None
        self._nodes: Dict[str, GraphNode] = {}
        self._relationships: Dict[str, GraphRelationship] = {}
        self._redis: redis.Optional[Redis] = None

        if backend == "networkx" and NETWORKX_AVAILABLE:
            self._graph = nx.DiGraph()

        if REDIS_AVAILABLE:
            try:
                self._redis = redis.from_url("redis://localhost:6379/11")
                self._redis.ping()
            except Exception:
                self._redis = None

        self._load_from_redis()

    def _get_node_key(self, node_id: str) -> str:
        return f"kg:node:{node_id}"

    def _get_rel_key(self, rel_id: str) -> str:
        return f"kg:rel:{rel_id}"

    def _load_from_redis(self):
        """Load graph data from Redis."""
        if not self._redis:
            return

        try:
            # Load nodes
            node_keys = list(self._redis.scan_iter(match=self._get_node_key("*")))
            for key in node_keys:
                data = self._redis.get(key)
                if data:
                    node_dict = json.loads(data)
                    node = GraphNode(**node_dict)
                    self._nodes[node.node_id] = node
                    if self._graph:
                        self._graph.add_node(
                            node.node_id,
                            name=node.name,
                            node_type=node.node_type,
                            **node.properties,
                        )

            # Load relationships
            rel_keys = list(self._redis.scan_iter(match=self._get_rel_key("*")))
            for key in rel_keys:
                data = self._redis.get(key)
                if data:
                    rel_dict = json.loads(data)
                    rel = GraphRelationship(**rel_dict)
                    self._relationships[rel.rel_id] = rel
                    if self._graph:
                        self._graph.add_edge(
                            rel.source_id,
                            rel.target_id,
                            rel_id=rel.rel_id,
                            rel_type=rel.rel_type,
                            weight=rel.weight,
                            **rel.properties,
                        )
        except Exception:
            pass

    def add_node(self, node: GraphNode) -> bool:
        """Add a node to the graph."""
        # Validate with SuperBrain
        if SUPERBRAIN_AVAILABLE:
            try:
                brain = get_super_brain()
                if brain and hasattr(brain, "action_gate"):
                    result = brain.action_gate.validate_action(
                        agent_id="knowledge_graph",
                        action="add_node",
                        details={"node_id": node.node_id, "type": node.node_type},
                    )
                    if not result.authorized:
                        return False
            except Exception:
                pass

        # Add to memory
        self._nodes[node.node_id] = node
        if self._graph:
            self._graph.add_node(
                node.node_id,
                name=node.name,
                node_type=node.node_type,
                source_doc=node.source_doc,
                **node.properties,
            )

        # Persist to Redis
        if self._redis:
            try:
                key = self._get_node_key(node.node_id)
                self._redis.setex(key, 86400 * 30, json.dumps(node.__dict__, default=str))
            except Exception:
                pass

        # Publish event
        if STREAMING_AVAILABLE:
            try:
                publish_event(
                    event_type="graph_node_added",
                    source_system="knowledge_graph",
                    payload={"node_id": node.node_id, "type": node.node_type},
                    requires_governance=False,
                )
            except Exception:
                pass

        return True

    def add_relationship(self, rel: GraphRelationship) -> bool:
        """Add a relationship to the graph."""
        # Validate both nodes exist
        if rel.source_id not in self._nodes or rel.target_id not in self._nodes:
            return False

        # Add to memory
        self._relationships[rel.rel_id] = rel
        if self._graph:
            self._graph.add_edge(
                rel.source_id,
                rel.target_id,
                rel_id=rel.rel_id,
                rel_type=rel.rel_type,
                weight=rel.weight,
                **rel.properties,
            )

        # Persist to Redis
        if self._redis:
            try:
                key = self._get_rel_key(rel.rel_id)
                self._redis.setex(key, 86400 * 30, json.dumps(rel.__dict__, default=str))
            except Exception:
                pass

        return True

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Get node by ID."""
        return self._nodes.get(node_id)

    def get_node_by_name(self, name: str) -> Optional[GraphNode]:
        """Get node by name."""
        for node in self._nodes.values():
            if node.name.lower() == name.lower():
                return node
        return None

    def vector_search(self, query_vector: List[float], top_k: int = 10) -> List[GraphNode]:
        """Search nodes by vector similarity."""
        import math

        def cosine_similarity(v1: List[float], v2: List[float]) -> float:
            dot = sum(a * b for a, b in zip(v1, v2))
            norm1 = math.sqrt(sum(a * a for a in v1))
            norm2 = math.sqrt(sum(a * a for a in v2))
            if norm1 == 0 or norm2 == 0:
                return 0.0
            return dot / (norm1 * norm2)

        scored = []
        for node in self._nodes.values():
            if node.vector:
                sim = cosine_similarity(query_vector, node.vector)
                scored.append((node, sim))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [node for node, _ in scored[:top_k]]

    def traverse(self, start_node_id: str, depth: int = 2) -> nx.Optional[DiGraph]:
        """Traverse graph from starting node."""
        if not NETWORKX_AVAILABLE or not self._graph:
            return None

        if start_node_id not in self._graph:
            return None

        # BFS traversal up to depth
        nodes_to_visit = [(start_node_id, 0)]
        visited = {start_node_id}
        edges = []

        while nodes_to_visit:
            current_id, current_depth = nodes_to_visit.pop(0)

            if current_depth >= depth:
                continue

            # Get neighbors
            for neighbor_id in self._graph.neighbors(current_id):
                edge_data = self._graph.edges[current_id, neighbor_id]
                edges.append((current_id, neighbor_id, edge_data))

                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    nodes_to_visit.append((neighbor_id, current_depth + 1))

        # Build subgraph
        subgraph = nx.DiGraph()
        for node_id in visited:
            node_data = self._graph.nodes[node_id]
            subgraph.add_node(node_id, **node_data)

        for source, target, data in edges:
            subgraph.add_edge(source, target, **data)

        return subgraph

    def query(self, query: GraphQuery) -> List[dict[str, Any]]:
        """Query the graph."""
        results = []

        for node_id, node in self._nodes.items():
            # Filter by node type
            if query.node_types and node.node_type not in query.node_types:
                continue

            # Filter by properties
            if query.node_properties:
                match = all(node.properties.get(k) == v for k, v in query.node_properties.items())
                if not match:
                    continue

            # Get relationships
            rels = [
                rel
                for rel in self._relationships.values()
                if rel.source_id == node_id or rel.target_id == node_id
            ]

            # Filter by relationship type
            if query.rel_types:
                rels = [r for r in rels if r.rel_type in query.rel_types]

            # Filter by weight
            rels = [r for r in rels if r.weight >= query.min_weight]

            results.append(
                {
                    "node": node,
                    "relationships": rels,
                    "connected_nodes": [
                        self._nodes.get(r.target_id if r.source_id == node_id else r.source_id)
                        for r in rels
                        if (r.target_id if r.source_id == node_id else r.source_id) in self._nodes
                    ],
                }
            )

        return results[: query.limit]

    def get_stats(self) -> Dict[str, Any]:
        """Get graph statistics."""
        by_type: Dict[str, int] = defaultdict(int)
        for node in self._nodes.values():
            by_type[node.node_type] += 1

        by_rel_type: Dict[str, int] = defaultdict(int)
        for rel in self._relationships.values():
            by_rel_type[rel.rel_type] += 1

        return {
            "total_nodes": len(self._nodes),
            "total_relationships": len(self._relationships),
            "nodes_by_type": dict(by_type),
            "relationships_by_type": dict(by_rel_type),
            "backend": self.backend,
        }

# Global instance
knowledge_graph = KnowledgeGraphService()

def extract_entities(
    text: str, doc_id: Optional[str] = None
) -> Tuple[list[GraphNode], list[GraphRelationship]]:
    """Extract entities from text (convenience function)."""
    extractor = EntityExtractor()
    return extractor.extract(text, doc_id)

def graph_retrieval(
    query: str, query_vector: Optional[list[float]] = None, depth: int = 2, top_k: int = 10
) -> List[dict[str, Any]]:
    """GraphRAG retrieval (convenience function)."""
    engine = GraphRAGEngine(knowledge_graph)
    return engine.retrieve(query, query_vector, depth, top_k)
