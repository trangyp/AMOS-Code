#!/usr/bin/env python3
"""
AMOS GitHub Connector — Repository Integration for trangyp/AMOS Ecosystem

Connects to all repositories under https://github.com/trangyp:
- AMOS-Code (main repository)
- AMOS-PUBLIC (public specs)
- ClawSpring (AI assistant framework)
- Any additional repos in the ecosystem

Features:
- Repository discovery and indexing
- Issue/PR tracking
- Code synchronization
- Release monitoring
- Automated documentation updates

Owner: Trang
Version: 1.0.0
"""

import asyncio
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc
from pathlib import Path
from typing import Any

import aiohttp


@dataclass
class GitHubRepository:
    """Represents a GitHub repository in the AMOS ecosystem."""

    name: str
    full_name: str
    url: str
    description: str = ""
    stars: int = 0
    forks: int = 0
    open_issues: int = 0
    default_branch: str = "main"
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    local_path: Optional[Path] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "full_name": self.full_name,
            "url": self.url,
            "description": self.description,
            "stars": self.stars,
            "forks": self.forks,
            "open_issues": self.open_issues,
            "default_branch": self.default_branch,
            "last_updated": self.last_updated.isoformat(),
            "local_path": str(self.local_path) if self.local_path else None,
        }


@dataclass
class RepositoryIssue:
    """GitHub issue from AMOS ecosystem."""

    number: int
    title: str
    state: str
    created_at: datetime
    updated_at: datetime
    labels: list[str] = field(default_factory=list)
    body: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "number": self.number,
            "title": self.title,
            "state": self.state,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "labels": self.labels,
        }


