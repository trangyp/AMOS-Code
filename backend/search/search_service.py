"""
AMOS SuperBrain Search & Discovery Layer v2.0.0

Hybrid search with BM25 + vector embeddings + RRF fusion.
Indexes 1,500+ knowledge files, 251+ engines, features.

Owner: Trang Phan
Version: 2.0.0
"""


import hashlib
import json
import math
import re
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Optional

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
from typing import Optional
from typing import Dict, List
    STREAMING_AVAILABLE = True
except ImportError:
    STREAMING_AVAILABLE = False


@dataclass
class SearchDocument:
    """Document in search index."""
    doc_id: str
    title: str
    content: str
    vector: Optional[list[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    doc_type: str = "general"
    created_at: float = field(default_factory=time.time)
    score: float = 0.0


@dataclass
class SearchResult:
    """Search result with relevance scoring."""
    document: SearchDocument
    lexical_score: float = 0.0
    vector_score: float = 0.0
    hybrid_score: float = 0.0
    rank_lexical: int = 0
    rank_vector: int = 0


class LexicalEngine:
    """BM25 lexical search engine."""
    K1 = 1.5
    B = 0.75

    def __init__(self):
        self._inverted_index: dict[str, dict[str, int]] = defaultdict(dict)
        self._doc_lengths: Dict[str, int] = {}
        self._avg_doc_length: float = 0.0
        self._total_docs: int = 0
        self._doc_freqs: Dict[str, int] = defaultdict(int)

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b[a-zA-Z]{2,}\b', text.lower())

    def _compute_idf(self, term: str) -> float:
        df = self._doc_freqs.get(term, 0)
        if df == 0:
            return 0.0
        return math.log((self._total_docs - df + 0.5) / (df + 0.5) + 1.0)

    def add_document(self, doc: SearchDocument):
        tokens = self._tokenize(doc.title + " " + doc.content)
        doc_len = len(tokens)
        self._doc_lengths[doc.doc_id] = doc_len
        self._total_docs += 1
        total_len = sum(self._doc_lengths.values())
        self._avg_doc_length = total_len / self._total_docs if self._total_docs > 0 else 0
        term_counts = defaultdict(int)
        for token in tokens:
            term_counts[token] += 1
        for term, count in term_counts.items():
            self._inverted_index[term][doc.doc_id] = count
            self._doc_freqs[term] += 1

    def search(self, query: str, top_k: int = 10) -> list[tuple[str, float]]:
        query_tokens = self._tokenize(query)
        scores: Dict[str, float] = defaultdict(float)
        for term in query_tokens:
            idf = self._compute_idf(term)
            if idf == 0:
                continue
            postings = self._inverted_index.get(term, {})
            for doc_id, tf in postings.items():
                doc_len = self._doc_lengths.get(doc_id, 0)
                avgdl = self._avg_doc_length if self._avg_doc_length > 0 else 1
                numerator = tf * (self.K1 + 1)
                denominator = tf + self.K1 * (1 - self.B + self.B * doc_len / avgdl)
                score = idf * numerator / denominator
                scores[doc_id] += score
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_scores[:top_k]


class VectorEngine:
    """Vector similarity search engine."""
    def __init__(self, vector_dim: int = 768):
        self._vectors: dict[str, list[float]] = {}
        self._dim = vector_dim

    def add_document(self, doc: SearchDocument):
        if doc.vector and len(doc.vector) == self._dim:
            self._vectors[doc.doc_id] = doc.vector

    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        dot = sum(a * b for a, b in zip(v1, v2))
        norm1 = math.sqrt(sum(a * a for a in v1))
        norm2 = math.sqrt(sum(a * a for a in v2))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)

    def search(self, query_vector: List[float], top_k: int = 10) -> list[tuple[str, float]]:
        scores = []
        for doc_id, vector in self._vectors.items():
            sim = self._cosine_similarity(query_vector, vector)
            scores.append((doc_id, sim))
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]


class HybridEngine:
    """RRF (Reciprocal Rank Fusion) hybrid search."""
    RRF_K = 60

    def fuse_results(
        self,
        lexical_results: list[tuple[str, float]],
        vector_results: list[tuple[str, float]],
        top_k: int = 10
    ) -> list[tuple[str, float]]:
        lexical_ranks = {doc_id: rank + 1 for rank, (doc_id, _) in enumerate(lexical_results)}
        vector_ranks = {doc_id: rank + 1 for rank, (doc_id, _) in enumerate(vector_results)}
        all_docs = set(lexical_ranks.keys()) | set(vector_ranks.keys())
        rrf_scores = {}
        for doc_id in all_docs:
            score = 0.0
            if doc_id in lexical_ranks:
                score += 1.0 / (self.RRF_K + lexical_ranks[doc_id])
            if doc_id in vector_ranks:
                score += 1.0 / (self.RRF_K + vector_ranks[doc_id])
            rrf_scores[doc_id] = score
        sorted_results = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_results[:top_k]


