"""WebSocket connection manager"""
from fastapi import WebSocket
from typing import List, Dict
import json
import logging

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manage WebSocket connections"""

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_ids: Dict[WebSocket, str] = {}

    async def connect(self, websocket: WebSocket, connection_id: str = None):
        """Accept and track WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        if connection_id:
            self.connection_ids[websocket] = connection_id
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.connection_ids:
            del self.connection_ids[websocket]
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal(self, message: dict, websocket: WebSocket):
        """Send message to specific WebSocket"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: str):
        """Broadcast message to all connected WebSockets"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting: {e}")
                disconnected.append(connection)

        # Clean up disconnected connections
        for connection in disconnected:
            self.disconnect(connection)

    async def broadcast_json(self, message: dict):
        """Broadcast JSON message to all connected WebSockets"""
        await self.broadcast(json.dumps(message))

    async def send_progress(self, job_id: str, progress: float, status: str, data: dict = None):
        """Send progress update to all clients"""
        message = {
            "type": "progress",
            "job_id": job_id,
            "progress": progress,
            "status": status,
            "data": data or {}
        }
        await self.broadcast_json(message)

    async def send_file_update(self, file_data: dict):
        """Send file update notification"""
        message = {
            "type": "file_update",
            "data": file_data
        }
        await self.broadcast_json(message)

    async def send_sync_update(self, job_id: str, files_synced: int, total_files: int):
        """Send sync progress update"""
        message = {
            "type": "sync_progress",
            "job_id": job_id,
            "files_synced": files_synced,
            "total_files": total_files,
            "progress": (files_synced / total_files * 100) if total_files > 0 else 0
        }
        await self.broadcast_json(message)

    async def send_upload_progress(self, file_id: str, progress: float, status: str):
        """Send upload progress update"""
        message = {
            "type": "upload_progress",
            "file_id": file_id,
            "progress": progress,
            "status": status
        }
        await self.broadcast_json(message)


# Global WebSocket manager instance
ws_manager = WebSocketManager()
