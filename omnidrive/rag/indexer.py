"""
File indexer for RAG system.
Extracts text from files and generates embeddings.
"""
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

from .embeddings import EmbeddingsGenerator
from .vector_store import VectorStore


class FileIndexer:
    """Index files for semantic search."""

    def __init__(
        self,
        embeddings_generator: EmbeddingsGenerator = None,
        vector_store: VectorStore = None
    ):
        """
        Initialize file indexer.

        Args:
            embeddings_generator: Embeddings generator instance
            vector_store: Vector store instance
        """
        self.embeddings = embeddings_generator or EmbeddingsGenerator()
        self.vector_store = vector_store or VectorStore()

    def index_file(
        self,
        file_path: str,
        file_id: str,
        service: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Index a single file for semantic search.

        Args:
            file_path: Path to the file
            file_id: Unique file identifier
            service: Cloud service name (google, folderfort, etc.)
            metadata: Additional metadata

        Returns:
            True if successful
        """
        try:
            # Extract text from file
            text = self._extract_text(file_path)
            if not text:
                print(f"  ⚠ Skipping {file_path}: no text extracted")
                return False

            # Generate embedding
            embedding = self.embeddings.embed_text(text)

            # Prepare metadata
            file_metadata = {
                'file_id': file_id,
                'service': service,
                'file_path': file_path,
                'file_name': os.path.basename(file_path),
                'file_size': os.path.getsize(file_path),
            }
            if metadata:
                file_metadata.update(metadata)

            # Add to vector store
            self.vector_store.add(
                ids=[file_id],
                embeddings=[embedding],
                documents=[text],
                metadatas=[file_metadata]
            )

            return True

        except Exception as e:
            print(f"  ✗ Error indexing {file_path}: {e}")
            return False

    def index_files(
        self,
        files: List[Dict[str, Any]],
        service: str
    ) -> Dict[str, int]:
        """
        Index multiple files.

        Args:
            files: List of file dictionaries with 'id' and 'name' keys
            service: Cloud service name

        Returns:
            Dictionary with indexing statistics
        """
        stats = {'success': 0, 'failed': 0, 'skipped': 0}

        for file_data in files:
            file_id = file_data.get('id')
            file_name = file_data.get('name')

            print(f"  📄 {file_name}")

            # For now, we can't index without the actual file path
            # In a full implementation, we would download files first
            stats['skipped'] += 1

        return stats

    def _extract_text(self, file_path: str) -> Optional[str]:
        """
        Extract text from a file based on its type.

        Args:
            file_path: Path to the file

        Returns:
            Extracted text or None
        """
        try:
            file_ext = Path(file_path).suffix.lower()

            # Text files
            if file_ext in ['.txt', '.md', '.py', '.js', '.html', '.css', '.json']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()

            # PDF files
            elif file_ext == '.pdf':
                if not PYPDF_AVAILABLE:
                    print("  ⚠ pypdf not installed, cannot index PDF files")
                    return None
                text = []
                with open(file_path, 'rb') as f:
                    reader = pypdf.PdfReader(f)
                    for page in reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text.append(page_text)
                return "\n".join(text)

            # DOCX files
            elif file_ext == '.docx':
                if not DOCX_AVAILABLE:
                    print("  ⚠ python-docx not installed, cannot index DOCX files")
                    return None
                doc = docx.Document(file_path)
                return "\n".join([paragraph.text for paragraph in doc.paragraphs])

            else:
                print(f"  ⚠ Unsupported file type: {file_ext}")
                return None

        except Exception as e:
            print(f"  ✗ Error extracting text: {e}")
            return None


class SemanticSearch:
    """Semantic search using RAG."""

    def __init__(
        self,
        embeddings_generator: EmbeddingsGenerator = None,
        vector_store: VectorStore = None
    ):
        """
        Initialize semantic search.

        Args:
            embeddings_generator: Embeddings generator instance
            vector_store: Vector store instance
        """
        self.embeddings = embeddings_generator or EmbeddingsGenerator()
        self.vector_store = vector_store or VectorStore()

    def search(
        self,
        query: str,
        top_k: int = 5,
        service: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for files using semantic query.

        Args:
            query: Search query in natural language
            top_k: Number of results to return
            service: Filter by service (google, folderfort, etc.)

        Returns:
            List of search results
        """
        try:
            # Generate query embedding
            query_embedding = self.embeddings.embed_text(query)

            # Build filter
            where = {'service': service} if service else None

            # Search vector store
            results = self.vector_store.search(
                query_embedding=query_embedding,
                top_k=top_k,
                where=where
            )

            return results

        except Exception as e:
            raise Exception(f"Search failed: {e}")
