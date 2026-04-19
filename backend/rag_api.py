"""
AMOS RAG (Retrieval-Augmented Generation) API
Integrates document upload, vector storage, and semantic search with chat.

Architecture:
- Document upload → Text extraction → Chunking → Vectorization → ChromaDB
- Chat query → Semantic search → Retrieve top-k chunks → Augment prompt → LLM
"""

import os
import uuid
import tempfile
from pathlib import Path
from typing import Any
from dataclasses import dataclass
from datetime import datetime, timezone

from flask import Blueprint, request, jsonify

# RAG Blueprint
rag_bp = Blueprint('rag', __name__, url_prefix='/rag')


@dataclass
class DocumentUpload:
    """Document upload metadata."""
    document_id: str
    filename: str
    content_type: str
    size_bytes: int
    upload_time: str
    chunk_count: int
    status: str  # processing, indexed, error
    error_message: str  = None


class DocumentProcessor:
    """Process uploaded documents for RAG."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def process_file(self, file_path: str, filename: str) -> tuple[list[str], DocumentUpload]:
        """
        Process uploaded file into chunks.

        Returns:
            (chunks, metadata) - Text chunks and document metadata
        """
        # Generate document ID
        document_id = str(uuid.uuid4())[:8]

        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Try binary files with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
            except Exception as e:
                return [], DocumentUpload(
                    document_id=document_id,
                    filename=filename,
                    content_type="unknown",
                    size_bytes=0,
                    upload_time=datetime.now(timezone.utc).isoformat(),
                    chunk_count=0,
                    status="error",
                    error_message=f"Failed to read file: {str(e)}"
                )

        # Chunk the content
        chunks = self._chunk_text(content)

        # Create metadata
        metadata = DocumentUpload(
            document_id=document_id,
            filename=filename,
            content_type=self._detect_content_type(filename),
            size_bytes=len(content.encode('utf-8')),
            upload_time=datetime.now(timezone.utc).isoformat(),
            chunk_count=len(chunks),
            status="indexed"
        )

        return chunks, metadata

    def _chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks."""
        chunks = []
        start = 0

        while start < len(text):
            # Find end of chunk
            end = start + self.chunk_size

            # Try to break at sentence or paragraph
            if end < len(text):
                # Look for sentence ending
                for break_char in ['.\n', '. ', '\n\n', '\n']:
                    pos = text.rfind(break_char, start, end + 100)
                    if pos != -1 and pos > start + self.chunk_size * 0.5:
                        end = pos + len(break_char)
                        break

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            # Move to next chunk with overlap
            start = end - self.chunk_overlap
            if start <= 0 or start >= len(text):
                break

        return chunks

    def _detect_content_type(self, filename: str) -> str:
        """Detect content type from filename."""
        ext = Path(filename).suffix.lower()

        content_types = {
            '.txt': 'text/plain',
            '.md': 'text/markdown',
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.py': 'text/x-python',
            '.js': 'text/javascript',
            '.html': 'text/html',
            '.css': 'text/css',
            '.json': 'application/json',
            '.csv': 'text/csv',
        }

        return content_types.get(ext, 'application/octet-stream')


class RAGManager:
    """Manages RAG operations - document storage and retrieval."""

    def __init__(self):
        self.processor = DocumentProcessor()
        self.documents: Dict[str, DocumentUpload] = {}
        self._vector_memory = None

    def get_vector_memory(self):
        """Get or initialize vector memory."""
        if self._vector_memory is None:
            from amos_vector_memory import AMOSVectorMemory, get_vector_memory
