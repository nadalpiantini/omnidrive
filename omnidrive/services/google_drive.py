"""
Google Drive service implementation.
"""
import os
import json
import time
from typing import List, Dict, Any, Optional
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from ..services.base import CloudService, ServiceError, AuthenticationError


# Google Drive API scopes
SCOPES = ['https://www.googleapis.com/auth/drive']


class GoogleDriveService(CloudService):
    """Google Drive cloud storage service."""

    # Cache configuration
    CACHE_TTL = 300  # 5 minutes

    def __init__(
        self,
        access_token: Optional[str] = None,
        credentials_path: Optional[str] = None,
        oauth_token_path: Optional[str] = None,
        use_oauth: bool = False
    ):
        """
        Initialize Google Drive service.

        Args:
            access_token: OAuth access token (not used with service account)
            credentials_path: Path to service account JSON file
            oauth_token_path: Path to OAuth token JSON file
            use_oauth: If True, use OAuth instead of service account
        """
        super().__init__(access_token)
        self.credentials_path = credentials_path or os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        self.oauth_token_path = oauth_token_path
        self.use_oauth = use_oauth
        self._service = None
        self._cache = {}  # Simple cache: {query_key: (timestamp, data)}
        self._page_size = 100  # Default page size for pagination

    def _get_oauth_credentials(self) -> Optional[Credentials]:
        """Load and refresh OAuth credentials from token file."""
        if not self.oauth_token_path or not os.path.exists(self.oauth_token_path):
            return None

        with open(self.oauth_token_path) as f:
            token_data = json.load(f)

        creds = Credentials(
            token=token_data.get('token'),
            refresh_token=token_data.get('refresh_token'),
            token_uri=token_data.get('token_uri'),
            client_id=token_data.get('client_id'),
            client_secret=token_data.get('client_secret'),
            scopes=token_data.get('scopes')
        )

        # Refresh if expired
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Save refreshed token
            new_token_data = {
                'token': creds.token,
                'refresh_token': creds.refresh_token,
                'token_uri': creds.token_uri,
                'client_id': creds.client_id,
                'client_secret': creds.client_secret,
                'scopes': list(creds.scopes) if creds.scopes else [],
                'expiry': creds.expiry.isoformat() + 'Z' if creds.expiry else None
            }
            with open(self.oauth_token_path, 'w') as f:
                json.dump(new_token_data, f)

        return creds

    @property
    def service(self):
        """Lazy-load the Google Drive service."""
        if self._service is None:
            creds = None

            # Try OAuth first if enabled
            if self.use_oauth and self.oauth_token_path:
                creds = self._get_oauth_credentials()

            # Fall back to service account
            if creds is None and self.credentials_path:
                if os.path.exists(self.credentials_path):
                    creds = service_account.Credentials.from_service_account_file(
                        self.credentials_path,
                        scopes=SCOPES
                    )

            if creds is None:
                raise AuthenticationError(
                    "Google credentials not found. "
                    "Configure OAuth token or service account."
                )

            self._service = build('drive', 'v3', credentials=creds)
        return self._service

    def _get_cache_key(self, folder_id: Optional[str], query: str, limit: int) -> str:
        """Generate cache key for list_files."""
        return f"{folder_id}:{query}:{limit}"

    def _get_from_cache(self, cache_key: str) -> Optional[List[Dict[str, Any]]]:
        """Get data from cache if not expired."""
        if cache_key in self._cache:
            timestamp, data = self._cache[cache_key]
            if time.time() - timestamp < self.CACHE_TTL:
                return data
        return None

    def _set_cache(self, cache_key: str, data: List[Dict[str, Any]]):
        """Store data in cache."""
        self._cache[cache_key] = (time.time(), data)

    def clear_cache(self):
        """Clear the file list cache."""
        self._cache.clear()

    def is_authenticated(self) -> bool:
        """Check if Google Drive is authenticated via OAuth or service account."""
        # Check OAuth token
        if self.use_oauth and self.oauth_token_path:
            if os.path.exists(self.oauth_token_path):
                return True
        # Check service account
        if self.credentials_path and os.path.exists(self.credentials_path):
            return True
        return False

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
        List files in Google Drive with caching and pagination.

        Args:
            folder_id: Parent folder ID to list from. None for root.
            limit: Maximum number of files to return
            **kwargs: Additional parameters (query, orderBy, use_cache, etc.)

        Returns:
            List of file metadata dictionaries

        Raises:
            ServiceError: If listing fails
        """
        try:
            # Check cache first
            use_cache = kwargs.get('use_cache', True)
            query = kwargs.get('query', '')
            cache_key = self._get_cache_key(folder_id, query, limit)

            if use_cache:
                cached_data = self._get_from_cache(cache_key)
                if cached_data is not None:
                    return cached_data[:limit]  # Return cached data, respecting limit

            # Build query
            if folder_id:
                query = f"'{folder_id}' in parents"
                if kwargs.get('query'):
                    query = f"({query}) and ({kwargs['query']})"

            # Fetch files with pagination
            all_files = []
            page_token = None

            while len(all_files) < limit:
                results = self.service.files().list(
                    pageSize=min(self._page_size, limit - len(all_files)),
                    q=query,
                    fields="nextPageToken, files(id, name, mimeType, size, parents, createdTime, modifiedTime)",
                    orderBy=kwargs.get('orderBy', 'name'),
                    pageToken=page_token
                ).execute()

                items = results.get('files', [])
                all_files.extend(items)

                # Check if we have more pages
                page_token = results.get('nextPageToken')
                if not page_token or len(all_files) >= limit:
                    break

            # Cache the results
            if use_cache:
                self._set_cache(cache_key, all_files)

            return all_files[:limit]

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
