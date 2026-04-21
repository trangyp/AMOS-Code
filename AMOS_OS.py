#!/usr/bin/env python3
"""AMOS OS - Canonical Operating System Interface

The unified OS layer for AMOS Canonical system.
Integrates all 6 repositories into a single coherent interface.

Usage:
    from AMOS_OS import get_os
    os = get_os()
    os.activate()
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# Root path setup
REPO_ROOT = Path(__file__).parent
sys.path.insert(0, str(REPO_ROOT))

# Import 6-repo components
sys.path.insert(0, str(REPO_ROOT / "AMOS_REPOS" / "AMOS-Code"))
sys.path.insert(0, str(REPO_ROOT / "AMOS_REPOS" / "AMOS-Consulting"))
sys.path.insert(0, str(REPO_ROOT / "AMOS_REPOS" / "AMOS-Claws"))
sys.path.insert(0, str(REPO_ROOT / "AMOS_REPOS" / "Mailinhconect"))
sys.path.insert(0, str(REPO_ROOT / "AMOS_REPOS" / "AMOS-Invest"))
sys.path.insert(0, str(REPO_ROOT / "AMOS_REPOS" / "AMOS-UNIVERSE"))


class AMOSOS:
    """Canonical AMOS Operating System.
    
    Provides unified access to:
    - 6 Repository Integration
    - 15 Organism Subsystems  
    - 100+ Cognitive Engines
    - Brain Interface
    """
    
    _instance: AMOSOS | None = None
    
    def __new__(cls) -> AMOSOS:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.root = REPO_ROOT
        self.repos: dict[str, Path] = {
            "AMOS-Code": REPO_ROOT / "AMOS_REPOS" / "AMOS-Code",
            "AMOS-Consulting": REPO_ROOT / "AMOS_REPOS" / "AMOS-Consulting",
            "AMOS-Claws": REPO_ROOT / "AMOS_REPOS" / "AMOS-Claws",
            "Mailinhconect": REPO_ROOT / "AMOS_REPOS" / "Mailinhconect",
            "AMOS-Invest": REPO_ROOT / "AMOS_REPOS" / "AMOS-Invest",
            "AMOS-UNIVERSE": REPO_ROOT / "AMOS_REPOS" / "AMOS-UNIVERSE",
        }
        self.organism_path = REPO_ROOT / "AMOS_ORGANISM_OS"
        self.status = "initialized"
        
    def activate(self) -> bool:
        """Activate full AMOS OS."""
        print("=" * 70)
        print("AMOS OS - ACTIVATION")
        print("=" * 70)
        
        # Check all 6 repos
        for name, path in self.repos.items():
            if path.exists():
                print(f"  ✓ {name}: linked")
            else:
                print(f"  ✗ {name}: missing")
        
        # Check organism
        if self.organism_path.exists():
            print(f"  ✓ Organism OS: {len(list(self.organism_path.iterdir()))} items")
        
        self.status = "active"
        print("=" * 70)
        return True
    
    def get_repo_path(self, name: str) -> Path | None:
        """Get path to a specific repository."""
        return self.repos.get(name)
    
    def get_canon_path(self) -> Path:
        """Get canonical _AMOS_CANON path."""
        return REPO_ROOT / "_00_AMOS_CANON"


# Global singleton
_amos_os: AMOSOS | None = None


def get_os() -> AMOSOS:
    """Get the canonical AMOS OS instance."""
    global _amos_os
    if _amos_os is None:
        _amos_os = AMOSOS()
    return _amos_os


if __name__ == "__main__":
    os = get_os()
    os.activate()