class SearchIndex:
    """Search index manager with auto-indexing."""
    INDICES = ["knowledge", "features", "engines", "documents"]

    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or "redis://localhost:6379/8"
        self._redis: Optional[redis.Redis] = None
        self._documents: Dict[str, SearchDocument] = {}
        self._lexical = LexicalEngine()
        self._vector = VectorEngine()
        self._hybrid = HybridEngine()
        if REDIS_AVAILABLE:
            try:
                self._redis = redis.from_url(self.redis_url)
                self._redis.ping()
            except Exception:
                self._redis = None
        self._load_index()

    def _get_doc_key(self, doc_id: str) -> str:
        return f"search:doc:{doc_id}"

    def _load_index(self):
        if not self._redis:
            return
        try:
            pattern = self._get_doc_key("*")
            keys = list(self._redis.scan_iter(match=pattern))
            for key in keys:
                data = self._redis.get(key)
                if data:
                    doc_dict = json.loads(data)
                    doc = SearchDocument(**doc_dict)
                    self._add_to_memory(doc)
        except Exception:
            pass

    def _add_to_memory(self, doc: SearchDocument):
        self._documents[doc.doc_id] = doc
        self._lexical.add_document(doc)
        self._vector.add_document(doc)

    def index_document(self, doc: SearchDocument) -> bool:
        if SUPERBRAIN_AVAILABLE:
            try:
                brain = get_super_brain()
                if brain and hasattr(brain, 'action_gate'):
                    result = brain.action_gate.validate_action(
                        agent_id="search_index",
                        action="index_document",
                        details={"doc_id": doc.doc_id, "type": doc.doc_type}
                    )
                    if not result.authorized:
                        return False
            except Exception:
                pass
        self._add_to_memory(doc)
        if self._redis:
            try:
                key = self._get_doc_key(doc.doc_id)
                self._redis.setex(key, 86400 * 30, json.dumps(doc.__dict__, default=str))
            except Exception:
                pass
        if STREAMING_AVAILABLE:
            try:
                publish_event(
                    event_type="document_indexed",
                    source_system="search",
                    payload={"doc_id": doc.doc_id, "type": doc.doc_type},
                    requires_governance=False
                )
            except Exception:
                pass
        return True

    def search(
        self,
        query: str,
        query_vector: Optional[list[float]] = None,
        mode: str = "hybrid",
        top_k: int = 10,
        doc_type: Optional[str] = None
    ) -> List[SearchResult]:
        if SUPERBRAIN_AVAILABLE:
            try:
                brain = get_super_brain()
                if brain and hasattr(brain, 'action_gate'):
                    result = brain.action_gate.validate_action(
                        agent_id="search",
                        action="search",
                        details={"query": query[:50], "mode": mode}
                    )
                    if not result.authorized:
                        return []
            except Exception:
                pass
        lexical_results = []
        vector_results = []
        if mode in ["lexical", "hybrid"]:
            lexical_results = self._lexical.search(query, top_k * 2)
        if mode in ["vector", "hybrid"] and query_vector:
            vector_results = self._vector.search(query_vector, top_k * 2)
        if mode == "hybrid" and lexical_results and vector_results:
            fused = self._hybrid.fuse_results(lexical_results, vector_results, top_k)
        elif lexical_results:
            fused = lexical_results[:top_k]
        elif vector_results:
            fused = vector_results[:top_k]
        else:
            fused = []
        results = []
        for rank, (doc_id, score) in enumerate(fused, 1):
            doc = self._documents.get(doc_id)
            if not doc:
                continue
            if doc_type and doc.doc_type != doc_type:
                continue
            result = SearchResult(
                document=doc,
                lexical_score=next((s for d, s in lexical_results if d == doc_id), 0.0),
                vector_score=next((s for d, s in vector_results if d == doc_id), 0.0),
                hybrid_score=score,
                rank_lexical=next((i + 1 for i, (d, _) in enumerate(lexical_results) if d == doc_id), 0),
                rank_vector=next((i + 1 for i, (d, _) in enumerate(vector_results) if d == doc_id), 0)
            )
            doc.score = score
            results.append(result)
        if STREAMING_AVAILABLE:
            try:
                publish_event(
                    event_type="search_executed",
                    source_system="search",
                    payload={"query": query[:50], "mode": mode, "results": len(results)},
                    requires_governance=False
                )
            except Exception:
                pass
        return results[:top_k]

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_documents": len(self._documents),
            "by_type": {doc_type: sum(1 for d in self._documents.values() if d.doc_type == doc_type)
                       for doc_type in set(d.doc_type for d in self._documents.values())},
            "avg_doc_length": self._lexical._avg_doc_length,
            "vocabulary_size": len(self._lexical._inverted_index)
        }


class SearchService:
    """Main search service facade."""

    def __init__(self, redis_url: Optional[str] = None):
        self._index = SearchIndex(redis_url)

    def search(
        self,
        query: str,
        mode: str = "hybrid",
        top_k: int = 10,
        doc_type: Optional[str] = None
    ) -> List[SearchResult]:
        return self._index.search(query, mode=mode, top_k=top_k, doc_type=doc_type)

    def index_document(self, doc: SearchDocument) -> bool:
        return self._index.index_document(doc)

    def get_stats(self) -> Dict[str, Any]:
        return self._index.get_stats()


search_index = SearchIndex()


def index_document(doc: SearchDocument) -> bool:
    return search_index.index_document(doc)


def search(query: str, mode: str = "hybrid", top_k: int = 10) -> List[SearchResult]:
    return search_index.search(query, mode=mode, top_k=top_k)


def get_search_stats() -> Dict[str, Any]:
    return search_index.get_stats()
