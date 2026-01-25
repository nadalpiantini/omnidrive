"""
File operation routes
Handles file listing, upload, download, delete
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../..'))

from omnidrive.services.google_drive import GoogleDriveService
from omnidrive.services.folderfort import FolderfortService
from omnidrive.auth import google as google_auth
from omnidrive.auth import folderfort as folderfort_auth

from models.responses import (
    FileListResponse,
    FileMetadata,
    FileUploadResponse,
    FileDownloadResponse
)
from models.requests import (
    FileListRequest,
    FileUploadRequest,
    FileDownloadRequest,
    FileDeleteRequest
)

router = APIRouter()


def get_service(service_name: str):
    """Get service instance based on service name"""
    if service_name == "google":
        if not google_auth.is_google_authenticated():
            raise HTTPException(status_code=401, detail="Not authenticated with Google Drive")
        return GoogleDriveService()

    elif service_name == "folderfort":
        if not folderfort_auth.is_folderfort_authenticated():
            raise HTTPException(status_code=401, detail="Not authenticated with Folderfort")
        token = folderfort_auth.get_folderfort_token()
        return FolderfortService(access_token=token)

    else:
        raise HTTPException(status_code=400, detail=f"Unknown service: {service_name}")


@router.get("/", response_model=FileListResponse)
async def list_files(service: str, folder_id: str = None, limit: int = 100):
    """List files from a cloud storage service"""
    try:
        service_instance = get_service(service)
        files = service_instance.list_files(folder_id=folder_id, limit=limit)

        # Convert to response format
        file_metadata = []
        for file_data in files:
            file_metadata.append(FileMetadata(
                id=file_data.get('id'),
                name=file_data.get('name'),
                size=file_data.get('size') or file_data.get('file_size'),
                mime_type=file_data.get('mimeType') or file_data.get('type'),
                created_time=file_data.get('createdTime'),
                modified_time=file_data.get('modifiedTime'),
                parent_id=file_data.get('parentId'),
                service=service
            ))

        return FileListResponse(
            service=service,
            files=file_metadata,
            total=len(file_metadata)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list files: {str(e)}"
        )


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    service: str = "google",
    parent_id: str = None
):
    """Upload a file to cloud storage"""
    import tempfile
    from api.websocket.handler import ws_manager

    try:
        service_instance = get_service(service)

        # Save uploaded file to temp
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            content = await file.read()
            tmp.write(content)
            temp_path = tmp.name

        try:
            # Upload to service
            result = service_instance.upload_file(temp_path, parent_id=parent_id)

            # Broadcast file update
            await ws_manager.send_file_update({
                "action": "uploaded",
                "service": service,
                "file": result
            })

            return FileUploadResponse(
                success=True,
                message=f"Successfully uploaded {file.filename}",
                file=FileMetadata(
                    id=result.get('id'),
                    name=result.get('name'),
                    size=result.get('size'),
                    mime_type=result.get('mimeType'),
                    service=service
                )
            )

        finally:
            # Clean up temp file
            os.unlink(temp_path)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )


@router.get("/{file_id}/download", response_model=FileDownloadResponse)
async def download_file(service: str, file_id: str):
    """Download a file from cloud storage"""
    import tempfile
    import uuid

    try:
        service_instance = get_service(service)

        # Create temp file for download
        temp_path = f"/tmp/omnidrive_download_{uuid.uuid4()}"

        # Download file
        downloaded_path = service_instance.download_file(file_id, temp_path)

        # Return file info (actual file streaming handled separately)
        return FileDownloadResponse(
            success=True,
            message=f"File downloaded successfully",
            file_path=downloaded_path
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Download failed: {str(e)}"
        )


@router.delete("/{file_id}")
async def delete_file(service: str, file_id: str, permanent: bool = False):
    """Delete a file from cloud storage"""
    try:
        service_instance = get_service(service)

        success = service_instance.delete_file(file_id, permanent=permanent)

        from api.websocket.handler import ws_manager
        await ws_manager.send_file_update({
            "action": "deleted",
            "service": service,
            "file_id": file_id
        })

        return {
            "success": success,
            "message": f"File {'permanently ' if permanent else ''}deleted successfully"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Delete failed: {str(e)}"
        )
