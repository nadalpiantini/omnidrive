"""
OmniDrive CLI - Main entry point.
Unified command-line tool for managing multiple cloud storage services.
"""
import click
import os
from typing import Optional
from .config import load_config
from .services import ServiceFactory
from .services.base import ServiceError, AuthenticationError
from .auth import google as google_auth
from .auth import folderfort as folderfort_auth
from .rag.embeddings import get_embeddings_generator
from .rag.indexer import FileIndexer, SemanticSearch
from .memory.serena_client import get_memory_manager
from .workflows.graphs import get_workflow_engine


# Configure ServiceFactory with auth modules
ServiceFactory._set_auth_modules({
    'google': google_auth,
    'folderfort': folderfort_auth,
})

# Supported drives
DRIVES = ServiceFactory.get_available_services()


@click.group()
@click.version_option(version="1.0.0", prog_name="OmniDrive CLI")
def cli():
    """
    OmniDrive CLI: Manage all your cloud drives.

    Unified command-line interface for Google Drive, Folderfort, OneDrive,
    Dropbox, and more - all in one place.
    """
    pass


@cli.command()
@click.option(
    '--drive',
    type=click.Choice(DRIVES),
    default='google',
    help="Which drive to list."
)
@click.option(
    '--limit',
    default=10,
    help="Maximum number of files to list."
)
def list(drive, limit):
    """List files in the specified cloud drive."""
    try:
        service = ServiceFactory.create_service(drive, auto_authenticate=False)

        # Check authentication and prompt if needed
        if not service.is_authenticated():
            click.secho(f"Not authenticated with {drive}.", fg='yellow')
            if click.confirm("Would you like to authenticate now?"):
                _authenticate_service(drive)
                service = ServiceFactory.create_service(drive, auto_authenticate=False)
            else:
                raise click.Abort()

        # List files
        files = service.list_files(limit=limit)

        if not files:
            click.echo(f"No files found in {drive}.")
        else:
            service_name = drive.capitalize()
            click.echo(f"\n📁 {service_name} Files (showing {len(files)}):")
            click.echo("-" * 60)
            for file in files:
                icon = _get_file_icon(file.get('mimeType') or file.get('type'))
                size = _format_size(file.get('size') or file.get('file_size'))
                click.echo(f"{icon} {file['name']}")
                if size:
                    click.echo(f"   ID: {file['id']} | Size: {size}")
                else:
                    click.echo(f"   ID: {file['id']}")

    except AuthenticationError as e:
        click.secho(f"Authentication error: {e}", fg='red')
        click.echo(f"Run: omnidrive auth {drive}")
    except ServiceError as e:
        click.secho(f"Service error: {e}", fg='red')
    except Exception as e:
        click.secho(f"Unexpected error: {e}", fg='red')


@cli.command()
@click.argument('drive', type=click.Choice(DRIVES))
@click.argument('file_id')
@click.option('--dest', default='.', help="Local destination folder.")
def download(drive, file_id, dest):
    """Download a file by ID from a drive to local."""
    try:
        service = ServiceFactory.create_service(drive, auto_authenticate=False)

        # Check authentication
        if not service.is_authenticated():
            click.secho(f"Not authenticated with {drive}.", fg='yellow')
            if click.confirm("Would you like to authenticate now?"):
                _authenticate_service(drive)
                service = ServiceFactory.create_service(drive, auto_authenticate=False)
            else:
                raise click.Abort()

        # Download file
        dest_path = service.download_file(file_id, dest)

        click.echo(f"✓ Downloaded to: {dest_path}")

    except AuthenticationError as e:
        click.secho(f"Authentication error: {e}", fg='red')
        click.echo(f"Run: omnidrive auth {drive}")
    except ServiceError as e:
        click.secho(f"Service error: {e}", fg='red')
    except Exception as e:
        click.secho(f"Unexpected error: {e}", fg='red')


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.argument('drive', type=click.Choice(DRIVES))
@click.option('--parent-id', help="Parent folder ID (optional)")
def upload(file_path, drive, parent_id):
    """Upload a file to a cloud storage service."""
    try:
        service = ServiceFactory.create_service(drive, auto_authenticate=False)

        # Check authentication
        if not service.is_authenticated():
            click.secho(f"Not authenticated with {drive}.", fg='yellow')
            if click.confirm("Would you like to authenticate now?"):
                _authenticate_service(drive)
                service = ServiceFactory.create_service(drive, auto_authenticate=False)
            else:
                raise click.Abort()

        # Show file info
        file_size = os.path.getsize(file_path)
        filename = os.path.basename(file_path)
        click.echo(f"\n📤 Uploading {filename}")
        click.echo(f"   Size: {_format_size(file_size)}")

        # Upload with real progress bar
        from tqdm import tqdm
        with tqdm(total=file_size, unit='B', unit_scale=True, desc="Uploading") as pbar:
            result = service.upload_file(file_path, parent_id=parent_id)
            pbar.update(file_size)  # Simple progress - TODO: Integrate with service for real-time updates

        click.echo(f"✓ Uploaded successfully!")
        click.echo(f"   ID: {result.get('id')}")
        click.echo(f"   Name: {result.get('name')}")

    except AuthenticationError as e:
        click.secho(f"Authentication error: {e}", fg='red')
        click.echo(f"Run: omnidrive auth {drive}")
    except ServiceError as e:
        click.secho(f"Service error: {e}", fg='red')
    except Exception as e:
        click.secho(f"Unexpected error: {e}", fg='red')


