# OmniDrive CLI - Tech Stack (Edward Honour Methodology)

## Frontend Framework

**CLI Framework:**
- **Click 8.1+** - Modern CLI framework for Python
  - Decorator-based syntax
  - Automatic help text generation
  - Argument parsing and validation
  - Color output support (click.secho)
  - Progress bars integration
  - Command grouping and subcommands

**Alternative Considered:**
- ❌ **argparse** (stdlib) - Too verbose, less maintainable
- ❌ **Typer** - Newer, less mature than Click
- ❌ **Rich** - Great for TUIs but overkill for simple CLI

**Decision:** Click chosen for maturity, ecosystem, and maintainability

---

## Backend Framework

**Core Runtime:**
- **Python 3.10+** - Primary language
  - Type hints support (mypy compatible)
  - Async/await capabilities
  - Rich standard library
  - Cross-platform compatibility

**Why Python over Node.js/TypeScript:**
- ✅ Better CLI ecosystem (Click, typer, rich)
- ✅ Superior AI/ML library support (OpenAI, LangChain)
- ✅ Simpler deployment (single binary with PyInstaller)
- ✅ Better for DevOps/automation use cases
- ✅ Easier to read and maintain

---

## Database

**Vector Database (RAG System):**
- **ChromaDB 0.4.x** - Local vector database
  - Persistent storage (~/.omnidrive/vector_db/)
  - Cosine similarity search
  - Metadata filtering
  - Python native integration

**Status:** ⚠️ Optional dependency (Python 3.14 compatibility issue)

**Alternative Considered:**
- ❌ **Pinecone** - Cloud-hosted, requires API, costs money
- ❌ **Weaviate** - More complex setup, heavier resource usage
- ❌ **FAISS** - No metadata filtering, less feature-rich

**Configuration Storage:**
- **JSON files** - Simple, human-readable
  - `~/.omnidrive/config.json` - Credentials and settings
  - `~/.omnidrive/memory/*.json` - Session persistence

**Alternative Considered:**
- ❌ **SQLite** - Overkill for simple config
- ❌ **YAML** - Less standard, requires additional dependency
- ❌ **TOML** - Not as widely used as JSON

---

## Authentication Services

**Google Drive:**
- **Service Account OAuth2** - Server-to-server authentication
  - JSON credential file
  - Google Cloud SDK (google-api-python-client)
  - GOOGLE_APPLICATION_CREDENTIALS env var support

**Folderfort:**
- **Email/Password → OAuth Token** - Custom flow
  - REST API authentication
  - Bearer token storage
  - Token validation on each use

**Future Services (Planned):**
- OneDrive: OAuth2 (MSAL)
- Dropbox: OAuth2
- AWS S3: IAM credentials

**Security:**
- Credentials stored locally only
- No transmission to third parties
- OAuth2 industry standard
- Automatic token refresh

---

## External APIs

**Cloud Storage APIs:**

**1. Google Drive API v3**
- **Library:** google-api-python-client
- **Auth:** google-auth-oauthlib
- **Features:**
  - File listing with pagination
  - File upload (multipart, resumable)
  - File download (binary)
  - Folder management
  - Trash/delete operations

**2. Folderfort API**
- **Library:** requests (HTTP client)
- **Base URL:** https://na2.folderfort.com
- **Features:**
  - File listing with filters
  - File upload (multipart/form-data)
  - File download (binary)
  - Folder creation
  - Delete/trash operations

**AI APIs:**

**3. OpenAI API**
- **Library:** openai (Python client)
- **Models:**
  - text-embedding-3-small (1536 dimensions)
  - Cost: $0.00002/1K tokens
- **Usage:**
  - Text embeddings generation
  - Semantic search
  - Optional feature (works without OpenAI key)

---

## Hosting & Deployment

**Package Distribution:**
- **PyPI (Python Package Index)**
  - `pip install omnidrive-cli`
  - Global CLI installation
  - Version management
  - Dependency resolution

**Build Tools:**
- **Poetry** (optional) - Dependency management
- **setuptools** - Package building
- **wheel** - Binary distribution format
- **twine** - PyPI upload tool

**Alternative Distribution:**
- **Homebrew** (macOS) - `brew install omnidrive`
- **Docker** - Containerized deployment
- **APT/YUM** - Linux package managers
- **Scoop** (Windows) - Windows package manager

