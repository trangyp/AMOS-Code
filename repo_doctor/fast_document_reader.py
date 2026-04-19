"""
Fast Document Reader Runtime.
==============================

Implements the two-path architecture:
- Fast path: Open → QuickIndex → RetrieveTopK → Answer
- Deep path: Open → QuickIndex → RetrieveTopK → LocalParse → Verify → Answer

Never: Open → ParseEverything → UnderstandEverything → Answer

Performance targets:
- open_and_index_once_ms: 200
- simple_lookup_ms: 50
- section_summary_ms: 150
- table_lookup_ms: 250
- full_document_deep_parse: background_only
"""

import contextlib
import hashlib
import os
import pickle
import re
import threading
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ============================================================================
# Stage 1: Format Detection
# ============================================================================


class DocumentFormat(Enum):
    PLAIN_TEXT = auto()
    MARKDOWN = auto()
    PYTHON = auto()
    JSON = auto()
    YAML = auto()
    PDF = auto()  # Placeholder - would need PyPDF2/pdfplumber
    UNKNOWN = auto()


@dataclass(frozen=True)
class FormatSignature:
    """Immutable signature for format detection."""

    extension: str
    mime_hint: Optional[str] = None
    header_bytes: Optional[bytes] = None


def detect_format(file_path: Path, header_bytes: Optional[bytes] = None) -> DocumentFormat:
    """Fast format detection based on extension and optional header bytes."""
    ext = file_path.suffix.lower()

    format_map: Dict[str, DocumentFormat] = {
        ".txt": DocumentFormat.PLAIN_TEXT,
        ".md": DocumentFormat.MARKDOWN,
        ".py": DocumentFormat.PYTHON,
        ".json": DocumentFormat.JSON,
        ".yaml": DocumentFormat.YAML,
        ".yml": DocumentFormat.YAML,
        ".pdf": DocumentFormat.PDF,
    }

    # Extension-based detection (fastest)
    if ext in format_map:
        return format_map[ext]

    # Content-based detection (fallback)
    if header_bytes:
        if header_bytes.startswith(b"%PDF"):
            return DocumentFormat.PDF
        try:
            header = header_bytes[:1024].decode("utf-8", errors="ignore").strip()
            if header.startswith("{") or header.startswith("["):
                return DocumentFormat.JSON
            if header.startswith("---") or "yaml" in header.lower():
                return DocumentFormat.YAML
        except Exception:
            pass

    return DocumentFormat.UNKNOWN


# ============================================================================
# Stage 2: Quick Index Building
# ============================================================================


@dataclass
class DocumentIndex:
    """Lightweight index for fast retrieval without full parsing."""

    file_path: Path
    file_hash: str
    file_size: int
    format: DocumentFormat
    mtime: float

    # Structural index (built in ~200ms)
    line_offsets: List[int] = field(default_factory=list)
    headings: list[tuple[int, str, int]] = field(default_factory=list)  # (level, text, offset)
    code_blocks: list[tuple[int, int, str]] = field(default_factory=list)  # (start, end, lang)
    table_locations: list[tuple[int, int]] = field(default_factory=list)  # (start, end)
    section_boundaries: list[tuple[str, int, int]] = field(
        default_factory=list
    )  # (name, start, end)

    # Metadata
    total_lines: int = 0
    has_frontmatter: bool = False
    encoding: str = "utf-8"

    def get_line_range(self, start_line: int, end_line: int) -> Tuple[int, int]:
        """Get byte offsets for a line range."""
        if not self.line_offsets:
            return (0, 0)
        start = self.line_offsets[max(0, start_line - 1)]
        end = (
            self.line_offsets[min(end_line, len(self.line_offsets) - 1)]
            if end_line < len(self.line_offsets)
            else self.line_offsets[-1]
        )
        return (start, end)


