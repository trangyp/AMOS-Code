#!/usr/bin/env python3
"""AMOS Knowledge Explorer - Navigate the 1,110+ knowledge files.

A knowledge compass that indexes and searches the massive AMOS knowledge base
in _AMOS_BRAIN/, making 4,000+ files accessible and usable.

Usage:
    python amos_knowledge_explorer.py
    python amos_knowledge_explorer.py search "consulting"
    python amos_knowledge_explorer.py map
    python amos_knowledge_explorer.py stats
"""

import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class KnowledgeFile:
    """Represents a knowledge file in the brain."""

    path: Path
    name: str
    size_bytes: int
    category: str
    domain: str
    engine_type: str
    relevance_score: float = 0.0

    @property
    def size_human(self) -> str:
        """Human-readable file size."""
        size = self.size_bytes
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"


class KnowledgeExplorer:
    """Explorer for the AMOS knowledge base.

    Indexes _AMOS_BRAIN/ structure and provides search capabilities
    across 1,110+ knowledge files, 55 kernels, 54 country packs, etc.
    """

    def __init__(self, brain_root: Path | None = None):
        self.brain_root = brain_root or Path(__file__).parent / "_AMOS_BRAIN"
        self._index: list[KnowledgeFile] = []
        self._categories: dict[str, int] = {}
        self._domains: dict[str, int] = {}
        self._indexed = False

    def index(self) -> KnowledgeExplorer:
        """Build index of all knowledge files."""
        if not self.brain_root.exists():
            print(f"❌ Brain root not found: {self.brain_root}")
            return self

        print("🔍 Indexing AMOS Knowledge Base...")
        print(f"   Root: {self.brain_root}")

        # Scan all JSON and TXT files
        for ext in ["*.json", "*.txt", "*.md"]:
            for file_path in self.brain_root.rglob(ext):
                if file_path.is_file():
                    self._add_to_index(file_path)

        self._indexed = True
        self._calculate_stats()

        print(f"✓ Indexed {len(self._index)} knowledge files")
        print(f"✓ Found {len(self._categories)} categories")
        print(f"✓ Found {len(self._domains)} domains")

        return self

    def _add_to_index(self, path: Path) -> None:
        """Add a file to the index."""
        # Determine category from path
        rel_path = path.relative_to(self.brain_root)
        parts = rel_path.parts

        category = "General"
        domain = "Unknown"
        engine_type = "Unknown"

        if len(parts) > 0:
            category = parts[0]

        # Extract domain from filename
        name_lower = path.stem.lower()
        if "consulting" in name_lower:
            domain = "Consulting"
            engine_type = "Consulting Engine"
        elif "cognitive" in name_lower or "brain" in name_lower:
            domain = "Cognition"
            engine_type = "Cognitive Engine"
        elif "coding" in name_lower or "code" in name_lower:
            domain = "Coding"
            engine_type = "Coding Engine"
        elif "legal" in name_lower:
            domain = "Legal"
            engine_type = "Legal Engine"
        elif "quantum" in name_lower:
            domain = "Quantum"
            engine_type = "Quantum Engine"
        elif "vn" in name_lower or "vietnam" in name_lower:
            domain = "Vietnam"
            engine_type = "Vietnam Engine"
        elif "ubi" in name_lower:
            domain = "UBI"
            engine_type = "UBI Engine"
        elif "kernel" in name_lower:
            domain = "Kernel"
            engine_type = "Kernel"
        elif "pack" in name_lower:
            domain = "Pack"
            engine_type = "Knowledge Pack"
        elif "universe" in name_lower or "cosmos" in name_lower:
            domain = "Universe"
            engine_type = "Universe Engine"
        elif "super" in name_lower or "x100" in name_lower:
            domain = "Super Scale"
            engine_type = "Super Engine"
        elif "automation" in name_lower:
            domain = "Automation"
            engine_type = "Automation Engine"
        elif "business" in name_lower or "finance" in name_lower or "bizfin" in name_lower:
            domain = "Business/Finance"
            engine_type = "BizFin Engine"
        elif "governance" in name_lower:
            domain = "Governance"
            engine_type = "Governance Engine"
        elif "tech" in name_lower:
            domain = "Technology"
            engine_type = "Tech Engine"
        elif "design" in name_lower:
            domain = "Design"
            engine_type = "Design Engine"
        elif "emotion" in name_lower:
            domain = "Emotion"
            engine_type = "Emotion Engine"
        elif "personality" in name_lower:
            domain = "Personality"
            engine_type = "Personality Engine"
        elif "science" in name_lower:
            domain = "Science"
            engine_type = "Scientific Engine"
        elif "omni" in name_lower:
            domain = "Omni"
            engine_type = "Omni Engine"
        elif "factory" in name_lower or "fabrication" in name_lower:
            domain = "Factory"
            engine_type = "Factory Engine"
        elif "unitaxi" in name_lower or "taxi" in name_lower:
            domain = "UniTaxi"
            engine_type = "UniTaxi Engine"
        elif "unipower" in name_lower:
            domain = "UniPower"
            engine_type = "UniPower Engine"
        elif "logic" in name_lower:
            domain = "Logic"
            engine_type = "Logic Engine"
        elif "consciousness" in name_lower:
            domain = "Consciousness"
            engine_type = "Consciousness Engine"
        elif "agent" in name_lower:
            domain = "Agent"
            engine_type = "Agent Engine"
        elif "archive" in name_lower:
            domain = "Archive"
            engine_type = "Archive Engine"
        elif "core" in name_lower:
            domain = "Core"
            engine_type = "Core Engine"
        elif "cognition" in name_lower:
            domain = "Cognition"
            engine_type = "Cognition Engine"
        elif "mind" in name_lower:
            domain = "Mind"
            engine_type = "Mind Engine"
        elif "os" in name_lower:
            domain = "OS"
            engine_type = "Operating System"

        file_info = KnowledgeFile(
            path=path,
            name=path.name,
            size_bytes=path.stat().st_size,
            category=category,
            domain=domain,
            engine_type=engine_type,
        )

        self._index.append(file_info)

    def _calculate_stats(self) -> None:
        """Calculate category and domain statistics."""
        for file_info in self._index:
            self._categories[file_info.category] = self._categories.get(file_info.category, 0) + 1
            self._domains[file_info.domain] = self._domains.get(file_info.domain, 0) + 1

    def search(self, query: str, top_n: int = 10) -> list[KnowledgeFile]:
        """Search knowledge base for matching files."""
        if not self._indexed:
            self.index()

        query_lower = query.lower()
        results = []

        for file_info in self._index:
            score = 0.0

            # Check name match
            if query_lower in file_info.name.lower():
                score += 3.0

            # Check domain match
            if query_lower in file_info.domain.lower():
                score += 2.0

            # Check engine type match
            if query_lower in file_info.engine_type.lower():
                score += 2.0

            # Check category match
            if query_lower in file_info.category.lower():
                score += 1.0

            # Check path match
            if query_lower in str(file_info.path).lower():
                score += 0.5

            if score > 0:
                file_info.relevance_score = score
                results.append(file_info)

        # Sort by relevance score (descending)
        results.sort(key=lambda x: x.relevance_score, reverse=True)

        return results[:top_n]

    def get_stats(self) -> dict:
        """Get knowledge base statistics."""
        if not self._indexed:
            self.index()

        total_size = sum(f.size_bytes for f in self._index)

        # Find largest files
        largest = sorted(self._index, key=lambda x: x.size_bytes, reverse=True)[:10]

        return {
            "total_files": len(self._index),
            "total_size_bytes": total_size,
            "total_size_human": self._human_size(total_size),
            "categories": dict(sorted(self._categories.items(), key=lambda x: x[1], reverse=True)),
            "domains": dict(sorted(self._domains.items(), key=lambda x: x[1], reverse=True)[:20]),
            "largest_files": [(f.name, f.size_human) for f in largest],
        }

    def _human_size(self, size_bytes: int) -> str:
        """Convert bytes to human-readable format."""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} PB"

    def recommend_engines(self, problem: str) -> list[KnowledgeFile]:
        """Recommend cognitive engines for a given problem."""
        if not self._indexed:
            self.index()

        problem_lower = problem.lower()

        # Domain-keyword mapping
        domain_keywords = {
            "consulting": ["consulting", "advisory", "strategy", "business"],
            "coding": ["code", "programming", "software", "development", "api"],
            "legal": ["legal", "law", "compliance", "contract", "regulation"],
            "vietnam": ["vietnam", "vn", "vietnamese"],
            "finance": ["finance", "financial", "investment", "money", "economics"],
            "technology": ["tech", "technology", "infrastructure", "system"],
            "design": ["design", "ux", "ui", "visual", "interface"],
            "cognition": ["brain", "cognitive", "thinking", "reasoning", "mind"],
            "science": ["science", "research", "experiment", "data"],
            "quantum": ["quantum", "probability", "timing"],
            "automation": ["automation", "workflow", "pipeline", "process"],
            "governance": ["governance", "policy", "risk", "compliance"],
        }

        # Find matching domains
        matching_domains = []
        for domain, keywords in domain_keywords.items():
            if any(kw in problem_lower for kw in keywords):
                matching_domains.append(domain)

        # Search for files in matching domains
        results = []
        for file_info in self._index:
            if file_info.domain.lower() in matching_domains:
                file_info.relevance_score = 2.0
                results.append(file_info)

        # Also do text search
        text_results = self.search(problem, top_n=20)
        results.extend(text_results)

        # Deduplicate and sort
        seen = set()
        unique_results = []
        for r in results:
            if r.path not in seen:
                seen.add(r.path)
                unique_results.append(r)

        unique_results.sort(key=lambda x: x.relevance_score, reverse=True)
        return unique_results[:15]


