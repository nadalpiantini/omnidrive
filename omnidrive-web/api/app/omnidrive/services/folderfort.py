"""
Folderfort service implementation.
"""
import os
import requests
from typing import List, Dict, Any, Optional
from ..services.base import CloudService, ServiceError, AuthenticationError


class FolderfortService(CloudService):
    """Folderfort cloud storage service."""

    BASE_URL = "https://na3.folderfort.com/api/v1"

    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize Folderfort service.

        Args:
            access_token: Folderfort API access token
        """
        super().__init__(access_token)
        self.session = requests.Session()

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication."""
        if not self.access_token:
            raise AuthenticationError(
                "Not authenticated with Folderfort",
                service_name="folderfort"
            )

        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def authenticate(self, email: str = None, password: str = None, **kwargs) -> str:
        """
        Authenticate with Folderfort using email and password.

        Args:
            email: Folderfort account email
            password: Folderfort account password
            **kwargs: Additional parameters (token_name)

        Returns:
            Access token

        Raises:
            AuthenticationError: If authentication fails
        """
        if not email or not password:
            raise AuthenticationError(
                "Email and password required for Folderfort authentication",
                service_name="folderfort"
            )

        token_name = kwargs.get('token_name', 'omnidrive-cli')

        try:
            response = requests.post(
                f"{self.BASE_URL}/auth/login",
                json={
                    "email": email,
                    "password": password,
                    "token_name": token_name
                }
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    self.access_token = data['user']['access_token']
                    return self.access_token
                else:
                    raise AuthenticationError(
                        f"Authentication failed: {data.get('message', 'Unknown error')}",
                        service_name="folderfort"
                    )
            elif response.status_code == 422:
                errors = response.json().get('errors', {})
                error_msg = ", ".join(errors.values())
                raise AuthenticationError(
                    f"Validation error: {error_msg}",
                    service_name="folderfort"
                )
            else:
                raise AuthenticationError(
                    f"HTTP {response.status_code}: {response.text}",
                    service_name="folderfort"
                )

        except requests.RequestException as e:
            raise AuthenticationError(
                f"Network error: {e}",
                service_name="folderfort"
            )

    def list_files(
        self,
        folder_id: Optional[str] = None,
        limit: int = 100,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        List files in Folderfort.

        Args:
            folder_id: Parent folder ID to list from. None for root.
            limit: Maximum number of files to return
            **kwargs: Additional parameters (deletedOnly, starredOnly, etc.)

        Returns:
            List of file metadata dictionaries

        Raises:
            ServiceError: If listing fails
        """
        try:
            params = {"perPage": limit}

            # Add optional filters
            if folder_id:
                params["parentIds"] = [folder_id]

            if kwargs.get('deleted_only'):
                params["deletedOnly"] = True

            if kwargs.get('starred_only'):
                params["starredOnly"] = True

            if kwargs.get('recent_only'):
                params["recentOnly"] = True

            if kwargs.get('shared_only'):
                params["sharedOnly"] = True

            if kwargs.get('query'):
                params["query"] = kwargs['query']

            if kwargs.get('type'):
                params["type"] = kwargs['type']

            response = requests.get(
                f"{self.BASE_URL}/drive/file-entries",
                headers=self._get_headers(),
                params=params
            )

            if response.status_code == 200:
                data = response.json()
                # API returns paginated response with 'data' key
                if isinstance(data, dict) and 'data' in data:
                    return data['data']
                return data
            elif response.status_code == 401:
                raise AuthenticationError(
                    "Invalid or expired access token",
                    service_name="folderfort"
                )
            else:
                raise ServiceError(
                    f"Failed to list files: HTTP {response.status_code}",
                    service_name="folderfort"
                )

        except requests.RequestException as e:
            raise ServiceError(
                f"Network error: {e}",
                service_name="folderfort"
            )

    def upload_file(
        self,
        file_path: str,
        parent_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Upload a file to Folderfort.

        Args:
            file_path: Local path to file to upload
            parent_id: Parent folder ID. None for root.
            **kwargs: Additional parameters (relativePath)

        Returns:
            Uploaded file metadata

        Raises:
            ServiceError: If upload fails
        """
        if not os.path.exists(file_path):
            raise ServiceError(
                f"File not found: {file_path}",
                service_name="folderfort"
            )

        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}

                data = {}
                if parent_id is not None:
                    data['parentId'] = parent_id

                if kwargs.get('relative_path'):
                    data['relativePath'] = kwargs['relative_path']

                # Don't include Content-Type in headers for multipart upload
                headers = {"Authorization": f"Bearer {self.access_token}"}

                response = requests.post(
                    f"{self.BASE_URL}/uploads",
                    headers=headers,
                    files=files,
                    data=data
                )

            if response.status_code == 201:
                result = response.json()
                if result.get('status') == 'success':
                    return result['fileEntry']
                else:
                    raise ServiceError(
                        f"Upload failed: {result.get('message', 'Unknown error')}",
                        service_name="folderfort"
                    )
            elif response.status_code == 401:
                raise AuthenticationError(
                    "Invalid or expired access token",
                    service_name="folderfort"
                )
            elif response.status_code == 403:
                raise ServiceError(
                    "Insufficient credits for this upload. Please purchase more credits.",
                    service_name="folderfort"
                )
            else:
                raise ServiceError(
                    f"Failed to upload file: HTTP {response.status_code}",
                    service_name="folderfort"
                )

        except requests.RequestException as e:
            raise ServiceError(
                f"Network error: {e}",
                service_name="folderfort"
            )

    def download_file(
        self,
        file_id: str,
        dest_path: str,
        **kwargs
    ) -> str:
        """
        Download a file from Folderfort.

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
            # Get file metadata to determine filename
            file_meta = self._get_file_metadata(file_id)
            filename = file_meta.get('name', file_id)

            # Determine destination path
            if os.path.isdir(dest_path):
                dest_path = os.path.join(dest_path, filename)

            # Get file URL from metadata
            file_url = file_meta.get('url')
            if not file_url:
                raise ServiceError(
                    f"File {file_id} does not have a download URL",
                    service_name="folderfort"
                )

            # Download file
            response = requests.get(
                f"{self.BASE_URL}/{file_url}",
                headers={"Authorization": f"Bearer {self.access_token}"},
                stream=True
            )

            if response.status_code == 200:
                with open(dest_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                return dest_path
            else:
                raise ServiceError(
                    f"Failed to download file: HTTP {response.status_code}",
                    service_name="folderfort"
                )

        except requests.RequestException as e:
            raise ServiceError(
                f"Network error: {e}",
                service_name="folderfort"
            )

    def delete_file(
        self,
        file_id: str,
        permanent: bool = False,
        **kwargs
    ) -> bool:
        """
        Delete a file from Folderfort.

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
            response = requests.delete(
                f"{self.BASE_URL}/file-entries",
                headers=self._get_headers(),
                json={
                    "entryIds": [file_id],
                    "deleteForever": permanent
                }
            )

            if response.status_code == 200:
                result = response.json()
                return result.get('status') == 'success'
            elif response.status_code == 401:
                raise AuthenticationError(
                    "Invalid or expired access token",
                    service_name="folderfort"
                )
            else:
                raise ServiceError(
                    f"Failed to delete file: HTTP {response.status_code}",
                    service_name="folderfort"
                )

        except requests.RequestException as e:
            raise ServiceError(
                f"Network error: {e}",
                service_name="folderfort"
            )

    def create_folder(
        self,
        name: str,
        parent_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a new folder in Folderfort.

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
            data = {"name": name}
            if parent_id is not None:
                data['parentId'] = parent_id

            response = requests.post(
                f"{self.BASE_URL}/folders",
                headers=self._get_headers(),
                json=data
            )

            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    return result['folder']
                else:
                    raise ServiceError(
                        f"Failed to create folder: {result.get('message', 'Unknown error')}",
                        service_name="folderfort"
                    )
            elif response.status_code == 401:
                raise AuthenticationError(
                    "Invalid or expired access token",
                    service_name="folderfort"
                )
            else:
                raise ServiceError(
                    f"Failed to create folder: HTTP {response.status_code}",
                    service_name="folderfort"
                )

        except requests.RequestException as e:
            raise ServiceError(
                f"Network error: {e}",
                service_name="folderfort"
            )

    def _get_file_metadata(self, file_id: str) -> Dict[str, Any]:
        """
        Get metadata for a specific file.

        Args:
            file_id: File ID

        Returns:
            File metadata

        Raises:
            ServiceError: If request fails
        """
        try:
            # For now, we can get this from list_files
            # In a full implementation, Folderfort may have a dedicated endpoint
            files = self.list_files()
            for file in files:
                if str(file.get('id')) == str(file_id):
                    return file

            raise ServiceError(
                f"File {file_id} not found",
                service_name="folderfort"
            )

        except Exception as e:
            raise ServiceError(
                f"Failed to get file metadata: {e}",
                service_name="folderfort"
            )
