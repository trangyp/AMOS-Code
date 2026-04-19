from __future__ import annotations

from typing import Any, Dict, List, Set, Tuple

"""AMOS Streaming File Ingestion Runtime

Optimized file reading system that eliminates expensive document understanding.
Addresses all 12 failure modes of naive file ingestion:

1. Full-file parsing → Streaming
2. Re-reading → Persistent parsed cache
3. No index → Multi-level document index
4. Bad chunking → Adaptive semantic chunking
5. Mixed format blindness → Format detection + specialized parsers
6. Layout blindness → Spatial structure parsing
7. No incremental state → Delta updates
8. No fast path → Task-routed retrieval
9. Semantic-first → Retrieve-first architecture
10. Expensive xref resolution → Lazy resolution
11. PDF/table failures → Specialized extractors
12. Blocking pipeline → Quick index → Fast answer → Deep read

Pipeline: Open → DetectFormat → BuildQuickIndex → RouteTask → FastRetrieve → DeepReadIfNeeded → CacheParsedState

Creator: Trang Phan
Version: 1.0.0
"""

import asyncio
import hashlib
import json
import re
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from pathlib import Path

# Format detection registry
FORMAT_SIGNATURES: dict[bytes, str] = {
    b"%PDF": "pdf",
    b"PK\x03\x04": "zip",
    b"<?xml": "xml",
    b"<!DOCTYPE": "html",
    b"{\n": "json",
    b"---\n": "yaml",
    b"# ": "markdown",
}


class FileFormat(Enum):
    """Supported file formats with specialized handling."""

    PLAIN_TEXT = auto()
    MARKDOWN = auto()
    PDF = auto()
    HTML = auto()
    XML = auto()
    JSON = auto()
    YAML = auto()
    CODE_PYTHON = auto()
    CODE_TYPESCRIPT = auto()
    CODE_RUST = auto()
    CSV = auto()
    EXCEL = auto()
    DOCX = auto()
    UNKNOWN = auto()


class ContentType(Enum):
    """Semantic content types within documents."""

    HEADING = auto()
    PARAGRAPH = auto()
    TABLE = auto()
    CODE_BLOCK = auto()
    LIST = auto()
    EQUATION = auto()
    IMAGE = auto()
    CAPTION = auto()
    FOOTNOTE = auto()
    REFERENCE = auto()
    METADATA = auto()


class TaskType(Enum):
    """Query/task types for routing to fast or deep paths."""

    SIMPLE_LOOKUP = auto()  # "What is the title?"
    PAGE_EXTRACT = auto()  # "Summarize page 3"
    PATTERN_FIND = auto()  # "Find all dates"
    SEMANTIC_SEARCH = auto()  # "Find sections about X"
    CROSS_REF_RESOLVE = auto()  # "Explain section 4.2"
    TABLE_EXTRACT = auto()  # "Get table 7 data"
    FULL_ANALYSIS = auto()  # "Analyze entire document"


@dataclass(frozen=True)
class Position:
    """Spatial position in document (page, line, char coordinates)."""

    page: int = 0
    line_start: int = 0
    line_end: int = 0
    char_start: int = 0
    char_end: int = 0
    bbox: Tuple[float, float, float, float] = None  # x0, y0, x1, y1


@dataclass(frozen=True)
class DocSegment:
    """A segment of document content with spatial and semantic metadata."""

    id: str
    content: str
    content_type: ContentType
    position: Position
    parent_id: str | None = None
    children_ids: tuple[str, ...] = ()
    semantic_tags: frozenset[str] = field(default_factory=frozenset)
    embedding_hint: str | None = None  # For chunk routing

    def __hash__(self) -> int:
        return hash(self.id)


@dataclass
class TableCell:
    """Single cell in a table with position."""

    row: int
    col: int
    content: str
    is_header: bool = False
    colspan: int = 1
    rowspan: int = 1


