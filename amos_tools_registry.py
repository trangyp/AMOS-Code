from typing import Any, Dict, List, Optional

"""AMOS Tools Registry
====================
Registers all AMOS tools with the brain for cognitive task execution.

Tools registered:
- Code Analyzer: AST-based code quality analysis
- GitHub Client: Repository and issue management
- Real-time Streaming: WebSocket and SSE streaming
"""

import asyncio
from collections.abc import Callable, Coroutine
from dataclasses import dataclass

from amos_brain.task_processor import BrainTaskProcessor
from amos_code_analyzer import AMOSCodeAnalyzer


@dataclass
class Tool:
    """A registered tool."""

    name: str
    description: str
    func: Callable[..., Coroutine[Any, Any, Any]]
    parameters: Dict[str, str]


class AMOSToolRegistry:
    """Registry of tools that AMOS brain can use."""

    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self._analyzer = AMOSCodeAnalyzer()

    def register(self, tool: Tool) -> None:
        """Register a tool."""
        self.tools[tool.name] = tool

    async def execute(self, tool_name: str, **kwargs: Any) -> Any:
        """Execute a registered tool."""
        tool = self.tools.get(tool_name)
        if not tool:
            return {"error": f"Tool '{tool_name}' not found"}

        try:
            return await tool.func(**kwargs)
        except Exception as e:
            return {"error": str(e)}

    def list_tools(self) -> List[dict[str, str]]:
        """List all registered tools."""
        return [
            {
                "name": t.name,
                "description": t.description,
                "parameters": list(t.parameters.keys()),
            }
            for t in self.tools.values()
        ]


# ============================================================================
# Tool Implementations
# ============================================================================


async def analyze_code_file(filepath: str) -> Dict[str, Any]:
    """Analyze a Python file for code quality issues."""
    from pathlib import Path

    analyzer = AMOSCodeAnalyzer()
    result = analyzer.analyze_file(Path(filepath))

    return {
        "file": result.file,
        "issues": [
            {
                "line": i.line,
                "type": i.issue_type,
                "message": i.message,
                "severity": i.severity,
            }
            for i in result.issues
        ],
        "metrics": result.metrics,
        "has_errors": result.has_errors,
        "issue_count": result.issue_count,
    }


async def analyze_code_directory(directory: str, max_files: int = 20) -> Dict[str, Any]:
    """Analyze all Python files in a directory."""

    analyzer = AMOSCodeAnalyzer()
    results = analyzer.analyze_directory(Path(directory), max_files=max_files)

    total_issues = sum(r.issue_count for r in results)
    files_with_errors = sum(1 for r in results if r.has_errors)

    return {
        "directory": directory,
        "files_analyzed": len(results),
        "total_issues": total_issues,
        "files_with_errors": files_with_errors,
        "files": [
            {
                "file": r.file,
                "issues": r.issue_count,
                "has_errors": r.has_errors,
            }
            for r in results
        ],
    }


async def get_repo_info(owner: str, repo: str) -> Dict[str, Any]:
    """Get GitHub repository information."""
    from amos_github_tool import GitHubToolForBrain

    tool = GitHubToolForBrain()

    try:
        analysis = await tool.analyze_repo(owner, repo)
        return analysis
    except Exception as e:
        return {"error": str(e), "owner": owner, "repo": repo}


# ============================================================================
# Global Registry Instance
# ============================================================================

_registry: Optional[AMOSToolRegistry] = None


def get_registry() -> AMOSToolRegistry:
    """Get or create the global tool registry."""
    global _registry

    if _registry is None:
        _registry = AMOSToolRegistry()

        # Register all tools
        _registry.register(
            Tool(
                name="analyze_code_file",
                description="Analyze a Python file for code quality issues",
                func=analyze_code_file,
                parameters={"filepath": "Path to Python file"},
            )
        )

        _registry.register(
            Tool(
                name="analyze_code_directory",
                description="Analyze all Python files in a directory",
                func=analyze_code_directory,
                parameters={
                    "directory": "Path to directory",
                    "max_files": "Maximum files to analyze (default 20)",
                },
            )
        )

        _registry.register(
            Tool(
                name="get_repo_info",
                description="Get GitHub repository information and analysis",
                func=get_repo_info,
                parameters={
                    "owner": "Repository owner",
                    "repo": "Repository name",
                },
            )
        )

    return _registry


# ============================================================================
# Brain Integration
# ============================================================================


class BrainWithTools:
    """AMOS brain enhanced with tool execution."""

    def __init__(self):
        self.brain = BrainTaskProcessor()
        self.registry = get_registry()

    async def process_with_tools(self, task: str) -> Dict[str, Any]:
        """Process task, using tools when needed."""

        # First, get brain analysis
        brain_result = self.brain.process(task)

        # Check if task requires tool execution
        task_lower = task.lower()
        tool_results = {}

        # Code analysis tasks
        if "analyze code" in task_lower or "code quality" in task_lower:
            # Extract file path from task
            words = task.split()
            for i, word in enumerate(words):
                if word.endswith(".py") and i > 0:
                    filepath = word.strip("'\".,")
                    tool_results["code_analysis"] = await self.registry.execute(
                        "analyze_code_file", filepath=filepath
                    )

        # GitHub tasks
        if "github" in task_lower or "repository" in task_lower:
            # Try to extract owner/repo
            match = re.search(r"(\w+)/(\w+)", task)
            if match:
                owner, repo = match.groups()
                tool_results["github_info"] = await self.registry.execute(
                    "get_repo_info", owner=owner, repo=repo
                )

        return {
            "brain_result": {
                "task_id": brain_result.task_id,
                "output": brain_result.output,
                "confidence": brain_result.confidence,
            },
            "tool_results": tool_results,
            "tools_used": list(tool_results.keys()),
        }


# ============================================================================
# Demo
# ============================================================================


async def demo():
    """Demonstrate tools registry."""

    print("=== AMOS Tools Registry Demo ===\n")

    # Show registered tools
    registry = get_registry()
    tools = registry.list_tools()

    print(f"Registered Tools ({len(tools)}):")
    for tool in tools:
        print(f"  - {tool['name']}: {tool['description']}")
    print()

    # Execute a tool
    print("Executing: analyze_code_file on amos_code_analyzer.py")
    result = await registry.execute("analyze_code_file", filepath="amos_code_analyzer.py")

    print(f"  File: {result['file']}")
    print(f"  Issues: {result['issue_count']}")
    print(f"  Has errors: {result['has_errors']}")
    print()

    # Use brain with tools
    print("Using BrainWithTools:")
    brain_tools = BrainWithTools()
    result = await brain_tools.process_with_tools("Analyze code quality in amos_code_analyzer.py")

    print(f"  Brain confidence: {result['brain_result']['confidence']}")
    print(f"  Tools used: {result['tools_used']}")
    if "code_analysis" in result["tool_results"]:
        analysis = result["tool_results"]["code_analysis"]
        print(f"  Found {analysis.get('issue_count', 0)} issues")


if __name__ == "__main__":
    asyncio.run(demo())