@cli.command()
@click.argument('drive', type=click.Choice(DRIVES))
@click.argument('file_id')
@click.option('--permanent', is_flag=True, help="Permanently delete (skip trash).")
def delete(drive, file_id, permanent):
    """Delete a file from cloud storage."""
    try:
        service = ServiceFactory.create_service(drive, auto_authenticate=False)

        # Check authentication
        if not service.is_authenticated():
            click.secho(f"Not authenticated with {drive}.", fg='yellow')
            if click.confirm("Would you like to authenticate now?"):
                _authenticate_service(drive)
                service = ServiceFactory.create_service(drive, auto_authenticate=False)
            else:
                raise click.Abort()

        # Confirm deletion
        if not permanent:
            msg = f"Move file to trash in {drive}?"
        else:
            msg = f"Permanently delete file from {drive}?"

        click.secho(f"⚠️  {msg}", fg='yellow', bold=True)
        if not click.confirm("This action cannot be undone. Continue?"):
            click.echo("Delete cancelled.")
            return

        # Delete file
        success = service.delete_file(file_id, permanent=permanent)

        if success:
            if permanent:
                click.echo("✓ File permanently deleted.")
            else:
                click.echo("✓ File moved to trash.")

    except AuthenticationError as e:
        click.secho(f"Authentication error: {e}", fg='red')
        click.echo(f"Run: omnidrive auth {drive}")
    except ServiceError as e:
        click.secho(f"Service error: {e}", fg='red')
    except Exception as e:
        click.secho(f"Unexpected error: {e}", fg='red')


@cli.command()
@click.argument('drive', type=click.Choice(DRIVES))
@click.argument('folder_name')
@click.option('--parent-id', help="Parent folder ID (optional).")
def create_folder(drive, folder_name, parent_id):
    """Create a new folder in cloud storage."""
    try:
        service = ServiceFactory.create_service(drive, auto_authenticate=False)

        # Check authentication
        if not service.is_authenticated():
            click.secho(f"Not authenticated with {drive}.", fg='yellow')
            if click.confirm("Would you like to authenticate now?"):
                _authenticate_service(drive)
                service = ServiceFactory.create_service(drive, auto_authenticate=False)
            else:
                raise click.Abort()

        # Create folder
        result = service.create_folder(folder_name, parent_id=parent_id)

        click.echo(f"✓ Folder created successfully!")
        click.echo(f"   Name: {result.get('name')}")
        click.echo(f"   ID: {result.get('id')}")

    except AuthenticationError as e:
        click.secho(f"Authentication error: {e}", fg='red')
        click.echo(f"Run: omnidrive auth {drive}")
    except ServiceError as e:
        click.secho(f"Service error: {e}", fg='red')
    except Exception as e:
        click.secho(f"Unexpected error: {e}", fg='red')