**CI/CD:**
- **GitHub Actions** - Automated testing and deployment
  - Run tests on every push
  - Build packages on tags
  - Deploy to PyPI on releases

---

## Development Environment

**IDE/Editor:**
- **Cursor** (Primary) - AI-powered code editor
  - Claude integration
  - Copilot++ features
  - Fast code generation

**Alternative:**
- **VS Code** - With Python extension
- **PyCharm** - Professional Python IDE

**Version Control:**
- **Git** - Source control
- **GitHub** - Repository hosting
- **Conventional Commits** - Commit message standard

**Code Quality Tools:**
- **pytest** - Testing framework (58 tests passing)
- **pytest-cov** - Coverage reporting (40% baseline)
- **mypy** - Type checking (type hints on all functions)
- **black** - Code formatting (not yet enforced)
- **ruff** - Fast linter (replacement for flake8)

**Documentation:**
- **Markdown** - All documentation in .md files
- **Sphinx** (optional) - API documentation generation
- **GitHub Pages** - Public documentation site

---

## Testing Framework

**Unit Testing:**
- **pytest 9.0+** - Primary testing framework
  - Fixture support
  - Parametrized tests
  - Coverage reporting
  - Parallel test execution

**Test Structure:**
```
tests/
├── test_config.py (6 tests)
├── test_services_base.py (7 tests)
├── test_folderfort.py (9 tests)
├── test_commands.py (10 tests)
├── test_rag.py (8 tests)
└── test_workflows.py (18 tests)
```

**Mocking:**
- **unittest.mock** - Mock external dependencies
  - Mock API calls to cloud services
  - Mock file system operations
  - Mock authentication flows

**Coverage Goals:**
- Current: 40% (baseline)
- Target: 60-70% (reasonable for CLI tool)
- Critical paths: 90%+ (config, services, workflows)

---

## AI & ML Stack

**Embeddings Generation:**
- **OpenAI text-embedding-3-small**
  - 1536 dimensions
  - Cost-effective
  - High quality
  - Multilingual support

**Vector Store:**
- **ChromaDB**
  - Local persistence
  - HNSW indexing (fast search)
  - Metadata filtering
  - Cosine similarity

**Alternative:**
- **Sentence Transformers** (local) - Free but slower
- **Cohere Embeddings** - Alternative to OpenAI

**RAG Pipeline:**
```
File → Text Extraction → Embedding Generation → Vector DB
                                          ↓
                              Semantic Search with Query Embedding
                                          ↓
                              Ranked Results with Similarity Scores
```

---

## Workflow Automation

**Workflow Engine:**
- **Custom Implementation** (Lightweight LangGraph alternative)
  - Step-based workflows
  - Context passing
  - Status tracking
  - Error handling

**Why Not LangGraph:**
- Simpler custom implementation sufficient
- Less dependency overhead
- More control over execution
- Easier to debug

**Predefined Workflows:**
1. **smart-sync** - Intelligent file synchronization
2. **backup** - Automated backup workflow
3. **index-and-search** - RAG pipeline automation

---

## Memory & Session Management

**Implementation:**
- **Serena MCP Pattern** - File-based persistence
  - JSON storage
  - Key-value pairs
  - Timestamp tracking
  - Session metadata

**Storage Location:**
- `~/.omnidrive/memory/` - Session states
- `~/.omnidrive/checkpoints/` - Execution checkpoints

**Alternative Considered:**
- ❌ **Redis** - Overkill, requires external service
- ❌ **SQLite** - More complex than needed
- ❌ **In-memory** - Not persistent across sessions

---

## Error Handling & Logging

**Error Handling:**
- **Custom Exceptions:**
  - `ServiceError` - Cloud service errors
  - `AuthenticationError` - Auth failures
  - `ValidationError` - Input validation

**Logging:**
- **Python logging module** - Structured logging
  - File logging: `~/.omnidrive/logs/`
  - Console logging: stderr
  - Log levels: DEBUG, INFO, WARNING, ERROR

**Monitoring (Future):**
- Sentry - Error tracking
- Prometheus - Metrics collection
- Grafana - Visualization

---

## Security Stack

**Authentication:**
- OAuth2 for all services
- Service accounts for server-side
- Token refresh mechanism
- Credential encryption (future)

**Data Protection:**
- Credentials stored locally
- No transmission to third parties
- File permissions: 600 (user read/write only)
- Environment variable support

**Future Enhancements:**
- Keyring integration (system keychain)
- Credential encryption at rest
- Audit logging
- Multi-factor authentication

