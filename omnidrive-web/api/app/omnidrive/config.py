"""
Configuration management for OmniDrive CLI.
Handles loading and saving configuration from local files.
"""
import os
import json
from pathlib import Path
from typing import Dict, Any


# Default configuration path
CONFIG_DIR = os.path.expanduser("~/.omnidrive")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")


def load_config() -> Dict[str, Any]:
    """
    Load configuration from local file.

    Returns:
        Dict with configuration data. Empty dict if file doesn't exist.
    """
    if not os.path.exists(CONFIG_PATH):
        return {}
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)


def save_config(cfg: Dict[str, Any]) -> None:
    """
    Save configuration to local file.

    Args:
        cfg: Configuration dictionary to save.
    """
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(cfg, f, indent=2)


def get_config_value(key: str, default: Any = None) -> Any:
    """
    Get a specific configuration value.

    Args:
        key: Configuration key (supports nested keys with dot notation)
        default: Default value if key doesn't exist

    Returns:
        Configuration value or default
    """
    cfg = load_config()
    keys = key.split('.')

    value = cfg
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return default

    return value


def set_config_value(key: str, value: Any) -> None:
    """
    Set a specific configuration value.

    Args:
        key: Configuration key (supports nested keys with dot notation)
        value: Value to set
    """
    cfg = load_config()
    keys = key.split('.')

    # Navigate to the parent of the final key
    current = cfg
    for k in keys[:-1]:
        if k not in current:
            current[k] = {}
        current = current[k]

    # Set the final key
    current[keys[-1]] = value

    save_config(cfg)
