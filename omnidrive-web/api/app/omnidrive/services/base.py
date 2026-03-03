"""
Base interface for all cloud storage services.
All services must inherit from CloudService and implement these methods.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path


class CloudService(ABC):
    """
    Abstract base class for cloud storage services.

    All cloud service implementations (Google Drive, Folderfort, etc.)
    must inherit from this class and implement all abstract methods.
    """

    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize the cloud service.

        Args:
            access_token: Authentication token for the service
        """
        self.access_token = access_token
        # Extract service name from class name (e.g., GoogleDriveService -> google_drive)
        class_name = self.__class__.__name__
        if class_name.endswith("Service"):
            class_name = class_name[:-7]  # Remove "Service" suffix
        # Convert CamelCase to snake_case
        import re
        self.service_name = re.sub(r'(?<!^)(?=[A-Z])', '_', class_name).lower()

    @abstractmethod
    def authenticate(self, **kwargs) -> str:
        """
        Authenticate with the service and return access token.

        Returns:
            Access token string

        Raises:
            AuthenticationError: If authentication fails
        """
        pass

    @abstractmethod
    def list_files(
        self,
        folder_id: Optional[str] = None,
        limit: int = 100,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        List files in the cloud storage.

        Args:
            folder_id: Parent folder ID to list from. None for root.
            limit: Maximum number of files to return
            **kwargs: Additional service-specific parameters

        Returns:
            List of file metadata dictionaries

        Raises:
            ServiceError: If the operation fails
        """
        pass

    @abstractmethod
    def upload_file(
        self,
        file_path: str,
        parent_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Upload a file to cloud storage.

        Args:
            file_path: Local path to file to upload
            parent_id: Parent folder ID. None for root.
            **kwargs: Additional service-specific parameters

        Returns:
            Uploaded file metadata

        Raises:
            ServiceError: If upload fails
        """
        pass

    @abstractmethod
    def download_file(
        self,
        file_id: str,
        dest_path: str,
        **kwargs
    ) -> str:
        """
        Download a file from cloud storage.

        Args:
            file_id: ID of file to download
            dest_path: Local destination path
            **kwargs: Additional service-specific parameters

        Returns:
            Path to downloaded file

        Raises:
            ServiceError: If download fails
        """
        pass

    @abstractmethod
    def delete_file(
        self,
        file_id: str,
        permanent: bool = False,
        **kwargs
    ) -> bool:
        """
        Delete a file from cloud storage.

        Args:
            file_id: ID of file to delete
            permanent: If True, delete permanently. If False, move to trash.
            **kwargs: Additional service-specific parameters

        Returns:
            True if successful

        Raises:
            ServiceError: If deletion fails
        """
        pass

    @abstractmethod
    def create_folder(
        self,
        name: str,
        parent_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a new folder.

        Args:
            name: Folder name
            parent_id: Parent folder ID. None for root.
            **kwargs: Additional service-specific parameters

        Returns:
            Created folder metadata

        Raises:
            ServiceError: If folder creation fails
        """
        pass

    def get_service_name(self) -> str:
        """Get the service name."""
        return self.service_name

    def is_authenticated(self) -> bool:
        """Check if the service is authenticated."""
        return self.access_token is not None


class ServiceError(Exception):
    """Base exception for service errors."""

    def __init__(self, message: str, service_name: str = ""):
        self.message = message
        self.service_name = service_name
        super().__init__(f"{service_name}: {message}" if service_name else message)


class AuthenticationError(ServiceError):
    """Exception raised when authentication fails."""

    pass