def print_search_results(results: list[KnowledgeFile], query: str):
    """Pretty print search results."""
    print(f"\n{'=' * 70}")
    print(f'  SEARCH RESULTS: "{query}"')
    print(f"{'=' * 70}")

    if not results:
        print("\n  No matching knowledge files found.")
        return

    print(f"\n  Found {len(results)} relevant files:\n")

    for i, file_info in enumerate(results, 1):
        print(f"  {i}. {file_info.name}")
        print(f"     📁 Category: {file_info.category}")
        print(f"     🏷️  Domain: {file_info.domain} | Type: {file_info.engine_type}")
        print(f"     📊 Size: {file_info.size_human} | Relevance: {file_info.relevance_score:.1f}")
        print(f"     📍 Path: {file_info.path.relative_to(file_info.path.parent.parent)}")
        print()


def print_stats(explorer: KnowledgeExplorer):
    """Print knowledge base statistics."""
    stats = explorer.get_stats()

    print(f"\n{'=' * 70}")
    print("  AMOS KNOWLEDGE BASE STATISTICS")
    print(f"{'=' * 70}")

    print("\n  📊 OVERVIEW:")
    print(f"     Total Files: {stats['total_files']:,}")
    print(f"     Total Size: {stats['total_size_human']}")

    print("\n  📁 TOP CATEGORIES:")
    for cat, count in list(stats["categories"].items())[:10]:
        print(f"     • {cat}: {count} files")

    print("\n  🏷️  TOP DOMAINS:")
    for domain, count in list(stats["domains"].items())[:15]:
        print(f"     • {domain}: {count} files")

    print("\n  📦 LARGEST FILES:")
    for name, size in stats["largest_files"]:
        print(f"     • {name[:50]:<50} {size:>10}")


