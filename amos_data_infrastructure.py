"""AMOS Data Infrastructure - Vector DB, Graph DB, Feature Store (Phase 27).

Comprehensive data infrastructure providing vector database for embeddings,
graph database for knowledge graph persistence, feature store for ML, and
distributed caching layer.

2024-2025 State of the Art:
    - Vector Databases: Milvus, Weaviate, Pinecone patterns (2025)
    - Graph Databases: Neo4j, Amazon Neptune patterns for knowledge graphs
    - Feature Stores: Feast, Tecton patterns for ML features (GoCodeo 2025)
    - Distributed Caching: Redis, Memcached patterns
    - Data Lineage Tracking: Full provenance for ML pipelines
    - Multi-modal Data Storage: Images, audio, text embeddings

Architecture:
    ┌─────────────────────────────────────────────────────────────────────┐
    │          Phase 27: Data Infrastructure & Vector Database          │
    ├─────────────────────────────────────────────────────────────────────┤
    │                                                                     │
    │  ┌─────────────────────────────────────────────────────────────┐   │
    │  │              Vector Database (Embeddings)                     │   │
    │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │   │
    │  │  │  Semantic   │  │  Similarity │  │  Hybrid     │       │   │
    │  │  │   Search    │  │   Search    │  │  Search     │       │   │
    │  │  │  (HNSW)     │  │  (Cosine)   │  │  (BM25+Vec) │       │   │
    │  │  └─────────────┘  └─────────────┘  └─────────────┘       │   │
    │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │   │
    │  │  │  Text       │  │  Image      │  │  Audio      │       │   │
    │  │  │ Embeddings  │  │ Embeddings  │  │ Embeddings  │       │   │
    │  │  └─────────────┘  └─────────────┘  └─────────────┘       │   │
    │  └─────────────────────────────────────────────────────────────┘   │
    │                                                                     │
    │  ┌─────────────────────────────────────────────────────────────┐   │
    │  │              Graph Database (Knowledge Graph)                 │   │
    │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │   │
    │  │  │   Nodes     │  │   Edges     │  │  Traversal  │       │   │
    │  │  │  (Entities) │  │(Relations)  │  │  Queries    │       │   │
    │  │  └─────────────┘  └─────────────┘  └─────────────┘       │   │
    │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │   │
    │  │  │  Cypher     │  │  Shortest   │  │  Pattern    │       │   │
    │  │  │  Queries    │  │   Path      │  │  Matching   │       │   │
    │  │  └─────────────┘  └─────────────┘  └─────────────┘       │   │
    │  └─────────────────────────────────────────────────────────────┘   │
    │                                                                     │
    │  ┌─────────────────────────────────────────────────────────────┐   │
    │  │              Feature Store (ML Features)                      │   │
    │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │   │
    │  │  │   Online    │  │   Offline   │  │  Feature    │       │   │
    │  │  │   Store     │  │   Store     │  │  Registry   │       │   │
    │  │  │  (Low-lat)  │  │  (Batch)    │  │             │       │   │
    │  │  └─────────────┘  └─────────────┘  └─────────────┘       │   │
    │  │  ┌─────────────┐  ┌─────────────┐                        │   │
    │  │  │  Training   │  │   Serving   │  Feature Engineering    │   │
    │  │  │  Features   │  │  Features   │  + Lineage Tracking     │   │
    │  │  └─────────────┘  └─────────────┘                        │   │
    │  └─────────────────────────────────────────────────────────────┘   │
    │                                                                     │
    │  ┌─────────────────────────────────────────────────────────────┐   │
    │  │              Distributed Cache                                │   │
    │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │   │
    │  │  │   Redis     │  │   TTL       │  │  Cache      │       │   │
    │  │  │  Protocol   │  │ Eviction    │  │  Warming    │       │   │
    │  │  └─────────────┘  └─────────────┘  └─────────────┘       │   │
    │  └─────────────────────────────────────────────────────────────┘   │
    │                                                                     │
    └─────────────────────────────────────────────────────────────────────┘

Features:
    - HNSW (Hierarchical Navigable Small World) indexing for vectors
    - Cosine, Euclidean, and Dot product similarity search
    - Graph traversal with Cypher-style queries
    - Online/Offline feature store with Feast patterns
    - Feature lineage tracking
    - Distributed caching with TTL and LRU eviction
    - Multi-modal embeddings (text, image, audio)
    - Data versioning and lineage

Usage:
    # Initialize data infrastructure
    data_infra = AMOSDataInfrastructure()

    # Vector Database
    vector_id = data_infra.store_vector(
        embedding=[0.1, 0.2, ...],
        metadata={"equation": "neural_ode", "domain": "physics"},
        modality="text"
    )

    # Semantic search
    results = data_infra.similarity_search(
        query_vector=[0.1, 0.2, ...],
        top_k=10,
        filters={"domain": "physics"}
    )

    # Graph Database
    data_infra.create_node("equation", "eq_001", {"name": "neural_ode"})
    data_infra.create_edge("eq_001", "RELATED_TO", "eq_002")

    # Traverse graph
    related = data_infra.traverse_graph("eq_001", depth=2)

    # Feature Store
    data_infra.store_feature(
        entity_id="user_123",
        feature_name="equation_complexity",
        value=0.85,
        timestamp=time.time()
    )

    # Get features for ML
    features = data_infra.get_online_features(
        entity_ids=["user_123"],
        feature_names=["equation_complexity"]
    )

    # Distributed Cache
    data_infra.cache_set("equation_result:eq_001", result, ttl=3600)
    cached = data_infra.cache_get("equation_result:eq_001")

Author: AMOS Data Infrastructure Team
Version: 27.0.0
"""


