#!/usr/bin/env python3
"""
OmniDrive CLI - A 360° Cloud Sync Solution
Unified command-line tool for managing multiple cloud storage services.
"""
import os
import json
import click
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from tqdm import tqdm

# === Config and Authentication ===

CONFIG_PATH = os.path.expanduser("~/.omnidrive/config.json")
SCOPES = ['https://www.googleapis.com/auth/drive']
DRIVES = ['google', 'onedrive', 'dropbox']  # Supported services


def load_config():
    """Load configuration from local file."""
    if not os.path.exists(CONFIG_PATH):
        return {}
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)


def save_config(cfg):
    """Save configuration to local file."""
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(cfg, f, indent=2)


def ensure_google_credentials():
    """
    Ensure Google Drive credentials exist.
    For simplicity, use a service account key file path from env or config.
    """
    cfg = load_config()
    key_path = cfg.get('google_key_path') or os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if not key_path or not os.path.exists(key_path):
        click.secho(
            "Google credentials not found. Please set GOOGLE_APPLICATION_CREDENTIALS "
            "or config 'google_key_path'.",
            fg='red'
        )
        raise click.Abort()
    creds = service_account.Credentials.from_service_account_file(
        key_path,
        scopes=SCOPES
    )
    service = build('drive', 'v3', credentials=creds)
    return service


# === Core Functionality ===

def list_google_files():
    """List files in Google Drive root."""
    service = ensure_google_credentials()
    try:
        results = service.files().list(
            pageSize=10,
            fields="files(id, name)"
        ).execute()
        items = results.get('files', [])
        if not items:
            click.echo("No files found in Google Drive.")
        else:
            click.echo("Google Drive Files:")
            for item in items:
                click.echo(f"  {item['name']} (ID: {item['id']})")
    except HttpError as error:
        click.secho(f"Error listing Google Drive files: {error}", fg='red')


def download_google_file(file_id, destination):
    """Download a file from Google Drive given its ID."""
    service = ensure_google_credentials()
    try:
        request = service.files().get_media(fileId=file_id)
        fh_path = os.path.join(destination, f"{file_id}.download")
        with open(fh_path, 'wb') as fh:
            downloader = build('drive', 'v3', credentials=service._credentials)
            downloader._http = service._http
            request.execute(fh.write)
        click.echo(f"Downloaded Google file {file_id} to {fh_path}")
    except HttpError as error:
        click.secho(f"Error downloading file {file_id}: {error}", fg='red')


# Placeholder functions for OneDrive and Dropbox
def list_onedrive_files():
    """List files in OneDrive (not implemented yet)."""
    click.echo("OneDrive listing not implemented yet.")


def list_dropbox_files():
    """List files in Dropbox (not implemented yet)."""
    click.echo("Dropbox listing not implemented yet.")


# === CLI Commands ===

@click.group()
@click.version_option(version="1.0", prog_name="OmniDrive CLI")
def cli():
    """OmniDrive CLI: Manage all your cloud drives."""
    pass


@cli.command()
@click.option(
    '--drive',
    type=click.Choice(DRIVES),
    default='google',
    help="Which drive to list (google, onedrive, dropbox)."
)
def list(drive):
    """List files in the specified cloud drive."""
    if drive == 'google':
        list_google_files()
    elif drive == 'onedrive':
        list_onedrive_files()
    elif drive == 'dropbox':
        list_dropbox_files()
    else:
        click.secho(f"Drive {drive} not supported.", fg='red')


@cli.command()
@click.argument('drive')
@click.option('--dest', default='.', help="Local destination folder.")
def download(drive, dest):
    """Download a file by ID from a drive to local."""
    if drive == 'google':
        file_id = click.prompt("Enter Google Drive file ID")
        download_google_file(file_id, dest)
    else:
        click.secho("Download from specified drive not yet supported.", fg='yellow')


@cli.command()
@click.argument('source', type=click.Choice(DRIVES))
@click.argument('target', type=click.Choice(DRIVES))
def sync(source, target):
    """Sync files from SOURCE drive to TARGET drive."""
    click.echo(
        f"Sync from {source} to {target} not implemented in this prototype.\n"
        "In a full implementation, we would compare file lists and transfer files."
    )


# === Entry Point ===

if __name__ == '__main__':
    cli()
