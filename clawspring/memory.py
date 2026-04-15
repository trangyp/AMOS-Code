"""Backward-compatibility shim — real implementation is in memory/ package."""

from memory.context import get_memory_context  # noqa: F401
from memory.store import (  # noqa: F401
    MemoryEntry,
    delete_memory,
    get_index_content,
    load_index,
    parse_frontmatter,
    save_memory,
    search_memory,
)