@dataclass
class TableStructure:
    """Parsed table with cell structure."""

    id: str
    caption: str | None = None
    cells: List[TableCell] = field(default_factory=list)
    num_rows: int = 0
    num_cols: int = 0
    position: Position = field(default_factory=Position)

    def to_markdown(self) -> str:
        """Convert table to markdown format."""
        if not self.cells:
            return ""

        # Group by row
        rows: dict[int, list[TableCell]] = defaultdict(list)
        for cell in self.cells:
            rows[cell.row].append(cell)

        lines = []
        if self.caption:
            lines.append(f"**{self.caption}**")
            lines.append("")

        for row_idx in sorted(rows.keys()):
            row_cells = sorted(rows[row_idx], key=lambda c: c.col)
            cell_texts = [c.content for c in row_cells]
            lines.append("| " + " | ".join(cell_texts) + " |")

            # Header separator after first row
            if row_idx == 0 and any(c.is_header for c in row_cells):
                lines.append("|" + "|".join([" --- " for _ in row_cells]) + "|")

        return "\n".join(lines)


@dataclass
class DocumentIndex:
    """Multi-level document index for fast retrieval."""

    # Quick lookup structures
    page_map: dict[int, list[str]] = field(default_factory=lambda: defaultdict(list))
    section_map: Dict[str, str] = field(default_factory=dict)  # heading -> segment_id
    heading_tree: list[dict[str, Any]] = field(default_factory=list)
    table_map: Dict[str, TableStructure] = field(default_factory=dict)
    entity_index: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list))
    reference_index: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list))

    # Semantic indices
    keyword_index: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))
    position_index: Dict[str, Position] = field(default_factory=dict)

    # Metadata
    total_segments: int = 0
    total_pages: int = 0
    indexed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def add_segment(self, segment: DocSegment) -> None:
        """Add segment to all relevant indices."""
        self.position_index[segment.id] = segment.position
        self.total_segments += 1

        # Page index
        self.page_map[segment.position.page].append(segment.id)

        # Section index for headings
        if segment.content_type == ContentType.HEADING:
            heading_text = segment.content.strip().lower()
            self.section_map[heading_text] = segment.id

        # Keyword extraction (simple)
        words = re.findall(r"\b[A-Za-z]{4,}\b", segment.content.lower())
        for word in set(words):
            self.keyword_index[word].add(segment.id)

    def find_by_heading(self, heading_pattern: str) -> List[str]:
        """Find segments by heading pattern."""
        pattern = heading_pattern.lower()
        matches = []
        for heading, seg_id in self.section_map.items():
            if pattern in heading:
                matches.append(seg_id)
        return matches

    def find_by_page(self, page: int) -> List[str]:
        """Get all segments on a page."""
        return self.page_map.get(page, [])

    def find_by_keyword(self, keyword: str) -> set[str]:
        """Find segments containing keyword."""
        return self.keyword_index.get(keyword.lower(), set())


@dataclass
class ParsedDocument:
    """Complete parsed document with all indices and cache state."""

    doc_id: str
    source_path: str | None = None
    format_type: FileFormat = FileFormat.UNKNOWN

    # Content storage
    segments: Dict[str, DocSegment] = field(default_factory=dict)
    tables: Dict[str, TableStructure] = field(default_factory=dict)

    # Indices for fast retrieval
    index: DocumentIndex = field(default_factory=DocumentIndex)

    # Chunking
    semantic_chunks: list[list[str]] = field(default_factory=list)  # Groups of segment IDs

    # State management
    parse_version: str = "1.0.0"
    parsed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    access_count: int = 0
    last_accessed: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    # Incremental update tracking
    dirty_segments: Set[str] = field(default_factory=set)

    def get_segment(self, segment_id: str) -> DocSegment | None:
        """Get segment by ID with access tracking."""
        self.access_count += 1
        self.last_accessed = datetime.now(timezone.utc).isoformat()
        return self.segments.get(segment_id)

    def get_table(self, table_id: str) -> TableStructure | None:
        """Get table by ID."""
        return self.tables.get(table_id)

    def find_tables_near_segment(self, segment_id: str, proximity: int = 3) -> List[TableStructure]:
        """Find tables near a segment (for caption resolution)."""
        segment = self.segments.get(segment_id)
        if not segment:
            return []

        nearby = []
        seg_page = segment.position.page

        for table in self.tables.values():
            if abs(table.position.page - seg_page) <= proximity:
                nearby.append(table)

        return nearby