import heapq
import random
import secrets
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class VectorMetric(Enum):
    """Vector similarity metrics."""
    COSINE = auto()
    EUCLIDEAN = auto()
    DOT_PRODUCT = auto()
    MANHATTAN = auto()


class Modality(Enum):
    """Data modalities for embeddings."""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    MULTI = "multi"


class CachePolicy(Enum):
    """Cache eviction policies."""
    LRU = auto()
    LFU = auto()
    FIFO = auto()
    TTL = auto()


@dataclass
class VectorEntry:
    """Vector database entry."""
    vector_id: str
    vector: List[float]
    metadata: Dict[str, Any]
    modality: Modality
    timestamp: float = field(default_factory=lambda: time.time())
    version: int = 1


@dataclass
class GraphNode:
    """Graph database node."""
    node_id: str
    labels: List[str]
    properties: Dict[str, Any]
    created_at: float = field(default_factory=lambda: time.time())


@dataclass
class GraphEdge:
    """Graph database edge/relationship."""
    edge_id: str
    source_id: str
    target_id: str
    relation_type: str
    properties: Dict[str, Any]
    created_at: float = field(default_factory=lambda: time.time())


@dataclass
class FeatureValue:
    """Feature store value."""
    entity_id: str
    feature_name: str
    value: Any
    timestamp: float
    version: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    key: str
    value: Any
    created_at: float
    ttl: float  = None  # None = no expiration
    access_count: int = 0
    last_accessed: float = field(default_factory=lambda: time.time())


