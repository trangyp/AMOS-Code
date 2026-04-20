"""AMOS Equation System - Search Engine.

Full-text search with Elasticsearch for equation discovery:
- Full-text search on name, description, formula
- Faceted search by tags, category, author
- Fuzzy matching for typo tolerance
- Auto-suggest for search queries
- Semantic search capabilities

Author: AMOS Search Team
Version: 2.0.0
"""

from dataclasses import dataclass
from datetime import UTC, datetime

UTC = UTC
from typing import Any

from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk


@dataclass
class SearchResult:
    """Search result item."""

    id: str
    score: float
    name: str
    formula: str
    description: str
    tags: list[str]
    author: str
    created_at: datetime
    highlight: dict[str, list[str]]  # Matched text snippets


@dataclass
class SearchResponse:
    """Search response with results and facets."""

    total: int
    took_ms: int
    results: list[SearchResult]
    facets: dict[str, dict[str, int]]  # Tag counts, category counts
    suggestions: list[str]  # Auto-suggest completions


class EquationSearchEngine:
    """Elasticsearch search engine for equations."""

    INDEX_NAME = "equations"

    def __init__(self, es_host: str = "http://localhost:9200"):
        self.es = AsyncElasticsearch([es_host])

    async def initialize(self) -> None:
        """Create index with mappings."""
        mapping = {
            "settings": {
                "number_of_shards": 3,
                "number_of_replicas": 1,
                "analysis": {
                    "analyzer": {
                        "equation_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": [
                                "lowercase",
                                "asciifolding",
                                "synonym_filter",
                            ],
                        },
                        "suggest_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": ["lowercase", "edge_ngram"],
                        },
                    },
                    "filter": {
                        "synonym_filter": {
                            "type": "synonym",
                            "synonyms": [
                                "derivative, differentiate, d/dx",
                                "integral, integration, ∫",
                                "quadratic, second-degree",
                            ],
                        },
                        "edge_ngram": {
                            "type": "edge_ngram",
                            "min_gram": 2,
                            "max_gram": 10,
                        },
                    },
                },
            },
            "mappings": {
                "properties": {
                    "id": {"type": "keyword"},
                    "name": {
                        "type": "text",
                        "analyzer": "equation_analyzer",
                        "fields": {
                            "keyword": {"type": "keyword"},
                            "suggest": {
                                "type": "text",
                                "analyzer": "suggest_analyzer",
                            },
                        },
                    },
                    "formula": {
                        "type": "text",
                        "analyzer": "equation_analyzer",
                    },
                    "description": {"type": "text", "analyzer": "standard"},
                    "latex": {"type": "text", "index": False},
                    "tags": {"type": "keyword"},
                    "category": {"type": "keyword"},
                    "author": {"type": "keyword"},
                    "author_id": {"type": "keyword"},
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"},
                    "verified": {"type": "boolean"},
                    "difficulty": {"type": "integer"},
                    "usage_count": {"type": "integer"},
                    "suggest": {
                        "type": "completion",
                        "analyzer": "suggest_analyzer",
                    },
                }
            },
        }

        # Create index if not exists
        if not await self.es.indices.exists(index=self.INDEX_NAME):
            await self.es.indices.create(index=self.INDEX_NAME, body=mapping)

    async def index_equation(self, equation: dict[str, Any]) -> None:
        """Index a single equation."""
        doc = {
            "id": str(equation["id"]),
            "name": equation["name"],
            "formula": equation.get("formula", ""),
            "description": equation.get("description", ""),
            "latex": equation.get("latex", ""),
            "tags": equation.get("tags", []),
            "category": equation.get("category", "general"),
            "author": equation.get("author", ""),
            "author_id": str(equation.get("author_id", "")),
            "created_at": equation.get("created_at", datetime.now(UTC)).isoformat(),
            "updated_at": equation.get("updated_at", datetime.now(UTC)).isoformat(),
            "verified": equation.get("verified", False),
            "difficulty": equation.get("difficulty", 1),
            "usage_count": equation.get("usage_count", 0),
            "suggest": {
                "input": [equation["name"]] + equation.get("tags", []),
            },
        }

        await self.es.index(
            index=self.INDEX_NAME,
            id=str(equation["id"]),
            document=doc,
        )

    async def bulk_index(self, equations: list[dict[str, Any]]) -> tuple[int, int]:
        """Bulk index multiple equations."""
        actions = []
        for eq in equations:
            actions.append(
                {
                    "_index": self.INDEX_NAME,
                    "_id": str(eq["id"]),
                    "_source": {
                        "id": str(eq["id"]),
                        "name": eq["name"],
                        "formula": eq.get("formula", ""),
                        "description": eq.get("description", ""),
                        "latex": eq.get("latex", ""),
                        "tags": eq.get("tags", []),
                        "category": eq.get("category", "general"),
                        "author": eq.get("author", ""),
                        "author_id": str(eq.get("author_id", "")),
                        "created_at": eq.get("created_at", datetime.now(UTC)).isoformat(),
                        "updated_at": eq.get("updated_at", datetime.now(UTC)).isoformat(),
                        "verified": eq.get("verified", False),
                        "difficulty": eq.get("difficulty", 1),
                        "usage_count": eq.get("usage_count", 0),
                        "suggest": {"input": [eq["name"]] + eq.get("tags", [])},
                    },
                }
            )

        success, errors = await async_bulk(self.es, actions)
        return success, errors

    async def search(
        self,
        query: str,
        filters: dict[str, Any] = None,
        sort_by: str = "relevance",
        page: int = 1,
        per_page: int = 20,
    ) -> SearchResponse:
        """Search equations with filters and facets."""
        must_clauses = []

        if query:
            # Multi-match query across name, formula, description
            must_clauses.append(
                {
                    "multi_match": {
                        "query": query,
                        "fields": ["name^3", "formula^2", "description", "tags^2"],
                        "type": "best_fields",
                        "fuzziness": "AUTO",
                        "prefix_length": 2,
                    }
                }
            )
        else:
            # Match all if no query
            must_clauses.append({"match_all": {}})

        # Apply filters
        filter_clauses = []
        if filters:
            if "tags" in filters:
                filter_clauses.append({"terms": {"tags": filters["tags"]}})
            if "category" in filters:
                filter_clauses.append({"term": {"category": filters["category"]}})
            if "author" in filters:
                filter_clauses.append({"term": {"author": filters["author"]}})
            if "verified" in filters:
                filter_clauses.append({"term": {"verified": filters["verified"]}})
            if "difficulty_min" in filters:
                filter_clauses.append({"range": {"difficulty": {"gte": filters["difficulty_min"]}}})
            if "difficulty_max" in filters:
                filter_clauses.append({"range": {"difficulty": {"lte": filters["difficulty_max"]}}})

        # Sort configuration
        sort_config = self._build_sort(sort_by)

        # Build query
        search_body = {
            "query": {
                "bool": {
                    "must": must_clauses,
                    "filter": filter_clauses,
                }
            },
            "sort": sort_config,
            "from": (page - 1) * per_page,
            "size": per_page,
            "highlight": {
                "fields": {
                    "name": {"fragment_size": 150, "number_of_fragments": 1},
                    "description": {"fragment_size": 150, "number_of_fragments": 2},
                    "formula": {"fragment_size": 100, "number_of_fragments": 1},
                },
                "pre_tags": ["<mark>"],
                "post_tags": ["</mark>"],
            },
            "aggs": {
                "tags": {"terms": {"field": "tags", "size": 20}},
                "categories": {"terms": {"field": "category", "size": 10}},
                "authors": {"terms": {"field": "author", "size": 10}},
                "verified_count": {"terms": {"field": "verified"}},
                "difficulty_stats": {"stats": {"field": "difficulty"}},
            },
        }

        # Execute search
        response = await self.es.search(
            index=self.INDEX_NAME,
            body=search_body,
        )

        # Parse results
        results = []
        for hit in response["hits"]["hits"]:
            source = hit["_source"]
            results.append(
                SearchResult(
                    id=hit["_id"],
                    score=hit["_score"] or 0.0,
                    name=source["name"],
                    formula=source.get("formula", ""),
                    description=source.get("description"),
                    tags=source.get("tags", []),
                    author=source.get("author", ""),
                    created_at=datetime.fromisoformat(source["created_at"]),
                    highlight=hit.get("highlight", {}),
                )
            )

        # Parse facets
        aggregations = response.get("aggregations", {})
        facets = {
            "tags": {
                b["key"]: b["doc_count"] for b in aggregations.get("tags", {}).get("buckets", [])
            },
            "categories": {
                b["key"]: b["doc_count"]
                for b in aggregations.get("categories", {}).get("buckets", [])
            },
            "authors": {
                b["key"]: b["doc_count"] for b in aggregations.get("authors", {}).get("buckets", [])
            },
        }

        # Get suggestions
        suggestions = await self.get_suggestions(query)

        return SearchResponse(
            total=response["hits"]["total"]["value"],
            took_ms=response["took"],
            results=results,
            facets=facets,
            suggestions=suggestions,
        )

    def _build_sort(self, sort_by: str) -> list[dict[str, Any]]:
        """Build sort configuration."""
        if sort_by == "relevance":
            return [{"_score": {"order": "desc"}}]
        elif sort_by == "newest":
            return [{"created_at": {"order": "desc"}}]
        elif sort_by == "oldest":
            return [{"created_at": {"order": "asc"}}]
        elif sort_by == "name_asc":
            return [{"name.keyword": {"order": "asc"}}]
        elif sort_by == "name_desc":
            return [{"name.keyword": {"order": "desc"}}]
        elif sort_by == "usage":
            return [{"usage_count": {"order": "desc"}}]
        elif sort_by == "difficulty":
            return [{"difficulty": {"order": "asc"}}]
        else:
            return [{"_score": {"order": "desc"}}]

    async def get_suggestions(self, query: str, size: int = 5) -> list[str]:
        """Get auto-complete suggestions."""
        if not query or len(query) < 2:
            return []

        suggest_body = {
            "suggest": {
                "name-suggest": {
                    "prefix": query,
                    "completion": {
                        "field": "suggest",
                        "size": size,
                        "fuzzy": {"fuzziness": "AUTO"},
                    },
                }
            }
        }

        response = await self.es.search(
            index=self.INDEX_NAME,
            body=suggest_body,
        )

        suggestions = []
        for option in response["suggest"]["name-suggest"][0]["options"]:
            suggestions.append(option["text"])

        return suggestions

    async def get_similar(self, equation_id: str, size: int = 5) -> list[SearchResult]:
        """Find similar equations using More Like This query."""
        mlt_body = {
            "query": {
                "more_like_this": {
                    "fields": ["name", "formula", "tags"],
                    "like": {"_index": self.INDEX_NAME, "_id": equation_id},
                    "min_term_freq": 1,
                    "max_query_terms": 12,
                    "min_doc_freq": 1,
                }
            },
            "size": size,
        }

        response = await self.es.search(
            index=self.INDEX_NAME,
            body=mlt_body,
        )

        results = []
        for hit in response["hits"]["hits"]:
            if hit["_id"] == equation_id:  # Exclude self
                continue
            source = hit["_source"]
            results.append(
                SearchResult(
                    id=hit["_id"],
                    score=hit["_score"] or 0.0,
                    name=source["name"],
                    formula=source.get("formula", ""),
                    description=source.get("description"),
                    tags=source.get("tags", []),
                    author=source.get("author", ""),
                    created_at=datetime.fromisoformat(source["created_at"]),
                    highlight={},
                )
            )

        return results

    async def delete_equation(self, equation_id: str) -> None:
        """Remove equation from index."""
        await self.es.delete(index=self.INDEX_NAME, id=equation_id)

    async def reindex_all(self, equations: list[dict[str, Any]]) -> tuple[int, int]:
        """Delete and reindex all equations."""
        # Delete existing index
        if await self.es.indices.exists(index=self.INDEX_NAME):
            await self.es.indices.delete(index=self.INDEX_NAME)

        # Recreate with mappings
        await self.initialize()

        # Bulk index
        return await self.bulk_index(equations)

    async def health_check(self) -> dict[str, Any]:
        """Check Elasticsearch health."""
        health = await self.es.cluster.health()
        return {
            "status": health["status"],
            "cluster_name": health["cluster_name"],
            "number_of_nodes": health["number_of_nodes"],
            "active_shards": health["active_primary_shards"],
            "unassigned_shards": health["unassigned_shards"],
        }

    async def close(self) -> None:
        """Close ES connection."""
        await self.es.close()


# Index sync utilities
class IndexSync:
    """Sync database changes to search index."""

    def __init__(self, search_engine: EquationSearchEngine):
        self.search = search_engine

    async def on_equation_created(self, equation: dict[str, Any]) -> None:
        """Handle equation creation."""
        await self.search.index_equation(equation)

    async def on_equation_updated(self, equation: dict[str, Any]) -> None:
        """Handle equation update."""
        await self.search.index_equation(equation)

    async def on_equation_deleted(self, equation_id: str) -> None:
        """Handle equation deletion."""
        await self.search.delete_equation(equation_id)
