"""Knowledge Graph — Semantic knowledge representation for AMOS."""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class EntityType(Enum):
    FILE = "file"
    MODULE = "module"
    FUNCTION = "function"
    CLASS = "class"
    CONCEPT = "concept"
    PERSON = "person"
    TASK = "task"
    PROJECT = "project"


class RelationType(Enum):
    DEPENDS_ON = "depends_on"
    IMPORTS = "imports"
    CALLS = "calls"
    CONTAINS = "contains"
    IMPLEMENTS = "implements"
    RELATED_TO = "related_to"
    PART_OF = "part_of"


@dataclass
class Entity:
    """A node in the knowledge graph."""

    id: str
    name: str
    entity_type: EntityType
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class Relation:
    """An edge in the knowledge graph."""

    source_id: str
    target_id: str
    relation_type: RelationType
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


class KnowledgeGraph:
    """Maintains semantic knowledge about the codebase and world.

    Responsibilities:
    - Store entities (files, functions, concepts)
    - Track relationships between entities
    - Query knowledge for context
    - Import/export knowledge
    """

    def __init__(self):
        self._entities: Dict[str, Entity] = {}
        self._relations: List[Relation] = []
        self._index_by_type: dict[EntityType, set[str]] = {}
        self._index_by_name: dict[str, set[str]] = {}

    def add_entity(self, entity: Entity) -> str:
        """Add an entity to the graph."""
        self._entities[entity.id] = entity

        # Index by type
        if entity.entity_type not in self._index_by_type:
            self._index_by_type[entity.entity_type] = set()
        self._index_by_type[entity.entity_type].add(entity.id)

        # Index by name
        if entity.name not in self._index_by_name:
            self._index_by_name[entity.name] = set()
        self._index_by_name[entity.name].add(entity.id)

        return entity.id

    def add_relation(self, relation: Relation) -> None:
        """Add a relation to the graph."""
        self._relations.append(relation)

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Get entity by ID."""
        return self._entities.get(entity_id)

    def find_entities(self, name: str = None, entity_type: EntityType = None) -> List[Entity]:
        """Find entities by name and/or type."""
        results = []

        if name and entity_type:
            # Both filters
            ids = self._index_by_name.get(name, set())
            type_ids = self._index_by_type.get(entity_type, set())
            for eid in ids & type_ids:
                if eid in self._entities:
                    results.append(self._entities[eid])
        elif name:
            # Name only
            for eid in self._index_by_name.get(name, set()):
                if eid in self._entities:
                    results.append(self._entities[eid])
        elif entity_type:
            # Type only
            for eid in self._index_by_type.get(entity_type, set()):
                if eid in self._entities:
                    results.append(self._entities[eid])
        else:
            # All entities
            results = list(self._entities.values())

        return results

    def get_related(self, entity_id: str, relation_type: RelationType = None) -> List[Entity]:
        """Get entities related to given entity."""
        related_ids = []

        for rel in self._relations:
            if rel.source_id == entity_id:
                if relation_type is None or rel.relation_type == relation_type:
                    related_ids.append(rel.target_id)
            elif rel.target_id == entity_id:
                if relation_type is None or rel.relation_type == relation_type:
                    related_ids.append(rel.source_id)

        return [self._entities[eid] for eid in related_ids if eid in self._entities]

    def build_from_directory(self, path: str = ".") -> int:
        """Build knowledge graph from directory structure."""
        import os

        count = 0

        for root, dirs, files in os.walk(path):
            # Skip hidden and cache directories
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".") and d not in ["__pycache__", "node_modules"]
            ]

            # Add directory as entity
            dir_id = f"dir:{root}"
            if dir_id not in self._entities:
                self.add_entity(
                    Entity(
                        id=dir_id,
                        name=root,
                        entity_type=EntityType.MODULE,
                        properties={"path": root, "type": "directory"},
                    )
                )
                count += 1

            # Add files as entities
            for filename in files:
                if filename.startswith("."):
                    continue

                filepath = os.path.join(root, filename)
                file_id = f"file:{filepath}"

                # Determine entity type from extension
                ext = filename.split(".")[-1] if "." in filename else ""
                entity_type = EntityType.FILE
                if ext == "py":
                    entity_type = EntityType.MODULE

                self.add_entity(
                    Entity(
                        id=file_id,
                        name=filename,
                        entity_type=entity_type,
                        properties={
                            "path": filepath,
                            "extension": ext,
                            "size": os.path.getsize(filepath),
                        },
                    )
                )

                # Add relation: directory contains file
                self.add_relation(
                    Relation(
                        source_id=dir_id,
                        target_id=file_id,
                        relation_type=RelationType.CONTAINS,
                    )
                )
                count += 1

        return count

    def query(self, entity_type: EntityType = None, limit: int = 100) -> List[Entity]:
        """Query entities."""
        if entity_type:
            return [self._entities[eid] for eid in self._index_by_type.get(entity_type, set())][
                :limit
            ]
        return list(self._entities.values())[:limit]

    def export_json(self) -> str:
        """Export graph to JSON."""
        data = {
            "entities": [
                {
                    "id": e.id,
                    "name": e.name,
                    "type": e.entity_type.value,
                    "properties": e.properties,
                }
                for e in self._entities.values()
            ],
            "relations": [
                {
                    "source": r.source_id,
                    "target": r.target_id,
                    "type": r.relation_type.value,
                }
                for r in self._relations
            ],
        }
        return json.dumps(data, indent=2)

    def status(self) -> Dict[str, Any]:
        """Get graph status."""
        return {
            "total_entities": len(self._entities),
            "total_relations": len(self._relations),
            "by_type": {t.value: len(ids) for t, ids in self._index_by_type.items()},
        }
