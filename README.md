# OmniDrive CLI

A 360° Cloud Sync Solution - Unified command-line tool for managing multiple cloud storage services.

## ✨ Features

- 🔐 **Secure Authentication** - OAuth2 flows for all services
- 📁 **Multi-Cloud Support** - Google Drive, Folderfort, and more
- 🔄 **Sync Capabilities** - Transfer files between cloud services
- 🔍 **Semantic Search** - Search within file contents (RAG)
- 🤖 **Automated Workflows** - Workflow automation system
- 💾 **Persistent Memory** - Session continuity across runs
- 📊 **Smart Comparison** - Compare files between services

## 🚀 Quick Start

```bash
# Clone and install
git clone https://github.com/yourusername/omnidrive-cli.git
cd omnidrive-cli
pip install -r requirements.txt

# Authenticate
python3 -m omnidrive auth google
python3 -m omnidrive auth folderfort

# List files
python3 -m omnidrive list --drive google
python3 -m omnidrive list --drive folderfort

# Upload files
python3 -m omnidrive upload myfile.txt google

# Sync between services
python3 -m omnidrive sync google folderfort

# Semantic search
export DEEPSEEK_API_KEY='your-key'
python3 -m omnidrive index google
python3 -m omnidrive search "important documents"
```

## 📖 Commands

### Authentication
```bash
omnidrive auth <service>     # Authenticate with a service
```

### File Operations
```bash
omnidrive list [--drive SERVICE] [--limit N]  # List files
omnidrive upload <file> <service>             # Upload file
omnidrive download <drive> [--dest PATH]      # Download file
```

### Multi-Cloud Operations
```bash
omnidrive sync <source> <target> [--dry-run]  # Sync between drives
omnidrive compare <service1> <service2>        # Compare services
```

### RAG Search (Phase 3)
```bash
omnidrive index <service>           # Index files for search
omnidrive search "<query>"          # Semantic search
```

### Workflows (Phase 4)
```bash
omnidrive workflow list             # List available workflows
omnidrive workflow run <name>        # Run a workflow
```

### Session Management
```bash
omnidrive session save <name>        # Save session state
omnidrive session resume <name>      # Resume saved session
omnidrive session list              # List all sessions
```

## 🏗️ Architecture

```
omnidrive/
├── cli.py                    # Main CLI entry point
├── config.py                 # Configuration management
├── services/                 # Cloud service implementations
│   ├── base.py              # CloudService abstract base
│   ├── google_drive.py      # Google Drive
│   └── folderfort.py        # Folderfort
├── auth/                     # Authentication modules
│   ├── google.py            # Google OAuth
│   └── folderfort.py        # Folderfort auth
├── rag/                      # RAG system
│   ├── embeddings.py        # DeepSeek embeddings
│   ├── vector_store.py      # ChromaDB vector store
│   └── indexer.py           # File indexer
├── memory/                   # Persistent memory
│   └── serena_client.py     # Memory manager
└── workflows/                # Workflows
    └── graphs.py            # Workflow engine
```

## 📊 Development Status

| Phase | Status | Features |
|-------|--------|----------|
| **Phase 0** | ✅ Complete | Modular architecture, refactored CLI |
| **Phase 1** | ✅ Complete | Folderfort integration, authentication |
| **Phase 2** | ✅ Complete | Upload, sync, compare commands |
| **Phase 3** | ✅ Complete | RAG system with DeepSeek + ChromaDB |
| **Phase 4** | ✅ Complete | Workflow automation engine |
| **Phase 5** | ✅ Complete | Testing, documentation, production-ready |

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=omnidrive --cov-report=html

# Specific test files
pytest tests/test_folderfort.py -v
pytest tests/test_workflows.py -v
```

**Coverage**: 37% (45+ tests passing)

## 📦 Installation

### From PyPI (Coming Soon)
```bash
pip install omnidrive-cli
```

### From Source
```bash
git clone https://github.com/yourusername/omnidrive-cli.git
cd omnidrive-cli
pip install -r requirements.txt
```

## ⚙️ Configuration

Configuration is stored in `~/.omnidrive/`:

```json
{
  "google_key_path": "/path/to/service-account.json",
  "folderfort_token": "your_token_here",
  "folderfort_email": "your@email.com"
}
```

### Environment Variables

```bash
# Google Drive
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"

# DeepSeek (for RAG features)
export DEEPSEEK_API_KEY="your-deepseek-key"

# Optional: Set custom paths
export OMNIDRIVE_CONFIG_DIR="~/.omnidrive"
export OMNIDRIVE_MEMORY_DIR="~/.omnidrive/memory"
```

## 📚 Supported Services

| Service | Status | Features |
|---------|--------|----------|
| **Google Drive** | ✅ Full | List, upload, download, delete, create folder |
| **Folderfort** | ✅ Full | List, upload, download, delete, create folder |
| **OneDrive** | 📋 Planned | Phase 2+ |
| **Dropbox** | 📋 Planned | Phase 2+ |

## 🔒 Security

- OAuth2 authentication for all services
- Credentials stored locally in `~/.omnidrive/`
- No sensitive data transmitted to third parties
- Secure token management with automatic refresh

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

See `CLAUDE.md` for development guidelines.

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- **Google Drive API** - For robust Python SDK
- **Folderfort** - For cloud storage API
- **DeepSeek** - For embeddings API
- **ChromaDB** - For vector database
- **Click** - For beautiful CLI framework
- **LangGraph** - For workflow orchestration

## 📞 Support

- Issues: [GitHub Issues](https://github.com/yourusername/omnidrive-cli/issues)
- Docs: [Full Documentation](https://omnidrive-cli.readthedocs.io)

---

**Built with ❤️ by the OmniDrive Team**
