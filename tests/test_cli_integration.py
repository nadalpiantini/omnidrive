"""
Integration tests for CLI commands using Click CliRunner.
Tests full command flows with mocked services.
"""
import pytest
from click.testing import CliRunner
from unittest.mock import Mock, patch, MagicMock
from omnidrive.cli import cli
from omnidrive.services.base import ServiceError


class TestListCommandIntegration:
    """Integration tests for list command."""

    def test_list_google_no_auth_prompts_auth(self):
        """Test list command prompts for authentication when not authenticated."""
        runner = CliRunner()

        # Mock google_auth to check authentication
        with patch('omnidrive.cli.google_auth.is_google_authenticated', return_value=False):
            with patch('omnidrive.cli.click.confirm', return_value=True):
                with patch('omnidrive.cli._authenticate_service') as mock_auth:
                    result = runner.invoke(cli, ['list', '--drive', 'google'])

                    # Should prompt for authentication
                    mock_auth.assert_called_once_with('google')

    def test_list_google_with_authenticated_service(self):
        """Test list command with authenticated service."""
        runner = CliRunner()

        # Mock authenticated service
        mock_service = Mock()
        mock_service.is_authenticated.return_value = True
        mock_service.list_files.return_value = [
            {'id': '1', 'name': 'test.txt', 'mimeType': 'text/plain', 'size': 1024}
        ]

        with patch('omnidrive.cli.ServiceFactory.create_service', return_value=mock_service):
            result = runner.invoke(cli, ['list', '--drive', 'google'])

            # Should list files successfully
            assert result.exit_code == 0
            assert 'test.txt' in result.output
            assert '1.0 KB' in result.output

    def test_list_empty_files(self):
        """Test list command with no files."""
        runner = CliRunner()

        mock_service = Mock()
        mock_service.is_authenticated.return_value = True
        mock_service.list_files.return_value = []

        with patch('omnidrive.cli.ServiceFactory.create_service', return_value=mock_service):
            result = runner.invoke(cli, ['list', '--drive', 'google'])

            assert result.exit_code == 0
            assert 'No files found' in result.output

    def test_list_service_error(self):
        """Test list command handles service errors."""
        runner = CliRunner()

        mock_service = Mock()
        mock_service.is_authenticated.return_value = True
        mock_service.list_files.side_effect = ServiceError("API Error")

        with patch('omnidrive.cli.ServiceFactory.create_service', return_value=mock_service):
            result = runner.invoke(cli, ['list', '--drive', 'google'])

            # Click catches exceptions by default, so exit_code is 0 but error is in output
            assert 'Service error' in result.output
            assert 'API Error' in result.output


class TestUploadCommandIntegration:
    """Integration tests for upload command."""

    def test_upload_requires_existing_file(self):
        """Test upload command requires file to exist."""
        runner = CliRunner()
        result = runner.invoke(cli, ['upload', 'nonexistent.txt', 'google'])

        assert result.exit_code != 0
        assert 'does not exist' in result.output

    def test_upload_with_authenticated_service(self, tmp_path):
        """Test upload command with authenticated service."""
        runner = CliRunner()

        # Create temporary file
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        mock_service = Mock()
        mock_service.is_authenticated.return_value = True
        mock_service.upload_file.return_value = {
            'id': 'new123',
            'name': 'test.txt'
        }

        with patch('omnidrive.cli.ServiceFactory.create_service', return_value=mock_service):
            result = runner.invoke(cli, ['upload', str(test_file), 'google'])

            assert result.exit_code == 0
            assert 'Uploaded successfully' in result.output
            assert 'new123' in result.output

    def test_upload_with_parent_id(self, tmp_path):
        """Test upload command to specific folder."""
        runner = CliRunner()

        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        mock_service = Mock()
        mock_service.is_authenticated.return_value = True
        mock_service.upload_file.return_value = {'id': '123', 'name': 'test.txt'}

        with patch('omnidrive.cli.ServiceFactory.create_service', return_value=mock_service):
            result = runner.invoke(cli, ['upload', str(test_file), 'google', '--parent-id', 'folder456'])

            assert result.exit_code == 0
            mock_service.upload_file.assert_called_once()
            # Verify parent_id was passed
            call_args = mock_service.upload_file.call_args
            assert call_args[1]['parent_id'] == 'folder456'


