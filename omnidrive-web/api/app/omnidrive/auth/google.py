"""
Authentication module for Google Drive.
Handles OAuth2 flow and service account authentication.
"""
import os
import click
from typing import Optional
from ..config import load_config, save_config, set_config_value


def authenticate_google() -> str:
    """
    Authenticate with Google Drive using service account.

    This will prompt the user for the path to their service account JSON file
    and save it to the configuration.

    Returns:
        Access token placeholder ("service_account")

    Raises:
        click.Abort: If authentication fails
    """
    cfg = load_config()

    # Check if already authenticated
    if 'google_key_path' in cfg and os.path.exists(cfg['google_key_path']):
        click.echo("✓ Already authenticated with Google Drive.")
        return "service_account"

    # Prompt for service account key path
    click.echo("\n🔐 Google Drive Authentication")
    click.echo("You need a service account JSON file.")
    click.echo("Create one at: https://console.cloud.google.com/apis/credentials\n")

    key_path = click.prompt(
        "Path to service account JSON file",
        type=click.Path(exists=True),
        default=os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')
    )

    if not key_path or not os.path.exists(key_path):
        click.secho("✗ Invalid file path.", fg='red')
        raise click.Abort()

    # Save to config
    set_config_value('google_key_path', os.path.abspath(key_path))

    click.echo(f"✓ Google Drive authenticated successfully!")
    click.echo(f"  Credentials saved to: ~/.omnidrive/config.json")

    return "service_account"


def get_google_credentials_path() -> Optional[str]:
    """
    Get the path to Google credentials from config.

    Returns:
        Path to service account JSON file, or None if not configured
    """
    cfg = load_config()
    key_path = cfg.get('google_key_path') or os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

    if key_path and os.path.exists(key_path):
        return key_path

    return None


def is_google_authenticated() -> bool:
    """
    Check if Google Drive is authenticated.

    Returns:
        True if credentials exist and file is accessible
    """
    return get_google_credentials_path() is not None
