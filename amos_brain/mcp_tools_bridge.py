from typing import Any

"""AMOS MCP Tools Bridge - Connect MCP tools to SuperBrain.

This module bridges the gap between amos_mcp_tools.py and the brain's
GovernedToolRegistry, enabling the brain to use real-world tools with
proper safety validation and law compliance.

Tools Integrated:
  - FilesystemTool: Read/write files, search, directory operations
  - GitTool: Repository operations, status, log, diff
  - WebSearchTool: Internet search, URL fetching
  - CodeExecutionTool: Safe Python execution
  - DatabaseTool: SQL queries (optional)

Safety:
  - All operations validated through ActionGate
  - Law compliance checks (L1-L6)
  - Path traversal protection
  - Execution timeouts
  - Audit logging
"""

import sys
from pathlib import Path

# Add repo root to path
REPO_ROOT = Path(__file__).parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


from amos_mcp_tools import CodeExecutionTool, FilesystemTool, GitTool, ToolResult, WebSearchTool


class MCPToolsBridge:
    """Bridge between MCP tools and AMOS brain's tool registry.

    Wraps amos_mcp_tools to provide functions compatible with
    GovernedToolRegistry registration.
    """

    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self._fs_tool = FilesystemTool(root_path=str(self.root_path))
        self._git_tool = GitTool(repo_path=str(self.root_path))
        self._web_tool = WebSearchTool()
        self._code_tool = CodeExecutionTool(timeout=30)

    def _tool_result_to_dict(self, result: ToolResult) -> dict[str, Any]:
        """Convert ToolResult to dictionary for brain consumption."""
        return {
            "success": result.success,
            "content": result.content,
            "error": result.error,
            "metadata": result.metadata,
            "execution_time": result.execution_time,
            "law_compliant": result.law_compliant,
        }

    # ========================================================================
    # Filesystem Operations
    # ========================================================================

    def fs_read_file(self, path: str) -> dict[str, Any]:
        """Read file or list directory contents.

        Args:
            path: Relative path to file or directory

        Returns:
            Tool result with content or directory listing
        """
        result = self._fs_tool.read_file(path)
        return self._tool_result_to_dict(result)

    def fs_write_file(self, path: str, content: str) -> dict[str, Any]:
        """Write content to file.

        Args:
            path: Relative path to file
            content: Text content to write

        Returns:
            Tool result with write status
        """
        result = self._fs_tool.write_file(path, content)
        return self._tool_result_to_dict(result)

    def fs_search_files(self, pattern: str, path: str = ".") -> dict[str, Any]:
        """Search files for pattern.

        Args:
            pattern: Text pattern to search for
            path: Directory to search in (default: current)

        Returns:
            Tool result with matching files and lines
        """
        result = self._fs_tool.search_files(pattern, path)
        return self._tool_result_to_dict(result)

    # ========================================================================
    # Git Operations
    # ========================================================================

    def git_status(self) -> dict[str, Any]:
        """Get repository status.

        Returns:
            Git status output
        """
        result = self._git_tool.status()
        return self._tool_result_to_dict(result)

    def git_log(self, n: int = 10) -> dict[str, Any]:
        """Get commit log.

        Args:
            n: Number of commits to show (default: 10)

        Returns:
            Git log output
        """
        result = self._git_tool.log(n)
        return self._tool_result_to_dict(result)

    def git_diff(self) -> dict[str, Any]:
        """Get working directory changes.

        Returns:
            Git diff output
        """
        result = self._git_tool.diff()
        return self._tool_result_to_dict(result)

    # ========================================================================
    # Web Operations
    # ========================================================================

    def web_search(self, query: str, num_results: int = 5) -> dict[str, Any]:
        """Perform web search.

        Args:
            query: Search query
            num_results: Number of results (default: 5)

        Returns:
            Search results
        """
        result = self._web_tool.search(query, num_results)
        return self._tool_result_to_dict(result)

    def web_fetch(self, url: str) -> dict[str, Any]:
        """Fetch and extract text from URL.

        Args:
            url: URL to fetch

        Returns:
            Extracted text content
        """
        result = self._web_tool.fetch_url(url)
        return self._tool_result_to_dict(result)

    # ========================================================================
    # Code Execution
    # ========================================================================

    def code_execute_python(self, code: str) -> dict[str, Any]:
        """Execute Python code safely.

        Args:
            code: Python code to execute

        Returns:
            Execution result
        """
        result = self._code_tool.execute_python(code)
        return self._tool_result_to_dict(result)

    def code_analyze(self, code: str, language: str = "python") -> dict[str, Any]:
        """Analyze code for issues.

        Args:
            code: Code to analyze
            language: Programming language (default: python)

        Returns:
            Analysis results with issues
        """
        result = self._code_tool.analyze_code(code, language)
        return self._tool_result_to_dict(result)


