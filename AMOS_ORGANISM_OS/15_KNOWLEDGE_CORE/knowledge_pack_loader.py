#!/usr/bin/env python3
"""Knowledge Pack Loader - KNOWLEDGE_CORE Subsystem
==================================================

Discovers and loads knowledge packs from _AMOS_BRAIN/Packs/.
Provides structured access to country, sector, and scenario data.

Owner: Trang
Version: 1.0.0
"""

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class KnowledgePack:
    """Represents a loaded knowledge pack."""

    name: str
    version: str
    description: str
    pack_type: str  # country, sector, scenario, etc.
    data: Dict[str, Any]
    file_path: Path
    size_bytes: int
    metadata: Dict[str, Any] = field(default_factory=dict)


class KnowledgePackLoader:
    """Discovers and loads knowledge packs from _AMOS_BRAIN.

    Pack Types:
    - Country Packs: Nation-specific knowledge (Vietnam, etc.)
    - Sector Packs: Industry-specific knowledge
    - Scenario Packs: Scenario-based knowledge
    - State Packs: State/province-level knowledge
    """

    PACKS_DIR = Path(__file__).parent.parent.parent / "_AMOS_BRAIN" / "Packs"

    def __init__(self):
        self.packs: Dict[str, KnowledgePack] = {}
        self._loaded = False
        self._stats = {"country_packs": 0, "sector_packs": 0, "scenario_packs": 0, "state_packs": 0}

    def load_all_packs(self) -> dict[str, KnowledgePack]:
        """Discover and load all knowledge packs."""
        if not self.PACKS_DIR.exists():
            print(f"[KNOWLEDGE] Packs directory not found: {self.PACKS_DIR}")
            return {}

        # Discover packs in all subdirectories
        pack_dirs = [
            self.PACKS_DIR / "Country_Packs",
            self.PACKS_DIR / "Sector_Packs",
            self.PACKS_DIR / "Scenario_Packs",
            self.PACKS_DIR / "State_Packs",
        ]

        total_files = 0
        for pack_dir in pack_dirs:
            if pack_dir.exists():
                json_files = list(pack_dir.glob("*.json"))
                total_files += len(json_files)

                for file_path in json_files:
                    try:
                        pack = self._load_pack(file_path)
                        if pack:
                            self.packs[pack.name] = pack
                            self._update_stats(pack.pack_type)
                    except Exception as e:
                        print(f"  ✗ Failed to load: {file_path.name} - {e}")

        self._loaded = True
        print(f"[KNOWLEDGE] Loaded {len(self.packs)} knowledge packs from {total_files} files")
        return self.packs

    def _load_pack(self, file_path: Path) -> Optional[KnowledgePack]:
        """Load a single knowledge pack."""
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        # Extract metadata
        meta = {}
        if isinstance(data, dict):
            meta = data.get("meta", {})
        elif isinstance(data, list) and len(data) > 0:
            meta = data[0].get("meta", {})

        name = meta.get("name", file_path.stem)
        version = meta.get("version", "v0")
        description = meta.get("description", "Knowledge pack")

        # Determine pack type from directory
        pack_type = self._determine_pack_type(file_path)

        return KnowledgePack(
            name=name,
            version=version,
            description=description,
            pack_type=pack_type,
            data=data,
            file_path=file_path,
            size_bytes=file_path.stat().st_size,
            metadata=meta,
        )

    def _determine_pack_type(self, file_path: Path) -> str:
        """Determine pack type from file path."""
        parent = file_path.parent.name.lower()
        if "country" in parent:
            return "country"
        elif "sector" in parent:
            return "sector"
        elif "scenario" in parent:
            return "scenario"
        elif "state" in parent:
            return "state"
        return "unknown"

    def _update_stats(self, pack_type: str):
        """Update pack statistics."""
        if pack_type == "country":
            self._stats["country_packs"] += 1
        elif pack_type == "sector":
            self._stats["sector_packs"] += 1
        elif pack_type == "scenario":
            self._stats["scenario_packs"] += 1
        elif pack_type == "state":
            self._stats["state_packs"] += 1

    def get_pack(self, name: str) -> Optional[KnowledgePack]:
        """Get a specific knowledge pack by name."""
        if not self._loaded:
            self.load_all_packs()
        return self.packs.get(name)

    def query_packs_by_type(self, pack_type: str) -> List[KnowledgePack]:
        """Query packs by type."""
        if not self._loaded:
            self.load_all_packs()
        return [p for p in self.packs.values() if p.pack_type == pack_type]

    def get_country_pack(self, country_name: str) -> Optional[KnowledgePack]:
        """Get pack for a specific country."""
        if not self._loaded:
            self.load_all_packs()

        for pack in self.packs.values():
            if pack.pack_type == "country":
                country = pack.metadata.get("country_name", "")
                if country and country.lower() == country_name.lower():
                    return pack
        return None

    def get_status(self) -> Dict[str, Any]:
        """Get loader status and statistics."""
        if not self._loaded:
            self.load_all_packs()

        total_size = sum(p.size_bytes for p in self.packs.values())

        return {
            "loaded": self._loaded,
            "total_packs": len(self.packs),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "stats": self._stats,
            "pack_names": list(self.packs.keys())[:10],  # First 10
        }


def main():
    """CLI demo of knowledge pack loader."""
    print("=" * 60)
    print("AMOS Knowledge Pack Loader")
    print("=" * 60)

    loader = KnowledgePackLoader()
    status = loader.get_status()

    print("\nStatus:")
    print(f"  Packs loaded: {status['total_packs']}")
    print(f"  Total size: {status['total_size_mb']} MB")

    print("\nPack Distribution:")
    for pack_type, count in status["stats"].items():
        if count > 0:
            print(f"  - {pack_type}: {count}")

    print("\nSample Packs:")
    for name in status["pack_names"][:5]:
        pack = loader.get_pack(name)
        if pack:
            size_kb = round(pack.size_bytes / 1024, 1)
            print(f"  ✓ {name}")
            print(f"    Type: {pack.pack_type}")
            print(f"    Size: {size_kb} KB")

    # Demo query
    print("\nDemo: Query Country Packs")
    country_packs = loader.query_packs_by_type("country")
    print(f"  Found {len(country_packs)} country packs")
    for pack in country_packs[:3]:
        country = pack.metadata.get("country_name", "Unknown")
        print(f"    - {pack.name} ({country})")

    print("\n" + "=" * 60)
    print("Knowledge Pack Loader ready")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
