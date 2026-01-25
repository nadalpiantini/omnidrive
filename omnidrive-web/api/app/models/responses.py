"""
Response models for API
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


# Auth Responses
class AuthResponse(BaseModel):
    """Authentication response"""
    success: bool
    message: str
    service: str
    token: Optional[str] = None


class AuthStatusResponse(BaseModel):
    """Authentication status response"""
    google_authenticated: bool
    folderfort_authenticated: bool
    google_email: Optional[str] = None
    folderfort_email: Optional[str] = None


# File Responses
class FileMetadata(BaseModel):
    """File metadata"""
    id: str
    name: str
    size: Optional[int] = None
    mime_type: Optional[str] = None
    created_time: Optional[str] = None
    modified_time: Optional[str] = None
    parent_id: Optional[str] = None
    service: str


class FileListResponse(BaseModel):
    """File list response"""
    service: str
    files: List[FileMetadata]
    total: int


class FileUploadResponse(BaseModel):
    """File upload response"""
    success: bool
    message: str
    file: Optional[FileMetadata] = None


class FileDownloadResponse(BaseModel):
    """File download response"""
    success: bool
    message: str
    file_path: Optional[str] = None


# Sync Responses
class SyncJobResponse(BaseModel):
    """Sync job response"""
    job_id: str
    status: str  # pending, running, completed, failed
    source: str
    target: str
    files_to_sync: int
    files_synced: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class SyncResponse(BaseModel):
    """Sync response"""
    job_id: str
    message: str
    dry_run: bool
    files_to_sync: List[str]


class CompareResponse(BaseModel):
    """Compare services response"""
    service1: str
    service2: str
    total_in_service1: int
    total_in_service2: int
    common_files: int
    only_in_service1: List[str]
    only_in_service2: List[str]


# Search Responses
class SearchResult(BaseModel):
    """Search result"""
    file_name: str
    service: str
    relevance: float
    snippet: Optional[str] = None
    metadata: Dict[str, Any]


class SearchResponse(BaseModel):
    """Search response"""
    query: str
    results: List[SearchResult]
    total: int


class IndexResponse(BaseModel):
    """Index response"""
    success: bool
    message: str
    files_indexed: int


# Workflow Responses
class WorkflowInfo(BaseModel):
    """Workflow information"""
    name: str
    description: str
    steps: int


class WorkflowsListResponse(BaseModel):
    """Workflows list response"""
    workflows: List[WorkflowInfo]


class WorkflowRunResponse(BaseModel):
    """Workflow run response"""
    job_id: str
    workflow_name: str
    status: str
    message: str


class WorkflowStatusResponse(BaseModel):
    """Workflow status response"""
    job_id: str
    workflow_name: str
    status: str
    current_step: int
    total_steps: int
    progress: float
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


# Error Response
class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: str
    status_code: int


# WebSocket Message
class WSMessage(BaseModel):
    """WebSocket message"""
    type: str
    data: Dict[str, Any]
