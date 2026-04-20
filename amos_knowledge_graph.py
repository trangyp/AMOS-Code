"""AMOS Knowledge Graph - Semantic Mathematical Knowledge Network (Phase 18).

Graph-based knowledge representation connecting 160+ equations across 36 domains
with semantic relationships, embeddings, and reasoning capabilities.

Architecture:
    1. Knowledge Graph Engine - Store entities and relationships
    2. Embedding Index - Semantic similarity search
    3. Relationship Discovery - Automated relation inference
    4. Query Interface - SPARQL-like semantic queries
    5. Graph Reasoning - Path finding and inference

Capabilities:
    - Graph storage of equations, concepts, domains
    - Semantic similarity search via embeddings
    - Relationship types: implements, related_to, belongs_to, generalizes
    - Automated relationship discovery
    - Knowledge graph queries and traversal
    - Concept path finding between equations

2024-2025 State of the Art:
    - Knowledge Graphs meet Multi-Modal (AAAI 2025)
    - GraphRAG - Community detection paradigm
    - Ontology-Driven KG Construction (Springer 2024)
    - Foundation models for KG reasoning (EMNLP 2025)

Usage:
    kg = AMOSKnowledgeGraph()

    # Add equation to graph
    kg.add_equation("sigmoid", domain="ML_AI", formula="σ(x)=1/(1+e^-x)")

    # Find related equations
    related = kg.find_related("sigmoid", relationship="similar_to")

    # Semantic search
    results = kg.semantic_search("activation function", top_k=5)

    # Path finding
    path = kg.find_path("entropy", "cross_entropy")

Author: AMOS Knowledge Team
Version: 18.0.0
"""

import json
import math
from dataclasses import dataclass, field
from datetime import UTC, datetime, timezone
from enum import Enum
from typing import Any, Optional

UTC = UTC
from collections import defaultdict, deque

try:
    from amos_superbrain_equation_bridge import AMOSSuperBrainBridge, Domain

    SUPERBRAIN_AVAILABLE = True
except ImportError:
    SUPERBRAIN_AVAILABLE = False


class RelationshipType(Enum):
    """Types of relationships in knowledge graph."""

    IMPLEMENTS = "implements"  # Equation implements concept
    RELATED_TO = "related_to"  # General relationship
    BELONGS_TO = "belongs_to"  # Domain membership
    GENERALIZES = "generalizes"  # Generalization hierarchy
    SPECIALIZES = "specializes"  # Inverse of generalizes
    DEPENDS_ON = "depends_on"  # Dependency
    SIMILAR_TO = "similar_to"  # Similarity
    ISOMORPHIC_TO = "isomorphic_to"  # Structural equivalence
    PROVES = "proves"  # Theorem proof relationship
    APPLIES_TO = "applies_to"  # Application domain


@dataclass
class KnowledgeNode:
    """Node in knowledge graph."""

    node_id: str
    node_type: str  # equation, concept, domain, pattern
    name: str
    description: str
    properties: dict[str, Any] = field(default_factory=dict)
    embedding: list[float] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class KnowledgeEdge:
    """Edge/relationship in knowledge graph."""

    edge_id: str
    source: str
    target: str
    relationship: RelationshipType
    weight: float
    properties: dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0


@dataclass
class SemanticPath:
    """Path between two nodes in graph."""

    start: str
    end: str
    nodes: list[str]
    edges: list[KnowledgeEdge]
    total_weight: float
    path_length: int


@dataclass
class SearchResult:
    """Semantic search result."""

    node: KnowledgeNode
    score: float
    match_type: str  # exact, semantic, related
    path_from_query: list[str]