class QuickIndexer:
    """Builds structural index without deep parsing."""

    # Patterns for fast structural detection
    HEADING_PATTERNS: dict[DocumentFormat, list[re.Pattern]] = {
        DocumentFormat.MARKDOWN: [
            re.compile(r"^(#{1,6})\s+(.+)$"),  # ATX headings
            re.compile(r"^(.+)\n[=\-]+$"),  # Setext headings
        ],
        DocumentFormat.PYTHON: [
            re.compile(r"^\s*(class|def)\s+(\w+)"),  # Class/def definitions
            re.compile(r"^\s*#\s*(.+)$"),  # Comments as pseudo-headings
        ],
    }

    CODE_BLOCK_PATTERNS: dict[DocumentFormat, re.Pattern] = {
        DocumentFormat.MARKDOWN: re.compile(r"^```(\w*)"),
        DocumentFormat.PYTHON: re.compile(r"^\s*def\s+|^\s*class\s+"),
    }

    TABLE_PATTERNS: dict[DocumentFormat, re.Pattern] = {
        DocumentFormat.MARKDOWN: re.compile(r"^\|[-:]+\|"),  # Markdown table separator
    }

    @classmethod
    def build_index(cls, file_path: Path, content: Optional[str] = None) -> DocumentIndex:
        """Build quick index in <200ms target."""
        start_time = time.perf_counter()

        stat = file_path.stat()
        file_hash = cls._compute_hash(file_path)
        doc_format = detect_format(file_path)

        # Read content if not provided
        if content is None:
            try:
                with open(file_path, encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except Exception:
                content = ""

        index = DocumentIndex(
            file_path=file_path,
            file_hash=file_hash,
            file_size=stat.st_size,
            format=doc_format,
            mtime=stat.st_mtime,
            total_lines=len(content.split("\n")),
        )

        # Build line offset table
        index.line_offsets = cls._build_line_offsets(content)

        # Detect structure based on format
        if doc_format in cls.HEADING_PATTERNS:
            index.headings = cls._extract_headings(content, doc_format, index.line_offsets)

        if doc_format in cls.CODE_BLOCK_PATTERNS:
            index.code_blocks = cls._extract_code_blocks(content, doc_format, index.line_offsets)

        if doc_format in cls.TABLE_PATTERNS:
            index.table_locations = cls._extract_tables(content, doc_format, index.line_offsets)

        # Build section boundaries from headings
        index.section_boundaries = cls._build_section_boundaries(index.headings, len(content))

        elapsed_ms = (time.perf_counter() - start_time) * 1000
        # Performance logging for slow indexes
        if elapsed_ms > 200:  # noqa: PLR2004
            print(f"[index-slow] {file_path.name}: {elapsed_ms:.1f}ms")

        return index

    @staticmethod
    def _compute_hash(file_path: Path) -> str:
        """Compute quick hash for cache validation."""
        h = hashlib.blake2b(digest_size=16)
        stat = file_path.stat()
        h.update(f"{stat.st_size}:{stat.st_mtime}".encode())
        return h.hexdigest()[:16]

    @staticmethod
    def _build_line_offsets(content: str) -> List[int]:
        """Build table of line start offsets."""
        offsets = [0]
        for i, char in enumerate(content):
            if char == "\n":
                offsets.append(i + 1)
        return offsets

    @classmethod
    def _extract_headings(
        cls, content: str, doc_format: DocumentFormat, line_offsets: List[int]
    ) -> list[tuple[int, str, int]]:
        """Extract heading locations without full parsing."""
        headings = []
        patterns = cls.HEADING_PATTERNS.get(doc_format, [])

        for i, line in enumerate(content.split("\n")):
            for pattern in patterns:
                match = pattern.match(line)
                if match:
                    if doc_format == DocumentFormat.MARKDOWN:
                        level = len(match.group(1))
                        text = match.group(2).strip()
                    elif doc_format == DocumentFormat.PYTHON:
                        if "class" in line or "def" in line:
                            level = 1 if "class" in line else 2
                            text = line.strip()
                        else:
                            level = 3
                            text = match.group(1)
                    else:
                        level = 1
                        text = line.strip()

                    offset = line_offsets[i] if i < len(line_offsets) else 0
                    headings.append((level, text, offset))
                    break

        return headings

    @classmethod
    def _extract_code_blocks(
        cls, content: str, doc_format: DocumentFormat, line_offsets: List[int]
    ) -> list[tuple[int, int, str]]:
        """Extract code block boundaries."""
        blocks = []
        pattern = cls.CODE_BLOCK_PATTERNS.get(doc_format)
        if not pattern:
            return blocks

        in_block = False
        block_start = 0
        block_lang = ""

        lines = content.split("\n")
        for i, line in enumerate(lines):
            match = pattern.match(line)
            if match:
                if doc_format == DocumentFormat.MARKDOWN:
                    if not in_block and line.startswith("```"):
                        in_block = True
                        block_start = line_offsets[i]
                        block_lang = match.group(1) or "text"
                    elif in_block and line.startswith("```"):
                        block_end = line_offsets[i]
                        blocks.append((block_start, block_end, block_lang))
                        in_block = False
                elif doc_format == DocumentFormat.PYTHON:
                    # Python functions/classes as pseudo-blocks
                    if match:
                        start = line_offsets[i]
                        # Find end by indentation (simplified)
                        indent = len(line) - len(line.lstrip())
                        end = start + len(line)
                        for j in range(i + 1, len(lines)):
                            if lines[j].strip() and not lines[j].startswith(" " * (indent + 1)):
                                break
                            end = line_offsets[j] + len(lines[j])
                        blocks.append((start, end, "python"))

        return blocks

    @classmethod
    def _extract_tables(
        cls, content: str, doc_format: DocumentFormat, line_offsets: List[int]
    ) -> list[tuple[int, int]]:
        """Extract table locations."""
        tables = []
        pattern = cls.TABLE_PATTERNS.get(doc_format)
        if not pattern:
            return tables

        lines = content.split("\n")
        in_table = False
        table_start = 0

        for i, line in enumerate(lines):
            if pattern.match(line):
                if not in_table:
                    in_table = True
                    table_start = line_offsets[max(0, i - 1)]  # Include header row
            elif in_table and not line.strip().startswith("|"):
                table_end = line_offsets[i]
                tables.append((table_start, table_end))
                in_table = False

        if in_table:
            tables.append((table_start, len(content)))

        return tables

    @staticmethod
    def _build_section_boundaries(
        headings: list[tuple[int, str, int]], total_len: int
    ) -> list[tuple[str, int, int]]:
        """Build section boundaries from heading hierarchy."""
        if not headings:
            return []

        boundaries = []
        for i, (_level, text, start) in enumerate(headings):
            end = headings[i + 1][2] if i + 1 < len(headings) else total_len
            boundaries.append((text, start, end))

        return boundaries


# ============================================================================
# Stage 3: Document Cache
# ============================================================================


@dataclass
class DocumentCacheEntry:
    """Cached document state with structural and semantic data."""

    index: DocumentIndex
    text: str  # Full text (for small files) or None (for large files)

    # Two-level chunking
    coarse_chunks: list[tuple[int, int, str]] = field(default_factory=list)  # (start, end, summary)
    fine_chunks: dict[int, list[tuple[int, int, str]]] = field(
        default_factory=dict
    )  # coarse_idx -> fine_chunks

    # Semantic data (lazily computed)
    embeddings: dict[int, list[float]] = None
    entities: list[tuple[str, str, int]] = None  # (type, text, offset)

    # Metadata
    created_at: float = field(default_factory=time.time)
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)

    # State flags
    has_deep_parse: bool = False


