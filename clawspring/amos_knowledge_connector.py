"""AMOS Knowledge Graph Connector - External data and knowledge integration."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from amos_runtime import get_runtime


@dataclass
class KnowledgeQuery:
    """Result from knowledge graph query."""

    query: str
    domain: str
    results: List[dict]
    confidence: float
    source: str
    limitations: List[str]
    law_compliance: dict
    gap_acknowledgment: str


class KnowledgeGraphKernel:
    """Knowledge graph operations - entities, relations, queries."""

    def query(self, query_text: str, domain: str = "general") -> KnowledgeQuery:
        """Execute knowledge graph query."""
        # Simulated knowledge retrieval
        results = []

        # Pattern-based entity extraction
        entities = self._extract_entities(query_text)
        relations = self._extract_relations(query_text)

        for entity in entities:
            results.append(
                {
                    "entity": entity,
                    "type": self._classify_entity(entity),
                    "relations": [r for r in relations if entity in r],
                }
            )

        return KnowledgeQuery(
            query=query_text,
            domain=domain,
            results=results,
            confidence=0.6 if results else 0.2,
            source="internal_graph",
            limitations=[
                "No external database access",
                "Pattern-based extraction only",
                "No semantic understanding",
            ],
            law_compliance={"L1": True, "L4": True, "L5": True},
            gap_acknowledgment=(
                "GAP: Knowledge query is pattern matching. "
                "No knowledge graph. No semantic retrieval. Not knowledge representation."
            ),
        )

    def _extract_entities(self, text: str) -> List[str]:
        """Extract potential entities from text."""
        # Simple noun phrase extraction simulation
        words = text.lower().split()
        entities = []

        entity_indicators = [
            "system",
            "engine",
            "kernel",
            "module",
            "component",
            "process",
            "function",
            "tool",
            "analysis",
            "design",
        ]

        for word in words:
            if word in entity_indicators:
                entities.append(word)

        return list(set(entities))

    def _extract_relations(self, text: str) -> List[str]:
        """Extract potential relations from text."""
        relation_indicators = [
            "analyzes",
            "processes",
            "generates",
            "creates",
            "connects",
            "integrates",
            "uses",
            "implements",
        ]

        words = text.lower().split()
        relations = [w for w in words if w in relation_indicators]

        return list(set(relations))

    def _classify_entity(self, entity: str) -> str:
        """Classify entity type."""
        classifications = {
            "system": "system",
            "engine": "component",
            "kernel": "component",
            "module": "component",
            "component": "component",
            "process": "process",
            "function": "function",
            "tool": "interface",
            "analysis": "operation",
            "design": "artifact",
        }
        return classifications.get(entity, "unknown")


class DataConnectorKernel:
    """External data connection - APIs, databases, files."""

    SUPPORTED_SOURCES = ["json", "csv", "api", "database", "file"]

    def connect(self, source_type: str, connection_params: dict) -> dict:
        """Connect to external data source."""
        if source_type not in self.SUPPORTED_SOURCES:
            return {
                "success": False,
                "error": f"Unsupported source type: {source_type}",
                "supported": self.SUPPORTED_SOURCES,
            }

        # Simulated connection
        return {
            "success": True,
            "source_type": source_type,
            "connection_id": f"conn_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "status": "connected",
            "limitations": [
                "No actual data access",
                "Connection is simulated",
                "No persistence",
            ],
        }

    def query_external(self, connection_id: str, query: str) -> dict:
        """Query external data source."""
        return {
            "connection_id": connection_id,
            "query": query,
            "results": [],
            "status": "simulated",
            "gap_acknowledgment": (
                "GAP: External data query is simulated. "
                "No database access. No API calls. Not data integration."
            ),
        }


class SemanticSearchKernel:
    """Semantic search - vector similarity, embeddings, relevance."""

    def search(self, query: str, corpus: Optional[List[str]] = None) -> dict:
        """Perform semantic search."""
        # Simulated semantic search
        results = []

        # Simple keyword matching as placeholder
        query_terms = query.lower().split()

        if corpus:
            for i, doc in enumerate(corpus[:5]):  # Limit to first 5
                score = sum(1 for term in query_terms if term in doc.lower())
                if score > 0:
                    results.append(
                        {
                            "document_id": i,
                            "score": score / len(query_terms),
                            "excerpt": doc[:100] + "..." if len(doc) > 100 else doc,
                        }
                    )

        results.sort(key=lambda x: x["score"], reverse=True)

        return {
            "query": query,
            "results_count": len(results),
            "results": results[:3],  # Top 3
            "method": "keyword_matching",
            "limitations": [
                "No vector embeddings",
                "No semantic understanding",
                "Keyword matching only",
            ],
            "gap_acknowledgment": (
                "GAP: Semantic search is keyword matching. "
                "No embeddings. No similarity search. Not semantic retrieval."
            ),
        }


class AMOSKnowledgeConnector:
    """Unified knowledge connector for external data and knowledge integration."""

    DOMAINS = {
        "knowledge_graph": KnowledgeGraphKernel,
        "data_connector": DataConnectorKernel,
        "semantic_search": SemanticSearchKernel,
    }

    def __init__(self):
        self.runtime = get_runtime()
        self.kernels: Dict[str, Any] = {}
        self._init_kernels()
        self.connections: Dict[str, dict] = {}

    def _init_kernels(self):
        """Initialize all knowledge kernels."""
        for domain, kernel_class in self.DOMAINS.items():
            self.kernels[domain] = kernel_class()

    def query_knowledge(
        self,
        query: str,
        domain: str = "general",
    ) -> KnowledgeQuery:
        """Query knowledge graph."""
        kernel = self.kernels.get("knowledge_graph")
        if kernel:
            return kernel.query(query, domain)

        return KnowledgeQuery(
            query=query,
            domain=domain,
            results=[],
            confidence=0.0,
            source="none",
            limitations=["Knowledge graph not available"],
            law_compliance={},
            gap_acknowledgment="GAP: No knowledge graph available.",
        )

    def connect_data_source(
        self,
        source_type: str,
        connection_params: dict,
    ) -> dict:
        """Connect to external data source."""
        kernel = self.kernels.get("data_connector")
        if kernel:
            result = kernel.connect(source_type, connection_params)
            if result.get("success"):
                conn_id = result.get("connection_id")
                self.connections[conn_id] = {
                    "type": source_type,
                    "params": connection_params,
                    "created": datetime.now().isoformat(),
                }
            return result

        return {
            "success": False,
            "error": "Data connector not available",
        }

    def semantic_search(
        self,
        query: str,
        corpus: Optional[List[str]] = None,
    ) -> dict:
        """Perform semantic search."""
        kernel = self.kernels.get("semantic_search")
        if kernel:
            return kernel.search(query, corpus)

        return {
            "query": query,
            "results_count": 0,
            "results": [],
            "error": "Semantic search not available",
        }

    def get_status(self) -> dict:
        """Get connector status."""
        return {
            "kernels_available": list(self.kernels.keys()),
            "active_connections": len(self.connections),
            "connection_details": [
                {"id": k, "type": v["type"]} for k, v in self.connections.items()
            ],
        }

    def get_findings_summary(self, query_result: KnowledgeQuery) -> str:
        """Generate human-readable findings summary."""
        lines = [
            "# AMOS Knowledge Connector Summary",
            "",
            f"Query: {query_result.query}",
            f"Domain: {query_result.domain}",
            f"Source: {query_result.source}",
            f"Confidence: {query_result.confidence:.2f}",
            f"Results: {len(query_result.results)}",
            "",
            "## Results",
            "",
        ]

        for i, result in enumerate(query_result.results[:5], 1):
            lines.append(f"{i}. Entity: {result.get('entity', 'unknown')}")
            lines.append(f"   Type: {result.get('type', 'unknown')}")
            if result.get("relations"):
                lines.append(f"   Relations: {', '.join(result['relations'][:3])}")
            lines.append("")

        lines.extend(
            [
                "## Limitations",
                "",
            ]
        )
        for limitation in query_result.limitations:
            lines.append(f"- {limitation}")

        lines.extend(
            [
                "",
                "## Gap Acknowledgment",
                query_result.gap_acknowledgment,
            ]
        )

        return "\n".join(lines)


# Singleton
_knowledge_connector: Optional[AMOSKnowledgeConnector] = None


def get_knowledge_connector() -> AMOSKnowledgeConnector:
    """Get singleton knowledge connector."""
    global _knowledge_connector
    if _knowledge_connector is None:
        _knowledge_connector = AMOSKnowledgeConnector()
    return _knowledge_connector


def query_knowledge(query: str, domain: str = "general") -> KnowledgeQuery:
    """Quick helper for knowledge queries."""
    return get_knowledge_connector().query_knowledge(query, domain)


def connect_data_source(source_type: str, params: dict) -> dict:
    """Quick helper for data source connection."""
    return get_knowledge_connector().connect_data_source(source_type, params)


if __name__ == "__main__":
    print("=" * 60)
    print("AMOS KNOWLEDGE CONNECTOR TEST")
    print("=" * 60)
    print()

    connector = get_knowledge_connector()

    # Test knowledge query
    test_query = "Analyze system architecture components and their relationships"
    print(f"Query: {test_query}")

    result = connector.query_knowledge(test_query, "architecture")

    print(f"Results: {len(result.results)}")
    print(f"Confidence: {result.confidence:.2f}")

    # Test data connection
    conn_result = connector.connect_data_source("json", {"path": "/tmp/test.json"})
    print(f"\nConnection: {conn_result.get('status', 'failed')}")

    # Test semantic search
    corpus = [
        "The AMOS system processes cognitive tasks efficiently",
        "Design patterns improve software architecture",
        "Knowledge graphs enable semantic queries",
    ]
    search_result = connector.semantic_search("cognitive processing", corpus)
    print(f"\nSearch results: {search_result['results_count']}")

    # Full summary
    print("\n" + "=" * 60)
    print(connector.get_findings_summary(result))

    # Status
    print("\n" + "=" * 60)
    status = connector.get_status()
    print("Connector Status:")
    print(f"  Kernels: {', '.join(status['kernels_available'])}")
    print(f"  Connections: {status['active_connections']}")

    print("\n" + "=" * 60)
    print("Knowledge Connector: OPERATIONAL")
    print("=" * 60)
    print("\n3 knowledge domains active:")
    print("  - Knowledge Graph (entity/relation extraction)")
    print("  - Data Connector (external source connection)")
    print("  - Semantic Search (content retrieval)")
    print()
    print("GAP: All operations are simulated. No real data access.")