class EmbeddingEngine:
    """Simple embedding generation for semantic similarity."""

    def __init__(self, dimension: int = 128):
        self.dimension = dimension
        self.vocab: dict[str, int] = {}
        self.vocab_size = 0

    def _tokenize(self, text: str) -> list[str]:
        """Simple tokenization."""
        return text.lower().replace("(", " ").replace(")", " ").replace(",", " ").split()

    def _build_vocab(self, texts: list[str]) -> None:
        """Build vocabulary from corpus."""
        for text in texts:
            for token in self._tokenize(text):
                if token not in self.vocab:
                    self.vocab[token] = self.vocab_size
                    self.vocab_size += 1

    def generate_embedding(self, text: str) -> list[float]:
        """Generate simple bag-of-words style embedding."""
        tokens = self._tokenize(text)
        embedding = [0.0] * self.dimension

        # Simple hash-based embedding
        for i, token in enumerate(tokens):
            idx = hash(token) % self.dimension
            embedding[idx] += 1.0

        # Normalize
        norm = math.sqrt(sum(x * x for x in embedding))
        if norm > 0:
            embedding = [x / norm for x in embedding]

        return embedding

    def cosine_similarity(self, emb1: list[float], emb2: list[float]) -> float:
        """Calculate cosine similarity between embeddings."""
        dot_product = sum(a * b for a, b in zip(emb1, emb2))
        norm1 = math.sqrt(sum(a * a for a in emb1))
        norm2 = math.sqrt(sum(b * b for b in emb2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)


class AMOSKnowledgeGraph:
    """
    Main knowledge graph for AMOS SuperBrain equation system.

    Manages entities (equations, concepts, domains) and their relationships,
    providing semantic search, path finding, and knowledge reasoning.
    """

    def __init__(self):
        self.nodes: dict[str, KnowledgeNode] = {}
        self.edges: dict[str, KnowledgeEdge] = {}
        self.adjacency: dict[str, list[str]] = defaultdict(list)
        self.embedding_engine = EmbeddingEngine()
        self.superbrain = AMOSSuperBrainBridge() if SUPERBRAIN_AVAILABLE else None

        if self.superbrain:
            self._import_from_superbrain()

    def _import_from_superbrain(self) -> None:
        """Import equations from SuperBrain bridge."""
        try:
            for name, meta in self.superbrain.registry.metadata.items():
                self.add_equation(
                    equation_id=name,
                    name=name,
                    formula=meta.formula,
                    domain=meta.domain.value,
                    description=meta.description,
                    pattern=meta.pattern.value,
                    invariants=meta.invariants,
                )

                # Add domain relationship
                domain_id = f"domain:{meta.domain.value}"
                if domain_id not in self.nodes:
                    self.add_domain(
                        domain_id=domain_id,
                        name=meta.domain.value,
                        description=f"Domain: {meta.domain.value}",
                    )

                self.add_relationship(name, domain_id, RelationshipType.BELONGS_TO)
        except Exception as e:
            print(f"Warning: Could not import from SuperBrain: {e}")

    def add_equation(
        self,
        equation_id: str,
        name: str,
        formula: str,
        domain: str,
        description: str = "",
        pattern: str = "",
        invariants: list[str] = None,
        properties: dict[str, Any] = None,
    ) -> KnowledgeNode:
        """Add equation node to graph."""
        # Generate embedding from formula and description
        text = f"{name} {formula} {description}"
        embedding = self.embedding_engine.generate_embedding(text)

        node = KnowledgeNode(
            node_id=equation_id,
            node_type="equation",
            name=name,
            description=description,
            properties={
                "formula": formula,
                "domain": domain,
                "pattern": pattern,
                "invariants": invariants or [],
                **(properties or {}),
            },
            embedding=embedding,
        )

        self.nodes[equation_id] = node
        return node

    def add_concept(
        self, concept_id: str, name: str, description: str, properties: dict[str, Any] = None
    ) -> KnowledgeNode:
        """Add concept node to graph."""
        embedding = self.embedding_engine.generate_embedding(f"{name} {description}")

        node = KnowledgeNode(
            node_id=concept_id,
            node_type="concept",
            name=name,
            description=description,
            properties=properties or {},
            embedding=embedding,
        )

        self.nodes[concept_id] = node
        return node

    def add_domain(self, domain_id: str, name: str, description: str) -> KnowledgeNode:
        """Add domain node to graph."""
        node = KnowledgeNode(
            node_id=domain_id, node_type="domain", name=name, description=description
        )

        self.nodes[domain_id] = node
        return node

    def add_relationship(
        self,
        source: str,
        target: str,
        relationship: RelationshipType,
        weight: float = 1.0,
        confidence: float = 1.0,
        properties: dict[str, Any] = None,
    ) -> KnowledgeEdge:
        """Add relationship between nodes."""
        edge_id = f"{source}_{relationship.value}_{target}"

        edge = KnowledgeEdge(
            edge_id=edge_id,
            source=source,
            target=target,
            relationship=relationship,
            weight=weight,
            confidence=confidence,
            properties=properties or {},
        )

        self.edges[edge_id] = edge
        self.adjacency[source].append(target)

        return edge

    def semantic_search(
        self, query: str, top_k: int = 5, node_type: str = None
    ) -> list[SearchResult]:
        """
        Semantic search over knowledge graph.

        Args:
            query: Search query
            top_k: Number of results
            node_type: Filter by node type

        Returns:
            List of search results with similarity scores
        """
        query_embedding = self.embedding_engine.generate_embedding(query)

        results = []
        for node_id, node in self.nodes.items():
            if node_type and node.node_type != node_type:
                continue

            if not node.embedding:
                continue

            similarity = self.embedding_engine.cosine_similarity(query_embedding, node.embedding)

            if similarity > 0.1:  # Threshold
                results.append(
                    SearchResult(
                        node=node, score=similarity, match_type="semantic", path_from_query=[]
                    )
                )

        # Sort by score
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]

    def find_related(
        self, node_id: str, relationship: Optional[RelationshipType] = None, depth: int = 1
    ) -> list[tuple[KnowledgeNode, KnowledgeEdge]]:
        """
        Find related nodes.

        Args:
            node_id: Starting node
            relationship: Filter by relationship type
            depth: Search depth

        Returns:
            List of (node, edge) tuples
        """
        if node_id not in self.nodes:
            return []

        results = []
        visited = {node_id}
        queue = deque([(node_id, 0)])

        while queue:
            current_id, current_depth = queue.popleft()

            if current_depth >= depth:
                continue

            for edge in self.edges.values():
                if edge.source == current_id:
                    if relationship and edge.relationship != relationship:
                        continue

                    if edge.target not in visited:
                        visited.add(edge.target)
                        if edge.target in self.nodes:
                            results.append((self.nodes[edge.target], edge))
                            queue.append((edge.target, current_depth + 1))

        return results

    def find_path(self, start: str, end: str, max_depth: int = 5) -> Optional[SemanticPath]:
        """
        Find path between two nodes using BFS.

        Args:
            start: Starting node ID
            end: Target node ID
            max_depth: Maximum search depth

        Returns:
            Semantic path or None if not found
        """
        if start not in self.nodes or end not in self.nodes:
            return None

        if start == end:
            return SemanticPath(
                start=start, end=end, nodes=[start], edges=[], total_weight=0, path_length=0
            )

        # BFS
        queue = deque([(start, [start], [], 0.0)])
        visited = {start}

        while queue:
            current, path_nodes, path_edges, weight = queue.popleft()

            if len(path_nodes) > max_depth:
                continue

            for edge in self.edges.values():
                if edge.source == current:
                    if edge.target == end:
                        # Found path
                        return SemanticPath(
                            start=start,
                            end=end,
                            nodes=path_nodes + [end],
                            edges=path_edges + [edge],
                            total_weight=weight + edge.weight,
                            path_length=len(path_nodes),
                        )

                    if edge.target not in visited:
                        visited.add(edge.target)
                        queue.append(
                            (
                                edge.target,
                                path_nodes + [edge.target],
                                path_edges + [edge],
                                weight + edge.weight,
                            )
                        )

        return None

    def discover_relationships(self, threshold: float = 0.7) -> list[KnowledgeEdge]:
        """
        Auto-discover relationships based on semantic similarity.

        Args:
            threshold: Similarity threshold for creating edges

        Returns:
            List of discovered edges
        """
        discovered = []

        # Find similar equations within same domain
        for node1_id, node1 in self.nodes.items():
            if node1.node_type != "equation":
                continue

            for node2_id, node2 in self.nodes.items():
                if node2.node_type != "equation":
                    continue

                if node1_id >= node2_id:  # Avoid duplicates
                    continue

                # Check if same domain
                domain1 = node1.properties.get("domain", "")
                domain2 = node2.properties.get("domain", "")

                if domain1 == domain2:
                    similarity = self.embedding_engine.cosine_similarity(
                        node1.embedding, node2.embedding
                    )

                    if similarity > threshold:
                        edge = self.add_relationship(
                            node1_id,
                            node2_id,
                            RelationshipType.SIMILAR_TO,
                            weight=similarity,
                            confidence=similarity,
                        )
                        discovered.append(edge)

        return discovered

    def query(
        self, node_type: str = None, domain: str = None, pattern: str = None
    ) -> list[KnowledgeNode]:
        """
        Query knowledge graph with filters.

        Args:
            node_type: Filter by node type
            domain: Filter by domain
            pattern: Filter by pattern

        Returns:
            List of matching nodes
        """
        results = []

        for node in self.nodes.values():
            if node_type and node.node_type != node_type:
                continue

            if domain and node.properties.get("domain") != domain:
                continue

            if pattern and node.properties.get("pattern") != pattern:
                continue

            results.append(node)

        return results

    def get_stats(self) -> dict[str, Any]:
        """Get knowledge graph statistics."""
        node_types = defaultdict(int)
        for node in self.nodes.values():
            node_types[node.node_type] += 1

        rel_types = defaultdict(int)
        for edge in self.edges.values():
            rel_types[edge.relationship.value] += 1

        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "node_types": dict(node_types),
            "relationship_types": dict(rel_types),
            "avg_degree": len(self.edges) / max(len(self.nodes), 1),
            "domains": len(
                set(
                    n.properties.get("domain", "")
                    for n in self.nodes.values()
                    if n.properties.get("domain")
                )
            ),
        }

    def export_graph(self) -> dict[str, Any]:
        """Export graph as JSON-serializable structure."""
        return {
            "nodes": [
                {
                    "id": n.node_id,
                    "type": n.node_type,
                    "name": n.name,
                    "description": n.description,
                    "properties": n.properties,
                }
                for n in self.nodes.values()
            ],
            "edges": [
                {
                    "id": e.edge_id,
                    "source": e.source,
                    "target": e.target,
                    "relationship": e.relationship.value,
                    "weight": e.weight,
                    "confidence": e.confidence,
                }
                for e in self.edges.values()
            ],
            "metadata": {
                "exported_at": datetime.now(timezone.utc).isoformat(),
                "stats": self.get_stats(),
            },
        }


