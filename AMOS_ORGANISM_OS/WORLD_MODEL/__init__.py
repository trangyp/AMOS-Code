# Stub to re-export from 08_WORLD_MODEL
import sys
from pathlib import Path

wm_path = Path(__file__).parent.parent / "08_WORLD_MODEL"
if str(wm_path) not in sys.path:
    sys.path.insert(0, str(wm_path))

# Knowledge & Context
from knowledge_graph import KnowledgeGraph, Entity, Relation, EntityType, RelationType
from context_mapper import ContextMapper, ContextMap
from semantic_index import SemanticIndex, IndexedDocument

# Economic & Geopolitical
from macroeconomic_scanner import (
    MacroeconomicScanner, EconomicIndicator, MarketSignal, IndicatorType,
    get_macro_scanner,
)
from geopolitical_monitor import (
    GeopoliticalMonitor, GeopoliticalEvent, RegionalStability,
    EventType, RiskLevel, get_geopolitical_monitor,
)
from sector_analyzer import (
    SectorAnalyzer, Sector, SupplyChainNode, SectorHealth,
    get_sector_analyzer,
)
from world_model_engine import (
    WorldModelEngine, WorldContext, get_world_model_engine,
)

__all__ = [
    # Knowledge & Context
    "KnowledgeGraph", "Entity", "Relation", "EntityType", "RelationType",
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