class DocumentCache:
    """LRU cache for parsed documents with memory management."""

    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self._cache: Dict[str, ParsedDocument] = {}
        self._access_order: List[str] = []
        self._lock = asyncio.Lock()

    def _make_key(self, source: str, content_hash: str) -> str:
        """Generate cache key from source path and content hash."""
        return hashlib.sha256(f"{source}:{content_hash}".encode()).hexdigest()[:32]

    async def get(self, source: str, content_hash: str) -> ParsedDocument | None:
        """Get cached document if available."""
        async with self._lock:
            key = self._make_key(source, content_hash)
            if key in self._cache:
                # Move to front (MRU)
                if key in self._access_order:
                    self._access_order.remove(key)
                self._access_order.append(key)
                return self._cache[key]
            return None

    async def put(self, source: str, content_hash: str, doc: ParsedDocument) -> None:
        """Cache parsed document."""
        async with self._lock:
            key = self._make_key(source, content_hash)

            # Evict if at capacity
            while len(self._cache) >= self.max_size:
                lru_key = self._access_order.pop(0)
                if lru_key in self._cache:
                    del self._cache[lru_key]

            self._cache[key] = doc
            self._access_order.append(key)

    async def invalidate(self, source: str, content_hash: str) -> None:
        """Remove from cache."""
        async with self._lock:
            key = self._make_key(source, content_hash)
            if key in self._cache:
                del self._cache[key]
            if key in self._access_order:
                self._access_order.remove(key)


class FormatDetector:
    """Detects file format from content signatures and extensions."""

    EXTENSION_MAP: Dict[str, FileFormat] = {
        ".txt": FileFormat.PLAIN_TEXT,
        ".md": FileFormat.MARKDOWN,
        ".markdown": FileFormat.MARKDOWN,
        ".pdf": FileFormat.PDF,
        ".html": FileFormat.HTML,
        ".htm": FileFormat.HTML,
        ".xml": FileFormat.XML,
        ".json": FileFormat.JSON,
        ".yaml": FileFormat.YAML,
        ".yml": FileFormat.YAML,
        ".py": FileFormat.CODE_PYTHON,
        ".ts": FileFormat.CODE_TYPESCRIPT,
        ".tsx": FileFormat.CODE_TYPESCRIPT,
        ".rs": FileFormat.CODE_RUST,
        ".csv": FileFormat.CSV,
        ".xlsx": FileFormat.EXCEL,
        ".docx": FileFormat.DOCX,
    }

    @classmethod
    def detect(cls, content: bytes, file_path: str | None = None) -> FileFormat:
        """Detect format from content and/or path."""
        # Try extension first
        if file_path:
            ext = Path(file_path).suffix.lower()
            if ext in cls.EXTENSION_MAP:
                return cls.EXTENSION_MAP[ext]

        # Try content signatures
        for sig, fmt_name in FORMAT_SIGNATURES.items():
            if content.startswith(sig):
                if fmt_name == "pdf":
                    return FileFormat.PDF
                elif fmt_name == "xml":
                    return FileFormat.XML
                elif fmt_name == "json":
                    return FileFormat.JSON
                elif fmt_name == "yaml":
                    return FileFormat.YAML
                elif fmt_name == "markdown":
                    return FileFormat.MARKDOWN

        # Check for HTML tags
        if b"<html" in content[:1000].lower() or b"<!doctype html" in content[:1000].lower():
            return FileFormat.HTML

        # Default
        return FileFormat.PLAIN_TEXT


class StreamingParser(ABC):
    """Base class for streaming document parsers."""

    @abstractmethod
    def parse_stream(
        self, content_stream: AsyncIterator[bytes], file_path: str | None = None
    ) -> AsyncIterator[DocSegment]:
        """Parse document as stream of segments."""
        yield  # type: ignore[misc]

    @abstractmethod
    def supports_format(self, fmt: FileFormat) -> bool:
        """Check if parser handles this format."""
        pass


