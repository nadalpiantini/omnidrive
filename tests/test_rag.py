"""
Tests for RAG system (embeddings, vector store, indexer).
"""
import pytest
from unittest.mock import Mock, patch
from omnidrive.rag.embeddings import EmbeddingsGenerator
from omnidrive.rag.vector_store import VectorStore
from omnidrive.rag.indexer import FileIndexer, SemanticSearch


class TestEmbeddingsGenerator:
    """Test embeddings generation."""

    @patch.dict('os.environ', {'DEEPSEEK_API_KEY': 'test-key'})
    def test_initialization(self):
        """Test embeddings generator initialization."""
        gen = EmbeddingsGenerator(api_key="test-key")
        assert gen.model == "deepseek-chat"
        assert gen.api_key == "test-key"

    @patch.dict('os.environ', {}, clear=True)
    def test_requires_api_key(self):
        """Test that API key is required."""
        with pytest.raises(ValueError):
            EmbeddingsGenerator()


class TestVectorStore:
    """Test vector store."""

    def test_initialization(self):
        """Test vector store initialization."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            store = VectorStore(persist_directory=tmpdir)
            assert store.collection_name == "omnidrive_files"

    def test_count_without_chromadb(self):
        """Test that ChromaDB is optional."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            store = VectorStore(persist_directory=tmpdir)
            # Count should fail if ChromaDB is not available
            if not store._chromadb_available:
                try:
                    store.count()
                    assert False, "Should have raised ImportError"
                except ImportError:
                    pass  # Expected
            else:
                # If ChromaDB is available, count should work
                count = store.count()
                assert count >= 0


class TestFileIndexer:
    """Test file indexer."""

    def test_initialization(self):
        """Test indexer initialization."""
        with patch('omnidrive.rag.indexer.EmbeddingsGenerator'):
            with patch('omnidrive.rag.indexer.VectorStore'):
                indexer = FileIndexer()
                assert indexer.embeddings is not None
                assert indexer.vector_store is not None

    def test_extract_text_txt(self):
        """Test extracting text from .txt files."""
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test content")
            temp_path = f.name

        try:
            with patch('omnidrive.rag.indexer.EmbeddingsGenerator'):
                with patch('omnidrive.rag.indexer.VectorStore'):
                    indexer = FileIndexer()
                    text = indexer._extract_text(temp_path)
                    assert text == "Test content"
        finally:
            os.unlink(temp_path)

    def test_extract_text_unsupported(self):
        """Test extracting text from unsupported file types."""
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(mode='w', suffix='.xyz', delete=False) as f:
            f.write("Test content")
            temp_path = f.name

        try:
            with patch('omnidrive.rag.indexer.EmbeddingsGenerator'):
                with patch('omnidrive.rag.indexer.VectorStore'):
                    indexer = FileIndexer()
                    text = indexer._extract_text(temp_path)
                    # Unsupported types return None
                    assert text is None
        finally:
            os.unlink(temp_path)


class TestSemanticSearch:
    """Test semantic search."""

    def test_initialization(self):
        """Test semantic search initialization."""
        with patch('omnidrive.rag.indexer.EmbeddingsGenerator'):
            with patch('omnidrive.rag.indexer.VectorStore'):
                search = SemanticSearch()
                assert search.embeddings is not None
                assert search.vector_store is not None
