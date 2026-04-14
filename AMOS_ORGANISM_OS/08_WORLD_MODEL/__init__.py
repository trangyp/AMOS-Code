"""08_WORLD_MODEL — External context, knowledge, and semantic understanding.

The world model subsystem of AMOS. Maintains knowledge graphs,
external context, macroeconomic data, geopolitical events, and
sector analysis for informed decision making.
"""

# Knowledge & Context
from .context_mapper import ContextMap, ContextMapper
from .geopolitical_monitor import (
    EventType,
    GeopoliticalEvent,
    GeopoliticalMonitor,
    RegionalStability,
    RiskLevel,
    get_geopolitical_monitor,
)
from .knowledge_graph import Entity, KnowledgeGraph, Relation

# Economic & Geopolitical
from .macroeconomic_scanner import (
    EconomicIndicator,
    IndicatorType,
    MacroeconomicScanner,
    MarketSignal,
    get_macro_scanner,
)
from .sector_analyzer import (
    Sector,
    SectorAnalyzer,
    SectorHealth,
    SupplyChainNode,
    get_sector_analyzer,
)
from .semantic_index import IndexedDocument, SemanticIndex
from .world_model_engine import (
    WorldContext,
    WorldModelEngine,
    get_world_model_engine,
)

__all__ = [
    # Knowledge & Context
    "KnowledgeGraph",
    "Entity",
    "Relation",
    "ContextMapper",
    "ContextMap",
    "SemanticIndex",
    "IndexedDocument",
    # Macroeconomic
    "MacroeconomicScanner",
    "EconomicIndicator",
    "MarketSignal",
    "IndicatorType",
    "get_macro_scanner",
    # Geopolitical
    "GeopoliticalMonitor",
    "GeopoliticalEvent",
    "RegionalStability",
    "EventType",
    "RiskLevel",
    "get_geopolitical_monitor",
    # Sector Analysis
    "SectorAnalyzer",
    "Sector",
    "SupplyChainNode",
    "SectorHealth",
    "get_sector_analyzer",
    # Main Engine
    "WorldModelEngine",
    "WorldContext",
    "get_world_model_engine",
]
