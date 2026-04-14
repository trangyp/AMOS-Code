"""
Repo Doctor Ingest Layer

Multi-language parsing and semantic extraction using:
- Tree-sitter: Incremental syntax trees
- CodeQL: Semantic databases with AST/CFG/data-flow
- Joern: Cross-language code property graphs
"""

from .codeql_bridge import CodeQLBridge
from .joern_bridge import JoernBridge
from .treesitter_ingest import TreeSitterIngest

__all__ = ["TreeSitterIngest", "CodeQLBridge", "JoernBridge"]