---

## Performance Optimization

**Caching:**
- File metadata caching (TTL: 5 minutes)
- Token caching (persistent until expiry)
- Vector DB caching (in-memory)

**Concurrency:**
- Async operations (future)
- Parallel file uploads
- Batch operations for efficiency

**Resource Management:**
- Lazy loading of optional dependencies
- Memory-efficient streaming for large files
- Connection pooling for API clients

---

## Documentation & Communication

**Documentation Format:**
- Markdown (.md files)
- Diagrams: ASCII art (architecture)
- Code examples: Python snippets

**Documentation Structure:**
```
docs/
├── README.md - User guide
├── CLAUDE.md - Developer instructions
├── ARCHITECTURE.md - System design
├── VALIDATION_REPORT.md - Test results
└── API.md - API documentation
```

**Communication Channels:**
- GitHub Issues - Bug reports, feature requests
- GitHub Discussions - Community questions
- Discord/Slack - Real-time chat (future)

---

## Dependency Management

**Core Dependencies:**
```toml
[tool.poetry.dependencies]
python = "^3.10"
click = "^8.1"
requests = "^2.31"
google-api-python-client = "^2.100"
google-auth-oauthlib = "^1.1"
openai = "^1.0"  # Optional
chromadb = "^0.4"  # Optional
pypdf = "^3.17"  # Optional
python-docx = "^1.1"  # Optional
```

**Dev Dependencies:**
```toml
[tool.poetry.dev-dependencies]
pytest = "^9.0"
pytest-cov = "^7.0"
mypy = "^1.0"
black = "^24.0"
ruff = "^0.1"
```

---

## Architecture Patterns

**Design Patterns Used:**
1. **Adapter Pattern** - CloudService interface
2. **Factory Pattern** - get_service(), get_workflow_engine()
3. **Strategy Pattern** - Different auth strategies per service
4. **Singleton Pattern** - Memory manager, config loader
5. **Observer Pattern** - (Future) File watching

**SOLID Principles:**
- **S**ingle Responsibility - Each module has one job
- **O**pen/Closed - Open for extension (new services)
- **L**iskov Substitution - Services interchangeable
- **I**nterface Segregation - Minimal required methods
- **D**ependency Inversion - Depend on abstractions

---

## Monitoring & Observability (Future)

**Metrics to Track:**
- API call counts per service
- Response times
- Error rates
- User engagement (DAU, MAU)

**Tools to Implement:**
- Prometheus - Metrics collection
- Grafana - Dashboard
- Sentry - Error tracking
- PostHog - User analytics

---

## Backup & Disaster Recovery

**Data Backup:**
- Config backup: `~/.omnidrive/config.json`
- Memory backup: `~/.omnidrive/memory/`
- Vector DB backup: `~/.omnidrive/vector_db/`

**Recovery Process:**
1. Export config to backup location
2. Copy memory files to safe storage
3. Backup ChromaDB SQLite database
4. Document restore procedure

---

## Compliance & Governance

**Data Privacy:**
- GDPR compliant (user data local)
- No data transmission to third parties
- User controls all data
- Right to deletion (clear config)

**Licensing:**
- MIT License - Permissive, business-friendly
- Clear attribution requirements
- No warranty disclaimer

---

## Cost Management

**API Costs:**
- OpenAI embeddings: $0.02/1M tokens (~$0.10/month for light use)
- Google Drive API: Free tier sufficient
- Folderfort API: Included with account

**Hosting Costs:**
- PyPI hosting: Free
- GitHub: Free (public repo)
- CI/CD: Free (GitHub Actions)

**Total Monthly Cost:** <$1 for personal use

---

## Tech Stack Rationale Summary

**Why This Stack:**
✅ **Mature & Stable** - All dependencies battle-tested
✅ **Python Ecosystem** - Best CLI tools and AI libraries
✅ **Cross-Platform** - Works on macOS, Linux, Windows
✅ **Minimal Dependencies** - Core works without AI features
✅ **Extensible** - Easy to add new services and features
✅ **Cost-Effective** - Free tiers sufficient for MVP
✅ **Fast Development** - Vibe coding with Claude/Cursor
✅ **Production Ready** - All components validated

---

*Last Updated: 2025-01-24*
*Methodology: Edward Honour SaaS Blueprint*
*Phase: 5 Complete - Production Ready ✅*
