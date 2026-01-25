"""
Tests for Folderfort service.
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from omnidrive.services.folderfort import FolderfortService
from omnidrive.services.base import AuthenticationError, ServiceError


class TestFolderfortService:
    """Test FolderfortService class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = FolderfortService(access_token="test_token")

    def test_initialization(self):
        """Test service initialization."""
        assert self.service.access_token == "test_token"
        assert self.service.service_name == "folderfort"
        assert self.service.is_authenticated()

    def test_initialization_no_token(self):
        """Test initialization without token."""
        service = FolderfortService()
        assert service.access_token is None
        assert not service.is_authenticated()

    def test_get_headers(self):
        """Test getting request headers."""
        headers = self.service._get_headers()
        assert headers["Authorization"] == "Bearer test_token"
        assert headers["Content-Type"] == "application/json"

    def test_get_headers_no_token(self):
        """Test getting headers without token raises error."""
        service = FolderfortService()
        with pytest.raises(AuthenticationError) as exc_info:
            service._get_headers()
        assert "Not authenticated" in str(exc_info.value)

    @patch('omnidrive.services.folderfort.requests.post')
    def test_authenticate_success(self, mock_post):
        """Test successful authentication."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'status': 'success',
            'user': {
                'access_token': 'new_token'
            }
        }
        mock_post.return_value = mock_response

        service = FolderfortService()
        token = service.authenticate(email="test@example.com", password="password")

        assert token == "new_token"
        assert service.access_token == "new_token"

    @patch('omnidrive.services.folderfort.requests.post')
    def test_authenticate_failure(self, mock_post):
        """Test authentication failure."""
        mock_response = Mock()
        mock_response.status_code = 422
        mock_response.json.return_value = {
            'status': 'error',
            'errors': {
                'email': 'Invalid email'
            }
        }
        mock_post.return_value = mock_response

        service = FolderfortService()
        with pytest.raises(AuthenticationError):
            service.authenticate(email="invalid", password="wrong")

    @patch('omnidrive.services.folderfort.requests.get')
    def test_list_files_success(self, mock_get):
        """Test successful file listing."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'id': '1',
                'name': 'file.txt',
                'type': 'text',
                'file_size': 1024
            }
        ]
        mock_get.return_value = mock_response

        files = self.service.list_files(limit=10)

        assert len(files) == 1
        assert files[0]['id'] == '1'
        assert files[0]['name'] == 'file.txt'

    @patch('omnidrive.services.folderfort.requests.get')
    def test_list_files_unauthorized(self, mock_get):
        """Test listing files with unauthorized access."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        with pytest.raises(AuthenticationError):
            self.service.list_files()

    @patch('builtins.open', create=True)
    @patch('omnidrive.services.folderfort.os.path.exists')
    @patch('omnidrive.services.folderfort.requests.post')
    def test_upload_file_success(self, mock_post, mock_exists, mock_open):
        """Test successful file upload."""
        # Mock file exists check
        mock_exists.return_value = True

        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            'status': 'success',
            'fileEntry': {
                'id': '2',
                'name': 'uploaded.txt'
            }
        }
        mock_post.return_value = mock_response

        # Mock file operations
        mock_file = MagicMock()
        mock_file.__enter__ = Mock(return_value=mock_file)
        mock_file.__exit__ = Mock(return_value=False)
        mock_open.return_value = mock_file

        result = self.service.upload_file('/path/to/file.txt')

        assert result['id'] == '2'
        assert result['name'] == 'uploaded.txt'

    @patch('omnidrive.services.folderfort.requests.delete')
    def test_delete_file_success(self, mock_delete):
        """Test successful file deletion."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'status': 'success'
        }
        mock_delete.return_value = mock_response

        result = self.service.delete_file('1')

        assert result is True

    @patch('omnidrive.services.folderfort.requests.post')
    def test_create_folder_success(self, mock_post):
        """Test successful folder creation."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'status': 'success',
            'folder': {
                'id': 'folder1',
                'name': 'New Folder'
            }
        }
        mock_post.return_value = mock_response

        result = self.service.create_folder('New Folder')

        assert result['id'] == 'folder1'
        assert result['name'] == 'New Folder'
