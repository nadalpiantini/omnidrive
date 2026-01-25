# OmniDrive CLI - Claude Code Instructions

## Project Overview

OmniDrive CLI is a unified command-line tool for managing multiple cloud storage services (Google Drive, Folderfort, OneDrive, Dropbox).

**Current Phase:** Phase 0 - Refactorization complete ✅

## Architecture

### Modular Structure
```
omnidrive/
├── __init__.py        # Package initialization
├── __main__.py        # Entry point for `python -m omnidrive`
├── cli.py             # Main CLI with Click
├── config.py          # Configuration management
│
├── services/          # Cloud service implementations
│   ├── base.py        # CloudService abstract base class
│   ├── google_drive.py  # Google Drive implementation
│   └── folderfort.py  # Folderfort implementation (Phase 1)
│
├── auth/              # Authentication modules
│   ├── google.py      # Google Drive authentication
│   └── folderfort.py  # Folderfort authentication (Phase 1)
│
├── commands/          # CLI command implementations (Phase 2)
├── rag/               # RAG system (Phase 3)
├── memory/            # Serena MCP integration (Phase 3)
└── workflows/         # LangGraph workflows (Phase 4)
```

## Development Guidelines

### Code Style
- **Python Version:** 3.10+
- **Style Guide:** PEP 8
- **Line Length:** 100 characters
- **Type Hints:** Required for all functions
- **Docstrings:** Google style docstrings

### Pattern: Service Implementation

All cloud services must:

1. **Inherit from `CloudService`** (in `services/base.py`)
2. **Implement all abstract methods:**
   - `authenticate()` - Return access token
   - `list_files()` - Return list of file metadata
   - `upload_file()` - Upload and return metadata
   - `download_file()` - Download to local path
   - `delete_file()` - Delete or move to trash
   - `create_folder()` - Create new folder

3. **Raise `ServiceError`** for failures
4. **Return consistent metadata:**
   ```python
   {
       "id": "file_id",
       "name": "filename.ext",
       "size": 1024,
       "mime": "mime/type",
       "createdTime": "2024-01-01T00:00:00Z",
       "modifiedTime": "2024-01-01T00:00:00Z"
   }
   ```

### Pattern: CLI Commands

Commands should:

1. **Check authentication first**
2. **Use `click` for CLI interface**
3. **Provide helpful error messages**
4. **Use icons and formatting for UX**
5. **Support `--help` on all commands**

## Testing

### Run Tests
```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=omnidrive --cov-report=html

# Specific test file
pytest tests/test_google_drive.py -v
```

### Test Structure
```python
# tests/test_service_name.py
import pytest
from omnidrive.services.service_name import ServiceNameService

class TestServiceNameService:
    def test_authenticate(self):
        # Test authentication
        pass

    def test_list_files(self):
        # Test listing files
        pass
```

## Common Tasks

### Adding a New Cloud Service

1. Create `omnidrive/services/new_service.py`
2. Implement `CloudService` interface
3. Create `omnidrive/auth/new_service.py`
4. Add service to `DRIVES` list in `cli.py`
5. Add CLI commands
6. Write tests
7. Update README

### Debugging

```bash
# Enable verbose logging
python3 -m omnidrive --verbose list google

# Check configuration
cat ~/.omnidrive/config.json

# Test authentication
python3 -m omnidrive auth google
```

## Key Files to Understand

### `omnidrive/services/base.py`
Abstract base class defining the interface all cloud services must implement.

### `omnidrive/services/google_drive.py`
Example implementation showing how to implement the CloudService interface.

### `omnidrive/cli.py`
Main CLI entry point using Click framework.

### `omnidrive/config.py`
Configuration management with load/save functionality.

## Phase-Specific Notes

### Phase 0: Refactorization ✅
- ✅ Created modular structure
- ✅ Extracted Google Drive to service class
- ✅ Created CloudService base interface
- ✅ Refactored CLI to use services
- ✅ Configuration management
- ✅ Authentication modules

### Phase 1: Folderfort Integration
- Implement `FolderfortService` class
- Implement Folderfort authentication
- Add `list`, `upload`, `download` commands
- Write tests

### Phase 2: Upload and Sync
- Implement `upload` command for all services
- Implement `sync` command between services
- Implement `compare` command
- Add progress bars
- Error handling with retries

### Phase 3: RAG System
- Choose Vector DB (ChromaDB/Pinecone)
- Implement embeddings generation
- Implement file indexing
- Implement semantic search
- Add `index` and `search` commands

### Phase 4: LangGraph Workflows
- Define agents
- Create workflow graphs
- Implement Smart Sync workflow
- Implement Backup workflow
- Add triggers system

### Phase 5: Production
- Complete test suite (80%+ coverage)
- Error handling robust
- Rate limiting
- Logging structured
- Documentation
- PyPI distribution

## Troubleshooting

### Import Errors
```bash
# Make sure you're in the project directory
cd omnidrive-cli

# Install dependencies
pip install -r requirements.txt

# Or with Poetry
poetry install
```

### Authentication Issues
```bash
# Check credentials file
cat ~/.omnidrive/config.json

# Re-authenticate
python3 -m omnidrive auth google
```

### Google Drive API Errors
- Make sure service account has Drive API enabled
- Check service account has proper permissions
- Verify quota limits

## Version History

- **1.0.0** - Initial release with Google Drive support (Phase 0)


<claude-mem-context>
# Recent Activity

<!-- This section is auto-generated by claude-mem. Edit content outside the tags. -->

### Jan 24, 2026

| ID | Time | T | Title | Read |
|----|------|---|-------|------|
| #84 | 7:59 PM | 🔴 | Corrected Folderfort Authentication Credentials | ~353 |
| #80 | 7:57 PM | ✅ | Created Folderfort Authentication Test Script for /api/v1/auth/login Endpoint | ~360 |
| #78 | " | 🟣 | Created Comprehensive Folderfort Endpoint Discovery Script | ~408 |
| #74 | 7:56 PM | 🟣 | Created Folderfort API Testing Script | ~370 |
| #72 | 7:55 PM | ✅ | Created Folderfort Authentication Test Script | ~294 |
| #67 | 7:03 PM | 🔵 | OmniDrive CLI Dependencies and Technology Stack | ~417 |
| #66 | " | 🔵 | OmniDrive CLI Architecture and Development Guidelines | ~601 |
| #65 | " | 🔵 | OmniDrive CLI Complete Requirements Documentation | ~610 |
| #64 | " | 🔵 | OmniDrive CLI Multi-Cloud Sync Tool Architecture and Capabilities | ~465 |
</claude-mem-context>