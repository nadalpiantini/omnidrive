"""
Authentication routes
Handles Google Drive and Folderfort authentication
"""
from fastapi import APIRouter, HTTPException, Depends
import sys
import os

# Add parent directory to path to import omnidrive modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../..'))

from omnidrive.auth import google as google_auth
from omnidrive.auth import folderfort as folderfort_auth
from omnidrive.config import load_config

from models.responses import AuthResponse, AuthStatusResponse
from models.requests import GoogleAuthRequest, FolderfortAuthRequest

router = APIRouter()


@router.get("/status", response_model=AuthStatusResponse)
async def get_auth_status():
    """Get authentication status for all services"""
    cfg = load_config()

    return AuthStatusResponse(
        google_authenticated=google_auth.is_google_authenticated(),
        folderfort_authenticated=folderfort_auth.is_folderfort_authenticated(),
        google_email=None,  # TODO: Extract from service account
        folderfort_email=cfg.get('folderfort_email')
    )


@router.post("/google", response_model=AuthResponse)
async def authenticate_google(request: GoogleAuthRequest):
    """
    Authenticate with Google Drive using service account

    Expects service account JSON content
    """
    try:
        # Save service account JSON to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(request.service_account_json)
            temp_path = f.name

        try:
            # Set environment variable for Google SDK
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = temp_path

            # Authenticate using existing auth module
            token = google_auth.authenticate_google()

            # Clean up temp file
            os.unlink(temp_path)

            return AuthResponse(
                success=True,
                message="Successfully authenticated with Google Drive",
                service="google",
                token=token
            )

        except Exception as e:
            # Clean up on error
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise e

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Google authentication failed: {str(e)}"
        )


@router.post("/folderfort", response_model=AuthResponse)
async def authenticate_folderfort(request: FolderfortAuthRequest):
    """
    Authenticate with Folderfort using email and password

    Returns OAuth access token
    """
    try:
        # Authenticate using existing auth module
        token = folderfort_auth.authenticate_folderfort(
            email=request.email,
            password=request.password
        )

        return AuthResponse(
            success=True,
            message="Successfully authenticated with Folderfort",
            service="folderfort",
            token=token
        )

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Folderfort authentication failed: {str(e)}"
        )


@router.post("/logout")
async def logout():
    """Logout from all services"""
    try:
        # TODO: Implement logout for each service
        # For now, just clear config
        from omnidrive.config import save_config
        save_config({})

        return {
            "success": True,
            "message": "Logged out successfully"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Logout failed: {str(e)}"
        )
