"""
Request models for API validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List


# Auth Models
class GoogleAuthRequest(BaseModel):
    """Google Drive authentication request"""
    service_account_json: str = Field(..., description="Service account JSON content")


class FolderfortAuthRequest(BaseModel):
    """Folderfort authentication request"""
    email: EmailStr
    password: str = Field(..., min_length=1)


# File Models
class FileListRequest(BaseModel):
    """File list request"""
    service: str = Field(..., pattern="^(google|folderfort)$")
    folder_id: Optional[str] = None
    limit: int = Field(100, ge=1, le=1000)


class FileUploadRequest(BaseModel):
    """File upload request"""
    service: str = Field(..., pattern="^(google|folderfort)$")
    parent_id: Optional[str] = None


class FileDownloadRequest(BaseModel):
    """File download request"""
    service: str = Field(..., pattern="^(google|folderfort)$")
    file_id: str


class FileDeleteRequest(BaseModel):
    """File delete request"""
    service: str = Field(..., pattern="^(google|folderfort)$")
    file_id: str
    permanent: bool = False


# Sync Models
class SyncRequest(BaseModel):
    """Sync request"""
    source: str = Field(..., pattern="^(google|folderfort)$")
    target: str = Field(..., pattern="^(google|folderfort)$")
    dry_run: bool = False
    limit: int = Field(100, ge=1, le=1000)


class CompareRequest(BaseModel):
    """Compare services request"""
    service1: str = Field(..., pattern="^(google|folderfort)$")
    service2: str = Field(..., pattern="^(google|folderfort)$")
    limit: int = Field(100, ge=1, le=1000)


# Search Models
class SearchRequest(BaseModel):
    """Semantic search request"""
    query: str = Field(..., min_length=1)
    service: Optional[str] = Field(None, pattern="^(google|folderfort)$")
    top_k: int = Field(5, ge=1, le=20)


class IndexRequest(BaseModel):
    """Index files request"""
    service: str = Field(..., pattern="^(google|folderfort)$")
    limit: int = Field(100, ge=1, le=1000)


# Workflow Models
class WorkflowRunRequest(BaseModel):
    """Run workflow request"""
    name: str = Field(..., pattern="^(smart-sync|backup)$")
    parameters: Optional[dict] = None