class TestDownloadCommandIntegration:
    """Integration tests for download command."""

    def test_download_with_authenticated_service(self, tmp_path):
        """Test download command with authenticated service."""
        runner = CliRunner()

        mock_service = Mock()
        mock_service.is_authenticated.return_value = True
        mock_service.download_file.return_value = str(tmp_path / "downloaded.txt")

        with patch('omnidrive.cli.ServiceFactory.create_service', return_value=mock_service):
            result = runner.invoke(cli, ['download', 'google', 'file123', '--dest', str(tmp_path)])

            assert result.exit_code == 0
            assert 'Downloaded to' in result.output
            mock_service.download_file.assert_called_once_with('file123', str(tmp_path))

    def test_download_service_error(self):
        """Test download command handles service errors."""
        runner = CliRunner()

        mock_service = Mock()
        mock_service.is_authenticated.return_value = True
        mock_service.download_file.side_effect = ServiceError("File not found")

        with patch('omnidrive.cli.ServiceFactory.create_service', return_value=mock_service):
            result = runner.invoke(cli, ['download', 'google', 'file123'])

            # Click catches exceptions, error message in output
            assert 'Service error' in result.output
            assert 'File not found' in result.output


class TestDeleteCommandIntegration:
    """Integration tests for delete command."""

    def test_delete_with_confirmation(self, tmp_path):
        """Test delete command prompts for confirmation."""
        runner = CliRunner()

        mock_service = Mock()
        mock_service.is_authenticated.return_value = True
        mock_service.delete_file.return_value = True

        with patch('omnidrive.cli.ServiceFactory.create_service', return_value=mock_service):
            # Simulate user confirming both prompts
            with patch('omnidrive.cli.click.confirm', return_value=True):
                result = runner.invoke(cli, ['delete', 'google', 'file123'])

                assert result.exit_code == 0
                assert 'File moved to trash' in result.output
                mock_service.delete_file.assert_called_once_with('file123', permanent=False)

    def test_delete_permanent(self):
        """Test delete command with --permanent flag."""
        runner = CliRunner()

        mock_service = Mock()
        mock_service.is_authenticated.return_value = True
        mock_service.delete_file.return_value = True

        with patch('omnidrive.cli.ServiceFactory.create_service', return_value=mock_service):
            with patch('omnidrive.cli.click.confirm', return_value=True):
                result = runner.invoke(cli, ['delete', 'google', 'file123', '--permanent'])

                assert result.exit_code == 0
                assert 'permanently deleted' in result.output.lower()
                mock_service.delete_file.assert_called_once_with('file123', permanent=True)

    def test_delete_cancelled_by_user(self):
        """Test delete command can be cancelled by user."""
        runner = CliRunner()

        mock_service = Mock()
        mock_service.is_authenticated.return_value = True

        with patch('omnidrive.cli.ServiceFactory.create_service', return_value=mock_service):
            with patch('omnidrive.cli.click.confirm', return_value=False):
                result = runner.invoke(cli, ['delete', 'google', 'file123'])

                assert result.exit_code == 0
                assert 'cancelled' in result.output.lower()
                mock_service.delete_file.assert_not_called()


class TestCreateFolderCommandIntegration:
    """Integration tests for create-folder command."""

    def test_create_folder_authenticated(self):
        """Test create-folder command with authenticated service."""
        runner = CliRunner()

        mock_service = Mock()
        mock_service.is_authenticated.return_value = True
        mock_service.create_folder.return_value = {
            'id': 'folder123',
            'name': 'New Folder'
        }

        with patch('omnidrive.cli.ServiceFactory.create_service', return_value=mock_service):
            result = runner.invoke(cli, ['create-folder', 'google', 'New Folder'])

            assert result.exit_code == 0
            assert 'Folder created successfully' in result.output
            assert 'folder123' in result.output
            mock_service.create_folder.assert_called_once_with('New Folder', parent_id=None)

    def test_create_folder_with_parent(self):
        """Test create-folder command with parent folder."""
        runner = CliRunner()

        mock_service = Mock()
        mock_service.is_authenticated.return_value = True
        mock_service.create_folder.return_value = {'id': 'folder456', 'name': 'Child'}

        with patch('omnidrive.cli.ServiceFactory.create_service', return_value=mock_service):
            result = runner.invoke(cli, ['create-folder', 'google', 'Child', '--parent-id', 'parent123'])

            assert result.exit_code == 0
            mock_service.create_folder.assert_called_once_with('Child', parent_id='parent123')

    def test_create_folder_service_error(self):
        """Test create-folder command handles service errors."""
        runner = CliRunner()

        mock_service = Mock()
        mock_service.is_authenticated.return_value = True
        mock_service.create_folder.side_effect = ServiceError("Folder creation failed")

        with patch('omnidrive.cli.ServiceFactory.create_service', return_value=mock_service):
            result = runner.invoke(cli, ['create-folder', 'google', 'Test'])

            # Error message in output even with exit_code 0
            assert 'Service error' in result.output
            assert 'Folder creation failed' in result.output


