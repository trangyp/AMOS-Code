"""Semantic Index — Document indexing and search for AMOS."""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class IndexedDocument:
    """A document in the semantic index."""

    id: str
    source: str
    content_hash: str
    tokens: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    indexed_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class SemanticIndex:
    """Indexes documents for semantic search.

    Responsibilities:
    - Index document content
    - Tokenize and normalize text
    - Search by keywords
    - Track document versions
    """

    def __init__(self):
        self._documents: dict[str, IndexedDocument] = {}
        self._token_index: dict[str, list[str]] = {}
        self._source_to_id: dict[str, str] = {}

    def index_document(
        self, source: str, content: str, metadata: dict[str, Any] = None
    ) -> IndexedDocument:
        """Index a document."""
        import hashlib
        import uuid

        # Compute hash
        content_hash = hashlib.md5(content.encode()).hexdigest()[:16]

        # Check if already indexed with same content
        if source in self._source_to_id:
            old_id = self._source_to_id[source]
            if old_id in self._documents:
                if self._documents[old_id].content_hash == content_hash:
                    return self._documents[old_id]

        # Tokenize
        tokens = self._tokenize(content)

        # Create document
        doc = IndexedDocument(
            id=str(uuid.uuid4())[:8],
            source=source,
            content_hash=content_hash,
            tokens=tokens,
            metadata=metadata or {},
        )

        # Store
        self._documents[doc.id] = doc
        self._source_to_id[source] = doc.id

        # Index tokens
        for token in set(tokens):
            if token not in self._token_index:
                self._token_index[token] = []
            self._token_index[token].append(doc.id)

        return doc

    def _tokenize(self, content: str) -> list[str]:
        """Simple tokenization."""
        # Normalize
        content = content.lower()
        # Remove special chars
        content = re.sub(r"[^\w\s]", " ", content)
        # Split and filter
        tokens = [t for t in content.split() if len(t) > 2]
        # Remove common stop words
        stop_words = {
            "the",
            "and",
            "for",
            "are",
            "but",
            "not",
            "you",
            "all",
            "can",
            "had",
            "her",
            "was",
            "one",
            "our",
            "out",
            "day",
            "get",
            "has",
            "him",
            "his",
            "how",
            "its",
            "may",
            "new",
            "now",
            "old",
            "see",
            "two",
            "way",
            "who",
            "boy",
            "did",
            "she",
            "use",
            "man",
        }
        return [t for t in tokens if t not in stop_words][:1000]  # Limit tokens

    def search(self, query: str, limit: int = 10) -> list[IndexedDocument]:
        """Search documents by query."""
        query_tokens = self._tokenize(query)

        if not query_tokens:
            return []

        # Score documents
        scores: dict[str, int] = {}
        for token in query_tokens:
            for doc_id in self._token_index.get(token, []):
                scores[doc_id] = scores.get(doc_id, 0) + 1

        # Sort by score
        sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)

        return [
            self._documents[doc_id] for doc_id in sorted_ids[:limit] if doc_id in self._documents
        ]

    def get_document(self, doc_id: str) -> Optional[IndexedDocument]:
        """Get document by ID."""
        return self._documents.get(doc_id)

    def index_file(self, filepath: str) -> Optional[IndexedDocument]:
        """Index a file from disk."""
        try:
            with open(filepath, encoding="utf-8", errors="ignore") as f:
                content = f.read()
            return self.index_document(filepath, content)
        except Exception:
            return None

    def status(self) -> dict[str, Any]:
        """Get index status."""
        total_tokens = sum(len(doc.tokens) for doc in self._documents.values())
        return {
            "total_documents": len(self._documents),
            "unique_tokens": len(self._token_index),
            "total_tokens": total_tokens,
        }