@cli.command()
@click.argument('source', type=click.Choice(DRIVES))
@click.argument('target', type=click.Choice(DRIVES))
@click.option('--dry-run', is_flag=True, help="Show what would be synced without actually syncing.")
@click.option('--limit', default=100, help="Maximum number of files to sync.")
def sync(source, target, dry_run, limit):
    """Sync files from SOURCE drive to TARGET drive."""
    if source == target:
        click.secho("Source and target must be different.", fg='red')
        return

    try:
        # Get files from source
        click.echo(f"\n🔄 Syncing from {source} to {target}")
        click.echo("=" * 60)

        source_files = _get_files_from_service(source, limit)
        target_files = _get_files_from_service(target, limit)

        # Find files in source that are not in target
        source_names = {f.get('name') for f in source_files}
        target_names = {f.get('name') for f in target_files}

        files_to_sync = source_names - target_names

        if not files_to_sync:
            click.echo("✓ All files already in sync!")
            return

        click.echo(f"\n📋 Files to sync: {len(files_to_sync)}")

        for file_name in files_to_sync:
            file_data = next(f for f in source_files if f.get('name') == file_name)
            icon = _get_file_icon(file_data.get('mimeType') or file_data.get('type'))
            size = _format_size(file_data.get('size') or file_data.get('file_size'))
            click.echo(f"{icon} {file_name} {size}")

        if dry_run:
            click.echo("\n[DRY RUN] No files were actually synced.")
        else:
            if not click.confirm(f"\nSync {len(files_to_sync)} files?"):
                click.echo("Sync cancelled.")
                return

            # Perform sync
            with click.progressbar(files_to_sync, label='Syncing') as bar:
                for file_name in bar:
                    file_data = next(f for f in source_files if f.get('name') == file_name)
                    # Download from source and upload to target
                    _sync_file(file_data, source, target)

            click.echo(f"\n✓ Synced {len(files_to_sync)} files!")

    except AuthenticationError as e:
        click.secho(f"Authentication error: {e}", fg='red')
    except ServiceError as e:
        click.secho(f"Service error: {e}", fg='red')
    except Exception as e:
        click.secho(f"Error: {e}", fg='red')


@cli.command()
@click.argument('service1', type=click.Choice(DRIVES))
@click.argument('service2', type=click.Choice(DRIVES))
@click.option('--limit', default=100, help="Maximum number of files to compare.")
def compare(service1, service2, limit):
    """Compare files between two cloud storage services."""
    if service1 == service2:
        click.secho("Services must be different.", fg='red')
        return

    try:
        click.echo(f"\n🔍 Comparing {service1} vs {service2}")
        click.echo("=" * 60)

        files1 = _get_files_from_service(service1, limit)
        files2 = _get_files_from_service(service2, limit)

        names1 = {f.get('name') for f in files1}
        names2 = {f.get('name') for f in files2}

        # Files only in service1
        only_in_1 = names1 - names2
        # Files only in service2
        only_in_2 = names2 - names1
        # Files in both
        common = names1 & names2

        click.echo(f"\n📊 Statistics:")
        click.echo(f"   Total in {service1}: {len(files1)}")
        click.echo(f"   Total in {service2}: {len(files2)}")
        click.echo(f"   Common files: {len(common)}")

        if only_in_1:
            click.echo(f"\n✅ Only in {service1} ({len(only_in_1)}):")
            for name in sorted(list(only_in_1))[:10]:
                file_data = next(f for f in files1 if f.get('name') == name)
                icon = _get_file_icon(file_data.get('mimeType') or file_data.get('type'))
                click.echo(f"   {icon} {name}")
            if len(only_in_1) > 10:
                click.echo(f"   ... and {len(only_in_1) - 10} more")

        if only_in_2:
            click.echo(f"\n✅ Only in {service2} ({len(only_in_2)}):")
            for name in sorted(list(only_in_2))[:10]:
                file_data = next(f for f in files2 if f.get('name') == name)
                icon = _get_file_icon(file_data.get('mimeType') or file_data.get('type'))
                click.echo(f"   {icon} {name}")
            if len(only_in_2) > 10:
                click.echo(f"   ... and {len(only_in_2) - 10} more")

        click.echo(f"\n✓ Comparison complete!")

    except Exception as e:
        click.secho(f"Error: {e}", fg='red')


# Helper functions for sync/compare

def _get_files_from_service(service: str, limit: int) -> list:
    """Get files from a cloud storage service."""
    service_obj = ServiceFactory.create_service(service, auto_authenticate=False)

    if not service_obj.is_authenticated():
        raise click.ClickException(
            f"Not authenticated with {service.capitalize()}. "
            f"Run 'omnidrive auth {service}'"
        )

    return service_obj.list_files(limit=limit)


