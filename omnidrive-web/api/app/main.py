"""
OmniDrive API - FastAPI Backend
REST API and WebSocket server for OmniDrive web dashboard
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager
import logging
from typing import List
import json

from api.routes import auth, files, sync, search, workflows
from api.websocket.handler import ws_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 OmniDrive API starting...")
    yield
    logger.info("🛑 OmniDrive API shutting down...")


# Create FastAPI app
app = FastAPI(
    title="OmniDrive API",
    description="Multi-cloud storage management API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://omnidrive.sujeto10.com",
        "https://omnidrive-web.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(files.router, prefix="/api/v1/files", tags=["Files"])
app.include_router(sync.router, prefix="/api/v1/sync", tags=["Sync"])
app.include_router(search.router, prefix="/api/v1/search", tags=["Search"])
app.include_router(workflows.router, prefix="/api/v1/workflows", tags=["Workflows"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "OmniDrive API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "google_drive": "available",
            "folderfort": "available"
        }
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back for now
            await ws_manager.broadcast(json.dumps({
                "type": "echo",
                "data": data
            }))
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
        logger.info("WebSocket client disconnected")


@app.on_event("startup")
async def startup_event():
    """Run on startup"""
    logger.info("✅ OmniDrive API started successfully")
    logger.info("📚 API Documentation: http://localhost:8000/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on shutdown"""
    logger.info("👋 OmniDrive API stopped")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
