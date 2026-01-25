"""
Authentication module for Folderfort.
Handles email/password authentication and token management.
"""
import click
import getpass
from typing import Optional
from ..config import load_config, set_config_value
from ..services.folderfort import FolderfortService


def authenticate_folderfort(email: Optional[str] = None, password: Optional[str] = None) -> str:
    """
    Authenticate with Folderfort using email and password.

    This will prompt the user for credentials if not provided,
    and save the access token to the configuration.

    Args:
        email: Folderfort account email (will prompt if not provided)
        password: Folderfort account password (will prompt if not provided)

    Returns:
        Access token

    Raises:
        click.Abort: If authentication fails
    """
    cfg = load_config()

    # Check if already authenticated
    if 'folderfort_token' in cfg:
        # Verify token is still valid
        service = FolderfortService(access_token=cfg['folderfort_token'])
        try:
            # Try to list files to verify token
            service.list_files(limit=1)
            click.echo("✓ Already authenticated with Folderfort.")
            return cfg['folderfort_token']
        except Exception:
            # Token is invalid, remove it and continue
            click.echo("Previous authentication expired. Please re-authenticate.")

    # Prompt for credentials
    click.echo("\n🔐 Folderfort Authentication")
    click.echo("Enter your Folderfort credentials.\n")

    if not email:
        email = click.prompt("Email")

    if not password:
        password = getpass.getpass("Password: ")

    # Authenticate
    try:
        service = FolderfortService()
        token = service.authenticate(email=email, password=password, token_name='omnidrive-cli')

        # Save token to config
        set_config_value('folderfort_token', token)
        set_config_value('folderfort_email', email)

        click.echo(f"✓ Folderfort authenticated successfully!")
        click.echo(f"  Token saved to: ~/.omnidrive/config.json")

        return token

    except Exception as e:
        click.secho(f"✗ Authentication failed: {e}", fg='red')
        raise click.Abort()


def get_folderfort_token() -> Optional[str]:
    """
    Get the Folderfort access token from config.

    Returns:
        Access token, or None if not configured
    """
    cfg = load_config()
    return cfg.get('folderfort_token')


def is_folderfort_authenticated() -> bool:
    """
    Check if Folderfort is authenticated.

    Returns:
        True if token exists and is valid
    """
    token = get_folderfort_token()
    if not token:
        return False

    # Verify token is still valid
    service = FolderfortService(access_token=token)
    try:
        service.list_files(limit=1)
        return True
    except Exception:
        return False


def logout_folderfort() -> bool:
    """
    Logout from Folderfort by removing the token.

    Returns:
        True if successful
    """
    try:
        from ..config import save_config
        cfg = load_config()

        # Remove Folderfort credentials
        cfg.pop('folderfort_token', None)
        cfg.pop('folderfort_email', None)

        # Save updated config
        save_config(cfg)

        click.echo("✓ Logged out from Folderfort")
        return True

    except Exception as e:
        click.secho(f"✗ Failed to logout: {e}", fg='red')
        return False