def _sync_file(file_data: dict, source: str, target: str):
    """Sync a single file from source to target."""
    import tempfile

    # Download from source
    source_service = ServiceFactory.create_service(source, auto_authenticate=False)

    # Upload to target
    target_service = ServiceFactory.create_service(target, auto_authenticate=False)

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        # Download
        source_service.download_file(file_data['id'], tmp.name)

        # Upload
        target_service.upload_file(tmp.name)

        # Cleanup
        os.unlink(tmp.name)


def _authenticate_service(service: str):
    """Authenticate with a cloud storage service."""
    if service == 'google':
        google_auth.authenticate_google()
    elif service == 'folderfort':
        folderfort_auth.authenticate_folderfort()
    else:
        raise click.ClickException(f"{service.capitalize()} authentication not implemented yet.")


@cli.command()
@click.argument('service', type=click.Choice(DRIVES))
def auth(service):
    """Authenticate with a cloud storage service."""
    try:
        _authenticate_service(service)
    except click.Abort:
        return


@cli.command()
@click.argument('service', type=click.Choice(DRIVES))
@click.option('--limit', default=100, help="Maximum number of files to index.")
def index(service, limit):
    """Index files from a cloud storage service for semantic search."""
    try:
        click.echo(f"\n🔍 Indexing {service} files for semantic search")
        click.echo("=" * 60)

        # Check for DeepSeek API key
        import os
        if not os.getenv('DEEPSEEK_API_KEY'):
            click.secho("⚠ DEEPSEEK_API_KEY environment variable not set.", fg='yellow')
            click.echo("Set it with: export DEEPSEEK_API_KEY='your-key-here'")
            click.echo("RAG features require DeepSeek API for embeddings (or use local sentence-transformers).")
            return

        # Get files from service
        files = _get_files_from_service(service, limit)

        if not files:
            click.echo("No files found to index.")
            return

        click.echo(f"Found {len(files)} files")
        click.echo("\n⚠ Note: Full file indexing requires downloading files first.")
        click.echo("This is a placeholder for the indexing feature.")
        click.echo("In production, files would be downloaded and indexed.")

        # Initialize indexer
        indexer = FileIndexer()

        # For now, just show what would be indexed
        for file_data in files[:5]:  # Show first 5 as example
            file_name = file_data.get('name')
            file_type = file_data.get('mimeType') or file_data.get('type', 'unknown')
            icon = _get_file_icon(file_type)
            click.echo(f"{icon} {file_name}")

        if len(files) > 5:
            click.echo(f"\n... and {len(files) - 5} more files")

    except Exception as e:
        click.secho(f"Error: {e}", fg='red')


@cli.command()
@click.argument('query')
@click.option('--service', type=click.Choice(DRIVES), help="Filter by service.")
@click.option('--top-k', default=5, help="Number of results to return.")
def search(query, service, top_k):
    """Search files using semantic search."""
    try:
        click.echo(f"\n🔍 Semantic Search: '{query}'")
        click.echo("=" * 60)

        # Check for DeepSeek API key
        import os
        if not os.getenv('DEEPSEEK_API_KEY'):
            click.secho("⚠ DEEPSEEK_API_KEY environment variable not set.", fg='yellow')
            click.echo("Set it with: export DEEPSEEK_API_KEY='your-key-here'")
            return

        # Initialize semantic search
        semantic_search = SemanticSearch()

        # Search
        click.echo(f"Searching (top {top_k} results)...")
        results = semantic_search.search(query, top_k=top_k, service=service)

        if not results:
            click.echo("No results found.")
            click.echo("\n💡 Tip: Index files first with: omnidrive index <service>")
            return

        # Display results
        for i, result in enumerate(results, 1):
            metadata = result.get('metadata', {})
            file_name = metadata.get('file_name', 'Unknown')
            file_service = metadata.get('service', 'unknown')
            distance = result.get('distance', 0)

            # Calculate similarity score
            similarity = (1 - distance) * 100

            click.echo(f"\n{i}. {file_name}")
            click.echo(f"   Service: {file_service}")
            click.echo(f"   Relevance: {similarity:.1f}%")

            # Show snippet of document text
            document = result.get('document', '')
            if document:
                snippet = document[:200] + "..." if len(document) > 200 else document
                click.echo(f"   Snippet: {snippet}")

        click.echo(f"\n✓ Found {len(results)} results")

    except Exception as e:
        click.secho(f"Error: {e}", fg='red')


