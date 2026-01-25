# OmniDrive CLI - Design Notes (Edward Honour Methodology)

## Architecture Overview

**System Architecture Pattern: Layered Architecture with Plugin System**

```
┌─────────────────────────────────────────────────────────────┐
│                      Presentation Layer                      │
│                    (CLI - Click Framework)                   │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    Application Layer                        │
│           (Commands, Workflows, Session Management)          │
└────┬───────────────┬───────────────┬──────────────────────┘
     │               │               │
┌────▼────┐  ┌──────▼──────┐  ┌───▼──────────────────────┐
│ Auth    │  │  Services   │  │      RAG System           │
│ Modules │  │  (Adapter)  │  │ (Optional AI Features)    │
└────┬────┘  └──────┬──────┘  └───┬──────────────────────┘
     │              │              │
┌────▼──────────────▼──────────────▼──────────────────────┐
│                  Persistence Layer                        │
│      (Config JSON, Memory Files, Vector DB)              │
└───────────────────────────────────────────────────────────┘
```

**Key Design Principles:**

1. **Separation of Concerns** - Each layer has distinct responsibility
2. **Dependency Inversion** - High-level layers don't depend on low-level details
3. **Open/Closed** - Open for extension (new services), closed for modification
4. **Interface Segregation** - Minimal, focused interfaces

---

## Design Patterns Applied

### 1. Adapter Pattern (CloudService Interface)

**Purpose:** Unify multiple cloud storage APIs under single interface

**Implementation:**
```python
from abc import ABC, abstractmethod

class CloudService(ABC):
    @abstractmethod
    def authenticate(self, **kwargs) -> str:
        """Authenticate and return access token"""
        pass

    @abstractmethod
    def list_files(self, folder_id=None, limit=100) -> List[Dict]:
        """List files in the service"""
        pass

    @abstractmethod
    def upload_file(self, file_path, parent_id=None) -> Dict:
        """Upload file to service"""
        pass

    @abstractmethod
    def download_file(self, file_id, dest_path) -> str:
        """Download file from service"""
        pass

    @abstractmethod
    def delete_file(self, file_id, permanent=False) -> bool:
        """Delete file from service"""
        pass

    @abstractmethod
    def create_folder(self, name, parent_id=None) -> Dict:
        """Create folder in service"""
        pass
```

**Benefits:**
- ✅ New services can be added without modifying existing code
- ✅ Services are interchangeable (sync between any two)
- ✅ Consistent error handling across all services
- ✅ Easy to mock for testing

**Services Implementing Interface:**
- GoogleDriveService (Google Drive API v3)
- FolderfortService (Folderfort REST API)
- (Future) OneDriveService, DropboxService, S3Service

---

### 2. Factory Pattern (Service Creation)

**Purpose:** Create service instances with proper initialization

**Implementation:**
```python
def get_service(service_name: str) -> CloudService:
    """Factory function to create service instances"""
    if service_name == 'google':
        return GoogleDriveService()
    elif service_name == 'folderfort':
        token = get_folderfort_token()
        return FolderfortService(access_token=token)
    else:
        raise ValueError(f"Unknown service: {service_name}")
```

**Benefits:**
- ✅ Centralized service creation logic
- ✅ Easy to add new services
- ✅ Consistent initialization

---

### 3. Strategy Pattern (Authentication Strategies)

**Purpose:** Different authentication methods per service

**Implementation:**
```python
# Google Drive: Service Account
def authenticate_google() -> str:
    key_path = prompt_for_service_account()
    validate_key_file(key_path)
    save_config('google_key_path', key_path)
    return "service_account"

# Folderfort: Email/Password OAuth
def authenticate_folderfort() -> str:
    email = prompt_for_email()
    password = prompt_for_password()
    service = FolderfortService()
    token = service.authenticate(email, password)
    save_config('folderfort_token', token)
    return token
```

**Benefits:**
- ✅ Each service has optimal auth flow
- ✅ Authentication logic encapsulated
- ✅ Easy to add new auth strategies

---

### 4. Singleton Pattern (Managers)

**Purpose:** Single instance for shared resources

