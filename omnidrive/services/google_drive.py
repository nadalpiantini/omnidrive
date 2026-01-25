"""
Google Drive service implementation.
"""
import os
from typing import List, Dict, Any, Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from ..services.base import CloudService, ServiceError, AuthenticationError


# Google Drive API scopes
SCOPES = ['https://www.googleapis.com/auth/drive']


class GoogleDriveService(CloudService):
    """Google Drive cloud storage service."""

    def __init__(self, access_token: Optional[str] = None, credentials_path: Optional[str] = None):
        """
        Initialize Google Drive service.

        Args:
            access_token: OAuth access token (not used with service account)
            credentials_path: Path to service account JSON file
        """
        super().__init__(access_token)
        self.credentials_path = credentials_path or os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        self._service = None

    @property
    def service(self):
        """Lazy-load the Google Drive service."""
        if self._service is None:
            if not self.credentials_path:
                raise AuthenticationError(
                    "Google credentials not found. "
                    "Set GOOGLE_APPLICATION_CREDENTIALS or provide credentials_path."
                )
            creds = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=SCOPES
            )
            self._service = build('drive', 'v3', credentials=creds)
        return self._service

    def authenticate(self, **kwargs) -> str:
        """
        Authenticate with Google Drive.

        For service account auth, this just validates the credentials file exists.

        Returns:
            Access token string (for service account, returns "service_account" placeholder)

        Raises:
            AuthenticationError: If credentials file not found
        """
        if not self.credentials_path or not os.path.exists(self.credentials_path):
            raise AuthenticationError(
                "Google credentials file not found",
                service_name="google"
            )

        # For service account, we don't get a traditional access token
        # Return a placeholder to indicate authentication succeeded
        self.access_token = "service_account"
        return self.access_token

    def list_files(
        self,
        folder_id: Optional[str] = None,
        limit: int = 100,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        List files in Google Drive.

        Args:
            folder_id: Parent folder ID to list from. None for root.
            limit: Maximum number of files to return
            **kwargs: Additional parameters (query, orderBy, etc.)

        Returns:
            List of file metadata dictionaries

        Raises:
            ServiceError: If listing fails
        """
        try:
            # Build query
            query = kwargs.get('query', '')
            if folder_id:
                query = f"'{folder_id}' in parents"
                if kwargs.get('query'):
                    query = f"({query}) and ({kwargs['query']})"

            # List files
            results = self.service.files().list(
                pageSize=limit,
                q=query,
                fields="files(id, name, mimeType, size, parents, createdTime, modifiedTime)",
                orderBy=kwargs.get('orderBy', 'name')
            ).execute()

            items = results.get('files', [])
            return items

        except HttpError as e:
            raise ServiceError(f"Failed to list files: {e}", service_name="google")

    def upload_file(
        self,
        file_path: str,
        parent_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Upload a file to Google Drive.

        Args:
            file_path: Local path to file to upload
            parent_id: Parent folder ID. None for root.
            **kwargs: Additional parameters

        Returns:
            Uploaded file metadata

        Raises:
            ServiceError: If upload fails
        """
        try:
            from googleapiclient.http import MediaFileUpload

            file_metadata = {'name': os.path.basename(file_path)}
            if parent_id:
                file_metadata['parents'] = [parent_id]

            media = MediaFileUpload(file_path, resumable=True)

            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,size,createdTime'
            ).execute()

            return file

        except HttpError as e:
            raise ServiceError(f"Failed to upload file: {e}", service_name="google")
        except Exception as e:
            raise ServiceError(f"Failed to upload file: {e}", service_name="google")

    def download_file(
        self,
        file_id: str,
        dest_path: str,
        **kwargs
    ) -> str:
        """
        Download a file from Google Drive.

        Args:
            file_id: ID of file to download
            dest_path: Local destination path (directory or full file path)
            **kwargs: Additional parameters

        Returns:
            Path to downloaded file

        Raises:
            ServiceError: If download fails
        """
        try:
            from googleapiclient.http import MediaIoBaseDownload
            import io

            # Get file metadata to determine filename
            file_meta = self.service.files().get(fileId=file_id, fields='name').execute()
            filename = file_meta.get('name', file_id)

            # Determine destination path
            if os.path.isdir(dest_path):
                dest_path = os.path.join(dest_path, filename)

            # Download file
            request = self.service.files().get_media(fileId=file_id)

            with open(dest_path, 'wb') as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()

            return dest_path

        except HttpError as e:
            raise ServiceError(f"Failed to download file: {e}", service_name="google")

    def delete_file(
        self,
        file_id: str,
        permanent: bool = False,
        **kwargs
    ) -> bool:
        """
        Delete a file from Google Drive.

        Args:
            file_id: ID of file to delete
            permanent: If True, delete permanently. If False, move to trash.
            **kwargs: Additional parameters

        Returns:
            True if successful

        Raises:
            ServiceError: If deletion fails
        """
        try:
            if permanent:
                self.service.files().delete(fileId=file_id).execute()
            else:
                # Move to trash
                self.service.files().update(
                    fileId=file_id,
                    body={'trashed': True}
                ).execute()
            return True

        except HttpError as e:
            raise ServiceError(f"Failed to delete file: {e}", service_name="google")

    def create_folder(
        self,
        name: str,
        parent_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a new folder in Google Drive.

        Args:
            name: Folder name
            parent_id: Parent folder ID. None for root.
            **kwargs: Additional parameters

        Returns:
            Created folder metadata

        Raises:
            ServiceError: If folder creation fails
        """
        try:
            file_metadata = {
                'name': name,
                'mimeType': 'application/vnd.google-apps.folder'
            }

            if parent_id:
                file_metadata['parents'] = [parent_id]

            folder = self.service.files().create(
                body=file_metadata,
                fields='id,name,createdTime'
            ).execute()

            return folder

        except HttpError as e:
            raise ServiceError(f"Failed to create folder: {e}", service_name="google")
