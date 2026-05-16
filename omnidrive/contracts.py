"""Shared API contracts — Pydantic models used by both CLI and API."""

from typing import Optional

from pydantic import BaseModel, Field


class FileMetadata(BaseModel):
    """Canonical file metadata returned by all cloud services."""

    id: str
    name: str
    size: Optional[int] = None
    mime: Optional[str] = None
    created_time: Optional[str] = None
    modified_time: Optional[str] = None
    service: Optional[str] = None
    parent_id: Optional[str] = None


class SyncResult(BaseModel):
    """Result of a sync operation between two services."""

    source: str
    target: str
    synced: int = 0
    skipped: int = 0
    failed: int = 0
    errors: list[str] = Field(default_factory=list)


class SearchResult(BaseModel):
    """Single search result from RAG."""

    id: str
    document: str
    metadata: dict = Field(default_factory=dict)
    distance: Optional[float] = None

    @property
    def similarity(self) -> Optional[float]:
        if self.distance is not None:
            return round((1 - self.distance) * 100, 1)
        return None


class AuthProvider(BaseModel):
    """Authentication provider status."""

    service: str
    authenticated: bool = False
    token_expiry: Optional[str] = None