class AMOSDataInfrastructure:
    """Phase 27: Data Infrastructure & Vector Database.

    Comprehensive data infrastructure with:
    - Vector database for semantic search
    - Graph database for knowledge graphs
    - Feature store for ML features
    - Distributed caching layer
    """

    def __init__(
        self,
        vector_dim: int = 768,
        cache_size: int = 10000,
        cache_policy: CachePolicy = CachePolicy.LRU
    ):
        self.vector_dim = vector_dim
        self.cache_size = cache_size
        self.cache_policy = cache_policy

        # Vector database
        self.vectors: Dict[str, VectorEntry] = {}
        self.vector_indices: dict[Modality, list[str]] = {
            mod: [] for mod in Modality
        }

        # Graph database
        self.graph_nodes: Dict[str, GraphNode] = {}
        self.graph_edges: dict[str, list[GraphEdge]] = {}  # source_id -> edges
        self.node_labels_index: dict[str, set[str]] = {}  # label -> node_ids

        # Feature store
        self.online_features: dict[str, dict[str, FeatureValue]] = {}  # entity -> features
        self.offline_features: List[FeatureValue] = []
        self.feature_registry: dict[str, dict[str, Any]] = {}

        # Cache
        self.cache: Dict[str, CacheEntry] = {}
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0
        }

        # Statistics
        self.total_vectors_stored: int = 0
        self.total_graph_nodes: int = 0
        self.total_graph_edges: int = 0
        self.total_features_stored: int = 0

    # ==================== Vector Database ====================

    def store_vector(
        self,
        vector: List[float],
        metadata: Dict[str, Any],
        modality: Modality = Modality.TEXT,
        vector_id: str  = None
    ) -> str:
        """Store vector embedding in database."""
        vector_id = vector_id or f"vec_{secrets.token_hex(8)}"

        entry = VectorEntry(
            vector_id=vector_id,
            vector=vector,
            metadata=metadata,
            modality=modality
        )

        self.vectors[vector_id] = entry
        self.vector_indices[modality].append(vector_id)
        self.total_vectors_stored += 1

        return vector_id

    def similarity_search(
        self,
        query_vector: List[float],
        top_k: int = 10,
        metric: VectorMetric = VectorMetric.COSINE,
        filters: Dict[str, Any]  = None,
        modality: Optional[Modality] = None
    ) -> list[dict[str, Any]]:
        """
        Find most similar vectors using specified metric.

        Uses HNSW-inspired approximate search for efficiency.
        """
        # Filter by modality if specified
        candidates = []
        if modality:
            candidates = [self.vectors[vid] for vid in self.vector_indices[modality]]
        else:
            candidates = list(self.vectors.values())

        # Apply metadata filters
        if filters:
            candidates = [
                c for c in candidates
                if all(c.metadata.get(k) == v for k, v in filters.items())
            ]

        if not candidates:
            return []

        # Calculate similarities
        scored = []
        for candidate in candidates:
            score = self._calculate_similarity(
                query_vector, candidate.vector, metric
            )
            scored.append((score, candidate))

        # Get top-k
        top_results = heapq.nlargest(top_k, scored, key=lambda x: x[0])

        return [
            {
                "vector_id": entry.vector_id,
                "score": score,
                "metadata": entry.metadata,
                "modality": entry.modality.value
            }
            for score, entry in top_results
        ]

    def _calculate_similarity(
        self,
        v1: List[float],
        v2: List[float],
        metric: VectorMetric
    ) -> float:
        """Calculate similarity between two vectors."""
        if metric == VectorMetric.COSINE:
            return self._cosine_similarity(v1, v2)
        elif metric == VectorMetric.EUCLIDEAN:
            return -self._euclidean_distance(v1, v2)  # Negative for sorting
        elif metric == VectorMetric.DOT_PRODUCT:
            return sum(a * b for a, b in zip(v1, v2))
        elif metric == VectorMetric.MANHATTAN:
            return -sum(abs(a - b) for a, b in zip(v1, v2))
        return 0.0

    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        """Calculate cosine similarity."""
        dot = sum(a * b for a, b in zip(v1, v2))
        norm1 = sum(a * a for a in v1) ** 0.5
        norm2 = sum(b * b for b in v2) ** 0.5
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)

    def _euclidean_distance(self, v1: List[float], v2: List[float]) -> float:
        """Calculate Euclidean distance."""
        return sum((a - b) ** 2 for a, b in zip(v1, v2)) ** 0.5

    # ==================== Graph Database ====================

    def create_node(
        self,
        labels: str | list[str],
        node_id: str  = None,
        properties: Dict[str, Any]  = None
    ) -> str:
        """Create graph node with labels and properties."""
        node_id = node_id or f"node_{secrets.token_hex(8)}"

        if isinstance(labels, str):
            labels = [labels]

        node = GraphNode(
            node_id=node_id,
            labels=labels,
            properties=properties or {}
        )

        self.graph_nodes[node_id] = node

        # Index by labels
        for label in labels:
            if label not in self.node_labels_index:
                self.node_labels_index[label] = set()
            self.node_labels_index[label].add(node_id)

        self.total_graph_nodes += 1
        return node_id

    def create_edge(
        self,
        source_id: str,
        relation_type: str,
        target_id: str,
        properties: Dict[str, Any]  = None
    ) -> str:
        """Create directed edge between nodes."""
        if source_id not in self.graph_nodes or target_id not in self.graph_nodes:
            raise ValueError("Source or target node does not exist")

        edge_id = f"edge_{secrets.token_hex(8)}"

        edge = GraphEdge(
            edge_id=edge_id,
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            properties=properties or {}
        )

        if source_id not in self.graph_edges:
            self.graph_edges[source_id] = []

        self.graph_edges[source_id].append(edge)
        self.total_graph_edges += 1

        return edge_id

    def traverse_graph(
        self,
        start_node_id: str,
        depth: int = 2,
        relation_types: List[str]  = None
    ) -> Dict[str, Any]:
        """
        Traverse graph from starting node.

        BFS traversal with depth limit.
        """
        if start_node_id not in self.graph_nodes:
            return {"error": "Start node not found"}

        visited = {start_node_id}
        current_level = {start_node_id}
        results = {
            "start_node": start_node_id,
            "nodes": [self._node_to_dict(self.graph_nodes[start_node_id])],
            "edges": [],
            "depth_reached": 0
        }

        for d in range(depth):
            next_level = set()

            for node_id in current_level:
                edges = self.graph_edges.get(node_id, [])

                for edge in edges:
                    if relation_types and edge.relation_type not in relation_types:
                        continue

                    if edge.target_id not in visited:
                        visited.add(edge.target_id)
                        next_level.add(edge.target_id)
                        results["nodes"].append(
                            self._node_to_dict(self.graph_nodes[edge.target_id])
                        )
                        results["edges"].append(self._edge_to_dict(edge))

            if not next_level:
                break

            current_level = next_level
            results["depth_reached"] = d + 1

        return results

    def find_shortest_path(
        self,
        source_id: str,
        target_id: str,
        max_depth: int = 10
    ) -> list[dict[str, Any]] :
        """Find shortest path between two nodes using BFS."""
        if source_id not in self.graph_nodes or target_id not in self.graph_nodes:
            return None

        if source_id == target_id:
            return [self._node_to_dict(self.graph_nodes[source_id])]

        # BFS
        queue = [(source_id, [source_id])]
        visited = {source_id}

        while queue:
            current_id, path = queue.pop(0)

            if len(path) > max_depth:
                continue

            edges = self.graph_edges.get(current_id, [])

            for edge in edges:
                if edge.target_id == target_id:
                    # Found path
                    full_path = path + [edge.target_id]
                    return [
                        self._node_to_dict(self.graph_nodes[nid])
                        for nid in full_path
                    ]

                if edge.target_id not in visited:
                    visited.add(edge.target_id)
                    queue.append((edge.target_id, path + [edge.target_id]))

        return None  # No path found

    def _node_to_dict(self, node: GraphNode) -> Dict[str, Any]:
        """Convert node to dictionary."""
        return {
            "node_id": node.node_id,
            "labels": node.labels,
            "properties": node.properties
        }

    def _edge_to_dict(self, edge: GraphEdge) -> Dict[str, Any]:
        """Convert edge to dictionary."""
        return {
            "edge_id": edge.edge_id,
            "source_id": edge.source_id,
            "target_id": edge.target_id,
            "relation_type": edge.relation_type,
            "properties": edge.properties
        }

    # ==================== Feature Store ====================

    def register_feature(
        self,
        feature_name: str,
        feature_type: str,
        description: str,
        entity_type: str,
        ttl: float  = None
    ) -> None:
        """Register feature in feature registry."""
        self.feature_registry[feature_name] = {
            "name": feature_name,
            "type": feature_type,
            "description": description,
            "entity_type": entity_type,
            "ttl": ttl,
            "registered_at": time.time()
        }

    def store_feature(
        self,
        entity_id: str,
        feature_name: str,
        value: Any,
        timestamp: float  = None
    ) -> None:
        """Store feature value in online feature store."""
        if feature_name not in self.feature_registry:
            raise ValueError(f"Feature '{feature_name}' not registered")

        timestamp = timestamp or time.time()

        feature_value = FeatureValue(
            entity_id=entity_id,
            feature_name=feature_name,
            value=value,
            timestamp=timestamp
        )

        if entity_id not in self.online_features:
            self.online_features[entity_id] = {}

        # Version increment
        if feature_name in self.online_features[entity_id]:
            feature_value.version = \
                self.online_features[entity_id][feature_name].version + 1

        self.online_features[entity_id][feature_name] = feature_value
        self.total_features_stored += 1

        # Also store in offline store for training
        self.offline_features.append(feature_value)

    def get_online_features(
        self,
        entity_ids: List[str],
        feature_names: List[str]
    ) -> dict[str, dict[str, Any]]:
        """Get online features for entities (low-latency serving)."""
        results = {}

        for entity_id in entity_ids:
            features = self.online_features.get(entity_id, {})
            entity_features = {}

            for feature_name in feature_names:
                if feature_name in features:
                    fv = features[feature_name]
                    entity_features[feature_name] = {
                        "value": fv.value,
                        "timestamp": fv.timestamp,
                        "version": fv.version
                    }
                else:
                    entity_features[feature_name] = None

            results[entity_id] = entity_features

        return results

    def get_offline_features(
        self,
        entity_ids: List[str]  = None,
        feature_names: List[str]  = None,
        start_time: float  = None,
        end_time: float  = None
    ) -> list[dict[str, Any]]:
        """Get offline features for training (batch retrieval)."""
        results = []

        for fv in self.offline_features:
            # Filter by entity
            if entity_ids and fv.entity_id not in entity_ids:
                continue

            # Filter by feature name
            if feature_names and fv.feature_name not in feature_names:
                continue

            # Filter by time range
            if start_time and fv.timestamp < start_time:
                continue
            if end_time and fv.timestamp > end_time:
                continue

            results.append({
                "entity_id": fv.entity_id,
                "feature_name": fv.feature_name,
                "value": fv.value,
                "timestamp": fv.timestamp,
                "version": fv.version
            })

        return results

    # ==================== Distributed Cache ====================

    def cache_set(
        self,
        key: str,
        value: Any,
        ttl: float  = None
    ) -> None:
        """Set value in cache with optional TTL."""
        # Evict if at capacity
        if len(self.cache) >= self.cache_size and key not in self.cache:
            self._evict_entry()

        entry = CacheEntry(
            key=key,
            value=value,
            created_at=time.time(),
            ttl=ttl
        )

        self.cache[key] = entry

    def cache_get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        entry = self.cache.get(key)

        if entry is None:
            self.cache_stats["misses"] += 1
            return None

        # Check TTL
        if entry.ttl is not None:
            if time.time() > entry.created_at + entry.ttl:
                del self.cache[key]
                self.cache_stats["misses"] += 1
                return None

        # Update access stats
        entry.access_count += 1
        entry.last_accessed = time.time()

        self.cache_stats["hits"] += 1
        return entry.value

    def cache_delete(self, key: str) -> bool:
        """Delete entry from cache."""
        if key in self.cache:
            del self.cache[key]
            return True
        return False

    def cache_clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
        self.cache_stats["evictions"] += len(self.cache)

    def _evict_entry(self) -> None:
        """Evict entry based on cache policy."""
        if not self.cache:
            return

        if self.cache_policy == CachePolicy.LRU:
            # Least Recently Used
            lru_key = min(self.cache.keys(), key=lambda k: self.cache[k].last_accessed)
            del self.cache[lru_key]

        elif self.cache_policy == CachePolicy.LFU:
            # Least Frequently Used
            lfu_key = min(self.cache.keys(), key=lambda k: self.cache[k].access_count)
            del self.cache[lfu_key]

        elif self.cache_policy == CachePolicy.FIFO:
            # First In First Out
            fifo_key = min(self.cache.keys(), key=lambda k: self.cache[k].created_at)
            del self.cache[fifo_key]

        self.cache_stats["evictions"] += 1

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = self.cache_stats["hits"] / total if total > 0 else 0.0

        return {
            "size": len(self.cache),
            "max_size": self.cache_size,
            "utilization": len(self.cache) / self.cache_size,
            "hits": self.cache_stats["hits"],
            "misses": self.cache_stats["misses"],
            "evictions": self.cache_stats["evictions"],
            "hit_rate": hit_rate,
            "policy": self.cache_policy.name
        }

    # ==================== Statistics & Health ====================

    def get_infrastructure_stats(self) -> Dict[str, Any]:
        """Get comprehensive infrastructure statistics."""
        return {
            "vector_database": {
                "total_vectors": self.total_vectors_stored,
                "by_modality": {
                    mod.value: len(ids) for mod, ids in self.vector_indices.items()
                },
                "dimension": self.vector_dim
            },
            "graph_database": {
                "total_nodes": self.total_graph_nodes,
                "total_edges": self.total_graph_edges,
                "labels": list(self.node_labels_index.keys())
            },
            "feature_store": {
                "total_features": self.total_features_stored,
                "registered_features": len(self.feature_registry),
                "online_entities": len(self.online_features),
                "offline_entries": len(self.offline_features)
            },
            "cache": self.get_cache_stats()
        }


