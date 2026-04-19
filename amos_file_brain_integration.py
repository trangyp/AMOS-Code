from typing import Any

"""AMOS File-Brain Integration

Real integration between streaming file ingestion and brain reading kernel.
Uses actual AMOS brain components for cognitive document processing.

Owner: Trang Phan
"""

import asyncio
import hashlib
import time
from dataclasses import dataclass, field
from datetime import datetime

# Import file ingestion runtime
from amos_file_ingestion_runtime import (
    ContentType,
    ParsedDocument,
    get_ingestion_runtime,
)

# Import brain reading kernel
try:
    from amos_reading_kernel import (
        AMOSReadingKernel,
        SegmentType,
        SignalClass,
        StableRead,
        get_reading_kernel,
        read_text,
    )

    READING_KERNEL_AVAILABLE = True
except ImportError:
    READING_KERNEL_AVAILABLE = False

# Import brain for cognitive processing
try:
    from typing import Any

    from amos_brain import get_super_brain, think

    BRAIN_AVAILABLE = True
except ImportError:
    BRAIN_AVAILABLE = False


@dataclass
class FileBrainResult:
    """Result of file processing through brain pipeline."""

    file_id: str
    source_path: str | None
    total_segments: int
    processed_segments: int
    stable_reads: list[dict[str, Any]]
    cognitive_summary: Dict[str, Any]
    processing_time_ms: float
    errors: List[str] = field(default_factory=list)


