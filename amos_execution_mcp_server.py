#!/usr/bin/env python3
"""AMOS Execution Platform MCP Server.

Exposes sandbox, browser, and research capabilities via Model Context Protocol (MCP).
Uses the official FastMCP SDK for state-of-the-art 2025 compatibility.

Tools exposed:
- execute_code: Run code in secure sandbox (E2B/Daytona/Docker)
- browse_web: Browser automation (Playwright)
- research_topic: Web search (Tavily/Brave)
- get_execution_status: Check platform health and available providers

Usage:
    # Install dependencies
    pip install mcp e2b daytona-sdk playwright aiohttp

    # Run with stdio transport (for Claude Desktop, etc.)
    python amos_execution_mcp_server.py

    # Run with HTTP transport
    python amos_execution_mcp_server.py --transport http --port 8000

MCP Configuration:
{
  "mcpServers": {
    "amos-execution": {
      "type": "stdio",
      "command": "python3",
      "args": ["/path/to/amos_execution_mcp_server.py"]
    }
  }
}

Environment Variables:
    E2B_API_KEY - E2B sandbox API key
    DAYTONA_API_KEY - Daytona sandbox API key
    DAYTONA_SERVER_URL - Daytona server URL
    TAVILY_API_KEY - Tavily search API key
    BRAVE_API_KEY - Brave search API key
"""

import os
import sys
from typing import Any

from pydantic import BaseModel, Field

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Try to import FastMCP
try:
    from mcp.server.fastmcp import FastMCP
    from mcp.types import CallToolResult, TextContent

    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("Error: mcp package not installed. Run: pip install mcp", file=sys.stderr)
    sys.exit(1)

# Import execution platform
try:
    from amos_execution_platform import (
        AMOSExecutionPlatform,
        BrowserAction,
        ExecutionResult,
        ExecutionStatus,
        ResearchQuery,
    )

    PLATFORM_AVAILABLE = True
except ImportError:
    PLATFORM_AVAILABLE = False
    print("Warning: amos_execution_platform not available", file=sys.stderr)

# Initialize FastMCP server
mcp = FastMCP("AMOS-Execution", json_response=True)

# Global platform instance (lazy initialization)
_platform: Optional[AMOSExecutionPlatform] = None


def get_platform() -> AMOSExecutionPlatform:
    """Get or initialize the execution platform."""
    global _platform
    if _platform is None:
        _platform = AMOSExecutionPlatform()
    return _platform


# ============================================================================
# Pydantic Models for Structured Output
# ============================================================================


class CodeExecutionResult(BaseModel):
    """Result of code execution in sandbox."""

    status: str = Field(description="Execution status: success, error, or timeout")
    stdout: str = Field(description="Standard output from execution")
    stderr: str = Field(description="Standard error from execution")
    exit_code: int = Field(description="Process exit code")
    execution_time_ms: float = Field(description="Execution time in milliseconds")
    provider: str = Field(description="Provider used (e2b, daytona, docker)")
    artifacts: Dict[str, Any] = Field(
        default_factory=dict, description="Any output files or artifacts generated"
    )


class WebBrowseResult(BaseModel):
    """Result of web browsing automation."""

    status: str = Field(description="Browse status: success or error")
    url: str = Field(description="URL that was browsed")
    title: str = Field(description="Page title")
    content_preview: str = Field(description="Preview of page content (first 1000 chars)")
    screenshot_path: str = Field(default=None, description="Path to screenshot if captured")
    actions_performed: int = Field(description="Number of actions performed")
    provider: str = Field(description="Browser provider used")


class ResearchResult(BaseModel):
    """Result of web research query."""

    status: str = Field(description="Research status: success or error")
    query: str = Field(description="Original search query")
    results_count: int = Field(description="Number of results found")
    results: list[dict[str, Any]] = Field(description="List of search results")
    provider: str = Field(description="Research provider used")


class ExecutionStatusResult(BaseModel):
    """Status of execution platform."""

    healthy: bool = Field(description="Overall platform health")
    sandbox_providers: list[str] = Field(description="Available sandbox providers")
    browser_providers: list[str] = Field(description="Available browser providers")
    research_providers: list[str] = Field(description="Available research providers")
    metrics: Dict[str, int] = Field(description="Usage metrics")


# ============================================================================
# MCP Tools
# ============================================================================


