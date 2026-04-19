# Stub to re-export from 08_WORLD_MODEL
import sys
from pathlib import Path

wm_path = Path(__file__).parent.parent / "08_WORLD_MODEL"
if str(wm_path) not in sys.path:
    sys.path.insert(0, str(wm_path))

# Knowledge & Context
from context_mapper import ContextMap, ContextMapper
from geopolitical_monitor import (
    EventType,
    GeopoliticalEvent,
    GeopoliticalMonitor,
    RegionalStability,
    RiskLevel,
    get_geopolitical_monitor,
)
from knowledge_graph import Entity, EntityType, KnowledgeGraph, Relation, RelationType

# Economic & Geopolitical
from macroeconomic_scanner import (
    EconomicIndicator,
    IndicatorType,
    MacroeconomicScanner,
    MarketSignal,
    get_macro_scanner,
)
from sector_analyzer import (
    Sector,
    SectorAnalyzer,
    SectorHealth,
    SupplyChainNode,
    get_sector_analyzer,
)
from semantic_index import IndexedDocument, SemanticIndex

from world_model_engine import (
    WorldContext,
    WorldModelEngine,
    get_world_model_engine,
)

__all__ = [
    # Knowledge & Context
    "KnowledgeGraph",
    "Entity",
    "Relation",
    "EntityType",
    "RelationType",
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
