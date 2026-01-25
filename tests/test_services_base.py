"""
Tests for CloudService base class.
"""
import pytest
from omnidrive.services.base import (
    CloudService,
    ServiceError,
    AuthenticationError
)


# Mock implementation for testing
class MockCloudService(CloudService):
    """Mock implementation of CloudService for testing."""

    def authenticate(self, **kwargs):
        self.access_token = "mock_token"
        return self.access_token

    def list_files(self, folder_id=None, limit=100, **kwargs):
        return [
            {"id": "1", "name": "file1.txt"},
            {"id": "2", "name": "file2.pdf"}
        ]

    def upload_file(self, file_path, parent_id=None, **kwargs):
        return {"id": "3", "name": "uploaded.txt"}

    def download_file(self, file_id, dest_path, **kwargs):
        return dest_path

    def delete_file(self, file_id, permanent=False, **kwargs):
        return True

    def create_folder(self, name, parent_id=None, **kwargs):
        return {"id": "folder1", "name": name}


def test_cloud_service_initialization():
    """Test CloudService initialization."""
    service = MockCloudService()
    assert service.service_name == "mock_cloud"
    assert service.access_token is None
    assert not service.is_authenticated()

    service_with_token = MockCloudService(access_token="token")
    assert service_with_token.access_token == "token"
    assert service_with_token.is_authenticated()


def test_cloud_service_authenticate():
    """Test authentication."""
    service = MockCloudService()
    token = service.authenticate()
    assert token == "mock_token"
    assert service.is_authenticated()


def test_cloud_service_list_files():
    """Test listing files."""
    service = MockCloudService()
    files = service.list_files(limit=10)

    assert len(files) == 2
    assert files[0]["id"] == "1"
    assert files[0]["name"] == "file1.txt"


def test_cloud_service_upload_file():
    """Test uploading file."""
    service = MockCloudService()
    result = service.upload_file("/path/to/file.txt")

    assert result["id"] == "3"
    assert result["name"] == "uploaded.txt"


def test_cloud_service_download_file():
    """Test downloading file."""
    service = MockCloudService()
    dest_path = service.download_file("file_id", "/tmp/file.txt")

    assert dest_path == "/tmp/file.txt"


def test_cloud_service_delete_file():
    """Test deleting file."""
    service = MockCloudService()
    result = service.delete_file("file_id")

    assert result is True


def test_cloud_service_create_folder():
    """Test creating folder."""
    service = MockCloudService()
    folder = service.create_folder("New Folder")

    assert folder["id"] == "folder1"
    assert folder["name"] == "New Folder"


def test_service_error():
    """Test ServiceError exception."""
    with pytest.raises(ServiceError) as exc_info:
        raise ServiceError("Test error", service_name="test")

    assert "Test error" in str(exc_info.value)
    assert "test" in str(exc_info.value)


def test_authentication_error():
    """Test AuthenticationError exception."""
    with pytest.raises(AuthenticationError):
        raise AuthenticationError("Auth failed", service_name="google")
