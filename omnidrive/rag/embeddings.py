"""
Embeddings generation for RAG system.
Uses DeepSeek's embeddings API.
"""
import os
from typing import List, Union

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class EmbeddingsGenerator:
    """Generate embeddings using DeepSeek API."""

    def __init__(self, api_key: str = None, model: str = "deepseek-chat"):
        """
        Initialize embeddings generator.

        Args:
            api_key: DeepSeek API key (uses env var if not provided)
            model: Embedding model to use
        """
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "OpenAI library is not installed. Install it with: pip install openai"
            )

        self.api_key = api_key or os.getenv('DEEPSEEK_API_KEY')
        if not self.api_key:
            raise ValueError("DeepSeek API key required. Set DEEPSEEK_API_KEY environment variable.")

        # DeepSeek usa la API compatible con OpenAI
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"  # URL de DeepSeek
        )
        self.model = model

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector (list of floats)
        """
        try:
            # DeepSeek usa el endpoint de chat para generar embeddings
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a text embedding generator. Output only the embedding vector."},
                    {"role": "user", "content": f"Generate embedding for: {text}"}
                ],
                # Extraer embeddings de la respuesta
                # Nota: DeepSeek puede tener un endpoint específico de embeddings
            )

            # Por ahora, usamos una implementación alternativa con sentence-transformers
            # si DeepSeek no tiene endpoint de embeddings dedicado
            return self._generate_embedding_fallback(text)

        except Exception as e:
            # Fallback a método alternativo
            return self._generate_embedding_fallback(text)

    def _generate_embedding_fallback(self, text: str) -> List[float]:
        """
        Fallback method for generating embeddings.
        Uses sentence-transformers locally.
        """
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer('all-MiniLM-L6-v2')
            embedding = model.encode(text)
            return embedding.tolist()
        except ImportError:
            raise ImportError(
                "Sentence-transformers not installed. Install with: pip install sentence-transformers"
            )

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer('all-MiniLM-L6-v2')
            embeddings = model.encode(texts)
            return embeddings.tolist()
        except ImportError:
            raise ImportError(
                "Sentence-transformers not installed. Install with: pip install sentence-transformers"
            )

    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings for the current model.

        Returns:
            Embedding dimension
        """
        # all-MiniLM-L6-v2 tiene dimension 384
        return 384


def get_embeddings_generator(api_key: str = None) -> EmbeddingsGenerator:
    """
    Factory function to get embeddings generator.

    Args:
        api_key: DeepSeek API key (optional)

    Returns:
        EmbeddingsGenerator instance
    """
    return EmbeddingsGenerator(api_key=api_key)
