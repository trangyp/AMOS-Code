"""WORLD_MODEL module — Alias for 08_WORLD_MODEL"""

import importlib.util
from pathlib import Path

# Load modules from 08_WORLD_MODEL using importlib
_08_WM_PATH = Path(__file__).parent.parent / "08_WORLD_MODEL"

# context_mapper
_spec_cm = importlib.util.spec_from_file_location("_ctx_map", _08_WM_PATH / "context_mapper.py")
_mod_cm = importlib.util.module_from_spec(_spec_cm)
_spec_cm.loader.exec_module(_mod_cm)
ContextMapper = _mod_cm.ContextMapper
ContextMap = _mod_cm.ContextMap

# geopolitical_monitor
_spec_gm = importlib.util.spec_from_file_location(
    "_geo_mon", _08_WM_PATH / "geopolitical_monitor.py"
)
_mod_gm = importlib.util.module_from_spec(_spec_gm)
_spec_gm.loader.exec_module(_mod_gm)
GeopoliticalMonitor = _mod_gm.GeopoliticalMonitor
GeopoliticalEvent = _mod_gm.GeopoliticalEvent
RegionalStability = _mod_gm.RegionalStability
EventType = _mod_gm.EventType
RiskLevel = _mod_gm.RiskLevel
get_geopolitical_monitor = _mod_gm.get_geopolitical_monitor

# knowledge_graph
_spec_kg = importlib.util.spec_from_file_location("_know_graph", _08_WM_PATH / "knowledge_graph.py")
_mod_kg = importlib.util.module_from_spec(_spec_kg)
_spec_kg.loader.exec_module(_mod_kg)
KnowledgeGraph = _mod_kg.KnowledgeGraph
Entity = _mod_kg.Entity
EntityType = _mod_kg.EntityType
Relation = _mod_kg.Relation
RelationType = _mod_kg.RelationType

# macroeconomic_scanner
_spec_ms = importlib.util.spec_from_file_location(
    "_macro_scan", _08_WM_PATH / "macroeconomic_scanner.py"
)
_mod_ms = importlib.util.module_from_spec(_spec_ms)
_spec_ms.loader.exec_module(_mod_ms)
MacroeconomicScanner = _mod_ms.MacroeconomicScanner
EconomicIndicator = _mod_ms.EconomicIndicator
IndicatorType = _mod_ms.IndicatorType
MarketSignal = _mod_ms.MarketSignal
get_macro_scanner = _mod_ms.get_macro_scanner

# sector_analyzer
_spec_sa = importlib.util.spec_from_file_location("_sect_anal", _08_WM_PATH / "sector_analyzer.py")
_mod_sa = importlib.util.module_from_spec(_spec_sa)
_spec_sa.loader.exec_module(_mod_sa)
SectorAnalyzer = _mod_sa.SectorAnalyzer
Sector = _mod_sa.Sector
SectorHealth = _mod_sa.SectorHealth
SupplyChainNode = _mod_sa.SupplyChainNode
get_sector_analyzer = _mod_sa.get_sector_analyzer

# semantic_index
_spec_si = importlib.util.spec_from_file_location("_sem_idx", _08_WM_PATH / "semantic_index.py")
_mod_si = importlib.util.module_from_spec(_spec_si)
_spec_si.loader.exec_module(_mod_si)
SemanticIndex = _mod_si.SemanticIndex
IndexedDocument = _mod_si.IndexedDocument

# world_model_engine
_spec_wme = importlib.util.spec_from_file_location("_wm_eng", _08_WM_PATH / "world_model_engine.py")
_mod_wme = importlib.util.module_from_spec(_spec_wme)
_spec_wme.loader.exec_module(_mod_wme)
WorldModelEngine = _mod_wme.WorldModelEngine
WorldContext = _mod_wme.WorldContext
get_world_model_engine = _mod_wme.get_world_model_engine

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