**Implementation:**
```python
# Memory Manager Singleton
_memory_manager_instance = None

def get_memory_manager() -> MemoryManager:
    global _memory_manager_instance
    if _memory_manager_instance is None:
        _memory_manager_instance = MemoryManager()
    return _memory_manager_instance

# Workflow Engine Singleton
_workflow_engine_instance = None

def get_workflow_engine() -> WorkflowEngine:
    global _workflow_engine_instance
    if _workflow_engine_instance is None:
        _workflow_engine_instance = WorkflowEngine()
        _workflow_engine_instance.register_workflow(create_smart_sync_workflow())
        _workflow_engine_instance.register_workflow(create_backup_workflow())
    return _workflow_engine_instance
```

**Benefits:**
- ✅ Single source of truth
- ✅ Resource efficiency
- ✅ Consistent state across application

---

### 5. Lazy Loading Pattern (Optional Dependencies)

**Purpose:** Load optional dependencies only when needed

**Implementation:**
```python
# RAG modules with lazy imports
try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

class VectorStore:
    def __init__(self):
        self._chromadb_available = CHROMADB_AVAILABLE
        self.client = None  # Don't initialize yet

    def _ensure_chromadb(self):
        """Raise error only when actually using ChromaDB"""
        if not self._chromadb_available:
            raise ImportError("ChromaDB not installed...")
```

**Benefits:**
- ✅ Core functionality works without RAG dependencies
- ✅ User gets helpful error only when using RAG features
- ✅ No import errors for basic CLI usage

---

## Data Models

### File Metadata Model

**Standardized across all services:**
```python
{
    "id": str,              # Unique file identifier
    "name": str,            # File name
    "size": int,            # File size in bytes
    "mime": str,            # MIME type (service-specific)
    "createdTime": str,     # ISO 8601 timestamp
    "modifiedTime": str,    # ISO 8601 timestamp
    "parentId": str,        # Parent folder ID
    "trashed": bool         # Is in trash
}
```

**Service-Specific Extensions:**
- Google Drive: `mimeType`, `webViewLink`
- Folderfort: `file_size`, `type`

---

### Configuration Model

**Config Schema:**
```python
{
    "google_key_path": str,      # Path to service account JSON
    "folderfort_token": str,     # OAuth access token
    "folderfort_email": str,     # User email
    "default_service": str       # Default service to use
}
```

**Storage:** `~/.omnidrive/config.json`

---

### Session Memory Model

**Session Schema:**
```python
{
    "timestamp": str,           # ISO 8601 timestamp
    "google_authenticated": bool,
    "folderfort_authenticated": bool,
    "last_command": str,        # Last executed command
    "context": Dict[str, Any]   # Additional context
}
```

**Storage:** `~/.omnidrive/memory/session_*.json`

---

### Workflow Context Model

**Context Schema:**
```python
{
    "workflow_name": str,
    "start_time": str,
    "current_step": int,
    "total_steps": int,
    "status": str,              # pending, in_progress, completed, failed
    "data": Dict[str, Any],     # Workflow-specific data
    "results": List[Dict]       # Step results
}
```

---

## UI/UX Guidelines

### Command Structure

**Naming Convention:**
- `verb` - Single word commands
- `verb noun` - Command with target
- `--option` - Long options with double dash
- `-o` - Short options (rare)

**Examples:**
```bash
omnidrive list                    # Good
omnidrive upload file.txt google  # Good
omnidrive sync google folderfort  # Good
```

---

### Output Formatting

**File Icons:**
```python
{
    "folder": "📁",
    "pdf": "📕",
    "word": "📘",
    "excel": "📗",
    "powerpoint": "📙",
    "image": "🖼️",
    "video": "🎬",
    "audio": "🎵",
    "default": "📄"
}
```

**File Sizes:**
- Human-readable format (1.2 KB, 3.4 MB, 1.1 GB)
- Automatic unit selection
- 1 decimal place precision

---

### Progress Indicators

**For Long Operations:**
```python
from tqdm import tqdm

with tqdm(files, desc='Syncing') as bar:
    for file in bar:
        sync_file(file)
```

**Visual Feedback:**
```python
✓ Success message with checkmark
✗ Error message with X
⚠ Warning message with triangle
→ Arrow for progress
```

---

### Color Usage

**Color Scheme:**
```python
click.secho("Success", fg='green')
click.secho("Error", fg='red')
click.secho("Warning", fg='yellow')
click.secho("Info", fg='blue')
```

**When to Use:**
- ✅ Green: Success, completion
- ❌ Red: Errors, failures
- ⚠️ Yellow: Warnings, cautions
- ℹ️ Blue: Informational messages

---

## Error Handling Strategy

### Exception Hierarchy

