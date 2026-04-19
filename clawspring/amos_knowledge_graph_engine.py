"""AMOS Knowledge Graph Engine - Semantic knowledge and entity relationships."""

from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class EntityType(Enum):
    """Types of entities in the knowledge graph."""
    PERSON = "person"
    ORGANIZATION = "organization"
    CONCEPT = "concept"
    EVENT = "event"
    LOCATION = "location"
    TECHNOLOGY = "technology"
    SYSTEM = "system"
    PROCESS = "process"
    DOMAIN = "domain"


class RelationType(Enum):
    """Types of relationships between entities."""
    IS_A = "is_a"
    PART_OF = "part_of"
    RELATED_TO = "related_to"
    CAUSES = "causes"
    DEPENDS_ON = "depends_on"
    USES = "uses"
    PRODUCES = "produces"
    LOCATED_IN = "located_in"
    OCCURRED_AT = "occurred_at"
    AUTHORED_BY = "authored_by"
    IMPLEMENTS = "implements"


@dataclass
class Entity:
    """Represents a node in the knowledge graph."""

    id: str
    name: str
    entity_type: EntityType
    attributes: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0


@dataclass
class Relation:
    """Represents an edge in the knowledge graph."""

    source_id: str
    target_id: str
    relation_type: RelationType
    weight: float = 1.0
    attributes: Dict[str, Any] = field(default_factory=dict)


class EntityExtractor:
    """Extract entities from text."""

    def __init__(self):
        self.patterns = {
            EntityType.PERSON: ["Trang Phan", "engineer", "researcher", "developer"],
            EntityType.ORGANIZATION: ["AMOS", "NASA", "UN", "IPCC", "IPBES"],
            EntityType.CONCEPT: ["intelligence", "consciousness", "system", "boundary"],
            EntityType.TECHNOLOGY: ["AI", "quantum computing", "neural network", "blockchain"],
            EntityType.SYSTEM: ["ecosystem", "climate system", "economy", "biosphere"],
            EntityType.DOMAIN: ["physics", "biology", "cognition", "planetary science"],
        }

    def extract_entities(self, text: str) -> List[Entity]:
        """Extract entities from input text."""
        entities = []
        entity_id = 0
        for entity_type, keywords in self.patterns.items():
            for keyword in keywords:
                if keyword.lower() in text.lower():
                    entities.append(Entity(
                        id=f"ent_{entity_id}",
                        name=keyword,
                        entity_type=entity_type,
                        attributes={"extracted_from": text[:50]},
                    ))
                    entity_id += 1
        return entities

    def extract_relations(self, text: str, entities: List[Entity]) -> List[Relation]:
        """Extract relations between entities."""
        relations = []
        relation_indicators = {
            RelationType.IS_A: ["is a", "is an", "are"],
            RelationType.PART_OF: ["part of", "component of", "within"],
            RelationType.CAUSES: ["causes", "leads to", "results in"],
            RelationType.DEPENDS_ON: ["depends on", "requires", "needs"],
            RelationType.USES: ["uses", "utilizes", "employs"],
            RelationType.RELATED_TO: ["related to", "associated with", "connected to"],
        }
        for i, ent1 in enumerate(entities):
            for j, ent2 in enumerate(entities):
                if i != j:
                    for rel_type, indicators in relation_indicators.items():
                        if any(ind in text.lower() for ind in indicators):
                            relations.append(Relation(
                                source_id=ent1.id,
                                target_id=ent2.id,
                                relation_type=rel_type,
                            ))
        return relations