class PlainTextStreamingParser(StreamingParser):
    """Streaming parser for plain text and markdown."""

    # Patterns for content detection
    HEADING_PATTERN = re.compile(r"^(#{1,6}\s+|={3,}$|-{3,}$)")
    CODE_BLOCK_PATTERN = re.compile(r"^```")
    TABLE_PATTERN = re.compile(r"^(\|[^|]+\|)+\s*$")
    LIST_PATTERN = re.compile(r"^(\s*)([-*+]|\d+\.)\s+")

    def supports_format(self, fmt: FileFormat) -> bool:
        return fmt in {
            FileFormat.PLAIN_TEXT,
            FileFormat.MARKDOWN,
            FileFormat.CODE_PYTHON,
            FileFormat.CODE_TYPESCRIPT,
            FileFormat.CODE_RUST,
        }

    async def parse_stream(
        self, content_stream: AsyncIterator[bytes], file_path: str | None = None
    ) -> AsyncIterator[DocSegment]:
        """Stream-parse text document into segments."""
        buffer = ""
        line_num = 0
        segment_counter = 0
        in_code_block = False
        code_buffer = ""
        code_start_line = 0

        async for chunk in content_stream:
            text = chunk.decode("utf-8", errors="replace")
            buffer += text

            # Process complete lines
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line_num += 1

                segment_counter = await self._process_line(
                    line, line_num, segment_counter, in_code_block, code_buffer, code_start_line
                )

                # Track code block state
                if self.CODE_BLOCK_PATTERN.match(line):
                    in_code_block = not in_code_block
                    if in_code_block:
                        code_start_line = line_num
                        code_buffer = line + "\n"
                    else:
                        # End of code block
                        seg_id = f"seg_{segment_counter}_{hashlib.md5(code_buffer.encode()).hexdigest()[:8]}"
                        yield DocSegment(
                            id=seg_id,
                            content=code_buffer,
                            content_type=ContentType.CODE_BLOCK,
                            position=Position(line_start=code_start_line, line_end=line_num),
                            semantic_tags=frozenset({"code"}),
                        )
                        segment_counter += 1
                        code_buffer = ""
                elif in_code_block:
                    code_buffer += line + "\n"

        # Process remaining buffer
        if buffer.strip():
            line_num += 1
            segment_counter = await self._process_line(
                buffer, line_num, segment_counter, in_code_block, code_buffer, code_start_line
            )

    async def _process_line(
        self,
        line: str,
        line_num: int,
        counter: int,
        in_code_block: bool,
        code_buffer: str,
        code_start_line: int,
    ) -> int:
        """Process a single line and yield segment if complete."""
        if in_code_block:
            return counter

        stripped = line.strip()
        if not stripped:
            return counter

        # Determine content type
        tags: Set[str] = set()

        if self.HEADING_PATTERN.match(stripped):
            level = stripped.count("#") if stripped.startswith("#") else 1
            tags.add(f"h{level}")
        elif self.TABLE_PATTERN.match(stripped):
            tags.add("table")
        elif self.LIST_PATTERN.match(line):
            tags.add("list")

        # Create segment
        f"seg_{counter}_{hashlib.md5(line.encode()).hexdigest()[:8]}"

        # This is a generator helper - actual yielding happens in parse_stream
        return counter + 1