```python
class OmniDriveError(Exception):
    """Base exception for all OmniDrive errors"""
    pass

class ServiceError(OmniDriveError):
    """Cloud service errors"""
    pass

class AuthenticationError(OmniDriveError):
    """Authentication failures"""
    pass

class ValidationError(OmniDriveError):
    """Input validation errors"""
    pass

class ConfigurationError(OmniDriveError):
    """Configuration errors"""
    pass
```

---

### Error Handling Patterns

**1. API Errors:**
```python
try:
    files = service.list_files()
except requests.HTTPError as e:
    if e.response.status_code == 401:
        click.secho("Authentication expired. Please re-authenticate.", fg='yellow')
    elif e.response.status_code == 429:
        click.secho("Rate limit exceeded. Please try again later.", fg='yellow')
    else:
        click.secho(f"API error: {e}", fg='red')
```

**2. File Operations:**
```python
try:
    service.upload_file(file_path)
except FileNotFoundError:
    click.secho(f"File not found: {file_path}", fg='red')
except PermissionError:
    click.secho(f"Permission denied: {file_path}", fg='red')
except Exception as e:
    click.secho(f"Upload failed: {e}", fg='red')
```

**3. Validation Errors:**
```python
if not os.path.exists(file_path):
    raise ValidationError(f"File does not exist: {file_path}")
```

---

## Security Architecture

### Credential Storage

**Location:** `~/.omnidrive/config.json`

**File Permissions:** 600 (user read/write only)

**Encryption:** Future - Use keyring integration

---

### Token Management

**Strategy:**
1. Store tokens in config file
2. Validate tokens on each use
3. Refresh expired tokens automatically
4. Prompt for re-authentication if refresh fails

**Implementation:**
```python
def get_valid_token(service: str) -> str:
    token = get_token_from_config(service)
    if not is_token_valid(token):
        token = refresh_token(service)
        if not token:
            prompt_for_reauthentication(service)
    return token
```

---

### OAuth2 Flow

**Google Drive:**
1. User provides service account JSON path
2. Validate JSON file structure
3. Save path to config
4. Use Google Cloud SDK for authentication

**Folderfort:**
1. User provides email/password
2. Call Folderfort auth API
3. Receive OAuth token
4. Save token to config
5. Validate token on each use

---

## Performance Considerations

### API Rate Limiting

**Strategy:**
- Exponential backoff for retries
- Track API usage per service
- Warn when approaching limits
- Queue operations if needed

**Implementation:**
```python
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
```

---

### File Streaming

**For Large Files:**
```python
def upload_large_file(file_path):
    chunk_size = 8 * 1024 * 1024  # 8MB chunks
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            upload_chunk(chunk)
```

**Benefits:**
- ✅ Lower memory usage
- ✅ Progress tracking
- ✅ Resumable uploads

---

### Caching Strategy

**File Metadata Cache:**
- TTL: 5 minutes
- In-memory dictionary
- Invalidate on file operations

**Token Cache:**
- Persistent (config file)
- Refresh when expired
- No TTL needed

---

## Testing Strategy

### Unit Testing

**Focus:**
- Individual functions
- Class methods
- Error conditions

**Example:**
```python
def test_format_size():
    assert _format_size(0) == "0.0 B"
    assert _format_size(1024) == "1.0 KB"
    assert _format_size(1024*1024) == "1.0 MB"
```

---

### Integration Testing

**Focus:**
- Service interactions
- CLI commands
- Workflows

**Example:**
```python
def test_sync_services():
    # Mock both services
    google = Mock(spec=GoogleDriveService)
    folderfort = Mock(spec=FolderfortService)

    # Execute sync
    sync_files('google', 'folderfort')

    # Verify interactions
    google.list_files.assert_called_once()
    folderfort.upload_file.assert_called()
```

---

### End-to-End Testing

**Focus:**
- Complete user workflows
- Real API calls (staging environment)
- Performance testing

**Automation:**
- GitHub Actions CI/CD
- Test on every push
- Coverage reporting

---

## Scalability Considerations

### Current Limitations

**File Count:**
- Practical limit: ~10,000 files per service
- Pagination implemented for list operations
- Configurable limit parameter

**File Size:**
- No theoretical limit (streaming)
- Practical limit: Available disk space
- Tested up to 5GB files

---

### Future Scalability

**Horizontal Scaling:**
- Distribute across multiple machines
- Use message queue for tasks
- Shared storage for config/memory