class FileBrainProcessor:
    """Processes files through both ingestion runtime and brain reading."""

    def __init__(self):
        self._runtime = get_ingestion_runtime()
        self._reading_kernel: Any = None
        self._brain: Any = None
        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize all components."""
        if self._initialized:
            return True

        # Initialize reading kernel
        if READING_KERNEL_AVAILABLE:
            try:
                self._reading_kernel = get_reading_kernel()
            except Exception as e:
                print(f"Reading kernel init failed: {e}")

        # Initialize brain
        if BRAIN_AVAILABLE:
            try:
                self._brain = get_super_brain()
            except Exception as e:
                print(f"Brain init failed: {e}")

        self._initialized = True
        return True

    async def process_file(
        self,
        content: bytes | str,
        source: str | None = None,
        context: Dict[str, Any] = None,
    ) -> FileBrainResult:
        """Process file through full pipeline: ingest → segment → brain read."""
        start_time = time.time()
        errors: List[str] = []

        # Initialize if needed
        if not self._initialized:
            await self.initialize()

        # Step 1: Ingest and parse document
        try:
            doc = await self._runtime.ingest(content, source)
        except Exception as e:
            errors.append(f"Ingestion failed: {e}")
            return FileBrainResult(
                file_id=hashlib.sha256(str(source).encode()).hexdigest()[:16],
                source_path=source,
                total_segments=0,
                processed_segments=0,
                stable_reads=[],
                cognitive_summary={},
                processing_time_ms=(time.time() - start_time) * 1000,
                errors=errors,
            )

        # Step 2: Process segments through brain reading kernel
        stable_reads: list[dict[str, Any]] = []
        processed_count = 0

        for seg_id, segment in doc.segments.items():
            # Skip non-text content for brain processing
            if segment.content_type not in {
                ContentType.PARAGRAPH,
                ContentType.HEADING,
                ContentType.LIST,
            }:
                continue

            if READING_KERNEL_AVAILABLE and self._reading_kernel:
                try:
                    stable_read = await read_text(
                        text=segment.content,
                        dialogue_context=context or {},
                        memory_context={"segment_id": seg_id, "source": source},
                        world_context={},
                    )

                    if stable_read:
                        stable_reads.append(
                            {
                                "segment_id": seg_id,
                                "read_type": stable_read.read_type.value
                                if hasattr(stable_read.read_type, "value")
                                else str(stable_read.read_type),
                                "confidence": stable_read.confidence,
                                "primary_signal": stable_read.primary_signal
                                if hasattr(stable_read, "primary_signal")
                                else None,
                                "content": segment.content[:100] + "..."
                                if len(segment.content) > 100
                                else segment.content,
                            }
                        )
                        processed_count += 1

                except Exception as e:
                    errors.append(f"Segment {seg_id} processing failed: {e}")
            else:
                # Fallback: basic segment info without brain processing
                stable_reads.append(
                    {
                        "segment_id": seg_id,
                        "read_type": "unprocessed",
                        "content": segment.content[:100] + "..."
                        if len(segment.content) > 100
                        else segment.content,
                        "content_type": segment.content_type.name
                        if hasattr(segment.content_type, "name")
                        else str(segment.content_type),
                    }
                )
                processed_count += 1

        # Step 3: Generate cognitive summary using brain
        cognitive_summary: Dict[str, Any] = {
            "file_structure": {
                "total_segments": doc.index.total_segments,
                "headings": len(
                    [s for s in doc.segments.values() if s.content_type == ContentType.HEADING]
                ),
                "paragraphs": len(
                    [s for s in doc.segments.values() if s.content_type == ContentType.PARAGRAPH]
                ),
                "tables": len(
                    [s for s in doc.segments.values() if s.content_type == ContentType.TABLE]
                ),
            },
            "processed_at": datetime.now(UTC).isoformat(),
        }

        # Add brain analysis if available
        if BRAIN_AVAILABLE and self._brain and stable_reads:
            try:
                # Use brain to analyze document patterns
                doc_text = "\n".join([s.get("content", "") for s in stable_reads[:5]])
                cognitive_summary["brain_analysis"] = await self._analyze_with_brain(doc_text)
            except Exception as e:
                errors.append(f"Brain analysis failed: {e}")

        elapsed_ms = (time.time() - start_time) * 1000

        return FileBrainResult(
            file_id=doc.doc_id,
            source_path=doc.source_path,
            total_segments=doc.index.total_segments,
            processed_segments=processed_count,
            stable_reads=stable_reads,
            cognitive_summary=cognitive_summary,
            processing_time_ms=elapsed_ms,
            errors=errors,
        )

    async def _analyze_with_brain(self, text: str) -> Dict[str, Any]:
        """Use brain to analyze document content."""
        if not BRAIN_AVAILABLE:
            return {"error": "Brain not available"}

        try:
            # Simple cognitive analysis via brain
            result = think(
                input_data={
                    "text": text[:500],  # Limit for brain processing
                    "task": "document_analysis",
                    "extract": ["main_topics", "intent", "complexity"],
                },
                context={"source": "file_brain_integration"},
            )
            return {"brain_result": result, "analyzed_chars": min(len(text), 500)}
        except Exception as e:
            return {"error": str(e)}

    async def query_file(
        self, doc: ParsedDocument, query: str, use_cognitive_search: bool = True
    ) -> Dict[str, Any]:
        """Query file using both index and brain if available."""
        start_time = time.time()

        # First: use fast path from ingestion runtime
        result = await self._runtime.query(doc, query)

        # If cognitive search enabled and brain available, enhance results
        if use_cognitive_search and BRAIN_AVAILABLE and self._brain:
            try:
                context = result.get("context", "")
                if context:
                    brain_insight = think(
                        input_data={
                            "context": context[:1000],
                            "query": query,
                            "task": "answer_from_context",
                        },
                        context={"source": "file_query"},
                    )
                    result["brain_enhancement"] = brain_insight
            except Exception as e:
                result["brain_error"] = str(e)

        result["latency_ms"] = (time.time() - start_time) * 1000
        return result


# Global processor instance
_processor: FileBrainProcessor | None = None


async def get_file_brain_processor() -> FileBrainProcessor:
    """Get or create global processor."""
    global _processor
    if _processor is None:
        _processor = FileBrainProcessor()
        await _processor.initialize()
    return _processor


async def process_file_with_brain(
    content: bytes | str, source: str | None = None, context: Dict[str, Any] = None
) -> FileBrainResult:
    """Convenience function for file → brain processing."""
    processor = await get_file_brain_processor()
    return await processor.process_file(content, source, context)


async def query_file_with_brain(doc: ParsedDocument, query: str) -> Dict[str, Any]:
    """Convenience function for cognitive file query."""
    processor = await get_file_brain_processor()
    return await processor.query_file(doc, query)


# Real execution test
if __name__ == "__main__":

    async def test():
        # Test with real content
        test_doc = """# Project Requirements

## Overview
Build a streaming document processor with cognitive capabilities.

## Goals
1. Fast file ingestion
2. Brain-powered analysis
3. Real-time querying

## Constraints
Must handle PDF, text, and code files efficiently.

## Questions
How do we optimize for large files?
"""

        print("Testing file-brain integration...")
        result = await process_file_with_brain(test_doc.encode(), source="test_requirements.md")

        print(f"\nFile ID: {result.file_id}")
        print(f"Total segments: {result.total_segments}")
        print(f"Processed: {result.processed_segments}")
        print(f"Time: {result.processing_time_ms:.2f}ms")
        print(f"Errors: {result.errors}")

        if result.stable_reads:
            print("\nFirst stable read:")
            print(result.stable_reads[0])

        if result.cognitive_summary:
            print("\nCognitive summary:")
            print(result.cognitive_summary)

    asyncio.run(test())
