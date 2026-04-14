#!/usr/bin/env python3
"""AMOS Knowledge Discovery Interface
=================================
Unified search and discovery for the complete AMOS knowledge ecosystem.

Features:
- Search 963+ JSON engines by name, domain, or content
- Browse 72 PDF manuals and training materials
- Query 55 country knowledge packs
- Access 19 sector packs
- Discovery mode for exploring unknown capabilities

Usage:
    python amos_knowledge_discovery.py [command] [options]

Commands:
    search <query>       Search all knowledge files
    list <category>      List engines by category (cognitive, tech, domains, etc.)
    browse               Interactive browser for all knowledge
    stats                Show ecosystem statistics
    load <engine>        Load specific engine into runtime
    pdf <name>           Find and list PDF manuals
    country <code>       Access country knowledge pack
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

sys.path.insert(0, str(Path(__file__).parent / "clawspring"))
sys.path.insert(0, str(Path(__file__).parent))


@dataclass
class KnowledgeItem:
    """Represents a knowledge item in the ecosystem."""

    name: str
    path: Path
    category: str
    size_bytes: int
    modified: datetime
    metadata: dict[str, Any] = field(default_factory=dict)


class KnowledgeDiscovery:
    """Discover and search the AMOS knowledge ecosystem."""

    def __init__(self, brain_root: Optional[Path] = None):
        self.brain_root = brain_root or Path(__file__).parent / "_AMOS_BRAIN"
        self.index: dict[str, list[KnowledgeItem]] = {
            "cognitive": [],
            "tech": [],
            "domains": [],
            "unipower": [],
            "kernels": [],
            "core": [],
            "packs": [],
            "training": [],
            "archive": [],
        }
        self.stats = {
            "total_files": 0,
            "total_size_mb": 0.0,
            "json_engines": 0,
            "pdf_manuals": 0,
            "txt_specs": 0,
        }

    def scan(self) -> dict[str, Any]:
        """Scan entire _AMOS_BRAIN directory and build index."""
        print("=" * 70)
        print("AMOS KNOWLEDGE DISCOVERY - SCANNING ECOSYSTEM")
        print("=" * 70)
        print(f"\nScanning: {self.brain_root}")

        if not self.brain_root.exists():
            return {"error": f"Brain root not found: {self.brain_root}"}

        # Scan all files
        all_files = list(self.brain_root.rglob("*"))
        total_size = 0

        for file_path in all_files:
            if file_path.is_file():
                self.stats["total_files"] += 1
                size = file_path.stat().st_size
                total_size += size

                # Categorize
                category = self._categorize(file_path)
                item = KnowledgeItem(
                    name=file_path.stem,
                    path=file_path,
                    category=category,
                    size_bytes=size,
                    modified=datetime.fromtimestamp(file_path.stat().st_mtime),
                )

                if category in self.index:
                    self.index[category].append(item)

                # Track by type
                if file_path.suffix == ".json":
                    self.stats["json_engines"] += 1
                elif file_path.suffix == ".pdf":
                    self.stats["pdf_manuals"] += 1
                elif file_path.suffix == ".txt":
                    self.stats["txt_specs"] += 1

        self.stats["total_size_mb"] = round(total_size / (1024 * 1024), 2)

        # Print summary
        print("\n✅ Scan Complete")
        print(f"  Total Files: {self.stats['total_files']}")
        print(f"  Total Size: {self.stats['total_size_mb']} MB")
        print(f"  JSON Engines: {self.stats['json_engines']}")
        print(f"  PDF Manuals: {self.stats['pdf_manuals']}")
        print(f"  Text Specs: {self.stats['txt_specs']}")
        print("\nBy Category:")
        for cat, items in sorted(self.index.items()):
            if items:
                cat_size = sum(i.size_bytes for i in items) / (1024 * 1024)
                print(f"  {cat:15s}: {len(items):4d} files ({cat_size:.1f} MB)")

        return self.stats

    def _categorize(self, path: Path) -> str:
        """Categorize a file based on its path."""
        path_str = str(path).lower()

        if "/training/" in path_str:
            return "training"
        elif "/cognitive/" in path_str:
            return "cognitive"
        elif "/kernels/tech/" in path_str:
            return "tech"
        elif "/kernels/" in path_str:
            return "kernels"
        elif "/domains/" in path_str:
            return "domains"
        elif "/unipower/" in path_str:
            return "unipower"
        elif "/packs/" in path_str:
            return "packs"
        elif "/core/" in path_str:
            return "core"
        elif "/_archive/" in path_str:
            return "archive"
        else:
            return "other"

    def search(self, query: str) -> list[KnowledgeItem]:
        """Search all knowledge by name or content."""
        query_lower = query.lower()
        results = []

        for category, items in self.index.items():
            for item in items:
                # Search in filename
                if query_lower in item.name.lower():
                    results.append(item)
                    continue

                # For JSON files, search in content
                if item.path.suffix == ".json" and item.size_bytes < 1000000:  # < 1MB
                    try:
                        with open(item.path, encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                            if query_lower in content.lower():
                                results.append(item)
                    except:
                        pass

        return results

    def list_category(self, category: str) -> list[KnowledgeItem]:
        """List all items in a category."""
        return self.index.get(category, [])

    def get_pdf_manuals(self) -> list[KnowledgeItem]:
        """Get all PDF training manuals."""
        pdfs = []
        for category, items in self.index.items():
            for item in items:
                if item.path.suffix == ".pdf":
                    pdfs.append(item)
        return sorted(pdfs, key=lambda x: x.size_bytes, reverse=True)

    def get_country_packs(self) -> list[KnowledgeItem]:
        """Get all country knowledge packs."""
        return [
            i
            for i in self.index.get("packs", [])
            if "country" in str(i.path).lower() or "vn_" in i.name.lower()
        ]

    def print_stats(self):
        """Print detailed statistics."""
        print("\n" + "=" * 70)
        print("AMOS KNOWLEDGE ECOSYSTEM STATISTICS")
        print("=" * 70)
        print(f"\nTotal Files: {self.stats['total_files']}")
        print(f"Total Size: {self.stats['total_size_mb']:.2f} MB")
        print("\nBreakdown:")
        print(f"  JSON Engines: {self.stats['json_engines']}")
        print(f"  PDF Manuals: {self.stats['pdf_manuals']}")
        print(f"  Text Specs: {self.stats['txt_specs']}")

        print("\nTop 10 Largest Files:")
        all_items = []
        for items in self.index.values():
            all_items.extend(items)

        for item in sorted(all_items, key=lambda x: x.size_bytes, reverse=True)[:10]:
            size_mb = item.size_bytes / (1024 * 1024)
            print(f"  {size_mb:8.2f} MB | {item.name[:50]}")

    def browse_interactive(self):
        """Interactive browser for knowledge discovery."""
        print("\n" + "=" * 70)
        print("AMOS KNOWLEDGE BROWSER")
        print("=" * 70)
        print("\nCommands:")
        print("  1. list <category>  - List files by category")
        print("  2. search <query>   - Search all knowledge")
        print("  3. pdfs             - List all PDF manuals")
        print("  4. countries        - List country packs")
        print("  5. stats            - Show statistics")
        print("  6. quit             - Exit browser")
        print(
            "\nCategories: cognitive, tech, domains, unipower, kernels, core, packs, training, archive"
        )

        while True:
            try:
                cmd = input("\n> ").strip().split()
                if not cmd:
                    continue

                if cmd[0] == "quit":
                    break
                elif cmd[0] == "stats":
                    self.print_stats()
                elif cmd[0] == "pdfs":
                    pdfs = self.get_pdf_manuals()
                    print(f"\nPDF Manuals ({len(pdfs)}):")
                    for pdf in pdfs[:20]:
                        size_mb = pdf.size_bytes / (1024 * 1024)
                        print(f"  {size_mb:6.2f} MB | {pdf.name[:60]}")
                elif cmd[0] == "countries":
                    countries = self.get_country_packs()
                    print(f"\nCountry Packs ({len(countries)}):")
                    for c in countries[:20]:
                        print(f"  {c.name[:50]}")
                elif cmd[0] == "list" and len(cmd) > 1:
                    items = self.list_category(cmd[1])
                    print(f"\n{cmd[1].upper()} ({len(items)} files):")
                    for item in sorted(items, key=lambda x: x.size_bytes, reverse=True)[:20]:
                        size_kb = item.size_bytes / 1024
                        print(f"  {size_kb:8.1f} KB | {item.name[:50]}")
                elif cmd[0] == "search" and len(cmd) > 1:
                    query = " ".join(cmd[1:])
                    results = self.search(query)
                    print(f"\nSearch Results for '{query}' ({len(results)} found):")
                    for r in results[:20]:
                        size_kb = r.size_bytes / 1024
                        print(f"  [{r.category:12s}] {size_kb:8.1f} KB | {r.name[:40]}")
                else:
                    print("Unknown command. Type 'quit' to exit.")
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")

        print("\nGoodbye!")


def main():
    parser = argparse.ArgumentParser(
        description="AMOS Knowledge Discovery Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python amos_knowledge_discovery.py scan
  python amos_knowledge_discovery.py stats
  python amos_knowledge_discovery.py search "biology"
  python amos_knowledge_discovery.py list cognitive
  python amos_knowledge_discovery.py browse
        """,
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="scan",
        choices=["scan", "stats", "search", "list", "browse", "pdfs", "countries"],
    )
    parser.add_argument("query", nargs="?", help="Search query or category")

    args = parser.parse_args()

    discovery = KnowledgeDiscovery()

    if args.command == "scan":
        discovery.scan()
    elif args.command == "stats":
        discovery.scan()
        discovery.print_stats()
    elif args.command == "search":
        discovery.scan()
        if args.query:
            results = discovery.search(args.query)
            print(f"\nFound {len(results)} results for '{args.query}':")
            for r in results[:30]:
                size_kb = r.size_bytes / 1024
                print(f"  [{r.category:12s}] {size_kb:8.1f} KB | {r.name[:50]}")
    elif args.command == "list":
        discovery.scan()
        if args.query:
            items = discovery.list_category(args.query)
            print(f"\n{args.query.upper()} ({len(items)} files):")
            for item in sorted(items, key=lambda x: x.size_bytes, reverse=True)[:30]:
                size_kb = item.size_bytes / 1024
                print(f"  {size_kb:8.1f} KB | {item.name[:50]}")
    elif args.command == "pdfs":
        discovery.scan()
        pdfs = discovery.get_pdf_manuals()
        print(f"\nPDF Manuals ({len(pdfs)}):")
        for pdf in pdfs:
            size_mb = pdf.size_bytes / (1024 * 1024)
            print(f"  {size_mb:6.2f} MB | {pdf.name[:60]}")
    elif args.command == "countries":
        discovery.scan()
        countries = discovery.get_country_packs()
        print(f"\nCountry Packs ({len(countries)}):")
        for c in countries:
            size_kb = c.size_bytes / 1024
            print(f"  {size_kb:8.1f} KB | {c.name[:50]}")
    elif args.command == "browse":
        discovery.scan()
        discovery.browse_interactive()

    return 0


if __name__ == "__main__":
    sys.exit(main())
