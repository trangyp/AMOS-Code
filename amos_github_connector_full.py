#!/usr/bin/env python3
"""
AMOS GitHub Connector - Full Integration for trangyp Repos
Connects all repositories under https://github.com/trangyp

Repos:
- AMOS-Claws (HTML/MIT)
- AMOS-Consulting (Python/MIT)
- Mailinhconect (HTML/MIT)
- AMOS-Invest (HTML/MIT)
- AMOS-Code (Python/Apache-2.0)
- AMOS-UNIVERSE (Python)
- mailinhconnect-web (TypeScript)
- AMOS-STAR (Python)
- AMOS (Private)
- AMOS-SYSTEM (Python)
"""

import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class GitHubRepo:
    """GitHub repository metadata."""

    name: str
    owner: str = "trangyp"
    language: str = ""
    license: str = ""
    private: bool = True
    local_path: Optional[Path] = None
    cloned: bool = False
    last_sync: datetime = None
    commit_count: int = 0

    @property
    def url(self) -> str:
        return f"https://github.com/{self.owner}/{self.name}"

    @property
    def ssh_url(self) -> str:
        return f"git@github.com:{self.owner}/{self.name}.git"


class AMOSGitHubConnector:
    """Connects to all trangyp GitHub repositories."""

    REPOS = [
        GitHubRepo("AMOS-Claws", language="HTML", license="MIT"),
        GitHubRepo("AMOS-Consulting", language="Python", license="MIT"),
        GitHubRepo("Mailinhconect", language="HTML", license="MIT"),
        GitHubRepo("AMOS-Invest", language="HTML", license="MIT"),
        GitHubRepo("AMOS-Code", language="Python", license="Apache-2.0"),
        GitHubRepo("AMOS-UNIVERSE", language="Python", license=""),
        GitHubRepo("mailinhconnect-web", language="TypeScript", license=""),
        GitHubRepo("AMOS-STAR", language="Python", license=""),
        GitHubRepo("AMOS", language="", license=""),
        GitHubRepo("AMOS-SYSTEM", language="Python", license=""),
    ]

    def __init__(self, base_path: str = "./github_repos"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        self.repos: Dict[str, GitHubRepo] = {}
        self._init_repos()

    def _init_repos(self) -> None:
        """Initialize repo tracking."""
        for repo in self.REPOS:
            repo.local_path = self.base_path / repo.name
            self.repos[repo.name] = repo

    def clone_all(self) -> Dict[str, bool]:
        """Clone all repositories."""
        results = {}
        for name, repo in self.repos.items():
            try:
                if repo.local_path.exists():
                    # Pull instead of clone
                    result = subprocess.run(
                        ["git", "pull"],
                        cwd=repo.local_path,
                        capture_output=True,
                        text=True,
                        timeout=60,
                    )
                    repo.cloned = result.returncode == 0
                else:
                    # Clone fresh
                    result = subprocess.run(
                        ["git", "clone", repo.url, str(repo.local_path)],
                        capture_output=True,
                        text=True,
                        timeout=120,
                    )
                    repo.cloned = result.returncode == 0

                if repo.cloned:
                    repo.last_sync = datetime.now(UTC)
                    repo.commit_count = self._get_commit_count(repo)

                results[name] = repo.cloned
            except Exception:
                results[name] = False
                repo.cloned = False

        return results

    def _get_commit_count(self, repo: GitHubRepo) -> int:
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

    def get_repo_stats(self) -> Dict[str, Any]:
        """Get statistics for all repos."""
        return {
            name: {
                "url": repo.url,
                "cloned": repo.cloned,
                "local_path": str(repo.local_path) if repo.local_path else None,
                "last_sync": repo.last_sync.isoformat() if repo.last_sync else None,
                "commits": repo.commit_count,
                "language": repo.language,
                "license": repo.license,
            }
            for name, repo in self.repos.items()
        }

    def get_all_files(self, extension: str = ".py") -> List[Path]:
        """Get all files with extension across all repos."""
        files = []
        for repo in self.repos.values():
            if repo.cloned and repo.local_path:
                files.extend(repo.local_path.rglob(f"*{extension}"))
        return files

    def sync_all(self) -> Dict[str, bool]:
        """Sync all repositories."""
        return self.clone_all()

    def get_all_repos(self) -> List[str]:
        """Get list of all repo names."""
        return list(self.repos.keys())

    def discover_repos(self) -> List[str]:
        """Discover available repos (returns configured repos)."""
        return self.get_all_repos()


# Global connector instance
_connector: Optional[AMOSGitHubConnector] = None


def get_github_connector(base_path: str = "./github_repos") -> AMOSGitHubConnector:
    """Get global GitHub connector instance."""
    global _connector
    if _connector is None:
        _connector = AMOSGitHubConnector(base_path)
    return _connector


# Convenience functions
def connect_all_repos() -> Dict[str, bool]:
    """Connect and clone all trangyp repos."""
    connector = get_github_connector()
    return connector.clone_all()


def get_repo_stats() -> Dict[str, Any]:
    """Get stats for all repos."""
    connector = get_github_connector()
    return connector.get_repo_stats()


if __name__ == "__main__":
    print("=" * 70)
    print("🌐 AMOS GitHub Connector - trangyp Repositories")
    print("=" * 70)
    print()

    connector = get_github_connector()

    print("Repositories configured:")
    for name, repo in connector.repos.items():
        print(f"  • {name} ({repo.language}) - {repo.license}")

    print()
    print("To clone all repos:")
    print("  connector.clone_all()")
    print()
    print("To get stats:")
    print("  connector.get_repo_stats()")
