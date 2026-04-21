#!/usr/bin/env python3
"""AMOS 6-Repository Linker - Master Integration Hub

Links all 6 AMOS repositories into one coherent ecosystem:
1. AMOS-Code (Core brain library)
2. AMOS-Consulting (Backend API hub)
3. AMOS-Claws (Operator frontend)
4. Mailinhconect (Product frontend)
5. AMOS-Invest (Investor frontend)
6. AMOS-UNIVERSE (Canonical knowledge layer)

Usage:
    python AMOS_6_REPO_LINKER.py --status
    python AMOS_6_REPO_LINKER.py --sync-all
    python AMOS_6_REPO_LINKER.py --link-check
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

UTC = timezone.utc


@dataclass
class RepoLink:
    """Link configuration for a repository."""

    name: str
    role: str
    package: str
    owner: str = "trangyp"
    language: str = ""
    license: str = ""
    endpoint: str = ""  # Public endpoint
    local_path: Optional[Path] = None
    github_url: str = ""
    dependencies: list[str] = field(default_factory=list)
    consumers: list[str] = field(default_factory=list)  # Repos that depend on this
    status: str = "unknown"  # linked, missing, error
    last_sync: Optional[datetime] = None
    commit_count: int = 0

    def __post_init__(self):
        if not self.github_url:
            self.github_url = f"https://github.com/{self.owner}/{self.name}"


class AMOS6RepoLinker:
    """Master linker for the 6-repository AMOS ecosystem."""

    # Canonical 6-repo definition
    REPOS = [
        RepoLink(
            name="AMOS-Code",
            role="Core brain library",
            package="amos-brain",
            language="Python",
            license="Apache-2.0",
            endpoint="",  # Library, no endpoint
            dependencies=["AMOS-UNIVERSE"],  # Optional contracts
            consumers=["AMOS-Consulting"],
        ),
        RepoLink(
            name="AMOS-Consulting",
            role="Backend API hub",
            package="amos-platform",
            language="Python",
            license="MIT",
            endpoint="api.amos.io",
            dependencies=["AMOS-Code", "AMOS-UNIVERSE"],
            consumers=["AMOS-Claws", "Mailinhconect", "AMOS-Invest"],
        ),
        RepoLink(
            name="AMOS-Claws",
            role="Operator frontend",
            package="amos-claws",
            language="HTML/TypeScript",
            license="MIT",
            endpoint="claws.amos.io",
            dependencies=["AMOS-Consulting", "AMOS-UNIVERSE"],
            consumers=[],
        ),
        RepoLink(
            name="Mailinhconect",
            role="Product frontend",
            package="mailinh-web",
            language="HTML/TypeScript",
            license="MIT",
            endpoint="app.amos.io",
            dependencies=["AMOS-Consulting", "AMOS-UNIVERSE"],
            consumers=[],
        ),
        RepoLink(
            name="AMOS-Invest",
            role="Investor frontend",
            package="amos-invest",
            language="HTML/TypeScript",
            license="MIT",
            endpoint="invest.amos.io",
            dependencies=["AMOS-Consulting", "AMOS-UNIVERSE"],
            consumers=[],
        ),
        RepoLink(
            name="AMOS-UNIVERSE",
            role="Canonical knowledge layer",
            package="amos-universe",
            language="Python",
            license="MIT",
            endpoint="universe.amos.io",
            dependencies=[],  # No runtime deps
            consumers=["AMOS-Code", "AMOS-Consulting", "AMOS-Claws", "Mailinhconect", "AMOS-Invest"],
        ),
    ]

    # Event topics that connect the repos
    EVENT_TOPICS = {
        # CLAWS events (Agent/Operator layer)
        "claws.session.started": ["AMOS-Claws", "AMOS-Consulting"],
        "claws.session.ended": ["AMOS-Claws", "AMOS-Consulting"],
        "claws.agent.requested": ["AMOS-Claws", "AMOS-Consulting"],
        "claws.agent.completed": ["AMOS-Consulting", "AMOS-Claws", "AMOS-Invest"],
        "claws.tool.invoked": ["AMOS-Claws", "AMOS-Consulting"],

        # MAILINH events (Product layer)
        "mailinh.lead.created": ["Mailinhconect", "AMOS-Consulting", "AMOS-Invest"],
        "mailinh.contact.submitted": ["Mailinhconect", "AMOS-Consulting"],
        "mailinh.user.registered": ["Mailinhconect", "AMOS-Consulting"],

        # INVEST events (Investor layer)
        "invest.report.requested": ["AMOS-Invest", "AMOS-Consulting"],
        "invest.signal.generated": ["AMOS-Consulting", "AMOS-Invest"],
        "invest.analytics.viewed": ["AMOS-Invest", "AMOS-Consulting"],

        # REPO events (Brain layer)
        "repo.scan.completed": ["AMOS-Consulting", "AMOS-Claws", "AMOS-Invest"],
        "repo.scan.failed": ["AMOS-Consulting", "AMOS-Claws"],
        "repo.fix.completed": ["AMOS-Consulting", "AMOS-Claws"],
        "repo.fix.failed": ["AMOS-Consulting", "AMOS-Claws"],

        # MODEL events (Memory layer)
        "model.run.completed": ["AMOS-Consulting", "AMOS-Claws", "AMOS-Invest"],
        "model.run.failed": ["AMOS-Consulting", "AMOS-Claws"],
        "model.loaded": ["AMOS-Consulting", "AMOS-Claws"],
        "model.unloaded": ["AMOS-Consulting", "AMOS-Claws"],

        # WORKFLOW events (Muscle layer)
        "workflow.started": ["AMOS-Consulting"],
        "workflow.completed": ["AMOS-Consulting", "AMOS-Claws", "Mailinhconect", "AMOS-Invest"],
        "workflow.failed": ["AMOS-Consulting", "AMOS-Claws"],
        "workflow.step.completed": ["AMOS-Consulting"],

        # UNIVERSE events (Canon layer) - NEW
        "universe.schema.updated": ["AMOS-UNIVERSE", "AMOS-Code", "AMOS-Consulting", "AMOS-Claws", "Mailinhconect", "AMOS-Invest"],
        "universe.contract.published": ["AMOS-UNIVERSE", "AMOS-Consulting", "AMOS-Claws", "Mailinhconect", "AMOS-Invest"],
        "universe.ontology.changed": ["AMOS-UNIVERSE", "AMOS-Consulting", "AMOS-Claws", "Mailinhconect", "AMOS-Invest"],

        # CONSULTING events (Root layer)
        "consulting.workflow.completed": ["AMOS-Consulting"],
        "consulting.task.created": ["AMOS-Consulting", "AMOS-Claws"],
        "consulting.task.updated": ["AMOS-Consulting", "AMOS-Claws"],

        # SYSTEM events (Root layer)
        "system.alert": ["AMOS-Consulting", "AMOS-Claws", "Mailinhconect", "AMOS-Invest"],
        "system.health.changed": ["AMOS-Consulting", "AMOS-Claws", "Mailinhconect", "AMOS-Invest"],
        "system.maintenance.scheduled": ["AMOS-Consulting", "AMOS-Claws", "Mailinhconect", "AMOS-Invest"],
    }

    def __init__(self, base_path: str = "./AMOS_REPOS"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        self.repos: dict[str, RepoLink] = {}
        self._init_repos()

    def _init_repos(self) -> None:
        """Initialize repo tracking."""
        for repo in self.REPOS:
            repo.local_path = self.base_path / repo.name
            self.repos[repo.name] = repo

    def link_all(self) -> dict[str, bool]:
        """Clone/link all 6 repositories."""
        results = {}
        for name, repo in self.repos.items():
            try:
                if repo.local_path.exists():
                    # Pull latest
                    result = subprocess.run(
                        ["git", "pull"],
                        cwd=repo.local_path,
                        capture_output=True,
                        text=True,
                        timeout=60,
                    )
                    repo.status = "linked" if result.returncode == 0 else "error"
                else:
                    # Clone fresh
                    result = subprocess.run(
                        ["git", "clone", repo.github_url, str(repo.local_path)],
                        capture_output=True,
                        text=True,
                        timeout=120,
                    )
                    repo.status = "linked" if result.returncode == 0 else "error"

                if repo.status == "linked":
                    repo.last_sync = datetime.now(UTC)
                    repo.commit_count = self._get_commit_count(repo)

                results[name] = repo.status == "linked"
            except Exception as e:
                repo.status = f"error: {e}"
                results[name] = False

        return results

    def _get_commit_count(self, repo: RepoLink) -> int:
        """Get commit count for repo."""
        try:
            result = subprocess.run(
                ["git", "rev-list", "--count", "HEAD"],
                cwd=repo.local_path,
                capture_output=True,
                text=True,
                timeout=30,
            )
            return int(result.stdout.strip()) if result.returncode == 0 else 0
        except Exception:
            return 0

    def get_dependency_graph(self) -> dict[str, Any]:
        """Get dependency graph of all repos."""
        return {
            name: {
                "dependencies": repo.dependencies,
                "consumers": repo.consumers,
                "layer": self._get_repo_layer(name),
            }
            for name, repo in self.repos.items()
        }

    def _get_repo_layer(self, name: str) -> str:
        """Get architectural layer for repo."""
        layers = {
            "AMOS-UNIVERSE": "Layer 11 (Canon)",
            "AMOS-Code": "Layer 01 (Brain)",
            "AMOS-Consulting": "Layer 00 (Root)",
            "AMOS-Claws": "Layer 09 (Social)",
            "Mailinhconect": "Layer 14 (Interfaces)",
            "AMOS-Invest": "Layer 14 (Interfaces)",
        }
        return layers.get(name, "Unknown")

    def get_event_routing(self) -> dict[str, Any]:
        """Get event routing map."""
        return {
            topic: {
                "publisher": repos[0] if repos else None,
                "subscribers": repos[1:] if len(repos) > 1 else [],
            }
            for topic, repos in self.EVENT_TOPICS.items()
        }

    def get_link_status(self) -> dict[str, Any]:
        """Get current link status of all repos."""
        return {
            name: {
                "status": repo.status,
                "local_path": str(repo.local_path) if repo.local_path else None,
                "github_url": repo.github_url,
                "last_sync": repo.last_sync.isoformat() if repo.last_sync else None,
                "commit_count": repo.commit_count,
                "endpoint": repo.endpoint,
                "role": repo.role,
            }
            for name, repo in self.repos.items()
        }

    def generate_architecture_doc(self) -> str:
        """Generate architecture documentation."""
        lines = [
            "# AMOS 6-Repository Architecture",
            "",
            "## Repository Overview",
            "",
            "| Repository | Role | Package | Endpoint | Layer |",
            "|------------|------|---------|----------|-------|",
        ]

        for name, repo in self.repos.items():
            layer = self._get_repo_layer(name)
            lines.append(
                f"| **{name}** | {repo.role} | `{repo.package}` | {repo.endpoint or 'N/A'} | {layer} |"
            )

        lines.extend([
            "",
            "## Dependency Graph",
            "",
            "```",
            "AMOS-UNIVERSE (Canonical Layer)",
            "       │",
            "       ├──► AMOS-Code (Core Library)",
            "       │",
            "       ├──► AMOS-Consulting (API Hub) ◄──┬─── AMOS-Claws",
            "       │                                   ├─── Mailinhconect",
            "       │                                   └─── AMOS-Invest",
            "       │",
            "       └──► All Frontends (via generated SDKs)",
            "```",
            "",
            "## Event Topics",
            "",
        ])

        for topic, routing in self.get_event_routing().items():
            lines.append(f"- `{topic}`: {routing['publisher']} → {', '.join(routing['subscribers'])}")

        lines.extend([
            "",
            "## API Endpoints (AMOS-Consulting)",
            "",
            "| Endpoint | Method | Description |",
            "|----------|--------|-------------|",
            "| `/v1/health` | GET | Health check |",
            "| `/v1/chat` | POST | Chat completion |",
            "| `/v1/brain/run` | POST | Execute brain cycle |",
            "| `/v1/repo/scan` | POST | Scan repository |",
            "| `/v1/repo/fix` | POST | Apply fixes |",
            "| `/v1/models` | GET | List LLM models |",
            "| `/v1/models/run` | POST | Run model inference |",
            "| `/v1/workflow/run` | POST | Execute workflow |",
            "| `/v1/universe/schemas` | GET | List schemas (NEW) |",
            "",
            "## Subdomains",
            "",
            "| Subdomain | Service | Repository |",
            "|-----------|---------|------------|",
            "| `api.amos.io` | API Gateway | AMOS-Consulting |",
            "| `claws.amos.io` | Operator UI | AMOS-Claws |",
            "| `app.amos.io` | Product UI | Mailinhconect |",
            "| `invest.amos.io` | Investor UI | AMOS-Invest |",
            "| `universe.amos.io` | Schema Registry | AMOS-UNIVERSE |",
        ])

        return "\n".join(lines)

    def print_status(self) -> None:
        """Print current status of all repo links."""
        print("=" * 80)
        print("🌐 AMOS 6-Repository Linker Status")
        print("=" * 80)
        print()

        status = self.get_link_status()
        for name, info in status.items():
            emoji = "✅" if info["status"] == "linked" else "❌" if "error" in str(info["status"]) else "⚠️"
            print(f"{emoji} {name}")
            print(f"   Role: {info['role']}")
            print(f"   Status: {info['status']}")
            print(f"   Path: {info['local_path']}")
            print(f"   Commits: {info['commit_count']}")
            if info['last_sync']:
                print(f"   Last Sync: {info['last_sync']}")
            print()

    def export_integration_config(self) -> dict[str, Any]:
        """Export integration configuration for CI/CD."""
        return {
            "repositories": [
                {
                    "name": repo.name,
                    "github_url": repo.github_url,
                    "role": repo.role,
                    "package": repo.package,
                    "endpoint": repo.endpoint,
                    "dependencies": repo.dependencies,
                }
                for repo in self.repos.values()
            ],
            "event_topics": self.EVENT_TOPICS,
            "dependency_graph": self.get_dependency_graph(),
            "generated_at": datetime.now(UTC).isoformat(),
        }


# Global linker instance
_linker: Optional[AMOS6RepoLinker] = None


def get_linker(base_path: str = "./AMOS_REPOS") -> AMOS6RepoLinker:
    """Get global linker instance."""
    global _linker
    if _linker is None:
        _linker = AMOS6RepoLinker(base_path)
    return _linker


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="AMOS 6-Repository Linker")
    parser.add_argument("--status", action="store_true", help="Show link status")
    parser.add_argument("--sync-all", action="store_true", help="Clone/pull all repos")
    parser.add_argument("--link-check", action="store_true", help="Check all links")
    parser.add_argument("--export-config", action="store_true", help="Export integration config")
    parser.add_argument("--generate-docs", action="store_true", help="Generate architecture docs")
    parser.add_argument("--base-path", default="./AMOS_REPOS", help="Base path for repos")

    args = parser.parse_args()

    linker = get_linker(args.base_path)

    if args.status:
        linker.print_status()

    elif args.sync_all:
        results = linker.link_all()
        print("\n🔗 Sync Results:")
        for name, success in results.items():
            emoji = "✅" if success else "❌"
            print(f"{emoji} {name}: {'linked' if success else 'failed'}")

    elif args.link_check:
        status = linker.get_link_status()
        all_linked = all(s["status"] == "linked" for s in status.values())
        print(f"\n{'✅' if all_linked else '❌'} Link Check: {'All repos linked' if all_linked else 'Some repos not linked'}")
        for name, info in status.items():
            print(f"  {'✅' if info['status'] == 'linked' else '❌'} {name}")

    elif args.export_config:
        config = linker.export_integration_config()
        print(json.dumps(config, indent=2))

    elif args.generate_docs:
        docs = linker.generate_architecture_doc()
        output_path = Path("AMOS_6_REPO_ARCHITECTURE_GENERATED.md")
        output_path.write_text(docs)
        print(f"✅ Generated architecture docs: {output_path}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()