def main():
    """CLI for knowledge graph."""
    import argparse

    parser = argparse.ArgumentParser(
        description="AMOS Knowledge Graph - Semantic Mathematical Network"
    )
    parser.add_argument("--demo", action="store_true", help="Run demonstration")
    parser.add_argument("--search", help="Semantic search query")
    parser.add_argument("--stats", action="store_true", help="Show stats")
    parser.add_argument("--export", help="Export graph to file")

    args = parser.parse_args()

    kg = AMOSKnowledgeGraph()

    if args.demo:
        print("🕸️ AMOS Knowledge Graph Demo")
        print("=" * 50)

        # Add some example equations
        print("\n1. Adding equations to graph...")
        kg.add_equation(
            "sigmoid_demo",
            "sigmoid",
            "σ(x)=1/(1+e^-x)",
            "ML_AI",
            "Sigmoid activation function",
            "activation",
            ["output in (0,1)"],
        )

        kg.add_equation(
            "relu_demo",
            "relu",
            "max(0,x)",
            "ML_AI",
            "ReLU activation function",
            "activation",
            ["non-negative output"],
        )

        kg.add_equation(
            "entropy_demo",
            "entropy",
            "-Σp(x)log(p(x))",
            "INFORMATION_THEORY",
            "Information entropy",
            "uncertainty",
            ["non-negative"],
        )

        print(f"   Added {len(kg.nodes)} nodes")

        # Add relationships
        print("\n2. Adding relationships...")
        kg.add_relationship("sigmoid_demo", "relu_demo", RelationshipType.SIMILAR_TO, weight=0.8)
        kg.add_relationship("sigmoid_demo", "entropy_demo", RelationshipType.RELATED_TO, weight=0.3)

        print(f"   Added {len(kg.edges)} edges")

        # Semantic search
        print("\n3. Semantic search for 'activation function':")
        results = kg.semantic_search("activation function", top_k=3)
        for r in results:
            print(f"   - {r.node.name}: {r.score:.2f}")

        # Find related
        print("\n4. Finding related to 'sigmoid':")
        related = kg.find_related("sigmoid_demo", depth=1)
        for node, edge in related:
            print(f"   - {node.name} ({edge.relationship.value})")

        # Discover relationships
        print("\n5. Auto-discovering relationships...")
        discovered = kg.discover_relationships(threshold=0.5)
        print(f"   Discovered {len(discovered)} new relationships")

        # Stats
        print("\n6. Knowledge Graph Stats:")
        stats = kg.get_stats()
        for key, value in stats.items():
            print(f"   {key}: {value}")

        print("\n✅ Demo complete!")

    elif args.search:
        print(f"Searching for: {args.search}")
        results = kg.semantic_search(args.search, top_k=5)
        for r in results:
            print(f"  - {r.node.name} ({r.node.node_type}): {r.score:.2f}")

    elif args.stats:
        stats = kg.get_stats()
        print(json.dumps(stats, indent=2))

    elif args.export:
        graph_data = kg.export_graph()
        with open(args.export, "w") as f:
            json.dump(graph_data, f, indent=2)
        print(f"Exported to {args.export}")

    else:
        print("🕸️ AMOS Knowledge Graph v18.0.0")
        print(f"   SuperBrain Available: {SUPERBRAIN_AVAILABLE}")
        print("\nUsage:")
        print("   python amos_knowledge_graph.py --demo")
        print("   python amos_knowledge_graph.py --search 'activation function'")
        print("   python amos_knowledge_graph.py --stats")
        print("   python amos_knowledge_graph.py --export graph.json")


if __name__ == "__main__":
    main()
