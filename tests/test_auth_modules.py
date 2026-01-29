"""
Tests for authentication modules to improve coverage from 16-25% to 40%+.
"""
import pytest
from unittest.mock import patch
import os


class TestGoogleAuth:
    """Tests for Google authentication module."""

    def test_is_google_authenticated_false(self):
        """Test is_google_authenticated returns False when no config."""
        from omnidrive.auth import google

        with patch('omnidrive.auth.google.load_config', return_value={}):
            result = google.is_google_authenticated()
            assert result is False


class TestFolderfortAuth:
    """Tests for Folderfort authentication module."""

    def test_is_folderfort_authenticated_false_no_token(self):
        """Test is_folderfort_authenticated returns False without token."""
        from omnidrive.auth import folderfort

        with patch('omnidrive.auth.folderfort.load_config', return_value={}):
            result = folderfort.is_folderfort_authenticated()
            assert result is False

    def test_get_folderfort_token_success(self):
        """Test get_folderfort_token retrieves token."""
        from omnidrive.auth import folderfort

        with patch('omnidrive.auth.folderfort.load_config', return_value={'folderfort_token': 'secret123'}):
            result = folderfort.get_folderfort_token()
            assert result == 'secret123'