class AMOSGitHubConnector:
    """
    Connector for trangyp GitHub repositories.

    Manages all AMOS ecosystem repositories and provides:
    - Repository discovery
    - Issue tracking
    - Code synchronization
    - Documentation fetching

    Usage:
        connector = AMOSGitHubConnector()
        await connector.discover_repos()
        repos = connector.get_all_repos()
    """

    _instance: Optional[AMOSGitHubConnector] = None
    GITHUB_API_BASE = "https://api.github.com"

    def __new__(cls) -> AMOSGitHubConnector:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, token: str = None):
        if hasattr(self, "_initialized"):
            return

        self.token = token or os.environ.get("GITHUB_TOKEN")
        self._repos: dict[str, GitHubRepository] = {}
        self._session: aiohttp.ClientSession = None
        self._initialized = False
        self._owner = "trangyp"

        # Known AMOS ecosystem repositories
        self._core_repos = [
            "AMOS-Code",
            "AMOS-PUBLIC",
            "ClawSpring",
        ]

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if self._session is None or self._session.closed:
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "AMOS-GitHub-Connector/1.0",
            }
            if self.token:
                headers["Authorization"] = f"token {self.token}"
            self._session = aiohttp.ClientSession(headers=headers)
        return self._session

    async def discover_repos(self) -> list[GitHubRepository]:
        """
        Discover all repositories under trangyp.

        Returns:
            List of discovered repositories
        """
        session = await self._get_session()
        url = f"{self.GITHUB_API_BASE}/users/{self._owner}/repos"

        discovered: list[GitHubRepository] = []

        try:
            async with session.get(url, params={"per_page": 100}) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    for repo_data in data:
                        repo = GitHubRepository(
                            name=repo_data["name"],
                            full_name=repo_data["full_name"],
                            url=repo_data["html_url"],
                            description=repo_data.get("description", ""),
                            stars=repo_data.get("stargazers_count", 0),
                            forks=repo_data.get("forks_count", 0),
                            open_issues=repo_data.get("open_issues_count", 0),
                            default_branch=repo_data.get("default_branch", "main"),
                            last_updated=datetime.fromisoformat(
                                repo_data["updated_at"].replace("Z", "+00:00")
                            ),
                        )
                        self._repos[repo.name] = repo
                        discovered.append(repo)

            print(f"✓ Discovered {len(discovered)} repositories")
            return discovered

        except Exception as e:
            print(f"❌ Failed to discover repos: {e}")
            return []

    async def get_repo_issues(
        self,
        repo_name: str,
        state: str = "open",
        labels: Optional[list[str] ] = None,
    ) -> list[RepositoryIssue]:
        """
        Get issues from a specific repository.

        Args:
            repo_name: Repository name
            state: Issue state (open/closed/all)
            labels: Filter by labels

        Returns:
            List of issues
        """
        session = await self._get_session()
        url = f"{self.GITHUB_API_BASE}/repos/{self._owner}/{repo_name}/issues"

        params: dict[str, Any] = {
            "state": state,
            "per_page": 100,
        }
        if labels:
            params["labels"] = ",".join(labels)

        issues: list[RepositoryIssue] = []

        try:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    for issue_data in data:
                        # Skip pull requests
                        if "pull_request" in issue_data:
                            continue

                        issue = RepositoryIssue(
                            number=issue_data["number"],
                            title=issue_data["title"],
                            state=issue_data["state"],
                            created_at=datetime.fromisoformat(
                                issue_data["created_at"].replace("Z", "+00:00")
                            ),
                            updated_at=datetime.fromisoformat(
                                issue_data["updated_at"].replace("Z", "+00:00")
                            ),
                            labels=[lbl["name"] for lbl in issue_data.get("labels", [])],
                            body=issue_data.get("body", ""),
                        )
                        issues.append(issue)

            return issues

        except Exception as e:
            print(f"❌ Failed to get issues: {e}")
            return []

    async def fetch_repo_content(
        self,
        repo_name: str,
        path: str = "",
        ref: str = "main",
    ) -> dict[str, Any]:
        """
        Fetch content from a repository path.

        Args:
            repo_name: Repository name
            path: File or directory path
            ref: Git reference (branch/tag/commit)

        Returns:
            Content data or None if failed
        """
        session = await self._get_session()
        url = f"{self.GITHUB_API_BASE}/repos/{self._owner}/{repo_name}/contents/{path}"

        try:
            async with session.get(url, params={"ref": ref}) as resp:
                if resp.status == 200:
                    return await resp.json()
                return None

        except Exception as e:
            print(f"❌ Failed to fetch content: {e}")
            return None

    async def fetch_raw_file(
        self,
        repo_name: str,
        path: str,
        ref: str = "main",
    ) -> str:
        """
        Fetch raw file content from a repository.

        Args:
            repo_name: Repository name
            path: File path
            ref: Git reference

        Returns:
            File content as string or None
        """
        raw_url = f"https://raw.githubusercontent.com/{self._owner}/{repo_name}/{ref}/{path}"
        session = await self._get_session()

        try:
            async with session.get(raw_url) as resp:
                if resp.status == 200:
                    return await resp.text()
                return None

        except Exception as e:
            print(f"❌ Failed to fetch file: {e}")
            return None

    def get_all_repos(self) -> list[GitHubRepository]:
        """Get all discovered repositories."""
        return list(self._repos.values())

    def get_core_repos(self) -> list[GitHubRepository]:
        """Get core AMOS ecosystem repositories."""
        return [self._repos[name] for name in self._core_repos if name in self._repos]

    async def sync_all_repos(self, base_path: Path) -> dict[str, Path]:
        """
        Clone or pull all repositories to local path.

        Args:
            base_path: Base directory for repositories

        Returns:
            Mapping of repo names to local paths
        """
        import subprocess

        synced: dict[str, Path] = {}

        for repo_name in self._core_repos:
            repo_path = base_path / repo_name

            if repo_path.exists():
                # Pull existing repo
                try:
                    subprocess.run(
                        ["git", "pull"],
                        cwd=repo_path,
                        capture_output=True,
                        check=True,
                    )
                    synced[repo_name] = repo_path
                    print(f"✓ Updated {repo_name}")
                except subprocess.CalledProcessError as e:
                    print(f"❌ Failed to pull {repo_name}: {e}")
            else:
                # Clone new repo
                try:
                    subprocess.run(
                        [
                            "git",
                            "clone",
                            f"https://github.com/{self._owner}/{repo_name}.git",
                            str(repo_path),
                        ],
                        capture_output=True,
                        check=True,
                    )
                    synced[repo_name] = repo_path
                    print(f"✓ Cloned {repo_name}")
                except subprocess.CalledProcessError as e:
                    print(f"❌ Failed to clone {repo_name}: {e}")

        return synced

    async def close(self):
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()


# Global connector instance
_github_connector: Optional[AMOSGitHubConnector] = None


async def get_github_connector() -> AMOSGitHubConnector:
    """Get or create the global GitHub connector."""
    global _github_connector
    if _github_connector is None:
        _github_connector = AMOSGitHubConnector()
        await _github_connector.discover_repos()
    return _github_connector


if __name__ == "__main__":

    async def test():
        connector = await get_github_connector()
        repos = connector.get_all_repos()
        print(f"\n📦 Found {len(repos)} repositories:")
        for repo in repos:
            print(
                f"  - {repo.name}: {repo.description[:50] if repo.description else 'No description'}..."
            )

        if repos:
            issues = await connector.get_repo_issues(repos[0].name)
            print(f"\n🎫 Open issues in {repos[0].name}: {len(issues)}")

        await connector.close()

    asyncio.run(test())