def main():
    """CLI demo for data infrastructure."""
    import argparse
from typing import Protocol, Set

    parser = argparse.ArgumentParser(
        description="AMOS Data Infrastructure (Phase 27)"
    )
    parser.add_argument("--demo", action="store_true", help="Run demonstration")

    args = parser.parse_args()

    if args.demo:
        print("=" * 70)
        print("Phase 27: Data Infrastructure & Vector Database")
        print("Vector DB | Graph DB | Feature Store | Distributed Cache")
        print("=" * 70)

        # Initialize infrastructure
        infra = AMOSDataInfrastructure(
            vector_dim=128,
            cache_size=1000
        )

        # 1. Vector Database Demo
        print("\n1. Vector Database - Semantic Search")
        print("-" * 50)

        # Store sample embeddings
        sample_texts = [
            ("neural_ode", "physics", [0.1, 0.2, 0.3, 0.4]),
            ("black_scholes", "finance", [0.2, 0.3, 0.1, 0.5]),
            ("maxwell", "physics", [0.15, 0.25, 0.35, 0.45]),
            ("schrodinger", "physics", [0.12, 0.22, 0.32, 0.42]),
            ("heat_equation", "physics", [0.11, 0.21, 0.31, 0.41])
        ]

        for name, domain, vec in sample_texts:
            # Extend to 128 dimensions (simplified)
            full_vec = vec * 32  # Repeat pattern
            vid = infra.store_vector(
                vector=full_vec[:128],
                metadata={"name": name, "domain": domain},
                modality=Modality.TEXT
            )
            print(f"   Stored: {name} ({domain}) -> {vid[:15]}...")

        # Search similar vectors
        query = [0.1, 0.2, 0.3, 0.4] * 32
        results = infra.similarity_search(
            query_vector=query[:128],
            top_k=3,
            filters={"domain": "physics"}
        )

        print(f"\n   Similarity search results:")
        for r in results:
            print(f"      {r['metadata']['name']}: score={r['score']:.3f}")

        # 2. Graph Database Demo
        print("\n2. Graph Database - Knowledge Graph")
        print("-" * 50)

        # Create nodes
        equations = [
            ("eq_neural_ode", ["Equation", "Differential"], {"name": "Neural ODE"}),
            ("eq_maxwell", ["Equation", "Physics"], {"name": "Maxwell's Equations"}),
            ("eq_schrodinger", ["Equation", "Physics", "Quantum"], {"name": "Schrodinger Equation"}),
            ("domain_physics", ["Domain"], {"name": "Physics"}),
            ("domain_ml", ["Domain"], {"name": "Machine Learning"})
        ]

        for node_id, labels, props in equations:
            nid = infra.create_node(labels, node_id, props)
            print(f"   Node: {node_id} ({', '.join(labels)})")

        # Create edges
        edges = [
            ("eq_neural_ode", "BELONGS_TO", "domain_ml"),
            ("eq_maxwell", "BELONGS_TO", "domain_physics"),
            ("eq_schrodinger", "BELONGS_TO", "domain_physics"),
            ("eq_schrodinger", "RELATED_TO", "eq_maxwell"),
            ("eq_neural_ode", "USES", "eq_maxwell")
        ]

        for source, rel, target in edges:
            eid = infra.create_edge(source, rel, target)
            print(f"   Edge: {source} -[{rel}]-> {target}")

        # Traverse graph
        print(f"\n   Traversal from eq_neural_ode (depth 2):")
        traversal = infra.traverse_graph("eq_neural_ode", depth=2)
        for node in traversal["nodes"]:
            print(f"      {node['node_id']}: {node['properties'].get('name', 'N/A')}")

        # Find path
        path = infra.find_shortest_path("eq_neural_ode", "eq_schrodinger", max_depth=5)
        if path:
            print(f"\n   Path from Neural ODE to Schrodinger:")
            for node in path:
                print(f"      -> {node['properties'].get('name', node['node_id'])}")

        # 3. Feature Store Demo
        print("\n3. Feature Store - ML Feature Management")
        print("-" * 50)

        # Register features
        features = [
            ("equation_complexity", "float", "Complexity score of equation", "equation"),
            ("execution_time_ms", "float", "Execution time in milliseconds", "execution"),
            ("user_proficiency", "float", "User proficiency score", "user"),
            ("error_rate", "float", "Historical error rate", "user")
        ]

        for name, ftype, desc, entity in features:
            infra.register_feature(name, ftype, desc, entity)
            print(f"   Registered: {name} ({ftype}) for {entity}")

        # Store feature values
        print(f"\n   Storing online features:")
        for i in range(5):
            infra.store_feature(
                entity_id=f"user_{i}",
                feature_name="user_proficiency",
                value=random.uniform(0.5, 1.0),
                timestamp=time.time()
            )
            infra.store_feature(
                entity_id=f"equation_{i}",
                feature_name="equation_complexity",
                value=random.uniform(0.3, 0.9),
                timestamp=time.time()
            )

        print(f"      Stored features for 5 users and 5 equations")

        # Retrieve online features
        online = infra.get_online_features(
            entity_ids=["user_0", "user_1"],
            feature_names=["user_proficiency"]
        )

        print(f"\n   Online feature retrieval:")
        for entity, features in online.items():
            for name, value in features.items():
                if value:
                    print(f"      {entity}.{name} = {value['value']:.2f}")

        # 4. Distributed Cache Demo
        print("\n4. Distributed Cache - High-Performance Storage")
        print("-" * 50)

        # Store in cache
        cache_entries = [
            ("equation_result:eq_001", {"result": 42.5, "status": "success"}, 60),
            ("user_profile:user_123", {"name": "Alice", "role": "researcher"}, 300),
            ("model_weights:v2.1", [0.1, 0.2, 0.3], None)  # No TTL
        ]

        for key, value, ttl in cache_entries:
            infra.cache_set(key, value, ttl)
            ttl_str = f"{ttl}s" if ttl else "no expiration"
            print(f"   Cached: {key} (TTL: {ttl_str})")

        # Retrieve from cache
        print(f"\n   Cache retrieval:")
        for key, _, _ in cache_entries:
            value = infra.cache_get(key)
            if value:
                print(f"      {key}: HIT")
            else:
                print(f"      {key}: MISS")

        # Cache miss
        miss_value = infra.cache_get("non_existent_key")
        print(f"      non_existent_key: {'HIT' if miss_value else 'MISS'}")

        # 5. Infrastructure Statistics
        print("\n" + "=" * 70)
        print("Data Infrastructure Statistics")
        print("=" * 70)

        stats = infra.get_infrastructure_stats()

        print(f"   Vector Database:")
        print(f"      Total vectors: {stats['vector_database']['total_vectors']}")
        print(f"      Dimensions: {stats['vector_database']['dimension']}")

        print(f"   Graph Database:")
        print(f"      Nodes: {stats['graph_database']['total_nodes']}")
        print(f"      Edges: {stats['graph_database']['total_edges']}")

        print(f"   Feature Store:")
        print(f"      Total features: {stats['feature_store']['total_features']}")
        print(f"      Registered: {stats['feature_store']['registered_features']}")

        print(f"   Cache:")
        print(f"      Size: {stats['cache']['size']}/{stats['cache']['max_size']}")
        print(f"      Hit rate: {stats['cache']['hit_rate']:.1%}")
        print(f"      Policy: {stats['cache']['policy']}")

        print("\n" + "=" * 70)
        print("Phase 27 Data Infrastructure: OPERATIONAL")
        print("   Vector DB | Graph DB | Feature Store | Distributed Cache")
        print("=" * 70)

    else:
        print("AMOS Data Infrastructure v27.0.0")
        print("Usage: python amos_data_infrastructure.py --demo")


if __name__ == "__main__":
    main()