class SemanticSearch:
    """Semantic search capabilities."""

    def __init__(self):
        self.embeddings: Dict[str, list[float]] = {}

    def compute_similarity(self, text1: str, text2: str) -> float:
        """Compute semantic similarity (simplified)."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        intersection = words1 & words2
        union = words1 | words2
        if not union:
            return 0.0
        return len(intersection) / len(union)

    def search(self, query: str, corpus: List[str], top_k: int = 5) -> List[tuple[str, float]]:
        """Search corpus for relevant documents."""
        scores = [(doc, self.compute_similarity(query, doc)) for doc in corpus]
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]


class KnowledgeInference:
    """Infer new knowledge from existing graph."""

    def __init__(self, graph: KnowledgeGraph):
        self.graph = graph

    def infer_transitive(self, entity_id: str, relation_type: RelationType) -> List[str]:
        """Infer transitive relationships."""
        results = []
        visited = set()
        queue = [entity_id]
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            relations = self.graph.get_relations_from(current)
            for rel in relations:
                if rel.relation_type == relation_type:
                    results.append(rel.target_id)
                    queue.append(rel.target_id)
        return results

    def find_paths(self, source: str, target: str, max_depth: int = 3) -> List[list[str]]:
        """Find paths between entities."""
        paths = []
        queue = [(source, [source])]
        while queue:
            current, path = queue.pop(0)
            if len(path) > max_depth:
                continue
            if current == target and len(path) > 1:
                paths.append(path)
                continue
            relations = self.graph.get_relations_from(current)
            for rel in relations:
                if rel.target_id not in path:
                    queue.append((rel.target_id, path + [rel.target_id]))
        return paths


class KnowledgeGraph:
    """Knowledge graph store and operations."""

    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.relations: List[Relation] = []
        self.entity_index: Dict[EntityType, list[str]] = defaultdict(list)

    def add_entity(self, entity: Entity) -> None:
        """Add entity to graph."""
        self.entities[entity.id] = entity
        self.entity_index[entity.entity_type].append(entity.id)

    def add_relation(self, relation: Relation) -> None:
        """Add relation to graph."""
        self.relations.append(relation)

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Get entity by ID."""
        return self.entities.get(entity_id)

    def get_relations_from(self, entity_id: str) -> List[Relation]:
        """Get all relations originating from entity."""
        return [r for r in self.relations if r.source_id == entity_id]

    def get_relations_to(self, entity_id: str) -> List[Relation]:
        """Get all relations targeting entity."""
        return [r for r in self.relations if r.target_id == entity_id]

    def get_neighbors(self, entity_id: str) -> List[Entity]:
        """Get neighboring entities."""
        rels = self.get_relations_from(entity_id)
        return [self.entities[r.target_id] for r in rels if r.target_id in self.entities]

    def query_by_type(self, entity_type: EntityType) -> List[Entity]:
        """Query entities by type."""
        ids = self.entity_index.get(entity_type, [])
        return [self.entities[i] for i in ids if i in self.entities]

    def get_statistics(self) -> Dict[str, Any]:
        """Get graph statistics."""
        return {
            "num_entities": len(self.entities),
            "num_relations": len(self.relations),
            "entity_types": {t.value: len(ids) for t, ids in self.entity_index.items()},
            "density": len(self.relations) / max(1, len(self.entities) ** 2),
        }


