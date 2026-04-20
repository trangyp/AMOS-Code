"""Extended tools for AMOS SuperBrain - Additional specialized capabilities.

This module provides 5 additional tools following MCP protocol standards:
1. web_search - Internet research capability
2. database_query - SQL/NoSQL data access
3. file_read_write - File I/O operations
4. calculate - Mathematical computations
5. git_operations - Version control operations

Reference: https://modelcontextprotocol.io/docs/learn/architecture
"""

from __future__ import annotations

import re
import subprocess
from datetime import UTC, datetime, timezone

UTC = UTC

UTC = timezone.utc
from pathlib import Path
from typing import Any

import requests


def web_search(query: str, max_results: int = 5) -> dict[str, Any]:
    """Search the web for information.

    Args:
        query: Search query string
        max_results: Maximum number of results (default: 5)

    Returns:
        Dictionary with search results
    """
    try:
        # Use DuckDuckGo HTML scraping (no API key required)
        url = "https://html.duckduckgo.com/html/"
        params = {"q": query}

        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()

        # Parse results (basic extraction)
        results = []
        if response.status_code == 200:
            # Extract titles and snippets
            titles = re.findall(r'<a[^>]*class="result__a"[^>]*>(.*?)</a>', response.text)
            snippets = re.findall(r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>', response.text)

            for i in range(min(len(titles), len(snippets), max_results)):
                results.append(
                    {
                        "title": re.sub(r"<[^>]+>", "", titles[i]),
                        "snippet": re.sub(r"<[^>]+>", "", snippets[i]),
                    }
                )

        return {
            "query": query,
            "results_count": len(results),
            "results": results,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "query": query,
            "error": str(e),
            "results": [],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


def database_query(
    query: str, db_type: str = "sqlite", connection_string: str = None
) -> dict[str, Any]:
    """Execute a database query.

    Args:
        query: SQL or NoSQL query string
        db_type: Database type (sqlite, postgres, mysql)
        connection_string: Database connection string (optional)

    Returns:
        Dictionary with query results
    """
    try:
        if db_type == "sqlite":
            import sqlite3

            # Use default connection if none provided
            if not connection_string:
                connection_string = ":memory:"

            conn = sqlite3.connect(connection_string)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(query)

            # Check if query returns data
            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                results = [dict(zip(columns, row)) for row in rows]
            else:
                results = []
                conn.commit()

            conn.close()

            return {
                "query": query,
                "db_type": db_type,
                "results": results,
                "row_count": len(results),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        else:
            return {
                "query": query,
                "db_type": db_type,
                "error": f"Database type '{db_type}' not yet supported",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
    except Exception as e:
        return {
            "query": query,
            "db_type": db_type,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


def file_read_write(
    operation: str, file_path: str, content: str = None, encoding: str = "utf-8"
) -> dict[str, Any]:
    """Read from or write to a file.

    Args:
        operation: Either "read" or "write"
        file_path: Path to the file
        content: Content to write (required for write operation)
        encoding: File encoding (default: utf-8)

    Returns:
        Dictionary with operation results
    """
    try:
        path = Path(file_path)

        if operation == "read":
            if not path.exists():
                return {
                    "operation": operation,
                    "file_path": str(path),
                    "error": "File not found",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

            content_read = path.read_text(encoding=encoding)
            return {
                "operation": operation,
                "file_path": str(path),
                "content": content_read,
                "size_bytes": len(content_read.encode(encoding)),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        elif operation == "write":
            if content is None:
                return {
                    "operation": operation,
                    "file_path": str(path),
                    "error": "Content required for write operation",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

            # Create parent directories if needed
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding=encoding)

            return {
                "operation": operation,
                "file_path": str(path),
                "bytes_written": len(content.encode(encoding)),
                "success": True,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        else:
            return {
                "operation": operation,
                "file_path": str(path),
                "error": f"Unknown operation: {operation}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    except Exception as e:
        return {
            "operation": operation,
            "file_path": file_path,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


def calculate(expression: str, variables: dict[str, float] = None) -> dict[str, Any]:
    """Evaluate a mathematical expression.

    Args:
        expression: Mathematical expression to evaluate
        variables: Optional dictionary of variable values

    Returns:
        Dictionary with calculation results
    """
    try:
        # Safe evaluation with limited operations
        allowed_names = {
            "abs": abs,
            "max": max,
            "min": min,
            "pow": pow,
            "round": round,
            "sum": sum,
            "len": len,
        }

        # Add math functions
        import math

        allowed_names.update(
            {
                "sin": math.sin,
                "cos": math.cos,
                "tan": math.tan,
                "sqrt": math.sqrt,
                "log": math.log,
                "log10": math.log10,
                "exp": math.exp,
                "pi": math.pi,
                "e": math.e,
            }
        )

        # Add variables if provided
        if variables:
            allowed_names.update(variables)

        # Compile and evaluate
        code = compile(expression, "<string>", "eval")

        # Check for unsafe operations
        for name in code.co_names:
            if name not in allowed_names and not name.startswith("__"):
                return {
                    "expression": expression,
                    "error": f"Unsafe operation: {name}",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

        result = eval(code, {"__builtins__": {}}, allowed_names)

        return {
            "expression": expression,
            "result": result,
            "variables_used": variables or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        return {
            "expression": expression,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


def git_operations(operation: str, repo_path: str = ".", args: list[str] = None) -> dict[str, Any]:
    """Execute git operations.

    Args:
        operation: Git command (status, log, diff, branch, etc.)
        repo_path: Path to the git repository
        args: Additional arguments for the git command

    Returns:
        Dictionary with git operation results
    """
    try:
        if args is None:
            args = []

        # Build git command
        cmd = ["git", "-C", repo_path, operation] + args

        # Execute git command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
        )

        return {
            "operation": operation,
            "repo_path": repo_path,
            "args": args,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode,
            "success": result.returncode == 0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except subprocess.TimeoutExpired:
        return {
            "operation": operation,
            "repo_path": repo_path,
            "error": "Git operation timed out",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except FileNotFoundError:
        return {
            "operation": operation,
            "repo_path": repo_path,
            "error": "Git not found. Is it installed?",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "operation": operation,
            "repo_path": repo_path,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# MCP-compliant tool schemas
TOOL_SCHEMAS = {
    "web_search": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query"},
            "max_results": {
                "type": "integer",
                "description": "Max results to return",
                "default": 5,
            },
        },
        "required": ["query"],
    },
    "database_query": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "SQL query"},
            "db_type": {
                "type": "string",
                "enum": ["sqlite", "postgres", "mysql"],
                "default": "sqlite",
            },
            "connection_string": {"type": "string", "description": "Connection string"},
        },
        "required": ["query"],
    },
    "file_read_write": {
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "enum": ["read", "write"],
                "description": "Operation type",
            },
            "file_path": {"type": "string", "description": "File path"},
            "content": {"type": "string", "description": "Content to write"},
            "encoding": {"type": "string", "default": "utf-8"},
        },
        "required": ["operation", "file_path"],
    },
    "calculate": {
        "type": "object",
        "properties": {
            "expression": {"type": "string", "description": "Math expression"},
            "variables": {"type": "object", "description": "Variable values"},
        },
        "required": ["expression"],
    },
    "git_operations": {
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "enum": ["status", "log", "diff", "branch", "show"],
                "description": "Git command",
            },
            "repo_path": {"type": "string", "description": "Repository path", "default": "."},
            "args": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Additional arguments",
            },
        },
        "required": ["operation"],
    },
}

TOOL_DESCRIPTIONS = {
    "web_search": "Search the web for information using DuckDuckGo",
    "database_query": "Execute SQL queries on SQLite/PostgreSQL/MySQL databases",
    "file_read_write": "Read from or write to files on the filesystem",
    "calculate": "Evaluate mathematical expressions with variables",
    "git_operations": "Execute git commands in a repository",
}
