"""
Sync routes
Handles cross-service synchronization and comparison
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
import sys
import os
import tempfile
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../..'))

from omnidrive.services.google_drive import GoogleDriveService
from omnidrive.services.folderfort import FolderfortService
from omnidrive.auth import google as google_auth
from omnidrive.auth import folderfort as folderfort_auth

from models.responses import SyncResponse, SyncJobResponse, CompareResponse
from models.requests import SyncRequest, CompareRequest

router = APIRouter()

# In-memory job storage (TODO: Replace with Redis/database)
sync_jobs = {}


def get_service(service_name: str):
    """Get service instance"""
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


@router.post("/compare", response_model=CompareResponse)
async def compare_services(request: CompareRequest):
    """Compare files between two cloud storage services"""
    try:
        if request.service1 == request.service2:
            raise HTTPException(status_code=400, detail="Services must be different")

        # Get files from both services
        service1 = get_service(request.service1)
        service2 = get_service(request.service2)

        files1 = service1.list_files(limit=request.limit)
        files2 = service2.list_files(limit=request.limit)

        # Extract file names
        names1 = {f.get('name') for f in files1}
        names2 = {f.get('name') for f in files2}

        # Find differences
        only_in_1 = list(names1 - names2)
        only_in_2 = list(names2 - names1)
        common = names1 & names2

        return CompareResponse(
            service1=request.service1,
            service2=request.service2,
            total_in_service1=len(files1),
            total_in_service2=len(files2),
            common_files=len(common),
            only_in_service1=only_in_1[:20],  # Limit to 20
            only_in_service2=only_in_2[:20]
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Comparison failed: {str(e)}"
        )


def run_sync_job(job_id: str, source: str, target: str, limit: int):
    """Background task to run sync"""
    import asyncio

    try:
        sync_jobs[job_id]["status"] = "running"
        sync_jobs[job_id]["started_at"] = datetime.now().isoformat()

        source_service = get_service(source)
        target_service = get_service(target)

        # Get files from source
        source_files = source_service.list_files(limit=limit)
        target_files = target_service.list_files(limit=limit)

        # Find files to sync
        source_names = {f.get('name'): f for f in source_files}
        target_names = {f.get('name') for f in target_files}

        files_to_sync = {name: file_data for name, file_data in source_names.items() if name not in target_names}

        sync_jobs[job_id]["files_to_sync"] = len(files_to_sync)

        # Sync files
        for file_name, file_data in files_to_sync.items():
            # Download from source
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                source_service.download_file(file_data['id'], tmp.name)
                # Upload to target
                target_service.upload_file(tmp.name)
                os.unlink(tmp.name)

            sync_jobs[job_id]["files_synced"] += 1

        sync_jobs[job_id]["status"] = "completed"
        sync_jobs[job_id]["completed_at"] = datetime.now().isoformat()

    except Exception as e:
        sync_jobs[job_id]["status"] = "failed"
        sync_jobs[job_id]["error"] = str(e)


@router.post("/", response_model=SyncResponse)
async def sync_services(request: SyncRequest, background_tasks: BackgroundTasks):
    """Sync files from source service to target service"""
    from datetime import datetime

    try:
        if request.source == request.target:
            raise HTTPException(status_code=400, detail="Source and target must be different")

        # Get files for preview
        source_service = get_service(request.source)
        target_service = get_service(request.target)

        source_files = source_service.list_files(limit=request.limit)
        target_files = target_service.list_files(limit=request.limit)

        source_names = {f.get('name') for f in source_files}
        target_names = {f.get('name') for f in target_files}

        files_to_sync = list(source_names - target_names)

        if request.dry_run:
            return SyncResponse(
                job_id="dry-run",
                message=f"Dry run: {len(files_to_sync)} files would be synced",
                dry_run=True,
                files_to_sync=files_to_sync
            )

        # Create sync job
        job_id = str(uuid.uuid4())
        sync_jobs[job_id] = {
            "job_id": job_id,
            "status": "pending",
            "source": request.source,
            "target": request.target,
            "files_to_sync": len(files_to_sync),
            "files_synced": 0,
            "started_at": None,
            "completed_at": None,
            "error": None
        }

        # Run sync in background
        background_tasks.add_task(
            run_sync_job,
            job_id,
            request.source,
            request.target,
            request.limit
        )

        return SyncResponse(
            job_id=job_id,
            message=f"Sync started: {len(files_to_sync)} files to sync",
            dry_run=False,
            files_to_sync=files_to_sync
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Sync failed: {str(e)}"
        )


@router.get("/status/{job_id}", response_model=SyncJobResponse)
async def get_sync_status(job_id: str):
    """Get sync job status"""
    if job_id not in sync_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = sync_jobs[job_id]

    return SyncJobResponse(**job)