**Vertical Scaling:**
- More memory for caching
- Faster CPU for encryption
- SSD for vector DB

---

## Monitoring & Observability (Future)

### Metrics to Track

**Technical Metrics:**
- API call latency
- Error rates
- Token refresh frequency
- File operation success rate

**User Metrics:**
- Commands executed
- Services used
- Features utilized
- Session duration

---

### Logging Strategy

**Log Levels:**
- DEBUG: Detailed diagnostic information
- INFO: General informational messages
- WARNING: Warning messages
- ERROR: Error messages
- CRITICAL: Critical failures

**Log Format:**
```python
[2025-01-24 10:30:45] [INFO] [omnidrive.cli] Command executed: list google
[2025-01-24 10:30:46] [ERROR] [omnidrive.services.google] API error: 401
```

**Log Rotation:**
- Daily log files
- Keep 30 days of logs
- Compress old logs

---

## Deployment Architecture

### Installation Methods

**1. PyPI (Primary):**
```bash
pip install omnidrive-cli
```

**2. Homebrew (macOS):**
```bash
brew tap omnidrive/tap
brew install omnidrive-cli
```

**3. Docker:**
```bash
docker pull omnidrive/cli
docker run -v ~/.omnidrive:/root/.omnidrive omnidrive/cli list google
```

---

### Update Strategy

**Versioning:**
- Semantic versioning (MAJOR.MINOR.PATCH)
- Changelog in CHANGELOG.md
- Git tags for releases

**Update Process:**
```bash
pip install --upgrade omnidrive-cli
```

---

## Internationalization (Future)

**Planned Languages:**
- English (primary)
- Spanish
- Portuguese
- French

**Implementation:**
- gettext for translations
- Locale-aware formatting
- Unicode support (UTF-8)

---

## Accessibility

**Screen Reader Support:**
- Clear text descriptions
- Aria labels (if web UI added)
- Keyboard navigation

**Color Blindness:**
- Don't rely on color alone
- Use icons + text
- High contrast mode support

---

## Documentation Strategy

### Target Audiences

**1. End Users:**
- README.md with quick start
- Command examples
- Troubleshooting guide

**2. Developers:**
- CLAUDE.md for Claude Code
- API documentation
- Architecture diagrams
- Contributing guide

**3. Contributors:**
- Development workflow
- Code style guide
- Pull request template
- Issue templates

---

### Documentation Format

**Markdown:**
- Easy to read
- Version control friendly
- GitHub renders nicely
- Code highlighting

**Diagrams:**
- ASCII art for architecture
- Mermaid for flowcharts (future)
- Screenshots for CLI usage (future)

---

## Future Enhancements

### Phase 6+ Features

**Real-time Sync:**
- File watching with inotify
- Event-driven sync
- Conflict resolution

**Advanced Workflows:**
- Conditional workflows
- Parallel execution
- Workflow composition

**Web Dashboard:**
- FastAPI backend
- Next.js frontend
- Real-time updates

---

## Design Trade-offs

### Chosen Python over Node.js

**Pros:**
- ✅ Better CLI ecosystem
- ✅ Superior AI libraries
- ✅ Simpler deployment
- ✅ More maintainable

**Cons:**
- ❌ Slower than Node.js (not critical for CLI)
- ❌ Global interpreter lock (not an issue for I/O bound)

---

### Chose CLI over GUI

**Pros:**
- ✅ Faster development
- ✅ Better for DevOps/automation
- ✅ Scriptable
- ✅ Lower resource usage

**Cons:**
- ❌ Steeper learning curve
- ❌ Less discoverable
- ❌ Not ideal for non-technical users

**Mitigation:**
- Comprehensive help text
- Clear error messages
- Examples in documentation

---

## References & Resources

**Design Inspiration:**
- `rclone` - Multi-cloud sync tool
- `aws-cli` - AWS command-line interface
- `gh` - GitHub CLI
- `kubectl` - Kubernetes CLI

**Architecture Resources:**
- Clean Architecture by Robert C. Martin
- Design Patterns: Gang of Four
- The Pragmatic Programmer

**Python Best Practices:**
- PEP 8 - Style Guide
- PEP 257 - Docstrings
- The Hitchhiker's Guide to Python

---

*Last Updated: 2025-01-24*
*Methodology: Edward Honour SaaS Blueprint*
*Phase: 5 Complete - Production Ready ✅*
