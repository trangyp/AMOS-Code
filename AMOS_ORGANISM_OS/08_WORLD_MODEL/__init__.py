"""
08_WORLD_MODEL — External context, knowledge, and semantic understanding.

The world model subsystem of AMOS. Maintains knowledge graphs,
external context, macroeconomic data, geopolitical events, and
sector analysis for informed decision making.
"""

# Knowledge & Context
from .knowledge_graph import KnowledgeGraph, Entity, Relation
from .context_mapper import ContextMapper, ContextMap
from .semantic_index import SemanticIndex, IndexedDocument

# Economic & Geopolitical
from .macroeconomic_scanner import (
    MacroeconomicScanner, EconomicIndicator, MarketSignal, IndicatorType,
    get_macro_scanner,
)
from .geopolitical_monitor import (
    GeopoliticalMonitor, GeopoliticalEvent, RegionalStability,
    EventType, RiskLevel, get_geopolitical_monitor,
)
from .sector_analyzer import (
    SectorAnalyzer, Sector, SupplyChainNode, SectorHealth,
    get_sector_analyzer,
)
from .world_model_engine import (
    WorldModelEngine, WorldContext, get_world_model_engine,
)

__all__ = [
    # Knowledge & Context
    "KnowledgeGraph", "Entity", "Relation",
    "ContextMapper", "ContextMap",
    "SemanticIndex", "IndexedDocument",
    # Macroeconomic
    "MacroeconomicScanner", "EconomicIndicator", "MarketSignal", "IndicatorType",
    "get_macro_scanner",
    # Geopolitical
    "GeopoliticalMonitor", "GeopoliticalEvent", "RegionalStability",
    "EventType", "RiskLevel", "get_geopolitical_monitor",
    # Sector Analysis
    "SectorAnalyzer", "Sector", "SupplyChainNode", "SectorHealth",
    "get_sector_analyzer",
    # Main Engine
    "WorldModelEngine", "WorldContext", "get_world_model_engine",
]