class KnowledgeGraphEngine:
    """AMOS Knowledge Graph Engine - Semantic knowledge and reasoning."""

    VERSION = "vInfinity_Knowledge_Graph_1.0.0"
    NAME = "AMOS_Knowledge_Graph_OMEGA"

    def __init__(self):
        self.graph = KnowledgeGraph()
        self.extractor = EntityExtractor()
        self.search = SemanticSearch()
        self.inference: Optional[KnowledgeInference] = None
        self._initialize_core_knowledge()

    def _initialize_core_knowledge(self) -> None:
        """Initialize with core AMOS knowledge."""
        # Core entities
        core_entities = [
            Entity("amos", "AMOS", EntityType.SYSTEM, {"version": "vInfinity"}),
            Entity("vomni", "vOmni Kernel", EntityType.SYSTEM, {"type": "meta-router"}),
            Entity("species", "Species Interaction Core", EntityType.SYSTEM, {"modules": "HIE,UMPL,UST,UIE,UEL"}),
            Entity("ubi", "UBI Stack", EntityType.SYSTEM, {"type": "neurobiological"}),
            Entity("planetary", "Planetary Stack", EntityType.SYSTEM, {"type": "earth_systems"}),
            Entity("trang", "Trang Phan", EntityType.PERSON, {"role": "Creator"}),
            Entity("cognition", "Cognition", EntityType.CONCEPT, {"domain": "intelligence"}),
            Entity("intelligence", "Intelligence", EntityType.CONCEPT, {"related": "cognition"}),
        ]
        for ent in core_entities:
            self.graph.add_entity(ent)
        # Core relations
        core_relations = [
            Relation("amos", "vomni", RelationType.IMPLEMENTS),
            Relation("amos", "species", RelationType.IMPLEMENTS),
            Relation("amos", "ubi", RelationType.IMPLEMENTS),
            Relation("amos", "planetary", RelationType.IMPLEMENTS),
            Relation("trang", "amos", RelationType.AUTHORED_BY),
            Relation("intelligence", "cognition", RelationType.IS_A),
            Relation("vomni", "cognition", RelationType.USES),
            Relation("species", "ubi", RelationType.DEPENDS_ON),
        ]
        for rel in core_relations:
            self.graph.add_relation(rel)
        self.inference = KnowledgeInference(self.graph)

    def analyze(self, query: str, context: Dict[str, Any]  = None) -> Dict[str, Any]:
        """Run knowledge graph analysis."""
        context = context or {}
        results: Dict[str, Any] = {
            "query": query[:100],
            "extracted_entities": [],
            "extracted_relations": [],
            "semantic_matches": [],
            "inferred_knowledge": [],
            "graph_stats": {},
            "recommendations": [],
        }
        # Extract entities from query
        entities = self.extractor.extract_entities(query)
        for ent in entities:
            self.graph.add_entity(ent)
        results["extracted_entities"] = [{"id": e.id, "name": e.name, "type": e.entity_type.value} for e in entities]
        # Extract relations
        relations = self.extractor.extract_relations(query, entities)
        for rel in relations:
            self.graph.add_relation(rel)
        results["extracted_relations"] = [{"source": r.source_id, "target": r.target_id, "type": r.relation_type.value} for r in relations]
        # Semantic search
        corpus = [
            "AMOS vInfinity is a comprehensive AI system",
            "Knowledge graphs represent semantic relationships",
            "Entity extraction identifies key concepts",
            "Inference derives new knowledge from existing facts",
        ]
        matches = self.search.search(query, corpus, top_k=3)
        results["semantic_matches"] = [{"text": m[0], "score": round(m[1], 2)} for m in matches]
        # Knowledge inference
        if self.inference and entities:
            for ent in entities[:2]:  # Limit for performance
                related = self.inference.infer_transitive(ent.id, RelationType.RELATED_TO)
                results["inferred_knowledge"].append({
                    "entity": ent.name,
                    "inferred_related": [self.graph.get_entity(r).name if self.graph.get_entity(r) else r for r in related[:5]],
                })
        # Graph statistics
        results["graph_stats"] = self.graph.get_statistics()
        # Generate recommendations
        recommendations = [
            "Knowledge Graph: Continue expanding entity extraction patterns",
            "Semantic Search: Implement proper embeddings for better similarity",
            "Inference: Add more sophisticated reasoning rules (transitive, symmetric)",
            "Integration: Link with Species Core for entity grounding in interaction context",
            "Scale: Consider vector database for large-scale knowledge storage",
        ]
        results["recommendations"] = recommendations
        return results

    def get_findings_summary(self, results: dict) -> str:
        """Generate findings summary."""
        lines = [
            f"# {self.NAME} {self.VERSION}",
            "",
            "Creator: Trang Phan | System: AMOS vInfinity",
            "Role: Semantic Knowledge Graph and Entity Relationship Analysis",
            "",
            "## Knowledge Graph Overview",
            "The Knowledge Graph Engine provides:",
            "- Entity extraction and type classification",
            "- Semantic relationship detection",
            "- Knowledge inference and reasoning",
            "- Graph-based semantic search",
            "- Cross-domain knowledge integration",
            "",
            "## Entity Extraction",
        ]
        entities = results.get("extracted_entities", [])
        lines.append(f"**Extracted {len(entities)} entities from query:**")
        for ent in entities[:5]:
            lines.append(f"- **{ent.get('name', 'N/A')}** ({ent.get('type', 'N/A')}) - ID: {ent.get('id', 'N/A')}")
        lines.extend([
            "",
            "## Relationship Extraction",
            f"**Detected {len(results.get('extracted_relations', []))} relations:**",
        ])
        for rel in results.get("extracted_relations", [])[:5]:
            lines.append(f"- {rel.get('source', 'N/A')} --[{rel.get('type', 'N/A')}]--> {rel.get('target', 'N/A')}")
        lines.extend([
            "",
            "## Semantic Search Results",
        ])
        for match in results.get("semantic_matches", []):
            lines.append(f"- **{match.get('text', 'N/A')[:50]}...** (score: {match.get('score', 0):.2f})")
        lines.extend([
            "",
            "## Knowledge Inference",
            "Inferred relationships through graph traversal:",
        ])
        for inf in results.get("inferred_knowledge", []):
            entity = inf.get('entity', 'N/A')
            related = inf.get('inferred_related', [])
            if related:
                lines.append(f"- **{entity}** is related to: {', '.join(related[:3])}")
        lines.extend([
            "",
            "## Graph Statistics",
        ])
        stats = results.get("graph_stats", {})
        lines.extend([
            f"- **Total Entities**: {stats.get('num_entities', 0)}",
            f"- **Total Relations**: {stats.get('num_relations', 0)}",
            f"- **Graph Density**: {stats.get('density', 0):.4f}",
        ])
        entity_types = stats.get('entity_types', {})
        if entity_types:
            lines.append("- **Entity Types**:")
            for etype, count in list(entity_types.items())[:5]:
                lines.append(f"  - {etype}: {count}")
        lines.extend([
            "",
            "## Supported Entity Types",
            "- **PERSON**: Individuals, authors, researchers",
            "- **ORGANIZATION**: Companies, institutions, groups",
            "- **CONCEPT**: Abstract ideas, theories, principles",
            "- **TECHNOLOGY**: Tools, systems, methods",
            "- **SYSTEM**: Complex integrated systems",
            "- **DOMAIN**: Fields of study, knowledge areas",
            "",
            "## Supported Relation Types",
            "- **IS_A**: Taxonomic relationship (subtype)",
            "- **PART_OF**: Component or membership",
            "- **CAUSES**: Causal relationship",
            "- **DEPENDS_ON**: Dependency or requirement",
            "- **USES**: Utilization relationship",
            "- **RELATED_TO**: General association",
            "",
            "## Integration with AMOS Core Stack",
            "The Knowledge Graph Engine connects to:",
            "- **vOmni Kernel**: Provides semantic routing context",
            "- **Species Interaction Core**: Grounds entities in human interaction",
            "- **Logic Core**: Enables formal reasoning over graph",
            "- **UBI Stack**: Links biological concepts to knowledge",
            "- **Planetary Stack**: Connects environmental knowledge",
            "",
            "## Recommendations",
        ])
        for i, rec in enumerate(results.get("recommendations", []), 1):
            lines.append(f"{i}. {rec}")
        lines.extend([
            "",
            "## Limitations",
            "- Simplified entity extraction (pattern-based)",
            "- Basic semantic similarity (Jaccard-based)",
            "- Limited inference rules",
            "- No external knowledge base integration",
            "- Static knowledge initialization",
        ])
        return "\n".join(lines)


# Singleton instance
_kg_engine: Optional[KnowledgeGraphEngine] = None


def get_knowledge_graph_engine() -> KnowledgeGraphEngine:
    """Get or create the Knowledge Graph Engine singleton."""
    global _kg_engine
    if _kg_engine is None:
        _kg_engine = KnowledgeGraphEngine()
    return _kg_engine
