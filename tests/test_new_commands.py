"""
Tests for new CLI commands: delete and create-folder.
"""
import pytest
from click.testing import CliRunner
from omnidrive.cli import cli


class TestDeleteCommand:
    """Test suite for delete command."""

    def test_delete_command_help(self):
        """Test delete command help text."""
        runner = CliRunner()
        result = runner.invoke(cli, ['delete', '--help'])
        assert result.exit_code == 0
        assert 'Delete a file' in result.output
        assert '--permanent' in result.output

    def test_delete_requires_drive(self):
        """Test delete requires drive argument."""
        runner = CliRunner()
        result = runner.invoke(cli, ['delete'])
        assert result.exit_code != 0
        assert 'Missing argument' in result.output

    def test_delete_requires_file_id(self):
        """Test delete requires file_id argument."""
        runner = CliRunner()
        result = runner.invoke(cli, ['delete', 'google'])
        assert result.exit_code != 0
        assert 'Missing argument' in result.output


class TestCreateFolderCommand:
    """Test suite for create-folder command."""

    def test_create_folder_command_help(self):
        """Test create-folder command help text."""
        runner = CliRunner()
        result = runner.invoke(cli, ['create-folder', '--help'])
        assert result.exit_code == 0
        assert 'Create a new folder' in result.output
        assert '--parent-id' in result.output

    def test_create_folder_requires_drive(self):
        """Test create-folder requires drive argument."""
        runner = CliRunner()
        result = runner.invoke(cli, ['create-folder'])
        assert result.exit_code != 0
        assert 'Missing argument' in result.output

    def test_create_folder_requires_folder_name(self):
        """Test create-folder requires folder_name argument."""
        runner = CliRunner()
        result = runner.invoke(cli, ['create-folder', 'google'])
        assert result.exit_code != 0
        assert 'Missing argument' in result.output

    def test_create_folder_with_parent_id_option(self):
        """Test create-folder accepts parent-id option."""
        runner = CliRunner()
        # Just verify arguments are accepted - actual functionality tested in integration tests
        result = runner.invoke(cli, ['create-folder', '--help'])
        assert result.exit_code == 0
        assert '--parent-id' in result.output


class TestServiceFactory:
    """Test ServiceFactory integration."""

    def test_service_factory_has_services(self):
        """Test ServiceFactory is properly configured."""
        from omnidrive.services import ServiceFactory

        services = ServiceFactory.get_available_services()
        assert 'google' in services
        assert 'folderfort' in services
        assert len(services) >= 2

    def test_drives_list_matches_factory(self):
        """Test DRIVES constant matches ServiceFactory."""
        from omnidrive.cli import DRIVES
        from omnidrive.services import ServiceFactory

        factory_services = set(ServiceFactory.get_available_services())
        drives_set = set(DRIVES)

        # All drives should be available in factory
        assert drives_set.issubset(factory_services)