def print_recommendations(explorer: KnowledgeExplorer, problem: str):
    """Print engine recommendations for a problem."""
    print(f"\n{'=' * 70}")
    print("  ENGINE RECOMMENDATIONS FOR:")
    print(f'  "{problem}"')
    print(f"{'=' * 70}")

    recommendations = explorer.recommend_engines(problem)

    if not recommendations:
        print("\n  No specific engines found. Try a more specific query.")
        return

    print(f"\n  🎯 RECOMMENDED COGNITIVE ENGINES ({len(recommendations)}):\n")

    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec.name}")
        print(f"     Type: {rec.engine_type}")
        print(f"     Domain: {rec.domain}")
        print(f"     Size: {rec.size_human}")
        print(f"     Match Score: {rec.relevance_score:.1f}/5.0")
        print()


def export_knowledge_map(explorer: KnowledgeExplorer, output_file: str = "knowledge_map.md"):
    """Export knowledge map to markdown."""
    stats = explorer.get_stats()

    content = f"""# AMOS Knowledge Base Map

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Overview

- **Total Files:** {stats["total_files"]:,}
- **Total Size:** {stats["total_size_human"]}
- **Categories:** {len(stats["categories"])}
- **Domains:** {len(stats["domains"])}

## Categories

"""

    for cat, count in list(stats["categories"].items()):
        content += f"- **{cat}:** {count} files\n"

    content += "\n## Domains\n\n"
    for domain, count in list(stats["domains"].items())[:30]:
        content += f"- **{domain}:** {count} files\n"

    content += "\n## Largest Files\n\n"
    content += "| File | Size |\n"
    content += "|------|------|\n"
    for name, size in stats["largest_files"]:
        content += f"| {name[:50]} | {size} |\n"

    content += "\n---\n*Generated by AMOS Knowledge Explorer*\n"

    output_path = Path(output_file)
    output_path.write_text(content)
    print(f"\n✓ Knowledge map exported to: {output_path.absolute()}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Explore the AMOS knowledge base")
    parser.add_argument(
        "command",
        choices=["search", "stats", "map", "recommend", "interactive"],
        default="interactive",
        nargs="?",
        help="Command to run",
    )
    parser.add_argument("query", nargs="?", help="Search query or problem description")

    args = parser.parse_args()

    # Initialize explorer
    explorer = KnowledgeExplorer()

    if args.command == "stats":
        explorer.index()
        print_stats(explorer)

    elif args.command == "search":
        if not args.query:
            args.query = input("Enter search query: ")
        explorer.index()
        results = explorer.search(args.query, top_n=15)
        print_search_results(results, args.query)

    elif args.command == "recommend":
        if not args.query:
            args.query = input("Describe your problem: ")
        explorer.index()
        print_recommendations(explorer, args.query)

    elif args.command == "map":
        explorer.index()
        print_stats(explorer)
        export_knowledge_map(explorer)

    else:  # interactive
        print("\n" + "=" * 70)
        print("  AMOS KNOWLEDGE EXPLORER")
        print("  Navigate 1,110+ knowledge files")
        print("=" * 70)

        explorer.index()

        while True:
            print("\nCommands: [s]earch, [r]ecommend, [t]ats, [m]ap, [q]uit")
            choice = input("> ").strip().lower()

            if choice in ["q", "quit", "exit"]:
                break

            elif choice in ["s", "search"]:
                query = input("Search query: ")
                results = explorer.search(query, top_n=10)
                print_search_results(results, query)

            elif choice in ["r", "recommend"]:
                problem = input("Describe your problem: ")
                print_recommendations(explorer, problem)

            elif choice in ["t", "stats", "st"]:
                print_stats(explorer)

            elif choice in ["m", "map"]:
                print_stats(explorer)
                export_knowledge_map(explorer)

            else:
                print("Unknown command. Try: s, r, t, m, q")

        print("\nGoodbye! 👋")

    return 0


if __name__ == "__main__":
    sys.exit(main())
