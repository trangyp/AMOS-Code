#!/usr/bin/env python3
"""AMOS Deep Inventory - Dynamic Discovery of All Features & Knowledge.

Dynamically scans the codebase to catalog:
- All engine classes and their methods
- All tools and integrations
- Knowledge files and specifications
- Demo scripts and examples
- Configuration and spec files

Usage: python amos_deep_inventory.py [--scan] [--export]
"""
import ast
import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

sys.path.insert(0, str(Path(__file__).parent))


@dataclass
class DiscoveredEngine:
    """A discovered engine from code analysis."""

    name: str
    file_path: str
    methods: list[str] = field(default_factory=list)
    purpose: str = ""
    engine_type: str = "unknown"


@dataclass
class DiscoveredTool:
    """A discovered tool from code analysis."""

    name: str
    file_path: str
    function: str
    description: str = ""
    parameters: list[str] = field(default_factory=list)


class AMOSDeepInventory:
    """Deep scanner for AMOS ecosystem capabilities."""

    def __init__(self, root_path: Optional[Path] = None):
        self.root = root_path or Path(__file__).parent
        self.engines: list[DiscoveredEngine] = []
        self.tools: list[DiscoveredTool] = []
        self.knowledge_files: list[Path] = []
        self.specs: list[Path] = []
        self.demos: list[Path] = []
        self.total_lines = 0
        self.total_files = 0

    def scan_python_files(self) -> None:
        """Scan all Python files for engines and tools."""
        exclude = {".venv", "__pycache__", ".git"}

        for py_file in self.root.rglob("*.py"):
            # Skip excluded directories
            if any(part in exclude for part in py_file.parts):
                continue

            try:
                content = py_file.read_text(encoding="utf-8")
                self.total_lines += len(content.splitlines())
                self.total_files += 1

                # Parse AST
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    # Find class definitions (potential engines)
                    if isinstance(node, ast.ClassDef):
                        if "Engine" in node.name or "Analyzer" in node.name:
                            methods = [
                                n.name
                                for n in node.body
                                if isinstance(n, ast.FunctionDef) and not n.name.startswith("_")
                            ]

                            engine = DiscoveredEngine(
                                name=node.name,
                                file_path=str(py_file.relative_to(self.root)),
                                methods=methods[:10],  # Limit methods shown
                                engine_type=self._classify_engine(node.name),
                            )
                            self.engines.append(engine)

                    # Find function definitions (potential tools)
                    if isinstance(node, ast.FunctionDef):
                        if node.name.startswith("_") or "test" in node.name.lower():
                            continue

                        # Check if it's a tool-like function
                        if any(
                            decorator_name(node) in ["tool", "Tool", "register"]
                            for node in node.decorator_list
                        ):
                            tool = DiscoveredTool(
                                name=node.name,
                                file_path=str(py_file.relative_to(self.root)),
                                function=node.name,
                            )
                            self.tools.append(tool)

            except Exception:
                pass  # Skip files that can't be parsed

    def _classify_engine(self, name: str) -> str:
        """Classify engine by name patterns."""
        if "Validator" in name or "Axiom" in name:
            return "validator"
        elif "Analyzer" in name:
            return "analyzer"
        elif "Executor" in name or "Worker" in name:
            return "executor"
        elif "Builder" in name or "Factory" in name:
            return "builder"
        elif "Decision" in name or "Router" in name:
            return "decision"
        elif "Predict" in name or "Forecast" in name:
            return "predictor"
        elif "Model" in name:
            return "modeler"
        else:
            return "domain"

    def scan_knowledge_bases(self) -> None:
        """Scan for knowledge files and specs."""
        # JSON specs
        for json_file in self.root.rglob("*.json"):
            if any(x in str(json_file) for x in ["_AMOS_BRAIN", "AMOS_", "spec", "engine"]):
                if ".venv" not in str(json_file):
                    self.specs.append(json_file.relative_to(self.root))

        # Knowledge files
        for ext in [".md", ".txt", ".json"]:
            for kf in self.root.rglob(f"*{ext}"):
                if any(x in str(kf).lower() for x in ["knowledge", "spec", "brain", "engine"]):
                    if ".venv" not in str(kf) and ".git" not in str(kf):
                        self.knowledge_files.append(kf.relative_to(self.root))

    def scan_demos(self) -> None:
        """Scan for demo and example scripts."""
        for demo_file in self.root.glob("amos_*.py"):
            if "demo" in demo_file.name or "cycle" in demo_file.name or "test" in demo_file.name:
                self.demos.append(demo_file.relative_to(self.root))

    def count_domain_engines(self) -> dict[str, int]:
        """Count engines by domain."""
        domains = {}
        for engine in self.engines:
            domain = engine.engine_type
            domains[domain] = domains.get(domain, 0) + 1
        return domains

    def generate_inventory(self) -> dict[str, Any]:
        """Generate complete inventory."""
        return {
            "metadata": {
                "scan_date": str(Path(__file__).stat().st_mtime),
                "total_files_scanned": self.total_files,
                "total_lines_of_code": self.total_lines,
                "root_directory": str(self.root),
            },
            "engines": {
                "count": len(self.engines),
                "by_type": self.count_domain_engines(),
                "list": [
                    {
                        "name": e.name,
                        "file": e.file_path,
                        "type": e.engine_type,
                        "methods": e.methods[:5],
                    }
                    for e in self.engines[:50]  # Limit output
                ],
            },
            "tools": {
                "count": len(self.tools),
                "list": [{"name": t.name, "file": t.file_path} for t in self.tools[:30]],
            },
            "knowledge_bases": {
                "specs_count": len(self.specs),
                "knowledge_files_count": len(self.knowledge_files),
                "sample_specs": [str(s) for s in self.specs[:10]],
                "sample_knowledge": [str(k) for k in self.knowledge_files[:10]],
            },
            "demos": {"count": len(self.demos), "list": [str(d) for d in self.demos]},
        }

    def print_summary(self) -> None:
        """Print formatted summary."""
        print("=" * 70)
        print("  🔬 AMOS DEEP INVENTORY")
        print("  Dynamic Codebase Analysis")
        print("=" * 70)
        print(f"\n  📁 Scanned: {self.total_files:,} files")
        print(f"  📝 Total Lines: {self.total_lines:,}")
        print(f"\n  🏗️  ENGINES DISCOVERED: {len(self.engines)}")

        by_type = self.count_domain_engines()
        for eng_type, count in sorted(by_type.items(), key=lambda x: -x[1]):
            print(f"     • {eng_type}: {count}")

        print(f"\n  🛠️  TOOLS DISCOVERED: {len(self.tools)}")

        print("\n  📚 KNOWLEDGE BASES:")
        print(f"     • JSON Specs: {len(self.specs)}")
        print(f"     • Knowledge Files: {len(self.knowledge_files)}")

        print(f"\n  🎬 DEMOS & EXAMPLES: {len(self.demos)}")
        for demo in self.demos[:10]:
            print(f"     • {demo}")
        if len(self.demos) > 10:
            print(f"     ... and {len(self.demos) - 10} more")

        print("\n" + "=" * 70)


def decorator_name(node):
    """Extract decorator name from AST node."""
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        return node.func.id
    return ""


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="AMOS Deep Inventory")
    parser.add_argument("--scan", action="store_true", help="Scan codebase")
    parser.add_argument("--export", type=str, help="Export to JSON file")
    parser.add_argument("--quick", action="store_true", help="Quick summary only")

    args = parser.parse_args()

    inventory = AMOSDeepInventory()

    if args.quick:
        # Quick scan - just count files
        result = subprocess.run(
            ["find", ".", "-name", "*.py", "-not", "-path", "./.venv/*"],
            capture_output=True,
            text=True,
            cwd=str(inventory.root),
        )
        py_files = len([l for l in result.stdout.split("\n") if l])
        print(f"Python files: {py_files}")
        return

    print("  Scanning codebase...")
    inventory.scan_python_files()
    inventory.scan_knowledge_bases()
    inventory.scan_demos()

    inventory.print_summary()

    if args.export:
        data = inventory.generate_inventory()
        Path(args.export).write_text(json.dumps(data, indent=2))
        print(f"  💾 Exported to: {args.export}")


if __name__ == "__main__":
    main()
