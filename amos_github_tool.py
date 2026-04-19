from typing import Any, Dict, List, Optional

"""AMOS GitHub Integration Tool
==============================
Real GitHub API integration using gidgethub + httpx.
Provides async GitHub operations that the AMOS brain can use.

Features:
- Repository operations (read, create issues, PRs)
- Code search and analysis
- Workflow monitoring
- Issue/PR management
"""

import asyncio
import os
from dataclasses import dataclass
from datetime import datetime, timezone

import httpx

try:
    from gidgethub import GitHubException
    from gidgethub.httpx import GitHubAPI

    _GIDGETHUB_AVAILABLE = True
except ImportError:
    _GIDGETHUB_AVAILABLE = False
    GitHubException = Exception  # type: ignore
    GitHubAPI = None  # type: ignore

@dataclass
class GitHubRepo:
    """GitHub repository data."""

    name: str
    owner: str
    description: str
    stars: int
    forks: int
    open_issues: int
    language: Optional[str]
    updated_at: str
    url: str

@dataclass
class GitHubIssue:
    """GitHub issue data."""

    number: int
    title: str
    state: str
    created_at: str
    updated_at: str
    author: str
    labels: List[str]
    url: str

class AMOSGitHubClient:
    """Async GitHub client for AMOS brain integration."""

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.environ.get("GITHUB_TOKEN")
        self._client: httpx.Optional[AsyncClient] = None
        self._github: Optional[GitHubAPI] = None

    async def __aenter__(self) -> AMOSGitHubClient:
        """Async context manager entry."""
        if not _GIDGETHUB_AVAILABLE:
            raise RuntimeError("gidgethub not installed. Run: pip install gidgethub")
        self._client = httpx.AsyncClient()
        self._github = GitHubAPI(
            self._client,
            "amos-github-tool",
            oauth_token=self.token,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()

    async def get_repo(self, owner: str, repo: str) -> GitHubRepo:
        """Get repository information."""
        if not self._github:
            raise RuntimeError("Client not initialized. Use async context manager.")

        data = await self._github.getitem(f"/repos/{owner}/{repo}")

        return GitHubRepo(
            name=data["name"],
            owner=data["owner"]["login"],
            description=data.get("description", ""),
            stars=data["stargazers_count"],
            forks=data["forks_count"],
            open_issues=data["open_issues_count"],
            language=data.get("language"),
            updated_at=data["updated_at"],
            url=data["html_url"],
        )

    async def list_issues(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        per_page: int = 10,
    ) -> List[GitHubIssue]:
        """List repository issues."""
        if not self._github:
            raise RuntimeError("Client not initialized. Use async context manager.")

        issues = []
        async for issue in self._github.getiter(
            f"/repos/{owner}/{repo}/issues",
            {"state": state, "per_page": str(per_page)},
        ):
            # Skip pull requests (GitHub API returns them as issues)
            if "pull_request" in issue:
                continue

            issues.append(
                GitHubIssue(
                    number=issue["number"],
                    title=issue["title"],
                    state=issue["state"],
                    created_at=issue["created_at"],
                    updated_at=issue["updated_at"],
                    author=issue["user"]["login"],
                    labels=[label["name"] for label in issue.get("labels", [])],
                    url=issue["html_url"],
                )

        return issues

    async def create_issue(
        self,
        owner: str,
        repo: str,
        title: str,
        body: str,
        labels: Optional[list[str]] = None,
    ) -> Dict[str, Any]:
        """Create a new issue."""
        if not self._github:
            raise RuntimeError("Client not initialized. Use async context manager.")

        data = {
            "title": title,
            "body": body,
        }
        if labels:
            data["labels"] = labels

        result = await self._github.post(f"/repos/{owner}/{repo}/issues", data=data)
        return result

    async def search_code(
        self,
        query: str,
        per_page: int = 10,
    ) -> list[dict[str, Any]]:
        """Search code across GitHub."""
        if not self._github:
            raise RuntimeError("Client not initialized. Use async context manager.")

        results = []
        async for item in self._github.getiter(
            "/search/code",
            {"q": query, "per_page": str(per_page)},
        ):
            results.append(
                {
                    "path": item["path"],
                    "repo": item["repository"]["full_name"],
                    "url": item["html_url"],
                    "score": item["score"],
                }
            )

        return results

    async def get_file_content(
        self,
        owner: str,
        repo: str,
        path: str,
        ref: str = "main",
    ) -> Optional[str]:
        """Get file content from repository."""
        if not self._github:
            raise RuntimeError("Client not initialized. Use async context manager.")

        try:
            data = await self._github.getitem(
                f"/repos/{owner}/{repo}/contents/{path}",
                {"ref": ref},
            )
            import base64
            content = base64.b64decode(data["content"]).decode("utf-8")
            return content
        except GitHubException:
            return None

    async def list_user_repos(
        self,
        username: str,
        per_page: int = 10,
    ) -> List[GitHubRepo]:
        """List user repositories."""
        if not self._github:
            raise RuntimeError("Client not initialized. Use async context manager.")

        repos = []
        async for data in self._github.getiter(
            f"/users/{username}/repos",
            {"per_page": str(per_page), "sort": "updated"},
        ):
            repos.append(
                GitHubRepo(
                    name=data["name"],
                    owner=data["owner"]["login"],
                    description=data.get("description", ""),
                    stars=data["stargazers_count"],
                    forks=data["forks_count"],
                    open_issues=data["open_issues_count"],
                    language=data.get("language"),
                    updated_at=data["updated_at"],
                    url=data["html_url"],
                )

        return repos

# ============================================================================
# AMOS Brain Integration
# ============================================================================

class GitHubToolForBrain:
    """GitHub tool that AMOS brain can use as a cognitive capability."""

    def __init__(self):
        self.client: Optional[AMOSGitHubClient] = None

    async def analyze_repo(
        self,
        owner: str,
        repo: str,
        context: Dict[str, Any]  = None,
    ) -> Dict[str, Any]:
        """Analyze a repository and return structured insights."""

        async with AMOSGitHubClient() as client:
            # Get repo info
            repo_data = await client.get_repo(owner, repo)

            # Get recent issues
            issues = await client.list_issues(owner, repo, state="open", per_page=5)

            # Analyze
            analysis = {
                "repo": {
                    "name": repo_data.name,
                    "owner": repo_data.owner,
                    "description": repo_data.description,
                    "url": repo_data.url,
                    "metrics": {
                        "stars": repo_data.stars,
                        "forks": repo_data.forks,
                        "open_issues": repo_data.open_issues,
                        "language": repo_data.language,
                    },
                "health_indicators": {
                    "issue_ratio": repo_data.open_issues / max(repo_data.stars, 1),
                    "has_description": bool(repo_data.description),
                    "is_active": self._is_recently_updated(repo_data.updated_at),
                },
                "open_issues": [
                    {
                        "number": i.number,
                        "title": i.title,
                        "labels": i.labels,
                        "url": i.url,
                    }
                    for i in issues[:5]
                ],
                "recommendations": self._generate_recommendations(repo_data, issues),
            }

            return analysis

    def _is_recently_updated(self, updated_at: str) -> bool:
        """Check if repo was updated in last 30 days."""
        try:
            updated = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
            days_since = (datetime.now(timezone.utc) - updated).days
            return days_since <= 30
        except (ValueError, TypeError):
            return False

    def _generate_recommendations(
        self,
        repo: GitHubRepo,
        issues: List[GitHubIssue],
    ) -> List[str]:
        """Generate recommendations based on repo analysis."""
        recs = []

        if repo.open_issues > 50:
            recs.append(f"High issue count ({repo.open_issues}). Consider triage.")

        if not repo.description:
            recs.append("Add repository description for better discoverability.")

        if not self._is_recently_updated(repo.updated_at):
            recs.append("Repository appears inactive. Consider maintenance.")

        # Check for common issue patterns
        bug_count = sum(1 for i in issues if "bug" in [l.lower() for l in i.labels])
        if bug_count > 5:
            recs.append(f"High bug count ({bug_count}). Prioritize bug fixes.")

        return recs

    async def find_similar_repos(
        self,
        language: str,
        topic: str,
        per_page: int = 5,
    ) -> list[dict[str, Any]]:
        """Find similar repositories by language and topic."""
        async with AMOSGitHubClient() as client:
            query = f"language:{language} topic:{topic} stars:>100"
            results = await client.search_code(query, per_page=per_page)
            return results

# ============================================================================
# CLI Interface
# ============================================================================

async def main():
    """CLI demo of GitHub tool."""

    tool = GitHubToolForBrain()

    # Demo: Analyze this repo
    print("=== AMOS GitHub Tool Demo ===\n")

    print("Analyzing trangyp/AMOS-code...")
    analysis = await tool.analyze_repo("trangyp", "AMOS-code")

    print(f"\nRepository: {analysis['repo']['owner']}/{analysis['repo']['name']}")
    print(f"Description: {analysis['repo']['description']}")
    print(f"Stars: {analysis['repo']['metrics']['stars']}")
    print(f"Open Issues: {analysis['repo']['metrics']['open_issues']}")
    print(f"Primary Language: {analysis['repo']['metrics']['language']}")

    print("\nHealth Indicators:")
    for key, value in analysis["health_indicators"].items():
        print(f"  {key}: {value}")

    print("\nRecent Open Issues:")
    for issue in analysis["open_issues"][:3]:
        print(f"  #{issue['number']}: {issue['title'][:60]}...")

    print("\nRecommendations:")
    for rec in analysis["recommendations"]:
        print(f"  - {rec}")

if __name__ == "__main__":
    # Check for token
    if not os.environ.get("GITHUB_TOKEN"):
        print("Warning: GITHUB_TOKEN not set. Some operations may fail.")
        print("Set GITHUB_TOKEN environment variable for authenticated requests.")
        print()

    asyncio.run(main())