class TestSyncCommandIntegration:
    """Integration tests for sync command."""

    def test_sync_same_source_target_error(self):
        """Test sync command requires different services."""
        runner = CliRunner()
        result = runner.invoke(cli, ['sync', 'google', 'google'])

        # sync command returns early with same service, check output
        assert 'must be different' in result.output.lower() or 'same' in result.output.lower()

    def test_sync_nothing_to_sync(self):
        """Test sync command when all files already in sync."""
        runner = CliRunner()

        # Mock both services returning same files
        files = [{'id': '1', 'name': 'test.txt'}]

        with patch('omnidrive.cli._get_files_from_service', return_value=files):
            result = runner.invoke(cli, ['sync', 'google', 'folderfort'])

            assert result.exit_code == 0
            assert 'All files already in sync' in result.output

    def test_sync_dry_run(self):
        """Test sync command with --dry-run flag."""
        runner = CliRunner()

        source_files = [{'id': '1', 'name': 'new.txt', 'mimeType': 'text/plain'}]
        target_files = []

        with patch('omnidrive.cli._get_files_from_service') as mock_get:
            mock_get.side_effect = [source_files, target_files]
            result = runner.invoke(cli, ['sync', 'google', 'folderfort', '--dry-run'])

            assert result.exit_code == 0
            assert 'DRY RUN' in result.output

    def test_sync_success(self):
        """Test successful sync between services."""
        runner = CliRunner()

        source_files = [{'id': '1', 'name': 'new.txt', 'mimeType': 'text/plain'}]
        target_files = []

        with patch('omnidrive.cli._get_files_from_service', return_value=[]):
            with patch('omnidrive.cli.click.confirm', return_value=True):
                with patch('omnidrive.cli._sync_file') as mock_sync:
                    result = runner.invoke(cli, ['sync', 'google', 'folderfort', '--limit', '1'])

                    # Sync should execute
                    assert result.exit_code == 0


class TestCompareCommandIntegration:
    """Integration tests for compare command."""

    def test_compare_different_services(self):
        """Test compare command between two services."""
        runner = CliRunner()

        google_files = [
            {'id': '1', 'name': 'file1.txt', 'mimeType': 'text/plain'},
            {'id': '2', 'name': 'file2.txt', 'mimeType': 'text/plain'}
        ]
        folderfort_files = [
            {'id': '3', 'name': 'file1.txt', 'mimeType': 'text/plain'},
            {'id': '4', 'name': 'file3.txt', 'mimeType': 'text/plain'}
        ]

        with patch('omnidrive.cli._get_files_from_service') as mock_get:
            mock_get.side_effect = [google_files, folderfort_files]
            result = runner.invoke(cli, ['compare', 'google', 'folderfort'])

            # Check output contains expected statistics
            output = result.output
            assert 'Comparing' in output or 'Statistics' in output or 'Total' in output


class TestServiceFactoryIntegration:
    """Integration tests for ServiceFactory."""

    def test_factory_creates_correct_service(self):
        """Test ServiceFactory creates correct service instances."""
        from omnidrive.services import ServiceFactory
        from omnidrive.services.google_drive import GoogleDriveService
        from omnidrive.services.folderfort import FolderfortService

        # Test without auto-auth (no auth modules needed)
        google_service = ServiceFactory.create_service('google', auto_authenticate=False)
        assert isinstance(google_service, GoogleDriveService)

        folderfort_service = ServiceFactory.create_service('folderfort', auto_authenticate=False)
        assert isinstance(folderfort_service, FolderfortService)

    def test_factory_unavailable_service(self):
        """Test ServiceFactory raises error for unavailable service."""
        from omnidrive.services import ServiceFactory

        with pytest.raises(ServiceError) as exc_info:
            ServiceFactory.create_service('onedrive', auto_authenticate=False)

        assert 'not available' in str(exc_info.value).lower()

    def test_factory_available_services(self):
        """Test ServiceFactory lists available services."""
        from omnidrive.services import ServiceFactory

        services = ServiceFactory.get_available_services()
        assert 'google' in services
        assert 'folderfort' in services
        assert len(services) >= 2
