"""AMOS Intelligent Modernization Orchestrator.

Systematically modernizes remaining deprecated patterns across the codebase
using priority-based batching, automated validation, and rollback capability.

Owner: Trang
Version: 1.0.0
"""

import asyncio
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc, timezone

UTC = UTC
from pathlib import Path
from typing import Any


@dataclass
class ModernizationBatch:
    """A batch of files to modernize."""

    name: str
    priority: int
    files: list[Path]
    patterns: list[str]
    completed: bool = False
    results: dict[str, Any] = field(default_factory=dict)
    started_at: str = None
    completed_at: str = None


@dataclass
class FileAnalysis:
    """Analysis of a single file."""

    path: Path
    has_datetime_issues: bool = False
    has_typing_issues: bool = False
    has_async_issues: bool = False
    has_bare_except: bool = False
    issue_count: int = 0


class IntelligentModernizer:
    """Orchestrates systematic codebase modernization."""

    def __init__(self, root_path: Path = None):
        self.root = root_path or Path.cwd()
        self.batches: list[ModernizationBatch] = []
        self.analyzed_files: list[FileAnalysis] = []
        self.report: dict[str, Any] = {}

    async def analyze_repository(self) -> list[FileAnalysis]:
        """Deep analysis of all Python files."""
        print("🔍 Analyzing repository for deprecated patterns...")

        py_files = list(self.root.rglob("*.py"))
        # Filter out unwanted directories
        py_files = [
            f
            for f in py_files
            if not any(
                part.startswith(".") or part in ["venv", "__pycache__", "node_modules"]
                for part in f.parts
            )
        ]

        analyses = []
        for filepath in py_files:
            analysis = await self._analyze_file(filepath)
            if analysis.issue_count > 0:
                analyses.append(analysis)

        self.analyzed_files = sorted(analyses, key=lambda x: x.issue_count, reverse=True)
        print(f"📊 Found {len(analyses)} files with issues")
        return self.analyzed_files

    async def _analyze_file(self, filepath: Path) -> FileAnalysis:
        """Analyze a single file for deprecated patterns."""
        analysis = FileAnalysis(path=filepath)

        try:
            content = filepath.read_text(encoding="utf-8")

            # Check datetime issues
            if "datetime.now(timezone.utc)" in content:
                analysis.has_datetime_issues = True
                analysis.issue_count += content.count("datetime.now(timezone.utc)")

            # Check typing issues
            typing_patterns = [
                r"from typing import.*\b(Optional|List|Dict|Set|Tuple|Union)\b",
                r"\bOptional\[",
                r"\bList\[",
                r"\bDict\[",
                r"\bSet\[",
                r"\bTuple\[",
                r"\bUnion\[",
            ]
            for pattern in typing_patterns:
                if re.search(pattern, content):
                    analysis.has_typing_issues = True
                    analysis.issue_count += len(re.findall(pattern, content))

            # Check async issues
            if "asyncio.get_event_loop()" in content:
                analysis.has_async_issues = True
                analysis.issue_count += content.count("asyncio.get_event_loop()")

            # Check bare except
            if re.search(r"except\s*:", content):
                analysis.has_bare_except = True
                analysis.issue_count += len(re.findall(r"except\s*:", content))

        except Exception as e:
            print(f"⚠️ Error analyzing {filepath}: {e}")

        return analysis

    def create_priority_batches(self) -> list[ModernizationBatch]:
        """Create prioritized modernization batches."""
        print("📋 Creating priority batches...")

        # Priority 1: Core system files (amos_*.py in root)
        core_files = [
            a.path
            for a in self.analyzed_files
            if a.path.parent == self.root and a.path.name.startswith("amos_")
        ]

        # Priority 2: Backend modules
        backend_files = [
            a.path
            for a in self.analyzed_files
            if "backend/" in str(a.path) and not a.path.name.startswith("test_")
        ]

        # Priority 3: ORGANISM_OS subsystems
        organism_files = [a.path for a in self.analyzed_files if "AMOS_ORGANISM_OS/" in str(a.path)]

        # Priority 4: Repo Doctor modules
        repo_doctor_files = [
            a.path
            for a in self.analyzed_files
            if "repo_doctor" in str(a.path) or "repo_doctor_omega" in str(a.path)
        ]

        # Priority 5: Integration and tools
        integration_files = [
            a.path
            for a in self.analyzed_files
            if any(x in str(a.path) for x in ["integration", "tools", "scripts"])
        ]

        # Priority 6: Remaining files
        analyzed_paths = set(
            core_files + backend_files + organism_files + repo_doctor_files + integration_files
        )
        remaining_files = [a.path for a in self.analyzed_files if a.path not in analyzed_paths]

        self.batches = [
            ModernizationBatch(
                name="Core System Files",
                priority=1,
                files=core_files[:20],  # Top 20 by issue count
                patterns=["datetime", "typing", "async"],
            ),
            ModernizationBatch(
                name="Backend Modules",
                priority=2,
                files=backend_files[:30],
                patterns=["datetime", "typing", "async"],
            ),
            ModernizationBatch(
                name="ORGANISM_OS Subsystems",
                priority=3,
                files=organism_files[:40],
                patterns=["datetime", "typing"],
            ),
            ModernizationBatch(
                name="Repo Doctor Modules",
                priority=4,
                files=repo_doctor_files[:25],
                patterns=["datetime", "typing"],
            ),
            ModernizationBatch(
                name="Integration & Tools",
                priority=5,
                files=integration_files[:25],
                patterns=["datetime", "typing"],
            ),
            ModernizationBatch(
                name="Remaining Files",
                priority=6,
                files=remaining_files[:50],
                patterns=["datetime", "typing"],
            ),
        ]

        # Remove empty batches
        self.batches = [b for b in self.batches if b.files]

        for batch in self.batches:
            print(f"  📦 {batch.name}: {len(batch.files)} files (P{batch.priority})")

        return self.batches

    async def run_batch(self, batch: ModernizationBatch, dry_run: bool = True) -> dict[str, Any]:
        """Run modernization on a single batch."""
        print(f"\n🚀 Processing batch: {batch.name}")
        batch.started_at = datetime.now(timezone.utc).isoformat()

        results = {
            "batch_name": batch.name,
            "files_processed": 0,
            "files_modified": 0,
            "total_changes": 0,
            "errors": [],
            "changes_by_file": {},
        }

        for filepath in batch.files:
            try:
                file_results = await self._modernize_file(filepath, batch.patterns, dry_run)
                results["files_processed"] += 1

                if file_results["changes"] > 0:
                    results["files_modified"] += 1
                    results["total_changes"] += file_results["changes"]
                    results["changes_by_file"][str(filepath)] = file_results["details"]

            except Exception as e:
                results["errors"].append(f"{filepath}: {e}")
                print(f"    ❌ Error: {filepath}: {e}")

        batch.completed = True
        batch.completed_at = datetime.now(timezone.utc).isoformat()
        batch.results = results

        print(
            f"  ✅ Batch complete: {results['files_modified']}/{results['files_processed']} files modified"
        )
        print(f"     Total changes: {results['total_changes']}")

        return results

    async def _modernize_file(
        self, filepath: Path, patterns: list[str], dry_run: bool
    ) -> dict[str, Any]:
        """Modernize a single file."""
        results = {"changes": 0, "details": []}

        try:
            content = filepath.read_text(encoding="utf-8")
            original_content = content

            # Apply datetime modernization
            if "datetime" in patterns and "datetime.now(timezone.utc)" in content:
                # Add timezone import if needed
                if "from datetime import datetime" in content and "timezone" not in content:
                    content = content.replace(
                        "from datetime import datetime", "from datetime import datetime, timezone
UTC = timezone.utc"
                    )
                    results["changes"] += 1
                    results["details"].append("Added timezone import")

                # Replace utcnow() calls
                utcnow_count = content.count("datetime.now(timezone.utc)")
                content = content.replace(
                    "datetime.now(timezone.utc)", "datetime.now(timezone.utc)"
                )
                if utcnow_count > 0:
                    results["changes"] += utcnow_count
                    results["details"].append(f"Replaced {utcnow_count} utcnow() calls")

            # Apply typing modernization
            if "typing" in patterns:
                # Replace X  with X
                optional_matches = len(re.findall(r"Optional\[([^\]]+)\]", content))
                if optional_matches > 0:
                    content = re.sub(r"Optional\[([^\]]+)\]", r"\1 ", content)
                    results["changes"] += optional_matches
                    results["details"].append(f"Replaced {optional_matches}   patterns")

                # Replace list[X] with list[X]
                list_matches = len(re.findall(r"List\[([^\]]+)\]", content))
                if list_matches > 0:
                    content = re.sub(r"List\[([^\]]+)\]", r"list[\1]", content)
                    results["changes"] += list_matches
                    results["details"].append(f"Replaced {list_matches} List[] patterns")

                # Replace dict[K, V] with dict[K,V]
                dict_matches = len(re.findall(r"Dict\[([^,\]]+),\s*([^\]]+)\]", content))
                if dict_matches > 0:
                    content = re.sub(r"Dict\[([^,\]]+),\s*([^\]]+)\]", r"dict[\1, \2]", content)
                    results["changes"] += dict_matches
                    results["details"].append(f"Replaced {dict_matches} Dict[] patterns")

                # Clean up typing imports
                if results["changes"] > 0:
                    lines = content.split("\n")
                    new_lines = []
                    for line in lines:
                        if line.strip().startswith("from typing import"):
                            # Keep only non-deprecated imports
                            imports = (
                                line.replace("from typing import", "")
                                .strip()
                                .rstrip(",")
                                .split(",")
                            )
                            new_imports = []
                            for imp in imports:
                                imp = imp.strip()
                                if imp and imp not in [
                                    "Optional",
                                    "List",
                                    "Dict",
                                    "Set",
                                    "Tuple",
                                    "Union",
                                ]:
                                    new_imports.append(imp)

                            if new_imports:
                                (
                                    new_lines.append(
                                        f"from typing import {', '.join(new_imports)}"
                                    ),
                                    Optional,
                                )
                        else:
                            new_lines.append(line)
                    content = "\n".join(new_lines)

            # Write changes if not dry run and changes were made
            if not dry_run and content != original_content:
                filepath.write_text(content, encoding="utf-8")
                # Verify syntax
                try:
                    compile(content, str(filepath), "exec")
                except SyntaxError as e:
                    # Rollback on syntax error
                    filepath.write_text(original_content, encoding="utf-8")
                    raise Exception(f"Syntax error after modernization: {e}")

            return results

        except Exception as e:
            raise Exception(f"Failed to modernize {filepath}: {e}")

    async def generate_report(self) -> dict[str, Any]:
        """Generate comprehensive modernization report."""
        self.report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "root_path": str(self.root),
            "total_files_analyzed": len(self.analyzed_files),
            "batches": len(self.batches),
            "summary": {
                "files_with_datetime_issues": sum(
                    1 for a in self.analyzed_files if a.has_datetime_issues
                ),
                "files_with_typing_issues": sum(
                    1 for a in self.analyzed_files if a.has_typing_issues
                ),
                "files_with_async_issues": sum(
                    1 for a in self.analyzed_files if a.has_async_issues
                ),
                "files_with_bare_except": sum(1 for a in self.analyzed_files if a.has_bare_except),
                "total_issues": sum(a.issue_count for a in self.analyzed_files),
            },
            "batch_results": [b.results for b in self.batches if b.completed],
            "top_files_by_issues": [
                {"path": str(a.path), "issues": a.issue_count} for a in self.analyzed_files[:20]
            ],
        }
        return self.report

    async def run_all_batches(self, dry_run: bool = True) -> dict[str, Any]:
        """Run all modernization batches."""
        print("\n" + "=" * 70)
        print("🚀 AMOS INTELLIGENT MODERNIZATION ORCHESTRATOR")
        print("=" * 70)
        print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
        print("=" * 70 + "\n")

        # Analysis phase
        await self.analyze_repository()

        # Batching phase
        self.create_priority_batches()

        # Execution phase
        all_results = []
        for batch in self.batches:
            results = await self.run_batch(batch, dry_run)
            all_results.append(results)

        # Reporting phase
        report = await self.generate_report()

        # Print summary
        print("\n" + "=" * 70)
        print("📊 MODERNIZATION SUMMARY")
        print("=" * 70)
        print(f"Files analyzed: {report['total_files_analyzed']}")
        print(f"Batches processed: {report['batches']}")
        print(f"Total issues found: {report['summary']['total_issues']}")
        print(f"  - datetime.now(timezone.utc): {report['summary']['files_with_datetime_issues']}")
        print(f"  - deprecated typing: {report['summary']['files_with_typing_issues']}")
        print(f"  - async patterns: {report['summary']['files_with_async_issues']}")
        print(f"  - bare except: {report['summary']['files_with_bare_except']}")
        print("=" * 70)

        return report


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="AMOS Intelligent Modernizer")
    parser.add_argument("--root", type=str, default=".", help="Root path to analyze")
    parser.add_argument("--live", action="store_true", help="Apply changes (not dry run)")
    parser.add_argument("--batch", type=str, help="Run specific batch only")
    parser.add_argument(
        "--report", type=str, default="modernization_report.json", help="Output report file"
    )

    args = parser.parse_args()

    root = Path(args.root).resolve()
    modernizer = IntelligentModernizer(root)

    report = await modernizer.run_all_batches(dry_run=not args.live)

    # Save report
    report_path = root / args.report
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n📄 Report saved to: {report_path}")

    return report


if __name__ == "__main__":
    asyncio.run(main())
