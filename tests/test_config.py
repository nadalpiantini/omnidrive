"""
Tests for configuration management.
"""
import os
import json
import pytest
from omnidrive.config import (
    load_config,
    save_config,
    get_config_value,
    set_config_value,
    CONFIG_PATH
)


@pytest.fixture
def clean_config():
    """Ensure clean config state before/after tests."""
    # Save original config if it exists
    original_config = None
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            original_config = f.read()

    yield

    # Restore original config or delete test config
    if original_config:
        with open(CONFIG_PATH, 'w') as f:
            f.write(original_config)
    elif os.path.exists(CONFIG_PATH):
        os.remove(CONFIG_PATH)


def test_load_config_empty(clean_config):
    """Test loading config when file doesn't exist."""
    cfg = load_config()
    # Config puede tener valores pre-existentes (Folderfort, etc)
    assert isinstance(cfg, dict)


def test_save_and_load_config(clean_config):
    """Test saving and loading config."""
    test_config = {
        'google_key_path': '/path/to/key.json',
        'folderfort_token': 'test_token'
    }

    save_config(test_config)
    loaded = load_config()

    assert loaded == test_config


def test_get_config_value(clean_config):
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


def test_set_config_value(clean_config):
    """Test setting specific config values."""
    # Set nested value
    set_config_value('google.key_path', '/new/path.json')
    assert get_config_value('google.key_path') == '/new/path.json'

    # Set simple value
    set_config_value('simple', 'value')
    assert get_config_value('simple') == 'value'


def test_set_config_value_preserves_existing(clean_config):
    """Test that set_config_value preserves existing values."""
    # Set initial values
    set_config_value('google.key_path', '/path1.json')
    set_config_value('google.enabled', True)

    # Set new value
    set_config_value('google.key_path', '/path2.json')

    # Check both values exist
    assert get_config_value('google.key_path') == '/path2.json'
    assert get_config_value('google.enabled') is True