@mcp.tool()
async def execute_code(
    code: str,
    language: str = "python",
    timeout_seconds: int = 30,
    provider_preference: str = None,
) -> CodeExecutionResult:
    """Execute code in a secure sandbox environment.

    Supports Python, JavaScript, TypeScript, and other languages.
    Automatically selects best available provider (E2B, Daytona, or Docker).

    Args:
        code: The code to execute
        language: Programming language (python, javascript, typescript, etc.)
        timeout_seconds: Maximum execution time (default: 30s)
        provider_preference: Preferred provider (e2b, daytona, docker) or None for auto

    Returns:
        CodeExecutionResult with stdout, stderr, exit code, and metadata
    """
    if not PLATFORM_AVAILABLE:
        return CodeExecutionResult(
            status="error",
            stdout="",
            stderr="Execution platform not available",
            exit_code=-1,
            execution_time_ms=0.0,
            provider="none",
        )

    platform = get_platform()

    try:
        result = await platform.execute_code_secure(
            code=code,
            language=language,
            preferred_provider=provider_preference,
        )

        return CodeExecutionResult(
            status=result.status.name.lower(),
            stdout=result.stdout,
            stderr=result.stderr,
            exit_code=result.exit_code,
            execution_time_ms=result.execution_time_ms,
            provider=result.provider,
            artifacts=result.artifacts or {},
        )
    except Exception as e:
        return CodeExecutionResult(
            status="error",
            stdout="",
            stderr=str(e),
            exit_code=-1,
            execution_time_ms=0.0,
            provider="none",
        )


@mcp.tool()
async def browse_web(
    url: str,
    actions: list[dict[str, Any]] = None,
    capture_screenshot: bool = False,
    wait_for_selector: str = None,
) -> WebBrowseResult:
    """Browse a web page and perform automated actions.

    Uses Playwright for browser automation. Can navigate, click, type,
    scroll, and capture screenshots.

    Args:
        url: The URL to browse
        actions: List of actions to perform (click, type, scroll, wait)
        capture_screenshot: Whether to capture a screenshot
        wait_for_selector: CSS selector to wait for before completing

    Returns:
        WebBrowseResult with page content, title, and screenshot info
    """
    if not PLATFORM_AVAILABLE:
        return WebBrowseResult(
            status="error",
            url=url,
            title="",
            content_preview="Execution platform not available",
            actions_performed=0,
            provider="none",
        )

    platform = get_platform()

    try:
        # Convert actions to BrowserAction objects
        browser_actions = []
        if actions:
            for action in actions:
                browser_actions.append(
                    BrowserAction(
                        action=action.get("action", "navigate"),
                        selector=action.get("selector"),
                        text=action.get("text"),
                        url=action.get("url"),
                        timeout_ms=action.get("timeout_ms", 5000),
                    )
                )

        result = await platform.browse_web(
            url=url,
            actions=browser_actions if browser_actions else None,
            capture_screenshot=capture_screenshot,
        )

        if result.get("status") == "error":
            return WebBrowseResult(
                status="error",
                url=url,
                title="",
                content_preview=result.get("error", "Unknown error"),
                actions_performed=0,
                provider=result.get("provider", "unknown"),
            )

        # Extract title from content (simplified)
        content = result.get("content", "")
        title = ""
        if "<title>" in content:
            title = content.split("<title>")[1].split("</title>")[0]

        return WebBrowseResult(
            status="success",
            url=result.get("url", url),
            title=title,
            content_preview=content[:1000] if content else "",
            screenshot_path=None,  # Would need to save screenshot to disk
            actions_performed=len(browser_actions),
            provider=result.get("provider", "unknown"),
        )
    except Exception as e:
        return WebBrowseResult(
            status="error",
            url=url,
            title="",
            content_preview=str(e),
            actions_performed=0,
            provider="none",
        )


@mcp.tool()
async def research_topic(
    query: str,
    num_results: int = 10,
    include_citations: bool = True,
    provider_preference: str = None,
) -> ResearchResult:
    """Research a topic using web search.

    Uses Tavily or Brave Search for AI-optimized web search.
    Returns structured results with titles, URLs, and content.

    Args:
        query: The search query
        num_results: Number of results to return (default: 10, max: 20)
        include_citations: Whether to include full content for citations
        provider_preference: Preferred provider (tavily, brave) or None for auto

    Returns:
        ResearchResult with search results and metadata
    """
    if not PLATFORM_AVAILABLE:
        return ResearchResult(
            status="error",
            query=query,
            results_count=0,
            results=[],
            provider="none",
        )

    platform = get_platform()

    try:
        result = await platform.research_topic(
            query=query,
            num_results=num_results,
            include_citations=include_citations,
            preferred_provider=provider_preference,
        )

        if result.get("status") == "error":
            return ResearchResult(
                status="error",
                query=query,
                results_count=0,
                results=[],
                provider=result.get("provider", "unknown"),
            )

        return ResearchResult(
            status="success",
            query=result.get("query", query),
            results_count=result.get("count", 0),
            results=result.get("results", []),
            provider=result.get("provider", "unknown"),
        )
    except Exception:
        return ResearchResult(
            status="error",
            query=query,
            results_count=0,
            results=[],
            provider="none",
        )


