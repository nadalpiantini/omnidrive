"""
Semantic search routes
Handles file indexing and semantic search using RAG
"""
import os
import sys

from fastapi import APIRouter, Depends, HTTPException

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../..'))

from auth.middleware import get_current_user
from models.requests import IndexRequest, SearchRequest
from models.responses import IndexResponse, SearchResponse, SearchResult

from omnidrive.rag.embeddings import OPENAI_AVAILABLE
from omnidrive.rag.indexer import SemanticSearch

router = APIRouter()


@router.post("/", response_model=SearchResponse)
async def semantic_search(
    request: SearchRequest,
    user: dict = Depends(get_current_user),
):
    """
    Perform semantic search across indexed files

    Requires OPENAI_API_KEY environment variable
    """
    try:
        if not OPENAI_AVAILABLE:
            raise HTTPException(
                status_code=400,
                detail="OpenAI library not available. Install with: pip install openai"
            )

        if not os.getenv('OPENAI_API_KEY'):
            raise HTTPException(
                status_code=400,
                detail="OPENAI_API_KEY environment variable not set"
            )

        # Initialize semantic search
        search = SemanticSearch()

        # Perform search
        results = search.search(
            query=request.query,
            top_k=request.top_k,
            service=request.service
        )

        # Convert to response format
        search_results = []
        for result in results:
            metadata = result.get('metadata', {})
            distance = result.get('distance', 0)

            search_results.append(SearchResult(
                file_name=metadata.get('file_name', 'Unknown'),
                service=metadata.get('service', 'unknown'),
                relevance=max(0, (1 - distance) * 100),  # Convert distance to relevance %
                snippet=result.get('document', '')[:200] + "..." if result.get('document') else None,
                metadata=metadata
            ))

        return SearchResponse(
            query=request.query,
            results=search_results,
            total=len(search_results)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        ) from e



@router.post("/index", response_model=IndexResponse)
async def index_files(
    request: IndexRequest,
    user: dict = Depends(get_current_user),
):
    """
    Index files from a cloud storage service for semantic search

    This is a placeholder - full implementation would:
    1. Download files from service
    2. Extract text content
    3. Generate embeddings
    4. Store in vector database
    """
    try:
        # TODO: Implement full indexing pipeline
        # For now, just return success message

        return IndexResponse(
            success=True,
            message=f"Indexing {request.service} files (feature coming soon)",
            files_indexed=0
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Indexing failed: {str(e)}"
        ) from e

