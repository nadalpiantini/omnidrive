"""
Tests for configuration management.
"""
import os

import pytest

from omnidrive.config import (
    config_dir,
    config_path,
    get_config_value,
    load_config,
    save_config,
    set_config_value,
)


@pytest.fixture
def temp_config(monkeypatch, tmp_path):
    """Redirect config to a temporary directory."""
    config_root = tmp_path / "omnidrive_config"
    config_root.mkdir()

    def _config_dir():
        return str(config_root)

    def _config_path():
        return str(config_root / "config.json")

    monkeypatch.setattr("omnidrive.config.config_dir", _config_dir)
    monkeypatch.setattr("omnidrive.config.config_path", _config_path)
    monkeypatch.setattr("omnidrive.config.CONFIG_DIR", str(config_root))
    monkeypatch.setattr("omnidrive.config.CONFIG_PATH", str(config_root / "config.json"))

    yield config_root

    # Cleanup: remove temp config file if it exists
    cfg_file = config_root / "config.json"
    if cfg_file.exists():
        cfg_file.unlink()


def test_load_config_empty(temp_config):
    """Test loading config when file doesn't exist."""
    cfg = load_config()
    assert cfg == {}


def test_save_and_load_config(temp_config):
    """Test saving and loading config."""
    test_config = {
        'google_key_path': '/path/to/key.json',
        'folderfort_token': 'test_token'
    }

    save_config(test_config)
    loaded = load_config()

    assert loaded == test_config


def test_get_config_value(temp_config):
    """Test getting specific config values."""
    test_config = {
        'google': {
            'key_path': '/path/to/key.json',
            'enabled': True
        },
        'simple_value': 'test'
    }

    save_config(test_config)

    # Test nested key
    assert get_config_value('google.key_path') == '/path/to/key.json'

    # Test simple key
    assert get_config_value('simple_value') == 'test'

    # Test non-existent key with default
    assert get_config_value('nonexistent', 'default') == 'default'


def test_set_config_value(temp_config):
    """Test setting specific config values."""
    # Set nested value
    set_config_value('google.key_path', '/new/path.json')
    assert get_config_value('google.key_path') == '/new/path.json'

    # Set simple value
    set_config_value('simple', 'value')
    assert get_config_value('simple') == 'value'


def test_set_config_value_preserves_existing(temp_config):
    """Test that set_config_value preserves existing values."""
    # Set initial values
    set_config_value('google.key_path', '/path1.json')
    set_config_value('google.enabled', True)

    # Set new value
    set_config_value('google.key_path', '/path2.json')

    # Check both values exist
    assert get_config_value('google.key_path') == '/path2.json'
    assert get_config_value('google.enabled') is True