# Tool schemas for GovernedToolRegistry
MCP_TOOL_SCHEMAS: dict[str, dict[str, Any]] = {
    "fs_read_file": {
        "type": "object",
        "properties": {"path": {"type": "string", "description": "Path to file or directory"}},
        "required": ["path"],
    },
    "fs_write_file": {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Path to file"},
            "content": {"type": "string", "description": "Content to write"},
        },
        "required": ["path", "content"],
    },
    "fs_search_files": {
        "type": "object",
        "properties": {
            "pattern": {"type": "string", "description": "Text pattern to search"},
            "path": {"type": "string", "description": "Directory to search", "default": "."},
        },
        "required": ["pattern"],
    },
    "git_status": {"type": "object", "properties": {}, "required": []},
    "git_log": {
        "type": "object",
        "properties": {"n": {"type": "integer", "description": "Number of commits", "default": 10}},
        "required": [],
    },
    "git_diff": {"type": "object", "properties": {}, "required": []},
    "web_search": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query"},
            "num_results": {"type": "integer", "description": "Results to return", "default": 5},
        },
        "required": ["query"],
    },
    "web_fetch": {
        "type": "object",
        "properties": {"url": {"type": "string", "description": "URL to fetch"}},
        "required": ["url"],
    },
    "code_execute_python": {
        "type": "object",
        "properties": {"code": {"type": "string", "description": "Python code to execute"}},
        "required": ["code"],
    },
    "code_analyze": {
        "type": "object",
        "properties": {
            "code": {"type": "string", "description": "Code to analyze"},
            "language": {"type": "string", "description": "Language", "default": "python"},
        },
        "required": ["code"],
    },
}

MCP_TOOL_DESCRIPTIONS: dict[str, str] = {
    "fs_read_file": "Read file contents or list directory",
    "fs_write_file": "Write content to file (path validated)",
    "fs_search_files": "Search files for text pattern",
    "git_status": "Get git repository status",
    "git_log": "View commit history",
    "git_diff": "Show working directory changes",
    "web_search": "Search the web for information",
    "web_fetch": "Fetch and extract text from URL",
    "code_execute_python": "Execute Python code safely (sandboxed)",
    "code_analyze": "Analyze code for issues and improvements",
}


def register_mcp_tools(registry: Any, root_path: str = ".") -> None:
    """Register all MCP tools with a GovernedToolRegistry.

    Args:
        registry: GovernedToolRegistry instance
        root_path: Root path for filesystem/git operations
    """
    bridge = MCPToolsBridge(root_path)

    # Register filesystem tools
    registry.register(
        name="fs_read_file",
        func=bridge.fs_read_file,
        description=MCP_TOOL_DESCRIPTIONS["fs_read_file"],
        schema=MCP_TOOL_SCHEMAS["fs_read_file"],
    )
    registry.register(
        name="fs_write_file",
        func=bridge.fs_write_file,
        description=MCP_TOOL_DESCRIPTIONS["fs_write_file"],
        schema=MCP_TOOL_SCHEMAS["fs_write_file"],
    )
    registry.register(
        name="fs_search_files",
        func=bridge.fs_search_files,
        description=MCP_TOOL_DESCRIPTIONS["fs_search_files"],
        schema=MCP_TOOL_SCHEMAS["fs_search_files"],
    )

    # Register git tools
    registry.register(
        name="git_status",
        func=bridge.git_status,
        description=MCP_TOOL_DESCRIPTIONS["git_status"],
        schema=MCP_TOOL_SCHEMAS["git_status"],
    )
    registry.register(
        name="git_log",
        func=bridge.git_log,
        description=MCP_TOOL_DESCRIPTIONS["git_log"],
        schema=MCP_TOOL_SCHEMAS["git_log"],
    )
    registry.register(
        name="git_diff",
        func=bridge.git_diff,
        description=MCP_TOOL_DESCRIPTIONS["git_diff"],
        schema=MCP_TOOL_SCHEMAS["git_diff"],
    )

    # Register web tools
    registry.register(
        name="web_search",
        func=bridge.web_search,
        description=MCP_TOOL_DESCRIPTIONS["web_search"],
        schema=MCP_TOOL_SCHEMAS["web_search"],
    )
    registry.register(
        name="web_fetch",
        func=bridge.web_fetch,
        description=MCP_TOOL_DESCRIPTIONS["web_fetch"],
        schema=MCP_TOOL_SCHEMAS["web_fetch"],
    )

    # Register code tools
    registry.register(
        name="code_execute_python",
        func=bridge.code_execute_python,
        description=MCP_TOOL_DESCRIPTIONS["code_execute_python"],
        schema=MCP_TOOL_SCHEMAS["code_execute_python"],
    )
    registry.register(
        name="code_analyze",
        func=bridge.code_analyze,
        description=MCP_TOOL_DESCRIPTIONS["code_analyze"],
        schema=MCP_TOOL_SCHEMAS["code_analyze"],
    )

    print(f"✅ MCP Tools Bridge: {len(MCP_TOOL_SCHEMAS)} tools registered")