@mcp.tool()
def get_execution_status() -> ExecutionStatusResult:
    """Get the status of the execution platform.

    Returns information about available providers, health status,
    and usage metrics.

    Returns:
        ExecutionStatusResult with platform status and metrics
    """
    if not PLATFORM_AVAILABLE:
        return ExecutionStatusResult(
            healthy=False,
            sandbox_providers=[],
            browser_providers=[],
            research_providers=[],
            metrics={},
        )

    platform = get_platform()
    status = platform.get_status()

    return ExecutionStatusResult(
        healthy=status.get("healthy", False),
        sandbox_providers=status.get("sandbox_providers", []),
        browser_providers=status.get("browser_providers", []),
        research_providers=status.get("research_providers", []),
        metrics=status.get("metrics", {}),
    )


# ============================================================================
# MCP Resources
# ============================================================================


@mcp.resource("execution://providers")
def get_providers_info() -> str:
    """Get information about available execution providers."""
    if not PLATFORM_AVAILABLE:
        return "Execution platform not available"

    platform = get_platform()
    status = platform.get_status()

    info = [
        "# AMOS Execution Platform Providers",
        "",
        "## Sandbox Providers",
    ]

    for provider in status.get("sandbox_providers", []):
        info.append(f"- {provider}")

    info.extend(["", "## Browser Providers"])
    for provider in status.get("browser_providers", []):
        info.append(f"- {provider}")

    info.extend(["", "## Research Providers"])
    for provider in status.get("research_providers", []):
        info.append(f"- {provider}")

    info.extend(
        [
            "",
            "## Setup Instructions",
            "",
            "### E2B (Cloud Sandbox)",
            "1. Get API key: https://e2b.dev",
            "2. Set environment: export E2B_API_KEY=...",
            "",
            "### Daytona (Fast Sandbox + Computer Use)",
            "1. Get API key: https://daytona.io",
            "2. Set environment: export DAYTONA_API_KEY=...",
            "",
            "### Playwright (Browser Automation)",
            "1. Install: pip install playwright",
            "2. Install browsers: playwright install chromium",
            "",
            "### Tavily (Web Search)",
            "1. Get API key: https://tavily.com",
            "2. Set environment: export TAVILY_API_KEY=...",
            "",
            "### Brave Search (Web Search)",
            "1. Get API key: https://brave.com/search/api",
            "2. Set environment: export BRAVE_API_KEY=...",
        ]
    )

    return "\n".join(info)


@mcp.resource("execution://examples")
def get_usage_examples() -> str:
    """Get usage examples for execution tools."""
    return """# AMOS Execution Platform Examples

## Execute Python Code
```json
{
  "code": "import math\\nprint(f'Pi = {math.pi}')\\nprint(f'Sum 1-100 = {sum(range(101))}')",
  "language": "python",
  "timeout_seconds": 30
}
```

## Browse Web Page
```json
{
  "url": "https://example.com",
  "capture_screenshot": true,
  "actions": [
    {"action": "click", "selector": "button#submit"},
    {"action": "wait", "timeout_ms": 2000}
  ]
}
```

## Research Topic
```json
{
  "query": "Python async best practices 2025",
  "num_results": 5,
  "include_citations": true
}
```

## Available Actions for Web Browse
- `navigate`: Go to URL
- `click`: Click element by CSS selector
- `type`: Type text into input field
- `scroll`: Scroll down page
- `wait`: Wait for milliseconds or selector
- `screenshot`: Capture screenshot
- `extract`: Extract page content
"""


# ============================================================================
# Main Entry Point
# ============================================================================


def main():
    """Run the MCP server."""
    import argparse

    parser = argparse.ArgumentParser(description="AMOS Execution MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default="stdio",
        help="Transport protocol (default: stdio)",
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Port for HTTP transport (default: 8000)"
    )
    parser.add_argument(
        "--host", default="127.0.0.1", help="Host for HTTP transport (default: 127.0.0.1)"
    )

    args = parser.parse_args()

    print("🚀 AMOS Execution MCP Server v2.0", file=sys.stderr)
    print(f"   Transport: {args.transport}", file=sys.stderr)

    if not PLATFORM_AVAILABLE:
        print("⚠️  Warning: Execution platform not available", file=sys.stderr)
    else:
        # Initialize platform
        platform = get_platform()
        status = platform.get_status()
        print(f"   Sandbox: {status.get('sandbox_providers', [])}", file=sys.stderr)
        print(f"   Browser: {status.get('browser_providers', [])}", file=sys.stderr)
        print(f"   Research: {status.get('research_providers', [])}", file=sys.stderr)

    print("\n📡 Server ready", file=sys.stderr)

    if args.transport == "http":
        mcp.run(transport="streamable-http", host=args.host, port=args.port)
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