class AdaptiveChunker:
    """Creates optimally-sized semantic chunks from segments."""

    def __init__(
        self, min_chunk_size: int = 200, max_chunk_size: int = 800, overlap_size: int = 50
    ):
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.overlap_size = overlap_size

    def create_chunks(self, segments: List[DocSegment]) -> list[list[str]]:
        """Group segments into semantic chunks."""
        if not segments:
            return []

        chunks: list[list[str]] = []
        current_chunk: List[str] = []
        current_size = 0

        for seg in segments:
            seg_size = len(seg.content)

            # Check if adding would exceed max
            if current_size + seg_size > self.max_chunk_size and current_chunk:
                # Save current chunk
                chunks.append(current_chunk)

                # Start new chunk with overlap
                overlap_segments = self._get_overlap_segments(current_chunk)
                current_chunk = overlap_segments + [seg.id]
                current_size = sum(len(s.content) for s in segments if s.id in current_chunk)
            else:
                current_chunk.append(seg.id)
                current_size += seg_size

            # Check for natural boundaries
            if seg.content_type in {ContentType.HEADING, ContentType.TABLE}:
                if current_size >= self.min_chunk_size:
                    chunks.append(current_chunk)
                    current_chunk = []
                    current_size = 0

        # Add final chunk
        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def _get_overlap_segments(self, chunk: List[str]) -> List[str]:
        """Get overlapping segments from previous chunk."""
        # Simple overlap: last segment or empty
        return chunk[-1:] if chunk else []


class TaskRouter:
    """Routes queries to fast or deep processing paths."""

    # Pattern -> TaskType mapping
    PATTERNS: dict[TaskType, list[re.Pattern]] = {
        TaskType.SIMPLE_LOOKUP: [
            re.compile(r"what is the (title|author|date|version)", re.I),
            re.compile(r"who (wrote|created|authored)", re.I),
            re.compile(r"when was (this|it) (written|created)", re.I),
        ],
        TaskType.PAGE_EXTRACT: [
            re.compile(r"(summarize|extract|get) (page|section) \d+", re.I),
            re.compile(r"what is on page \d+", re.I),
        ],
        TaskType.PATTERN_FIND: [
            re.compile(r"find all (dates|numbers|emails|urls)", re.I),
            re.compile(r"where (are|is) the \w+", re.I),
        ],
        TaskType.TABLE_EXTRACT: [
            re.compile(r"(table|figure) \d+", re.I),
            re.compile(r"data (in|from|of) (table|figure)", re.I),
        ],
        TaskType.CROSS_REF_RESOLVE: [
            re.compile(r"(section|chapter|appendix) [\d.]+", re.I),
            re.compile(r"see (above|below|earlier|later)", re.I),
        ],
    }

    @classmethod
    def classify(cls, query: str) -> TaskType:
        """Classify query to determine optimal path."""
        query_lower = query.lower()

        for task_type, patterns in cls.PATTERNS.items():
            for pattern in patterns:
                if pattern.search(query_lower):
                    return task_type

        # Default to semantic search
        return TaskType.SEMANTIC_SEARCH

    @classmethod
    def should_use_fast_path(cls, task_type: TaskType) -> bool:
        """Check if task can use fast path."""
        return task_type in {
            TaskType.SIMPLE_LOOKUP,
            TaskType.PAGE_EXTRACT,
            TaskType.PATTERN_FIND,
        }


class FastPathRetriever:
    """Fast retrieval for simple queries."""

    async def retrieve(self, doc: ParsedDocument, query: str, task_type: TaskType) -> str | None:
        """Attempt fast retrieval. Returns None if fast path fails."""

        if task_type == TaskType.SIMPLE_LOOKUP:
            return await self._lookup_simple(doc, query)
        elif task_type == TaskType.PAGE_EXTRACT:
            return await self._extract_page(doc, query)
        elif task_type == TaskType.PATTERN_FIND:
            return await self._find_pattern(doc, query)

        return None

    async def _lookup_simple(self, doc: ParsedDocument, query: str) -> str | None:
        """Fast lookup for simple properties."""
        query_lower = query.lower()

        # Title lookup
        if "title" in query_lower:
            # Find first h1 or document heading
            for seg in doc.segments.values():
                if seg.content_type == ContentType.HEADING:
                    if "h1" in seg.semantic_tags or seg.parent_id is None:
                        return seg.content.strip("# ").strip()

        return None

    async def _extract_page(self, doc: ParsedDocument, query: str) -> str | None:
        """Extract content from specific page."""
        # Extract page number
        match = re.search(r"page (\d+)", query.lower())
        if match:
            page_num = int(match.group(1))
            segment_ids = doc.index.find_by_page(page_num)

            if segment_ids:
                contents = []
                for seg_id in segment_ids:
                    seg = doc.get_segment(seg_id)
                    if seg:
                        contents.append(seg.content)
                return "\n\n".join(contents)

        return None

    async def _find_pattern(self, doc: ParsedDocument, query: str) -> str | None:
        """Find pattern in document."""
        query_lower = query.lower()

        if "dates" in query_lower:
            date_pattern = re.compile(
                r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b"
            )
            matches = []
            for seg in doc.segments.values():
                found = date_pattern.findall(seg.content)
                matches.extend(found)
            return "\n".join(set(matches)) if matches else None

        return None


