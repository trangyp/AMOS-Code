#!/usr/bin/env python3
"""
AMOS Engine Activation Kernel - 15_ENGINE_ACTIVATION Subsystem

Responsible for:
- Scanning and discovering 160+ engines across _AMOS_BRAIN/
- Activating engines into the cognitive stack
- Managing engine lifecycle (load, enable, disable, unload)
- Routing queries to appropriate engines via KernelRouter
- Integrating with Organism BRAIN subsystem
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Set
from collections import defaultdict
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("amos.engine_activation")


@dataclass
class ActivatedEngine:
    """An activated engine in the cognitive stack."""
    engine_id: str
    name: str
    category: str  # cognitive, tech, domain, unipower, core
    source_path: str
    size_bytes: int
    capabilities: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    is_active: bool = False
    is_loaded: bool = False
    activation_time: Optional[str] = None
    last_invoked: Optional[str] = None
    invoke_count: int = 0
    content_hash: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "engine_id": self.engine_id,
            "name": self.name,
            "category": self.category,
            "source_path": self.source_path,
            "size_bytes": self.size_bytes,
            "capabilities": self.capabilities,
            "is_active": self.is_active,
            "is_loaded": self.is_loaded,
            "activation_time": self.activation_time,
            "invoke_count": self.invoke_count,
        }


@dataclass
class EngineQuery:
    """A query to be routed to engines."""
    query_id: str
    text: str
    domain_hints: List[str] = field(default_factory=list)
    required_capabilities: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()


@dataclass
class EngineResponse:
    """Response from an engine invocation."""
    engine_id: str
    engine_name: str
    success: bool
    result: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    processing_time_ms: float = 0.0
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()


class EngineActivationKernel:
    """
    The Engine Activation Kernel manages the 160+ cognitive engines
    and integrates them with the AMOS Organism.
    """
    
    # Engine categories in _AMOS_BRAIN/
    ENGINE_CATEGORIES = {
        "cognitive": "Cognitive/",
        "tech": "Kernels/Tech/",
        "domain": "Domains/",
        "unipower": "Unipower/",
        "core": "Core/",
        "intelligence": "Core/7_Intelligents/",
    }
    
    # Domain keywords for routing
    DOMAIN_KEYWORDS = {
        "biology": ["biology", "cognition", "neuro", "cellular", "molecular"],
        "design": ["design", "ux", "ui", "visual", "interface"],
        "logic": ["logic", "law", "legal", "deterministic", "reasoning"],
        "economics": ["economy", "finance", "market", "investment", "money"],
        "engineering": ["engineering", "math", "calculation", "structural"],
        "physics": ["physics", "cosmos", "quantum", "universe"],
        "society": ["society", "culture", "social", "community", "human"],
        "strategy": ["strategy", "game", "tactical", "plan", "competition"],
        "tech": ["code", "programming", "software", "tech", "system"],
        "vietnam": ["vietnam", "vietnamese", "vn_legal", "vn_omni"],
        "australia": ["australia", "australian", "au_legal", "au_workforce"],
        "china": ["china", "chinese", "cn_legal"],
        "ubi": ["ubi", "biological", "somatic", "neurobiological"],
    }
    
    def __init__(self, organism_root: Path, brain_instance=None):
        self.root = organism_root
        self.brain_root = organism_root.parent / "_AMOS_BRAIN"
        self.activation_path = organism_root / "15_ENGINE_ACTIVATION"
        self.activation_path.mkdir(parents=True, exist_ok=True)
        
        # Reference to organism brain instance
        self.brain_instance = brain_instance
        
        # Engine registry
        self.engines: Dict[str, ActivatedEngine] = {}
        self.category_index: Dict[str, Set[str]] = defaultdict(set)
        self.capability_index: Dict[str, Set[str]] = defaultdict(set)
        self.domain_index: Dict[str, Set[str]] = defaultdict(set)
        
        # Loaded engine content (for large engines, lazy loaded)
        self.engine_content: Dict[str, Dict[str, Any]] = {}
        
        # Invocation handlers
        self._handlers: Dict[str, Callable] = {}
        self._initialize_handlers()
        
        # Statistics
        self.stats = {
            "engines_discovered": 0,
            "engines_activated": 0,
            "engines_loaded": 0,
            "queries_processed": 0,
            "total_invocations": 0,
            "activation_by_category": defaultdict(int),
        }
        
        logger.info(f"EngineActivationKernel initialized at {self.activation_path}")
    
    def _initialize_handlers(self):
        """Initialize engine invocation handlers."""
        self._handlers = {
            "cognitive": self._invoke_cognitive_engine,
            "tech": self._invoke_tech_engine,
            "domain": self._invoke_domain_engine,
            "unipower": self._invoke_unipower_engine,
            "core": self._invoke_core_engine,
            "intelligence": self._invoke_intelligence_engine,
        }
    
    def scan_and_discover(self) -> Dict[str, Any]:
        """Scan _AMOS_BRAIN/ and discover all engine files."""
        logger.info("Scanning for engines in _AMOS_BRAIN/...")
        
        discovered = 0
        skipped = 0
        
        for category, subpath in self.ENGINE_CATEGORIES.items():
            category_path = self.brain_root / subpath
            if not category_path.exists():
                logger.warning(f"Category path not found: {category_path}")
                continue
            
            # Find all JSON engine files
            for json_file in category_path.rglob("*.json"):
                if json_file.is_file() and ("engine" in json_file.stem.lower() or "kernel" in json_file.stem.lower()):
                    try:
                        if self._register_engine(json_file, category):
                            discovered += 1
                        else:
                            skipped += 1
                    except Exception as e:
                        logger.error(f"Failed to register {json_file}: {e}")
                        skipped += 1
        
        self.stats["engines_discovered"] = discovered
        
        logger.info(f"Discovery complete: {discovered} engines registered, {skipped} skipped")
        
        return {
            "discovered": discovered,
            "skipped": skipped,
            "by_category": {k: len(v) for k, v in self.category_index.items()},
        }
    
    def _register_engine(self, engine_file: Path, category: str) -> bool:
        """Register a single engine file."""
        # Generate engine ID
        engine_id = f"{category}/{engine_file.stem}"
        
        # Check if already registered
        if engine_id in self.engines:
            return False
        
        # Get file info
        size = engine_file.stat().st_size
        
        # Determine capabilities from name
        name_lower = engine_file.stem.lower()
        capabilities = self._extract_capabilities(name_lower)
        
        # Create engine record
        engine = ActivatedEngine(
            engine_id=engine_id,
            name=engine_file.stem,
            category=category,
            source_path=str(engine_file.relative_to(self.brain_root)),
            size_bytes=size,
            capabilities=capabilities,
            content_hash="",  # Will compute on load
        )
        
        self.engines[engine_id] = engine
        self.category_index[category].add(engine_id)
        
        # Index by capabilities
        for cap in capabilities:
            self.capability_index[cap].add(engine_id)
        
        # Index by domain
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            if any(kw in name_lower for kw in keywords):
                self.domain_index[domain].add(engine_id)
        
        return True
    
    def _extract_capabilities(self, name_lower: str) -> List[str]:
        """Extract capabilities from engine name."""
        capabilities = []
        
        if "cognition" in name_lower or "biology" in name_lower:
            capabilities.append("cognitive_reasoning")
        if "design" in name_lower:
            capabilities.append("design_systems")
        if "logic" in name_lower or "law" in name_lower:
            capabilities.append("legal_reasoning")
        if "econ" in name_lower or "finance" in name_lower:
            capabilities.append("economic_analysis")
        if "engineer" in name_lower or "math" in name_lower:
            capabilities.append("technical_computation")
        if "physics" in name_lower:
            capabilities.append("physical_systems")
        if "society" in name_lower:
            capabilities.append("social_dynamics")
        if "strategy" in name_lower:
            capabilities.append("strategic_thinking")
        if "code" in name_lower or "coding" in name_lower:
            capabilities.append("code_generation")
        if "tech" in name_lower:
            capabilities.append("technology")
        if "vietnam" in name_lower or "vn_" in name_lower:
            capabilities.append("vietnam_context")
        if "australia" in name_lower or "au_" in name_lower:
            capabilities.append("australia_context")
        if "china" in name_lower or "cn_" in name_lower:
            capabilities.append("china_context")
        
        return capabilities if capabilities else ["general"]
    
    def activate_engine(self, engine_id: str, load_content: bool = False) -> bool:
        """Activate a registered engine."""
        if engine_id not in self.engines:
            logger.error(f"Engine not found: {engine_id}")
            return False
        
        engine = self.engines[engine_id]
        
        if engine.is_active:
            logger.debug(f"Engine already active: {engine_id}")
            return True
        
        try:
            # Load content if requested and file is not too large
            if load_content and engine.size_bytes < 10 * 1024 * 1024:  # < 10MB
                self._load_engine_content(engine_id)
            
            # Mark as active
            engine.is_active = True
            engine.activation_time = datetime.utcnow().isoformat()
            
            self.stats["engines_activated"] += 1
            self.stats["activation_by_category"][engine.category] += 1
            
            logger.info(f"Activated engine: {engine_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to activate {engine_id}: {e}")
            return False
    
    def _load_engine_content(self, engine_id: str) -> bool:
        """Load engine content from file."""
        engine = self.engines[engine_id]
        engine_path = self.brain_root / engine.source_path
        
        try:
            with open(engine_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
            
            self.engine_content[engine_id] = content
            engine.is_loaded = True
            engine.content_hash = hashlib.md5(
                json.dumps(content, sort_keys=True).encode()
            ).hexdigest()[:16]
            
            self.stats["engines_loaded"] += 1
            return True
            
        except Exception as e:
            logger.error(f"Failed to load content for {engine_id}: {e}")
            return False
    
    def activate_by_category(self, category: str) -> int:
        """Activate all engines in a category."""
        engine_ids = list(self.category_index.get(category, []))
        activated = 0
        
        for engine_id in engine_ids:
            if self.activate_engine(engine_id):
                activated += 1
        
        logger.info(f"Activated {activated}/{len(engine_ids)} engines in category: {category}")
        return activated
    
    def activate_all(self, skip_large: bool = True) -> Dict[str, Any]:
        """Activate all discovered engines."""
        logger.info("Activating all discovered engines...")
        
        activated = 0
        skipped = 0
        
        for engine_id, engine in self.engines.items():
            if skip_large and engine.size_bytes > 50 * 1024 * 1024:
                logger.info(f"Skipping large engine: {engine_id} ({engine.size_bytes / 1024 / 1024:.1f} MB)")
                skipped += 1
                continue
            
            if self.activate_engine(engine_id, load_content=False):
                activated += 1
        
        return {
            "activated": activated,
            "skipped": skipped,
            "total": len(self.engines),
            "by_category": dict(self.stats["activation_by_category"]),
        }
    
    def route_query(self, query_text: str) -> List[str]:
        """Determine which engines should handle a query."""
        query_lower = query_text.lower()
        matched_engines = set()
        
        # Match by domain keywords
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            if any(kw in query_lower for kw in keywords):
                matched_engines.update(self.domain_index.get(domain, set()))
        
        # Match by capability hints in query
        capability_hints = {
            "code": "code_generation",
            "design": "design_systems",
            "law": "legal_reasoning",
            "finance": "economic_analysis",
            "strategy": "strategic_thinking",
        }
        for hint, capability in capability_hints.items():
            if hint in query_lower:
                matched_engines.update(self.capability_index.get(capability, set()))
        
        # Filter to active engines only
        active_matches = [
            eid for eid in matched_engines
            if eid in self.engines and self.engines[eid].is_active
        ]
        
        # If no matches, return fallback engines
        if not active_matches:
            fallback = [
                "cognitive/AMOS_Deterministic_Logic_And_Law_Engine_v0",
                "cognitive/AMOS_Strategy_Game_Engine_v0",
                "cognitive/AMOS_Engineering_And_Mathematics_Engine_v0",
            ]
            return [e for e in fallback if e in self.engines and self.engines[e].is_active]
        
        return active_matches[:10]  # Limit to top 10
    
    def invoke_engine(self, engine_id: str, query: EngineQuery) -> Optional[EngineResponse]:
        """Invoke a specific engine for a query."""
        if engine_id not in self.engines:
            return None
        
        engine = self.engines[engine_id]
        
        if not engine.is_active:
            logger.warning(f"Engine not active: {engine_id}")
            return None
        
        try:
            # Get handler for category
            handler = self._handlers.get(engine.category, self._invoke_generic)
            
            # Invoke
            start_time = datetime.utcnow()
            result = handler(engine, query)
            elapsed = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Update stats
            engine.invoke_count += 1
            engine.last_invoked = datetime.utcnow().isoformat()
            self.stats["total_invocations"] += 1
            
            return EngineResponse(
                engine_id=engine_id,
                engine_name=engine.name,
                success=True,
                result=result,
                confidence=result.get("confidence", 0.7),
                processing_time_ms=elapsed,
            )
            
        except Exception as e:
            logger.error(f"Engine invocation failed {engine_id}: {e}")
            return EngineResponse(
                engine_id=engine_id,
                engine_name=engine.name,
                success=False,
                result={"error": str(e)},
                confidence=0.0,
            )
    
    def process_query(self, query_text: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Process a query through the appropriate engines."""
        self.stats["queries_processed"] += 1
        
        # Create query object
        query = EngineQuery(
            query_id=f"qry_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            text=query_text,
            context=context or {},
        )
        
        # Route to engines
        engine_ids = self.route_query(query_text)
        
        # Invoke each engine
        responses = []
        for engine_id in engine_ids:
            response = self.invoke_engine(engine_id, query)
            if response:
                responses.append(response)
        
        # Aggregate results
        return {
            "query_id": query.query_id,
            "query_text": query_text,
            "engines_used": [r.engine_id for r in responses],
            "responses": [r.to_dict() for r in responses],
            "successful": sum(1 for r in responses if r.success),
            "failed": sum(1 for r in responses if not r.success),
            "average_confidence": sum(r.confidence for r in responses) / len(responses) if responses else 0,
        }
    
    # Invocation handlers by category
    def _invoke_cognitive_engine(self, engine: ActivatedEngine, query: EngineQuery) -> Dict[str, Any]:
        """Invoke a cognitive engine."""
        return {
            "type": "cognitive_analysis",
            "engine": engine.name,
            "query": query.text,
            "principles_applied": ["rule_of_2", "rule_of_4"],
            "confidence": 0.85,
        }
    
    def _invoke_tech_engine(self, engine: ActivatedEngine, query: EngineQuery) -> Dict[str, Any]:
        """Invoke a tech kernel."""
        return {
            "type": "technical_analysis",
            "engine": engine.name,
            "query": query.text,
            "recommendations": ["scalable", "secure", "maintainable"],
            "confidence": 0.80,
        }
    
    def _invoke_domain_engine(self, engine: ActivatedEngine, query: EngineQuery) -> Dict[str, Any]:
        """Invoke a domain engine."""
        return {
            "type": "domain_analysis",
            "engine": engine.name,
            "query": query.text,
            "domain_specific": True,
            "confidence": 0.75,
        }
    
    def _invoke_unipower_engine(self, engine: ActivatedEngine, query: EngineQuery) -> Dict[str, Any]:
        """Invoke a unipower engine."""
        return {
            "type": "unipower_analysis",
            "engine": engine.name,
            "query": query.text,
            "ecosystem_context": True,
            "confidence": 0.80,
        }
    
    def _invoke_core_engine(self, engine: ActivatedEngine, query: EngineQuery) -> Dict[str, Any]:
        """Invoke a core engine."""
        return {
            "type": "core_processing",
            "engine": engine.name,
            "query": query.text,
            "master_os": "AMOS_Brain_Master_Os_v0" in engine.name,
            "confidence": 0.90,
        }
    
    def _invoke_intelligence_engine(self, engine: ActivatedEngine, query: EngineQuery) -> Dict[str, Any]:
        """Invoke a 7 Intelligences engine."""
        return {
            "type": "intelligence_analysis",
            "engine": engine.name,
            "query": query.text,
            "intelligence_domain": engine.name.replace("AMOS_", "").replace("_Engine_v0", ""),
            "confidence": 0.85,
        }
    
    def _invoke_generic(self, engine: ActivatedEngine, query: EngineQuery) -> Dict[str, Any]:
        """Generic engine invocation."""
        return {
            "type": "generic",
            "engine": engine.name,
            "query": query.text,
            "confidence": 0.70,
        }
    
    def get_state(self) -> Dict[str, Any]:
        """Get current activation state."""
        return {
            "engines_discovered": len(self.engines),
            "engines_activated": self.stats["engines_activated"],
            "engines_loaded": self.stats["engines_loaded"],
            "queries_processed": self.stats["queries_processed"],
            "total_invocations": self.stats["total_invocations"],
            "by_category": {k: len(v) for k, v in self.category_index.items()},
            "activation_by_category": dict(self.stats["activation_by_category"]),
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    def get_engine_stats(self) -> Dict[str, Any]:
        """Get detailed engine statistics."""
        active_engines = [e for e in self.engines.values() if e.is_active]
        
        # Find most invoked
        most_invoked = sorted(
            active_engines,
            key=lambda e: e.invoke_count,
            reverse=True
        )[:10]
        
        # Category breakdown
        category_stats = {}
        for cat, engine_ids in self.category_index.items():
            active_count = sum(1 for eid in engine_ids if self.engines[eid].is_active)
            category_stats[cat] = {
                "total": len(engine_ids),
                "active": active_count,
            }
        
        return {
            "total_engines": len(self.engines),
            "active_engines": len(active_engines),
            "inactive_engines": len(self.engines) - len(active_engines),
            "most_invoked": [(e.name, e.invoke_count) for e in most_invoked],
            "category_breakdown": category_stats,
        }
    
    def shutdown(self):
        """Shutdown and cleanup."""
        logger.info("EngineActivationKernel shutdown complete")


if __name__ == "__main__":
    # Test the engine activation kernel
    import sys
    root = Path(__file__).parent.parent
    
    print("=" * 60)
    print("AMOS Engine Activation Kernel - Test")
    print("=" * 60)
    
    activation = EngineActivationKernel(root)
    
    print("\n=== Test 1: Discovery ===")
    discovery = activation.scan_and_discover()
    print(f"Discovered: {discovery['discovered']} engines")
    print(f"By category: {discovery['by_category']}")
    
    print("\n=== Test 2: Activate by Category ===")
    for category in ["cognitive", "tech", "core"]:
        count = activation.activate_by_category(category)
        print(f"Activated {count} {category} engines")
    
    print("\n=== Test 3: Query Routing ===")
    test_queries = [
        "How do I design a secure API?",
        "What are the legal requirements in Vietnam?",
        "Explain quantum computing",
        "Analyze this biological data",
    ]
    
    for query in test_queries:
        engines = activation.route_query(query)
        print(f"\nQuery: '{query}'")
        print(f"  Routed to: {len(engines)} engines")
        for eid in engines[:3]:
            print(f"    - {eid}")
    
    print("\n=== Test 4: Process Query ===")
    result = activation.process_query("Design a secure API for financial transactions")
    print(f"Query ID: {result['query_id']}")
    print(f"Engines used: {result['engines_used']}")
    print(f"Successful: {result['successful']}")
    print(f"Average confidence: {result['average_confidence']:.2f}")
    
    print("\n=== Test 5: State Summary ===")
    state = activation.get_state()
    print(json.dumps(state, indent=2))
    
    print("\n=== Test 6: Engine Stats ===")
    stats = activation.get_engine_stats()
    print(f"Total: {stats['total_engines']}")
    print(f"Active: {stats['active_engines']}")
    print(f"Most invoked: {stats['most_invoked'][:3]}")
    
    activation.shutdown()
    print("\n" + "=" * 60)
    print("Engine Activation Kernel test complete!")
    print("=" * 60)
