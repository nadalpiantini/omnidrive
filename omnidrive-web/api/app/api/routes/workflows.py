"""
Workflow routes
Handles workflow execution and management
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
import sys
import os
import uuid
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../..'))

from omnidrive.workflows.graphs import get_workflow_engine
from api.websocket.handler import ws_manager

from models.responses import (
    WorkflowsListResponse,
    WorkflowInfo,
    WorkflowRunResponse,
    WorkflowStatusResponse
)
from models.requests import WorkflowRunRequest

router = APIRouter()

# In-memory job storage
workflow_jobs = {}


@router.get("/", response_model=WorkflowsListResponse)
async def list_workflows():
    """List all available workflows"""
    try:
        engine = get_workflow_engine()
        workflows = engine.list_workflows()

        workflow_list = []
        for wf in workflows:
            workflow_list.append(WorkflowInfo(
                name=wf['name'],
                description=wf['description'],
                steps=wf['steps']
            ))

        return WorkflowsListResponse(workflows=workflow_list)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list workflows: {str(e)}"
        )


def run_workflow_job(job_id: str, workflow_name: str, parameters: dict = None):
    """Background task to run workflow"""
    try:
        workflow_jobs[job_id]["status"] = "running"
        workflow_jobs[job_id]["started_at"] = datetime.now().isoformat()

        engine = get_workflow_engine()

        # Execute workflow
        result = engine.execute_workflow(workflow_name)

        # Update job status
        if result.status.value == "completed":
            workflow_jobs[job_id]["status"] = "completed"
        else:
            workflow_jobs[job_id]["status"] = "failed"
            workflow_jobs[job_id]["error"] = result.message

        workflow_jobs[job_id]["completed_at"] = datetime.now().isoformat()

        # Broadcast completion
        import asyncio
        asyncio.create_task(ws_manager.broadcast_json({
            "type": "workflow_complete",
            "job_id": job_id,
            "workflow_name": workflow_name,
            "status": workflow_jobs[job_id]["status"]
        }))

    except Exception as e:
        workflow_jobs[job_id]["status"] = "failed"
        workflow_jobs[job_id]["error"] = str(e)


@router.post("/{name}/run", response_model=WorkflowRunResponse)
async def run_workflow(
    name: str,
    background_tasks: BackgroundTasks,
    request: WorkflowRunRequest = None
):
    """Run a workflow"""
    try:
        # Get workflow engine
        engine = get_workflow_engine()

        # Validate workflow exists
        workflows = engine.list_workflows()
        workflow_names = [wf['name'] for wf in workflows]

        if name not in workflow_names:
            raise HTTPException(status_code=404, detail=f"Workflow '{name}' not found")

        # Create job
        job_id = str(uuid.uuid4())
        workflow_jobs[job_id] = {
            "job_id": job_id,
            "workflow_name": name,
            "status": "pending",
            "current_step": 0,
            "total_steps": 0,
            "progress": 0.0,
            "started_at": None,
            "completed_at": None,
            "error": None
        }

        # Run workflow in background
        background_tasks.add_task(
            run_workflow_job,
            job_id,
            name,
            request.parameters if request else None
        )

        return WorkflowRunResponse(
            job_id=job_id,
            workflow_name=name,
            status="pending",
            message=f"Workflow '{name}' started"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to run workflow: {str(e)}"
        )


@router.get("/{name}/status/{job_id}", response_model=WorkflowStatusResponse)
async def get_workflow_status(name: str, job_id: str):
    """Get workflow execution status"""
    if job_id not in workflow_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = workflow_jobs[job_id]

    return WorkflowStatusResponse(**job)