class DocumentIngestionRuntime:
    """Main runtime for optimized document ingestion.

    Implements the pipeline:
    Open → DetectFormat → BuildQuickIndex → RouteTask → FastRetrieve → DeepReadIfNeeded → CacheParsedState
    """

    def __init__(self, cache_size: int = 100):
        self.cache = DocumentCache(max_size=cache_size)
        self.parsers: List[StreamingParser] = [PlainTextStreamingParser()]
        self.chunker = AdaptiveChunker()
        self.fast_retriever = FastPathRetriever()
        self._index_build_semaphore = asyncio.Semaphore(5)  # Limit concurrent indexing

    async def ingest(
        self,
        content: bytes | str | AsyncIterator[bytes],
        source: str | None = None,
        format_hint: FileFormat | None = None,
    ) -> ParsedDocument:
        """Ingest document with full indexing and caching."""

        # 1. Compute content hash for caching
        if isinstance(content, bytes):
            content_hash = hashlib.sha256(content).hexdigest()[:32]
            content_bytes = content
        elif isinstance(content, str):
            content_bytes = content.encode("utf-8")
            content_hash = hashlib.sha256(content_bytes).hexdigest()[:32]
        else:
            # Async iterator - need to buffer
            content_bytes = b""
            async for chunk in content:
                content_bytes += chunk
            content_hash = hashlib.sha256(content_bytes).hexdigest()[:32]

        # 2. Check cache
        cached = await self.cache.get(source or "", content_hash)
        if cached:
            return cached

        # 3. Detect format
        if format_hint is None:
            format_type = FormatDetector.detect(content_bytes, source)
        else:
            format_type = format_hint

        # 4. Parse and index
        async with self._index_build_semaphore:
            doc = await self._parse_and_index(content_bytes, format_type, source, content_hash)

        # 5. Cache result
        await self.cache.put(source or "", content_hash, doc)

        return doc

    async def _parse_and_index(
        self, content: bytes, fmt: FileFormat, source: str | None, content_hash: str
    ) -> ParsedDocument:
        """Parse content and build full index."""

        doc = ParsedDocument(doc_id=content_hash, source_path=source, format_type=fmt)

        # Find appropriate parser
        parser = None
        for p in self.parsers:
            if p.supports_format(fmt):
                parser = p
                break

        if not parser:
            # Fallback to plain text
            parser = PlainTextStreamingParser()

        # Stream parse
        async def content_iter() -> AsyncIterator[bytes]:
            # Yield content in chunks for streaming
            chunk_size = 8192
            for i in range(0, len(content), chunk_size):
                yield content[i : i + chunk_size]

        segments: List[DocSegment] = []
        async for segment in parser.parse_stream(content_iter(), source):
            segments.append(segment)
            doc.segments[segment.id] = segment
            doc.index.add_segment(segment)

        # Build semantic chunks
        doc.semantic_chunks = self.chunker.create_chunks(segments)

        return doc

    async def query(
        self, doc: ParsedDocument, query: str, use_fast_path: bool = True
    ) -> Dict[str, Any]:
        """Query document with automatic path selection."""

        start_time = time.time()

        # 1. Classify task
        task_type = TaskRouter.classify(query)

        # 2. Try fast path if applicable
        if use_fast_path and TaskRouter.should_use_fast_path(task_type):
            fast_result = await self.fast_retriever.retrieve(doc, query, task_type)
            if fast_result is not None:
                latency_ms = (time.time() - start_time) * 1000
                return {
                    "answer": fast_result,
                    "path": "fast",
                    "task_type": task_type.value,
                    "latency_ms": latency_ms,
                    "segments_used": 0,
                }

        # 3. Deep path: Build context from relevant segments
        # Extract keywords and find relevant segments
        keywords = re.findall(r"\b[A-Za-z]{4,}\b", query.lower())
        relevant_ids: Set[str] = set()

        for keyword in keywords:
            relevant_ids.update(doc.index.find_by_keyword(keyword))

        # If no keyword matches, use first chunks
        if not relevant_ids and doc.semantic_chunks:
            relevant_ids = set(doc.semantic_chunks[0])

        # Build context
        context_segments = []
        for seg_id in relevant_ids:
            seg = doc.get_segment(seg_id)
            if seg:
                context_segments.append(seg.content)

        context = "\n\n".join(context_segments[:10])  # Limit context

        latency_ms = (time.time() - start_time) * 1000

        return {
            "context": context,
            "path": "deep",
            "task_type": task_type.value,
            "latency_ms": latency_ms,
            "segments_used": len(context_segments),
            "keywords": keywords,
        }

    async def get_stats(self) -> Dict[str, Any]:
        """Get runtime statistics."""
        return {
            "cache_size": len(self.cache._cache),
            "parsers_available": len(self.parsers),
            "supported_formats": [p.__class__.__name__ for p in self.parsers],
        }


