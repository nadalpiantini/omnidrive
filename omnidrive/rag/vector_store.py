"""
Vector store for RAG system using ChromaDB.
"""
import os
from typing import List, Dict, Any, Optional

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False


class VectorStore:
    """Vector store for semantic search using ChromaDB."""

    def __init__(
        self,
        collection_name: str = "omnidrive_files",
        persist_directory: str = None
    ):
        """
        Initialize vector store.

        Args:
            collection_name: Name of the ChromaDB collection
            persist_directory: Directory to persist vector DB (uses ~/.omnidrive/vector_db if None)
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        self._chromadb_available = CHROMADB_AVAILABLE

    def _ensure_chromadb(self):
        """Ensure ChromaDB is available before operations."""
        if not self._chromadb_available:
            raise ImportError(
                "ChromaDB is not installed or incompatible with Python 3.14+\n"
                "Install with: pip install 'chromadb<0.5.0' --upgrade\n"
                "RAG features require ChromaDB for vector storage."
            )

    def _initialize_collection(self):
        """Initialize or load the ChromaDB collection."""
        if self.persist_directory is None:
            self.persist_directory = os.path.expanduser("~/.omnidrive/vector_db")

        # Create persist directory if it doesn't exist
        os.makedirs(self.persist_directory, exist_ok=True)

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )

        try:
            # Try to get existing collection
            self.collection = self.client.get_collection(name=self.collection_name)
        except:
            # Create new collection if it doesn't exist
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )

    def add(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: List[Dict[str, Any]]
    ):
        """
        Add documents to the vector store.

        Args:
            ids: List of unique document IDs
            embeddings: List of embedding vectors
            documents: List of document texts
            metadatas: List of metadata dictionaries
        """
        self._ensure_chromadb()
        self._initialize_collection()

        try:
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
        except Exception as e:
            raise Exception(f"Failed to add documents to vector store: {e}")

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            where: Optional metadata filter

        Returns:
            List of search results with metadata
        """
        self._ensure_chromadb()
        self._initialize_collection()

        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where
            )

            # Format results
            formatted_results = []
            if results['ids'] and results['ids'][0]:
                for i, doc_id in enumerate(results['ids'][0]):
                    formatted_results.append({
                        'id': doc_id,
                        'document': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i] if 'distances' in results else None
                    })

            return formatted_results

        except Exception as e:
            raise Exception(f"Failed to search vector store: {e}")

    def delete(self, ids: List[str]):
        """
        Delete documents from the vector store.

        Args:
            ids: List of document IDs to delete
        """
        self._ensure_chromadb()
        self._initialize_collection()

        try:
            self.collection.delete(ids=ids)
        except Exception as e:
            raise Exception(f"Failed to delete documents: {e}")

    def get(self, ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get documents by IDs.

        Args:
            ids: List of document IDs

        Returns:
            List of documents
        """
        self._ensure_chromadb()
        self._initialize_collection()

        try:
            results = self.collection.get(ids=ids)
            return results
        except Exception as e:
            raise Exception(f"Failed to get documents: {e}")

    def count(self) -> int:
        """
        Get the total number of documents in the collection.

        Returns:
            Number of documents
        """
        self._ensure_chromadb()
        self._initialize_collection()
        return self.collection.count()

    def clear(self):
        """Clear all documents from the collection."""
        self._ensure_chromadb()
        self._initialize_collection()

        try:
            # Delete and recreate collection
            self.client.delete_collection(name=self.collection_name)
            self._initialize_collection()
        except Exception as e:
            raise Exception(f"Failed to clear collection: {e}")


def get_vector_store(collection_name: str = "omnidrive_files") -> VectorStore:
    """
    Factory function to get vector store.

    Args:
        collection_name: Name of the collection

    Returns:
        VectorStore instance
    """
    return VectorStore(collection_name=collection_name)
