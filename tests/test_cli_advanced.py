"""
Advanced CLI tests for index, search, session, and workflow commands.
Tests coverage gaps to reach 70% target.
"""
import pytest
from click.testing import CliRunner
from unittest.mock import Mock, patch, MagicMock
from omnidrive.cli import cli


class TestIndexCommand:
    """Tests for index command."""

    def test_index_without_api_key(self):
        """Test index command handles missing API key."""
        runner = CliRunner()

        with patch.dict('os.environ', {}, clear=False):
            # Remove DEEPSEEK_API_KEY if it exists
            import os
            env = os.environ.copy()
            env.pop('DEEPSEEK_API_KEY', None)

            with patch('os.getenv', return_value=None):
                result = runner.invoke(cli, ['index', 'google'])

                assert 'DEEPSEEK_API_KEY' in result.output or 'not set' in result.output.lower()

    def test_index_with_authenticated_service(self):
        """Test index command with authenticated service."""
        runner = CliRunner()

        mock_service = Mock()
        mock_service.is_authenticated.return_value = True
        mock_service.list_files.return_value = [
            {'id': '1', 'name': 'doc.txt', 'mimeType': 'text/plain'},
            {'id': '2', 'name': 'file.pdf', 'mimeType': 'application/pdf'}
        ]

        with patch.dict('os.environ', {'DEEPSEEK_API_KEY': 'test-key'}):
            with patch('omnidrive.cli.ServiceFactory.create_service', return_value=mock_service):
                result = runner.invoke(cli, ['index', 'google'])

                assert result.exit_code == 0
                assert 'Indexing' in result.output or 'Found' in result.output


class TestSearchCommand:
    """Tests for search command."""

    def test_search_without_api_key(self):
        """Test search command handles missing API key."""
        runner = CliRunner()

        with patch.dict('os.environ', {}, clear=False):
            with patch('os.getenv', return_value=None):
                result = runner.invoke(cli, ['search', 'test query'])

                assert 'DEEPSEEK_API_KEY' in result.output or 'not set' in result.output.lower()

    def test_search_with_results(self):
        """Test search command with results."""
        runner = CliRunner()

        mock_search = Mock()
        mock_search.search.return_value = [
            {
                'document': 'test content',
                'metadata': {'file_name': 'test.txt', 'service': 'google'},
                'distance': 0.3
            }
        ]

        with patch.dict('os.environ', {'DEEPSEEK_API_KEY': 'test-key'}):
            with patch('omnidrive.cli.SemanticSearch', return_value=mock_search):
                result = runner.invoke(cli, ['search', 'test query', '--top-k', '5'])

                assert result.exit_code == 0
                assert 'test.txt' in result.output or 'Relevance' in result.output


class TestSessionCommands:
    """Tests for session management commands."""

    def test_session_save(self):
        """Test session save command."""
        runner = CliRunner()

        mock_memory = Mock()
        mock_memory.write_memory = Mock()

        with patch('omnidrive.cli.get_memory_manager', return_value=mock_memory):
            with patch('omnidrive.cli.google_auth.is_google_authenticated', return_value=True):
                with patch('omnidrive.cli.folderfort_auth.is_folderfort_authenticated', return_value=False):
                    result = runner.invoke(cli, ['session', 'save', 'test-session'])

                    assert result.exit_code == 0
                    assert 'saved' in result.output.lower()
                    mock_memory.write_memory.assert_called_once()

    def test_session_resume_nonexistent(self):
        """Test session resume with nonexistent session."""
        runner = CliRunner()

        mock_memory = Mock()
        mock_memory.read_memory.return_value = None

        with patch('omnidrive.cli.get_memory_manager', return_value=mock_memory):
            result = runner.invoke(cli, ['session', 'resume', 'nonexistent'])

            assert 'not found' in result.output.lower()

    def test_session_list_empty(self):
        """Test session list with no sessions."""
        runner = CliRunner()

        mock_memory = Mock()
        mock_memory.list_memories.return_value = []

        with patch('omnidrive.cli.get_memory_manager', return_value=mock_memory):
            result = runner.invoke(cli, ['session', 'list'])

            assert result.exit_code == 0
            assert 'no saved sessions' in result.output.lower()


class TestWorkflowCommands:
    """Tests for workflow management commands."""

    def test_workflow_list(self):
        """Test workflow list command."""
        runner = CliRunner()

        mock_engine = Mock()
        mock_engine.list_workflows.return_value = [
            {
                'name': 'smart_sync',
                'description': 'Smart sync workflow',
                'steps': ['list', 'compare', 'sync']
            }
        ]

        with patch('omnidrive.cli.get_workflow_engine', return_value=mock_engine):
            result = runner.invoke(cli, ['workflow', 'list'])

            assert result.exit_code == 0
            assert 'smart_sync' in result.output

    def test_workflow_run_success(self):
        """Test workflow run successful execution."""
        runner = CliRunner()

        mock_result = Mock()
        mock_result.status.value = 'completed'
        mock_result.message = 'Workflow completed'

        mock_engine = Mock()
        mock_engine.execute_workflow.return_value = mock_result

        with patch('omnidrive.cli.get_workflow_engine', return_value=mock_engine):
            result = runner.invoke(cli, ['workflow', 'run', 'smart_sync'])

            assert result.exit_code == 0
            assert 'completed' in result.output.lower()

    def test_workflow_run_failure(self):
        """Test workflow run with failure."""
        runner = CliRunner()

        mock_result = Mock()
        mock_result.status.value = 'failed'
        mock_result.message = 'Workflow failed'

        mock_engine = Mock()
        mock_engine.execute_workflow.return_value = mock_result

        with patch('omnidrive.cli.get_workflow_engine', return_value=mock_engine):
            result = runner.invoke(cli, ['workflow', 'run', 'smart_sync'])

            assert 'failed' in result.output.lower()


class TestAuthCommandIntegration:
    """Tests for auth command."""

    def test_auth_google(self):
        """Test auth command for Google."""
        runner = CliRunner()

        with patch('omnidrive.cli.google_auth.authenticate_google') as mock_auth:
            result = runner.invoke(cli, ['auth', 'google'])

            assert result.exit_code == 0
            mock_auth.assert_called_once()

    def test_auth_folderfort(self):
        """Test auth command for Folderfort."""
        runner = CliRunner()

        with patch('omnidrive.cli.folderfort_auth.authenticate_folderfort') as mock_auth:
            result = runner.invoke(cli, ['auth', 'folderfort'])

            assert result.exit_code == 0
            mock_auth.assert_called_once()

    def test_auth_unsupported_service(self):
        """Test auth command with unsupported service."""
        runner = CliRunner()

        result = runner.invoke(cli, ['auth', 'onedrive'])

        # Check output contains appropriate message
        assert 'onedrive' in result.output.lower() or 'not implemented' in result.output.lower()


class TestHelperFunctions:
    """Tests for CLI helper functions."""

    def test_authenticate_service_google(self):
        """Test _authenticate_service for Google."""
        from omnidrive.cli import _authenticate_service

        with patch('omnidrive.cli.google_auth.authenticate_google') as mock_auth:
            _authenticate_service('google')
            mock_auth.assert_called_once()

    def test_authenticate_service_unsupported(self):
        """Test _authenticate_service with unsupported service."""
        from omnidrive.cli import _authenticate_service

        with pytest.raises(Exception):  # ClickException
            _authenticate_service('onedrive')
