"""
08_WORLD_MODEL — External context, knowledge, and semantic understanding.

The world model subsystem of AMOS. Maintains knowledge graphs,
external context, and semantic understanding of the environment.
"""

from .knowledge_graph import KnowledgeGraph, Entity, Relation
from .context_mapper import ContextMapper, ContextMap
from .semantic_index import SemanticIndex, IndexedDocument

__all__ = [
    "KnowledgeGraph",
    "Entity",
    "Relation",
    "ContextMapper",
    "ContextMap",
    "SemanticIndex",
    "IndexedDocument",
]
