"""
Tests for CLI commands (upload, sync, compare).
"""
import os
import pytest
from click.testing import CliRunner
from omnidrive.cli import cli


class TestCLICommands:
    """Test CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_upload_command_help(self):
        """Test upload command help."""
        result = self.runner.invoke(cli, ['upload', '--help'])
        assert result.exit_code == 0
        assert 'Upload a file' in result.output

    def test_upload_requires_file(self):
        """Test upload requires existing file."""
        result = self.runner.invoke(cli, ['upload', '/nonexistent/file.txt', 'google'])
        assert result.exit_code != 0
        assert 'does not exist' in result.output

    def test_sync_command_help(self):
        """Test sync command help."""
        result = self.runner.invoke(cli, ['sync', '--help'])
        assert result.exit_code == 0
        assert 'Sync files' in result.output

    def test_sync_same_source_target(self):
        """Test sync rejects same source and target."""
        result = self.runner.invoke(cli, ['sync', 'google', 'google'])
        assert 'must be different' in result.output

    def test_compare_command_help(self):
        """Test compare command help."""
        result = self.runner.invoke(cli, ['compare', '--help'])
        assert result.exit_code == 0
        assert 'Compare files' in result.output

    def test_compare_same_services(self):
        """Test compare rejects same services."""
        result = self.runner.invoke(cli, ['compare', 'google', 'google'])
        assert 'must be different' in result.output

    def test_list_command(self):
        """Test list command."""
        result = self.runner.invoke(cli, ['list', '--help'])
        assert result.exit_code == 0
        assert 'list' in result.output.lower()

    def test_download_command(self):
        """Test download command."""
        result = self.runner.invoke(cli, ['download', '--help'])
        assert result.exit_code == 0
        assert 'Download' in result.output

    def test_auth_command(self):
        """Test auth command."""
        result = self.runner.invoke(cli, ['auth', '--help'])
        assert result.exit_code == 0
        assert 'Authenticate' in result.output


class TestHelperFunctions:
    """Test helper functions in CLI."""

    def test_format_size(self):
        """Test file size formatting."""
        from omnidrive.cli import _format_size

        assert _format_size(100) == "100.0 B"
        assert _format_size(1024) == "1.0 KB"
        assert _format_size(1024 * 1024) == "1.0 MB"
        assert _format_size(1024 * 1024 * 1024) == "1.0 GB"
        assert _format_size(None) == ""
        assert _format_size(0) == "0.0 B"

    def test_get_file_icon(self):
        """Test file icon selection."""
        from omnidrive.cli import _get_file_icon

        assert _get_file_icon('application/vnd.google-apps.folder') == "📁"
        assert _get_file_icon('application/pdf') == "📕"
        assert _get_file_icon('image/jpeg') == "🖼️ "
        assert _get_file_icon('video/mp4') == "🎬"
        assert _get_file_icon('audio/mp3') == "🎵"
        assert _get_file_icon('application/msword') == "📘"
        assert _get_file_icon(None) == "📄"
