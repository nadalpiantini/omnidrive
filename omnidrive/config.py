"""
Configuration management for OmniDrive CLI.
Handles loading and saving configuration from local files.

Path resolution is lazy (per-call) so HOME monkeypatching in tests is honored —
constants resolved at import time would freeze to whatever HOME was set when
the module first loaded, causing tests in fresh CI environments to silently
read the developer's real ~/.omnidrive instead of the temp HOME.
"""
import json
import os
from typing import Any, Dict


def config_dir() -> str:
    """Return the OmniDrive config directory, resolved per call."""
    return os.path.expanduser("~/.omnidrive")


def config_path() -> str:
    """Return the full path to config.json, resolved per call."""
    return os.path.join(config_dir(), "config.json")


# Back-compat module attributes. Marked legacy — prefer config_dir() /
# config_path() in new code. These resolve once at import time and are kept
# only so existing `from omnidrive.config import CONFIG_PATH` keeps importing
# without crashing. Anything that needs HOME-aware paths should call the
# functions above.
CONFIG_DIR = config_dir()
CONFIG_PATH = config_path()


def load_config() -> Dict[str, Any]:
    """
    Load configuration from local file.

    Returns:
        Dict with configuration data. Empty dict if file doesn't exist.
    """
    path = config_path()
    if not os.path.exists(path):
        return {}
    with open(path, 'r') as f:
        return json.load(f)


def save_config(cfg: Dict[str, Any]) -> None:
    """
    Save configuration to local file.

    Args:
        cfg: Configuration dictionary to save.
    """
    os.makedirs(config_dir(), exist_ok=True)
    with open(config_path(), 'w') as f:
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