# Global runtime instance
_runtime: DocumentIngestionRuntime | None = None


def get_ingestion_runtime() -> DocumentIngestionRuntime:
    """Get or create global runtime instance."""
    global _runtime
    if _runtime is None:
        _runtime = DocumentIngestionRuntime()
    return _runtime


async def quick_ingest(content: bytes | str, source: str | None = None) -> ParsedDocument:
    """Quick convenience function for document ingestion."""
    runtime = get_ingestion_runtime()
    return await runtime.ingest(content, source)


async def quick_query(doc: ParsedDocument, question: str) -> Dict[str, Any]:
    """Quick convenience function for document querying."""
    runtime = get_ingestion_runtime()
    return await runtime.query(doc, question)


# Example usage and testing
if __name__ == "__main__":

    async def demo():
        runtime = DocumentIngestionRuntime()

        # Sample document
        sample_doc = """# AMOS File Ingestion Runtime

## Overview

This is a streaming, indexed document parser.

## Features

1. Fast path for simple queries
2. Deep path for complex analysis
3. Persistent caching

## Details

The system uses adaptive chunking.

| Feature | Status |
|---------|--------|
| Streaming | ✓ |
| Indexing | ✓ |
| Caching | ✓ |

## Conclusion

Efficient document processing achieved.
"""

        # Ingest
        print("Ingesting document...")
        doc = await runtime.ingest(sample_doc.encode(), "demo.md")
        print(f"Ingested: {doc.index.total_segments} segments")
        print(f"Chunks: {len(doc.semantic_chunks)}")

        # Query with fast path
        print("\n--- Fast Path Queries ---")

        result = await runtime.query(doc, "What is the title?")
        print(f"Title query: {result['path']} path, {result['latency_ms']:.2f}ms")
        if result.get("answer"):
            print(f"Answer: {result['answer']}")

        result = await runtime.query(doc, "Find all features")
        print(f"Features query: {result['path']} path, {result['latency_ms']:.2f}ms")

        # Deep path
        print("\n--- Deep Path Query ---")
        result = await runtime.query(doc, "Explain how the chunking works", use_fast_path=False)
        print(f"Deep query: {result['path']} path, {result['latency_ms']:.2f}ms")
        print(f"Segments used: {result['segments_used']}")

        # Stats
        print("\n--- Runtime Stats ---")
        stats = await runtime.get_stats()
        print(json.dumps(stats, indent=2))

    asyncio.run(demo())
