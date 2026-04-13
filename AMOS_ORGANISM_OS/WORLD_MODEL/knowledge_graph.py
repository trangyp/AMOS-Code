# Stub to re-export from 08_WORLD_MODEL
import sys
from pathlib import Path

wm_path = Path(__file__).parent.parent / "08_WORLD_MODEL"
if str(wm_path) not in sys.path:
    sys.path.insert(0, str(wm_path))

from knowledge_graph import KnowledgeGraph, Entity, Relation, EntityType, RelationType

__all__ = ["KnowledgeGraph", "Entity", "Relation", "EntityType", "RelationType"]