@cli.group()
def session():
    """Manage persistent sessions."""
    pass


@session.command()
@click.argument('name')
def save(name):
    """Save current session state."""
    try:
        memory = get_memory_manager()

        # Get current state
        from datetime import datetime
        state = {
            'timestamp': datetime.now().isoformat(),
            'google_authenticated': google_auth.is_google_authenticated(),
            'folderfort_authenticated': folderfort_auth.is_folderfort_authenticated(),
        }

        memory.write_memory(f"session_{name}", state)
        click.echo(f"✓ Session '{name}' saved")

    except Exception as e:
        click.secho(f"Error: {e}", fg='red')


@session.command()
@click.argument('name')
def resume(name):
    """Resume a saved session."""
    try:
        memory = get_memory_manager()
        state = memory.read_memory(f"session_{name}")

        if not state:
            click.secho(f"Session '{name}' not found", fg='red')
            return

        click.echo(f"📋 Resuming session '{name}'")
        click.echo(f"   Saved at: {state.get('timestamp', 'Unknown')}")
        click.echo(f"   Google authenticated: {state.get('google_authenticated', False)}")
        click.echo(f"   Folderfort authenticated: {state.get('folderfort_authenticated', False)}")

    except Exception as e:
        click.secho(f"Error: {e}", fg='red')


@session.command('list')
def list_sessions():
    """List all saved sessions."""
    try:
        memory = get_memory_manager()
        sessions = [m for m in memory.list_memories() if m['key'].startswith('session_')]

        if not sessions:
            click.echo("No saved sessions found.")
            return

        click.echo("\n💾 Saved Sessions:")
        click.echo("-" * 60)
        for session in sessions:
            name = session['key'].replace('session_', '')
            timestamp = session.get('timestamp', 'Unknown')
            click.echo(f"  • {name} (saved: {timestamp})")

    except Exception as e:
        click.secho(f"Error: {e}", fg='red')


@cli.group()
def workflow():
    """Manage automated workflows."""
    pass


@workflow.command('list')
def list_workflows_cmd():
    """List available workflows."""
    try:
        engine = get_workflow_engine()
        workflows = engine.list_workflows()

        if not workflows:
            click.echo("No workflows found.")
            return

        click.echo("\n⚙️ Available Workflows:")
        click.echo("-" * 60)
        for wf in workflows:
            click.echo(f"  • {wf['name']}")
            click.echo(f"    {wf['description']}")
            click.echo(f"    Steps: {wf['steps']}")

    except Exception as e:
        click.secho(f"Error: {e}", fg='red')


@workflow.command()
@click.argument('name')
def run(name):
    """Run a workflow."""
    try:
        engine = get_workflow_engine()

        click.echo(f"\n🚀 Running workflow: {name}")
        click.echo("=" * 60)

        result = engine.execute_workflow(name)

        if result.status.value == "completed":
            click.echo(f"✓ {result.message}")
        else:
            click.secho(f"✗ {result.message}", fg='red')

    except Exception as e:
        click.secho(f"Error: {e}", fg='red')


# Helper functions

def _get_file_icon(mime_type: str) -> str:
    """Get an icon for a file based on MIME type."""
    if not mime_type:
        return "📄"

    if 'folder' in mime_type:
        return "📁"
    elif 'pdf' in mime_type:
        return "📕"
    elif 'document' in mime_type or 'word' in mime_type:
        return "📘"
    elif 'spreadsheet' in mime_type or 'excel' in mime_type:
        return "📗"
    elif 'presentation' in mime_type or 'powerpoint' in mime_type:
        return "📙"
    elif 'image' in mime_type:
        return "🖼️ "
    elif 'video' in mime_type:
        return "🎬"
    elif 'audio' in mime_type:
        return "🎵"
    else:
        return "📄"


def _format_size(size_bytes: Optional[int]) -> str:
    """Format file size in human-readable format."""
    if size_bytes is None:
        return ""

    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


if __name__ == '__main__':
    cli()