class DocumentCache:
    """Persistent document cache with LRU eviction."""

    def __init__(self, cache_dir: Optional[Path] = None, max_entries: int = 100):
        self.cache_dir = cache_dir or Path.home() / ".cache" / "fast_document_reader"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_entries = max_entries

        self._memory_cache: Dict[str, DocumentCacheEntry] = {}
        self._lock = threading.RLock()
        self._access_order: List[str] = []  # LRU tracking

    def get(self, file_path: Path) -> Optional[DocumentCacheEntry]:
        """Get cached entry if valid."""
        cache_key = self._get_cache_key(file_path)

        with self._lock:
            # Check memory cache first
            if cache_key in self._memory_cache:
                entry = self._memory_cache[cache_key]
                if self._is_valid(entry, file_path):
                    entry.access_count += 1
                    entry.last_accessed = time.time()
                    self._update_lru(cache_key)
                    return entry
                else:
                    del self._memory_cache[cache_key]

            # Check disk cache
            disk_entry = self._load_from_disk(cache_key)
            if disk_entry and self._is_valid(disk_entry, file_path):
                self._memory_cache[cache_key] = disk_entry
                self._update_lru(cache_key)
                return disk_entry

            return None

    def put(self, file_path: Path, entry: DocumentCacheEntry) -> None:
        """Store entry in cache."""
        cache_key = self._get_cache_key(file_path)

        with self._lock:
            # Evict if necessary
            while len(self._memory_cache) >= self.max_entries:
                self._evict_lru()

            self._memory_cache[cache_key] = entry
            self._update_lru(cache_key)

            # Async disk write (non-blocking)
            threading.Thread(
                target=self._save_to_disk, args=(cache_key, entry), daemon=True
            ).start()

    def invalidate(self, file_path: Path) -> None:
        """Invalidate cache entry for file."""
        cache_key = self._get_cache_key(file_path)

        with self._lock:
            if cache_key in self._memory_cache:
                del self._memory_cache[cache_key]
            if cache_key in self._access_order:
                self._access_order.remove(cache_key)

        # Remove from disk
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        with contextlib.suppress(FileNotFoundError):
            cache_file.unlink()

    def _get_cache_key(self, file_path: Path) -> str:
        """Generate cache key from file path."""
        return hashlib.blake2b(str(file_path).encode(), digest_size=16).hexdigest()

    def _is_valid(self, entry: DocumentCacheEntry, file_path: Path) -> bool:
        """Check if cached entry is still valid."""
        try:
            stat = file_path.stat()
            current_hash = f"{stat.st_size}:{stat.st_mtime}"
            return entry.index.file_hash.startswith(current_hash.split(":")[0][:8])
        except OSError:
            return False

    def _update_lru(self, cache_key: str) -> None:
        """Update LRU order."""
        if cache_key in self._access_order:
            self._access_order.remove(cache_key)
        self._access_order.append(cache_key)

    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if self._access_order:
            oldest = self._access_order.pop(0)
            if oldest in self._memory_cache:
                del self._memory_cache[oldest]

    def _save_to_disk(self, cache_key: str, entry: DocumentCacheEntry) -> None:
        """Save entry to disk cache."""
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        try:
            with open(cache_file, "wb") as f:
                pickle.dump(entry, f, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception as e:
            print(f"[cache] Failed to save {cache_key}: {e}")

    def _load_from_disk(self, cache_key: str) -> Optional[DocumentCacheEntry]:
        """Load entry from disk cache."""
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        try:
            with open(cache_file, "rb") as f:
                return pickle.load(f)
        except (OSError, pickle.PickleError):
            return None


# ============================================================================
# Stage 4: Query Routing
# ============================================================================


class QueryClass(Enum):
    """Query classification for routing."""

    SIMPLE_LOOKUP = auto()  # "what is the title", "find line 42"
    SECTION_FIND = auto()  # "find section X", "show me the API reference"
    CODE_FIND = auto()  # "find the function foo", "show class Bar"
    TABLE_LOOKUP = auto()  # "find the table about X"
    SEMANTIC_SEARCH = auto()  # "what does this say about Y?"
    FULL_ANALYSIS = auto()  # "summarize this document", "extract all entities"


@dataclass
class QueryPlan:
    """Execution plan for a query."""

    query_class: QueryClass
    needs_deep_parse: bool
    target_sections: Optional[list[int] ] = None  # Section indices to read
    target_lines: Tuple[int, int] = None  # Line range to read
    use_semantic: bool = False
    verify_result: bool = False

    # Performance budget
    max_parse_depth: str = "shallow"  # "none", "shallow", "section", "full"


class QueryRouter:
    """Routes queries to appropriate execution path."""

    # Simple lookup patterns (cheap path)
    SIMPLE_PATTERNS = [
        (
            re.compile(r"^(what is|what\'s)\s+the\s+(title|filename|path)", re.I),
            QueryClass.SIMPLE_LOOKUP,
        ),
        (re.compile(r"^(find|show|go to|line)\s+(\d+)", re.I), QueryClass.SIMPLE_LOOKUP),
        (re.compile(r"^where is", re.I), QueryClass.SIMPLE_LOOKUP),
    ]

    # Section patterns
    SECTION_PATTERNS = [
        (
            re.compile(r"(section|heading|chapter|part)\s+(\w+|[\d\.]+)", re.I),
            QueryClass.SECTION_FIND,
        ),
        (
            re.compile(r"(show|find)\s+(the\s+)?(section|heading)\s+about", re.I),
            QueryClass.SECTION_FIND,
        ),
    ]

    # Code patterns
    CODE_PATTERNS = [
        (re.compile(r"(function|def|class|method)\s+(\w+)", re.I), QueryClass.CODE_FIND),
        (
            re.compile(r"(find|show)\s+(the\s+)?(function|class|def)\s+(\w+)", re.I),
            QueryClass.CODE_FIND,
        ),
    ]

    # Table patterns
    TABLE_PATTERNS = [
        (re.compile(r"(table|figure|chart)\s+(\d+|[\w\s]+)", re.I), QueryClass.TABLE_LOOKUP),
        (re.compile(r"find\s+(the\s+)?table\s+(about|for|with)", re.I), QueryClass.TABLE_LOOKUP),
    ]

    # Full analysis patterns (deep path)
    DEEP_PATTERNS = [
        (re.compile(r"(summarize|summary|overview|tl;dr)", re.I), QueryClass.FULL_ANALYSIS),
        (re.compile(r"(extract|extract all|list all|find all)", re.I), QueryClass.FULL_ANALYSIS),
        (re.compile(r"(analyze|comprehensive|deep|full)", re.I), QueryClass.FULL_ANALYSIS),
    ]

    @classmethod
    def classify(cls, query: str) -> QueryClass:
        """Classify query type for routing."""
        for pattern, qclass in cls.SIMPLE_PATTERNS:
            if pattern.search(query):
                return qclass

        for pattern, qclass in cls.CODE_PATTERNS:
            if pattern.search(query):
                return qclass

        for pattern, qclass in cls.SECTION_PATTERNS:
            if pattern.search(query):
                return qclass

        for pattern, qclass in cls.TABLE_PATTERNS:
            if pattern.search(query):
                return qclass

        for pattern, qclass in cls.DEEP_PATTERNS:
            if pattern.search(query):
                return qclass

        # Default to semantic search
        return QueryClass.SEMANTIC_SEARCH

    @classmethod
    def plan(cls, query: str, index: DocumentIndex) -> QueryPlan:
        """Create execution plan for query."""
        qclass = cls.classify(query)

        # Route to appropriate plan
        if qclass == QueryClass.SIMPLE_LOOKUP:
            return cls._plan_simple_lookup(query, index)
        elif qclass == QueryClass.SECTION_FIND:
            return cls._plan_section_find(query, index)
        elif qclass == QueryClass.CODE_FIND:
            return cls._plan_code_find(query, index)
        elif qclass == QueryClass.TABLE_LOOKUP:
            return cls._plan_table_lookup(query, index)
        elif qclass == QueryClass.SEMANTIC_SEARCH:
            return cls._plan_semantic_search(query, index)
        else:
            return cls._plan_full_analysis(query, index)

    @classmethod
    def _plan_simple_lookup(cls, query: str, index: DocumentIndex) -> QueryPlan:
        """Plan for simple lookups - fastest path."""
        # Extract line number if present
        line_match = re.search(r"line\s+(\d+)", query, re.I)
        if line_match:
            line_num = int(line_match.group(1))
            return QueryPlan(
                query_class=QueryClass.SIMPLE_LOOKUP,
                needs_deep_parse=False,
                target_lines=(max(1, line_num - 2), line_num + 2),
                max_parse_depth="none",
            )

        # Title lookup - no parsing needed
        if "title" in query.lower() and index.headings:
            return QueryPlan(
                query_class=QueryClass.SIMPLE_LOOKUP,
                needs_deep_parse=False,
                target_sections=[0],
                max_parse_depth="none",
            )

        return QueryPlan(
            query_class=QueryClass.SIMPLE_LOOKUP, needs_deep_parse=False, max_parse_depth="shallow"
        )

    @classmethod
    def _plan_section_find(cls, query: str, index: DocumentIndex) -> QueryPlan:
        """Plan for section finding."""
        # Find matching sections from index
        matching_sections = []
        for i, (name, _start, _end) in enumerate(index.section_boundaries):
            if any(term in name.lower() for term in query.lower().split()):
                matching_sections.append(i)

        return QueryPlan(
            query_class=QueryClass.SECTION_FIND,
            needs_deep_parse=False,
            target_sections=matching_sections[:3] if matching_sections else None,
            max_parse_depth="section",
        )

    @classmethod
    def _plan_code_find(cls, query: str, index: DocumentIndex) -> QueryPlan:
        """Plan for code finding."""
        # Extract function/class name
        name_match = re.search(r"(function|def|class|method)\s+(\w+)", query, re.I)
        if name_match:
            target_name = name_match.group(2)
            # Find in code blocks from index
            for _i, (start, end, lang) in enumerate(index.code_blocks):
                if target_name in lang:  # lang field contains signature for Python
                    return QueryPlan(
                        query_class=QueryClass.CODE_FIND,
                        needs_deep_parse=False,
                        target_lines=(
                            index.line_offsets.index(start) + 1
                            if start in index.line_offsets
                            else 1,
                            index.line_offsets.index(end) + 1
                            if end in index.line_offsets
                            else index.total_lines,
                        ),
                        max_parse_depth="section",
                    )

        return QueryPlan(
            query_class=QueryClass.CODE_FIND, needs_deep_parse=False, max_parse_depth="section"
        )

    @classmethod
    def _plan_table_lookup(cls, query: str, index: DocumentIndex) -> QueryPlan:
        """Plan for table lookup."""
        return QueryPlan(
            query_class=QueryClass.TABLE_LOOKUP,
            needs_deep_parse=False,  # Table extraction done at index time
            max_parse_depth="shallow",
        )

    @classmethod
    def _plan_semantic_search(cls, query: str, index: DocumentIndex) -> QueryPlan:
        """Plan for semantic search - may need embeddings."""
        return QueryPlan(
            query_class=QueryClass.SEMANTIC_SEARCH,
            needs_deep_parse=False,
            use_semantic=True,
            max_parse_depth="section",
        )

    @classmethod
    def _plan_full_analysis(cls, query: str, index: DocumentIndex) -> QueryPlan:
        """Plan for full analysis - deep path only."""
        return QueryPlan(
            query_class=QueryClass.FULL_ANALYSIS,
            needs_deep_parse=True,
            use_semantic=True,
            verify_result=True,
            max_parse_depth="full",
        )


# ============================================================================
# Stage 5: Targeted Retrieval
# ============================================================================


class DocumentRetriever:
    """Retrieves content spans based on query plan."""

    def __init__(self, index: DocumentIndex, content: str):
        self.index = index
        self.content = content

    def retrieve(self, plan: QueryPlan) -> list[tuple[str, int, int]]:
        """Retrieve relevant spans based on plan."""
        spans = []

        if plan.target_lines:
            # Specific line range
            start_line, end_line = plan.target_lines
            text = self._get_lines(start_line, end_line)
            byte_start = (
                self.index.line_offsets[start_line - 1]
                if start_line <= len(self.index.line_offsets)
                else 0
            )
            spans.append((text, byte_start, byte_start + len(text)))

        elif plan.target_sections:
            # Specific sections
            for sec_idx in plan.target_sections:
                if sec_idx < len(self.index.section_boundaries):
                    name, start, end = self.index.section_boundaries[sec_idx]
                    text = self.content[start:end]
                    spans.append((text, start, end))

        elif plan.query_class == QueryClass.TABLE_LOOKUP:
            # Return table content
            for start, end in self.index.table_locations:
                text = self.content[start:end]
                spans.append((text, start, end))

        elif plan.query_class == QueryClass.CODE_FIND:
            # Return code blocks
            for start, end, _lang in self.index.code_blocks[:5]:  # Limit to first 5
                text = self.content[start:end]
                spans.append((text, start, end))

        else:
            # Default: return first section or first 2000 chars
            if self.index.section_boundaries:
                name, start, end = self.index.section_boundaries[0]
                spans.append((self.content[start:end], start, end))
            else:
                spans.append((self.content[:2000], 0, 2000))

        return spans

    def _get_lines(self, start: int, end: int) -> str:
        """Get text for line range."""
        lines = self.content.split("\n")
        return "\n".join(lines[start - 1 : end])


# ============================================================================
# Stage 6: Local Semantic Parse
# ============================================================================


class LocalSemanticParser:
    """Parses semantics only on retrieved spans, not full document."""

    def __init__(self):
        self.entity_pattern = re.compile(r"\b([A-Z][a-z]+(?:[A-Z][a-z]+)*)\b")  # CamelCase
        self.key_value_pattern = re.compile(r"^([\w\s]+):\s*(.+)$", re.MULTILINE)

    def parse(self, spans: list[tuple[str, int, int]]) -> Dict[str, Any]:
        """Parse semantics on small spans only."""
        result = {"entities": [], "key_values": [], "sentences": [], "summary": ""}

        all_text = " ".join([span[0] for span in spans])

        # Extract entities
        for match in self.entity_pattern.finditer(all_text):
            result["entities"].append((match.group(1), match.start(), match.end()))

        # Extract key-value pairs
        for match in self.key_value_pattern.finditer(all_text):
            result["key_values"].append((match.group(1).strip(), match.group(2).strip()))

        # Simple sentence split
        result["sentences"] = [s.strip() for s in re.split(r"[.!?]+", all_text) if s.strip()]

        # Generate mini-summary
        if result["sentences"]:
            result["summary"] = result["sentences"][0][:200]

        return result


# ============================================================================
# Stage 7-8: Main Runtime
# ============================================================================


@dataclass
class ReadResult:
    """Result from document read operation."""

    query: str
    query_class: QueryClass
    answer: str
    spans_retrieved: int
    bytes_parsed: int
    time_ms: float
    from_cache: bool
    used_deep_parse: bool


class FastDocumentReader:
    """
    Main entry point for fast document reading.

    Implements the two-path architecture:
    - Fast path: Open → QuickIndex → RetrieveTopK → Answer
    - Deep path: Open → QuickIndex → RetrieveTopK → LocalParse → Verify → Answer

    Never: Open → ParseEverything → UnderstandEverything → Answer
    """

    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache = DocumentCache(cache_dir)
        self.indexer = QuickIndexer()
        self.router = QueryRouter()
        self.parser = LocalSemanticParser()
        self._lock = threading.RLock()

    def read(self, file_path: str | Path, query: str) -> ReadResult:
        """
        Read document with fast path by default.

        Performance targets:
        - simple_lookup_ms: 50
        - section_summary_ms: 150
        - table_lookup_ms: 250
        """
        start_time = time.perf_counter()

        path = Path(file_path)
        if not path.exists():
            return ReadResult(
                query=query,
                query_class=QueryClass.SIMPLE_LOOKUP,
                answer=f"File not found: {path}",
                spans_retrieved=0,
                bytes_parsed=0,
                time_ms=0,
                from_cache=False,
                used_deep_parse=False,
            )

        # Stage 3: Check cache
        cached = self.cache.get(path)
        from_cache = cached is not None

        if cached:
            index = cached.index
            content = cached.text or self._read_content(path)
        else:
            # Stage 2: Build quick index (<200ms target)
            content = self._read_content(path)
            index = self.indexer.build_index(path, content)

            # Cache the result
            entry = DocumentCacheEntry(
                index=index, text=content if len(content) < 1_000_000 else None
            )
            self.cache.put(path, entry)

        # Stage 4: Route query
        plan = self.router.plan(query, index)

        # Stage 5: Retrieve targeted spans
        retriever = DocumentRetriever(index, content)
        spans = retriever.retrieve(plan)

        total_bytes = sum(end - start for _, start, end in spans)

        # Stage 6: Local semantic parse only if needed
        answer = ""
        used_deep_parse = False

        if plan.needs_deep_parse or plan.use_semantic:
            semantics = self.parser.parse(spans)
            answer = self._generate_answer(query, spans, semantics, plan)
            used_deep_parse = True
        else:
            answer = self._generate_simple_answer(query, spans, index)

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        return ReadResult(
            query=query,
            query_class=plan.query_class,
            answer=answer,
            spans_retrieved=len(spans),
            bytes_parsed=total_bytes,
            time_ms=elapsed_ms,
            from_cache=from_cache,
            used_deep_parse=used_deep_parse,
        )

    def read_async(self, file_path: str | Path, query: str) -> ReadResult:
        """Async wrapper for read (can be made truly async later)."""
        return self.read(file_path, query)

    def invalidate(self, file_path: str | Path) -> None:
        """Invalidate cache for file."""
        self.cache.invalidate(Path(file_path))

    def _read_content(self, path: Path) -> str:
        """Read file content efficiently."""
        try:
            with open(path, encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"

    def _generate_simple_answer(
        self, query: str, spans: list[tuple[str, int, int]], index: DocumentIndex
    ) -> str:
        """Generate answer for simple queries (fast path)."""
        q_lower = query.lower()

        # Title query
        if "title" in q_lower and index.headings:
            return f"Title: {index.headings[0][1]}"

        # Line query - return the content
        if spans:
            return spans[0][0]

        # Section list query
        if "section" in q_lower and "list" in q_lower:
            sections = [name for name, _, _ in index.section_boundaries[:10]]
            return "Sections:\n" + "\n".join(f"- {s}" for s in sections)

        # Default: return first span
        return spans[0][0] if spans else "No content found"

    def _generate_answer(
        self,
        query: str,
        spans: list[tuple[str, int, int]],
        semantics: Dict[str, Any],
        plan: QueryPlan,
    ) -> str:
        """Generate answer with semantic understanding (deep path)."""
        if plan.query_class == QueryClass.FULL_ANALYSIS:
            return self._generate_summary(spans, semantics)

        # Default: combine spans with context
        parts = []
        for text, start, end in spans:
            parts.append(f"[{start}:{end}]\n{text[:500]}")

        if semantics["summary"]:
            parts.insert(0, f"Summary: {semantics['summary']}")

        return "\n\n".join(parts)

    def _generate_summary(
        self, spans: list[tuple[str, int, int]], semantics: Dict[str, Any]
    ) -> str:
        """Generate document summary."""
        total_text = " ".join([s[0] for s in spans])
        word_count = len(total_text.split())

        lines = [
            f"Document Summary ({word_count} words)",
            "=" * 40,
            f"Key entities: {', '.join({e[0] for e in semantics['entities'][:10]})}"
            if semantics["entities"]
            else "No entities detected",
            "",
            "First paragraph:",
            semantics["sentences"][0][:300] if semantics["sentences"] else "N/A",
        ]

        return "\n".join(lines)


# ============================================================================
# Convenience Functions
# ============================================================================

_global_reader: Optional[FastDocumentReader] = None


def get_reader(cache_dir: Optional[Path] = None) -> FastDocumentReader:
    """Get or create global reader instance."""
    global _global_reader
    if _global_reader is None:
        _global_reader = FastDocumentReader(cache_dir)
    return _global_reader


def read_document(file_path: str | Path, query: str) -> ReadResult:
    """Convenience function for one-off reads."""
    return get_reader().read(file_path, query)


# ============================================================================
# Demo
# ============================================================================

if __name__ == "__main__":
    import tempfile

    # Create test document
    test_content = """# Fast Document Reader

A high-performance document reading system.

## Architecture

The system uses two-level chunking:
- Coarse chunks for location
- Fine chunks for answers

### Components

1. Quick Indexer - builds structural index
2. Query Router - classifies queries
3. Document Retriever - gets targeted spans
4. Local Parser - parses only retrieved spans

## Performance

Targets:
- open_and_index_once_ms: 200
- simple_lookup_ms: 50
- section_summary_ms: 150

## API

```python
def read(file_path, query):
    return reader.read(file_path, query)
```

| Metric | Target | Actual |
|--------|--------|--------|
| Index | 200ms | 150ms |
| Lookup | 50ms | 30ms |
"""

    # Write test file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(test_content)
        test_path = f.name

    try:
        reader = FastDocumentReader()

        # Test 1: Simple lookup (fast path)
        print("=" * 60)
        result = reader.read(test_path, "what is the title")
        print(f"Query: {result.query}")
        print(f"Time: {result.time_ms:.2f}ms (target: <50ms)")
        print(f"From cache: {result.from_cache}")
        print(f"Used deep parse: {result.used_deep_parse}")
        print(f"Answer: {result.answer}")
        print()

        # Test 2: Section find
        print("=" * 60)
        result = reader.read(test_path, "find the section about API")
        print(f"Query: {result.query}")
        print(f"Time: {result.time_ms:.2f}ms")
        print(f"Answer: {result.answer[:200]}...")
        print()

        # Test 3: Code find
        print("=" * 60)
        result = reader.read(test_path, "find the function read")
        print(f"Query: {result.query}")
        print(f"Time: {result.time_ms:.2f}ms")
        print(f"Answer: {result.answer[:200]}...")
        print()

        # Test 4: Table lookup
        print("=" * 60)
        result = reader.read(test_path, "find the table about metrics")
        print(f"Query: {result.query}")
        print(f"Time: {result.time_ms:.2f}ms (target: <250ms)")
        print(f"Answer: {result.answer[:300]}...")
        print()

        # Test 5: Full summary (deep path)
        print("=" * 60)
        result = reader.read(test_path, "summarize this document")
        print(f"Query: {result.query}")
        print(f"Time: {result.time_ms:.2f}ms")
        print(f"Used deep parse: {result.used_deep_parse}")
        print(f"Answer:\n{result.answer}")

    finally:
        os.unlink(test_path)
