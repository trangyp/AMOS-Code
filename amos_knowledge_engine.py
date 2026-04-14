#!/usr/bin/env python3
"""
AMOS Knowledge Engine Integration (Layer 23)
===============================================

Connects the 160+ knowledge engines from _AMOS_BRAIN/ to the Brain.
Provides unified access to:
- 30 Tech Kernels
- 13 Cognitive Engines  
- 17 Unipower Engines
- 55 Country Packs
- 19 Sector Packs
- Domain-specific engines

Usage:
    from amos_knowledge_engine import KnowledgeEngine
    
    ke = KnowledgeEngine()
    ke.load_all_engines()
    
    # Query specific domain
    result = ke.query("software", "How to design a scalable API?")
    result = ke.query("legal", "What are compliance requirements?")

Creator: Trang Phan
System: AMOS vInfinity - Layer 23
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class EngineInfo:
    """Information about a knowledge engine."""
    name: str
    domain: str
    path: str
    size: int
    loaded: bool = False


class KnowledgeEngine:
    """
    Knowledge Engine Integrator - Layer 23.
    
    Manages 160+ engines from _AMOS_BRAIN/:
    - Tech Kernels (30): Automation, Coding, Design, ML, Cloud, Security
    - Cognitive Engines (13): Biology, Design, Law, Econ, Math, Physics, Society
    - Unipower Engines (17): Global operations, regional intelligence
    - Domain Engines (15+): Country, sector, state packs
    
    Provides unified query interface across all domains.
    """
    
    KNOWLEDGE_PATH = Path("_AMOS_BRAIN")
    
    def __init__(self):
        self.engines: Dict[str, EngineInfo] = {}
        self.loaded_count = 0
        self.domains: set = set()
        
    def discover_engines(self) -> Dict[str, int]:
        """
        Discover all available knowledge engines.
        
        Returns:
            Summary of discovered engines by category
        """
        discovered = {
            "tech_kernels": 0,
            "cognitive": 0,
            "unipower": 0,
            "domains": 0,
            "country_packs": 0,
            "sector_packs": 0,
            "total": 0
        }
        
        knowledge_path = Path(self.KNOWLEDGE_PATH)
        if not knowledge_path.exists():
            return discovered
            
        # Discover Tech Kernels
        tech_path = knowledge_path / "Kernels" / "Tech"
        if tech_path.exists():
            for f in tech_path.glob("*.json"):
                name = f.stem
                self.engines[name] = EngineInfo(
                    name=name,
                    domain="tech",
                    path=str(f),
                    size=f.stat().st_size
                )
                discovered["tech_kernels"] += 1
                self.domains.add("tech")
                
        # Discover Cognitive Engines
        cognitive_path = knowledge_path / "Cognitive"
        if cognitive_path.exists():
            for f in cognitive_path.glob("*.json"):
                name = f.stem
                self.engines[name] = EngineInfo(
                    name=name,
                    domain="cognitive",
                    path=str(f),
                    size=f.stat().st_size
                )
                discovered["cognitive"] += 1
                self.domains.add("cognitive")
                
        # Discover Unipower Engines
        unipower_path = knowledge_path / "Unipower"
        if unipower_path.exists():
            for f in unipower_path.glob("*.json"):
                name = f.stem
                self.engines[name] = EngineInfo(
                    name=name,
                    domain="unipower",
                    path=str(f),
                    size=f.stat().st_size
                )
                discovered["unipower"] += 1
                self.domains.add("unipower")
                
        # Discover Domain Engines
        domains_path = knowledge_path / "Domains"
        if domains_path.exists():
            for f in domains_path.glob("*.json"):
                name = f.stem
                self.engines[name] = EngineInfo(
                    name=name,
                    domain="domain",
                    path=str(f),
                    size=f.stat().st_size
                )
                discovered["domains"] += 1
                self.domains.add("domain")
                
        # Count packs
        country_path = knowledge_path / "Packs" / "Country_Packs"
        if country_path.exists():
            discovered["country_packs"] = len(list(country_path.iterdir()))
            
        sector_path = knowledge_path / "Packs" / "Sector_Packs"
        if sector_path.exists():
            discovered["sector_packs"] = len(list(sector_path.iterdir()))
            
        discovered["total"] = len(self.engines)
        return discovered
    
    def load_engine(self, engine_name: str) -> Optional[Dict[str, Any]]:
        """Load a specific engine by name."""
        if engine_name not in self.engines:
            return None
            
        engine = self.engines[engine_name]
        try:
            with open(engine.path, 'r') as f:
                data = json.load(f)
                engine.loaded = True
                self.loaded_count += 1
                return data
        except Exception as e:
            return {"error": str(e)}
            
    def query(self, domain: str, question: str) -> Dict[str, Any]:
        """
        Query knowledge engines in a domain.
        
        Args:
            domain: Domain to query (tech, cognitive, legal, etc.)
            question: Question to answer
            
        Returns:
            Query results with cognitive analysis
        """
        # Get brain guidance
        from amos_brain import think
        brain_response = think(f"Query {domain}: {question}")
        
        # Find relevant engines
        relevant = [
            e for e in self.engines.values()
            if e.domain == domain or domain in e.name.lower()
        ]
        
        return {
            "domain": domain,
            "question": question,
            "brain_reasoning": brain_response.reasoning[:3],
            "relevant_engines": len(relevant),
            "engines": [e.name for e in relevant[:5]],
            "law_compliant": brain_response.law_compliant,
            "confidence": brain_response.confidence,
            "layer": "L23"
        }
    
    def get_engine_info(self, engine_name: str) -> Optional[EngineInfo]:
        """Get information about a specific engine."""
        return self.engines.get(engine_name)
    
    def list_domains(self) -> List[str]:
        """List all available knowledge domains."""
        return sorted(list(self.domains))
    
    def list_engines(self, domain: Optional[str] = None) -> List[str]:
        """List all engines, optionally filtered by domain."""
        if domain:
            return sorted([e.name for e in self.engines.values() if e.domain == domain])
        return sorted(list(self.engines.keys()))
    
    def status(self) -> Dict[str, Any]:
        """Get knowledge engine status."""
        return {
            "total_engines": len(self.engines),
            "loaded_engines": self.loaded_count,
            "domains": len(self.domains),
            "domain_list": self.list_domains(),
            "layer": 23,
            "status": "active"
        }


# Global instance
_knowledge_engine: Optional[KnowledgeEngine] = None


def get_knowledge_engine() -> KnowledgeEngine:
    """Get global knowledge engine instance."""
    global _knowledge_engine
    if _knowledge_engine is None:
        _knowledge_engine = KnowledgeEngine()
        _knowledge_engine.discover_engines()
    return _knowledge_engine


def query_knowledge(domain: str, question: str) -> Dict[str, Any]:
    """Quick knowledge query."""
    return get_knowledge_engine().query(domain, question)


def list_knowledge_domains() -> List[str]:
    """List available knowledge domains."""
    return get_knowledge_engine().list_domains()


if __name__ == "__main__":
    print("=" * 70)
    print("AMOS Knowledge Engine Integration (Layer 23)")
    print("=" * 70)
    print()
    
    ke = KnowledgeEngine()
    discovered = ke.discover_engines()
    
    print("Knowledge Engine Discovery:")
    print(f"  Tech Kernels: {discovered['tech_kernels']}")
    print(f"  Cognitive Engines: {discovered['cognitive']}")
    print(f"  Unipower Engines: {discovered['unipower']}")
    print(f"  Domain Engines: {discovered['domains']}")
    print(f"  Country Packs: {discovered['country_packs']}")
    print(f"  Sector Packs: {discovered['sector_packs']}")
    print(f"  Total Engines: {discovered['total']}")
    print()
    
    print(f"Domains: {', '.join(ke.list_domains())}")
    print()
    
    # Sample query
    print("Sample Query (tech domain):")
    result = ke.query("tech", "Best practices for API design")
    print(f"  Relevant engines: {result['relevant_engines']}")
    print(f"  Brain reasoning: {result['brain_reasoning'][0]}")
    print()
    
    print("=" * 70)
    print("Layer 23: Knowledge Engine Integration - Active")
    print("=" * 70)