from typing import List
from typing import Dict
            self._vector_memory = get_vector_memory()
            if not self._vector_memory._initialized:
                self._vector_memory.initialize()
        return self._vector_memory

    def upload_document(self, file_path: str, filename: str) -> DocumentUpload:
        """Process and store document for RAG."""
        # Process file into chunks
        chunks, metadata = self.processor.process_file(file_path, filename)

        if metadata.status == "error":
            self.documents[metadata.document_id] = metadata
            return metadata

        # Store chunks in vector memory
        try:
            vector_memory = self.get_vector_memory()

            for i, chunk in enumerate(chunks):
                # Create unique chunk ID
                chunk_id = f"{metadata.document_id}_chunk_{i}"

                # Add to vector memory with metadata
                vector_memory.add_memory(
                    content=chunk,
                    memory_type="semantic",
                    metadata={
                        "document_id": metadata.document_id,
                        "filename": filename,
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "upload_time": metadata.upload_time
                    }
                )

            self.documents[metadata.document_id] = metadata
            return metadata

        except Exception as e:
            metadata.status = "error"
            metadata.error_message = f"Failed to index: {str(e)}"
            self.documents[metadata.document_id] = metadata
            return metadata

    def retrieve_context(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Retrieve relevant document chunks for query.

        Returns:
            List of relevant chunks with scores and metadata
        """
        try:
            vector_memory = self.get_vector_memory()

            # Search for relevant memories
            results = vector_memory.search_similar(
                query=query,
                k=top_k,
                memory_type="semantic"
            )

            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "content": result.get("content", ""),
                    "score": result.get("relevance_score", 0.0),
                    "document_id": result.get("metadata", {}).get("document_id", "unknown"),
                    "filename": result.get("metadata", {}).get("filename", "unknown"),
                    "chunk_index": result.get("metadata", {}).get("chunk_index", 0)
                })

            return formatted_results

        except Exception as e:
            print(f"[RAG] Retrieval error: {e}")
            return []

    def get_documents(self) -> List[DocumentUpload]:
        """Get all uploaded documents."""
        return sorted(
            self.documents.values(),
            key=lambda x: x.upload_time,
            reverse=True
        )

    def delete_document(self, document_id: str) -> bool:
        """Delete document from RAG system."""
        if document_id not in self.documents:
            return False

        try:
            # Remove from vector memory
            vector_memory = self.get_vector_memory()
            # This would need implementation in vector_memory to delete by metadata
            # For now, just mark as deleted

            del self.documents[document_id]
            return True

        except Exception as e:
            print(f"[RAG] Delete error: {e}")
            return False


# Global RAG manager instance
_rag_manager = None

def get_rag_manager() -> RAGManager:
    """Get global RAG manager instance."""
    global _rag_manager
    if _rag_manager is None:
        _rag_manager = RAGManager()
    return _rag_manager


# API Endpoints

@rag_bp.route("/documents", methods=["POST"])
def upload_document():
    """
    Upload document for RAG.

    Request: multipart/form-data with 'file' field
    Response: {"document_id": "...", "status": "indexed", "chunks": 12}
    """
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "Empty filename"}), 400

        # Save to temp file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=Path(file.filename).suffix) as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name

        try:
            # Process and index
            rag_manager = get_rag_manager()
            result = rag_manager.upload_document(tmp_path, file.filename)

            return jsonify({
                "document_id": result.document_id,
                "filename": result.filename,
                "status": result.status,
                "chunks": result.chunk_count,
                "size_bytes": result.size_bytes,
                "upload_time": result.upload_time,
                "error": result.error_message
            })

        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@rag_bp.route("/documents", methods=["GET"])
def list_documents():
    """List all uploaded documents."""
    try:
        rag_manager = get_rag_manager()
        documents = rag_manager.get_documents()

        return jsonify({
            "documents": [
                {
                    "document_id": doc.document_id,
                    "filename": doc.filename,
                    "content_type": doc.content_type,
                    "size_bytes": doc.size_bytes,
                    "chunk_count": doc.chunk_count,
                    "upload_time": doc.upload_time,
                    "status": doc.status
                }
                for doc in documents
            ]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@rag_bp.route("/documents/<document_id>", methods=["DELETE"])
def delete_document(document_id):
    """Delete document from RAG system."""
    try:
        rag_manager = get_rag_manager()
        success = rag_manager.delete_document(document_id)

        if not success:
            return jsonify({"error": "Document not found"}), 404

        return jsonify({"status": "deleted", "document_id": document_id})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@rag_bp.route("/retrieve", methods=["POST"])
def retrieve_context():
    """
    Retrieve relevant context for a query.

    Request: {"query": "What is Python?", "top_k": 5}
    Response: {"results": [{"content": "...", "score": 0.89, "filename": "..."}]}
    """
    try:
        data = request.get_json() or {}
        query = data.get("query", "")
        top_k = data.get("top_k", 5)

        if not query:
            return jsonify({"error": "Query is required"}), 400

        rag_manager = get_rag_manager()
        results = rag_manager.retrieve_context(query, top_k=top_k)

        return jsonify({
            "query": query,
            "results": results,
            "count": len(results)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@rag_bp.route("/chat", methods=["POST"])
def chat_with_rag():
    """
    Chat with RAG-enhanced context.

    Request: {
        "message": "Explain Python",
        "session_id": "abc123",
        "context": "Feeling tired",
        "top_k": 5,
        "include_citations": true
    }

    Response: {
        "content": "Based on your documents...",
        "citations": [{"filename": "doc.txt", "excerpt": "..."}],
        "sources_used": 3
    }
    """
    try:
        data = request.get_json() or {}
        message = data.get("message", "")
        top_k = data.get("top_k", 5)
        include_citations = data.get("include_citations", True)

        if not message:
            return jsonify({"error": "Message is required"}), 400

        # Retrieve relevant context
        rag_manager = get_rag_manager()
        context_results = rag_manager.retrieve_context(message, top_k=top_k)

        # Build augmented prompt
        if context_results:
            context_text = "\n\n".join([
                f"[From {r['filename']}]: {r['content']}"
                for r in context_results
            ])

            augmented_message = f"""Based on the following context, answer the question:

Context:
{context_text}

Question: {message}

Provide a comprehensive answer using the information from the context above."""
        else:
            augmented_message = message

        # Forward to regular chat endpoint logic
        # This would integrate with the existing chat system
        # For now, return the augmented message structure

        return jsonify({
            "message": message,
            "augmented_prompt": augmented_message,
            "context_chunks": len(context_results),
            "sources": [
                {"filename": r["filename"], "score": r["score"]}
                for r in context_results
            ] if include_citations else [],
            "mode": "rag"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Register blueprint function
def register_rag_routes(app):
    """Register RAG routes with Flask app."""
    app.register_blueprint(rag_bp)
    print("[RAG] Routes registered: /rag/*")
