# OmniDrive

Multi-cloud storage CLI and web dashboard for Google Drive and Folderfort.

## What Works Now

- **CLI**: list, upload, download, delete, sync, compare across Google Drive and Folderfort
- **Web dashboard**: browse files, upload, sync, view auth status (Next.js + FastAPI backend)
- **Desktop app**: Electron wrapper around the web dashboard (builds successfully)
- **API**: FastAPI backend with JWT auth, file operations, sync jobs

## Known Limitations

- **Semantic search indexing**: Not yet implemented. The search API exists but requires an indexing pipeline that is still in development.
- **Workflows**: LangGraph integration is stubbed; workflows are defined but not fully wired to execution.
- **Real-time sync**: No automatic/background sync. Sync is manual via CLI or dashboard.
- **OneDrive/Dropbox**: Not implemented (placeholder only).
- **Coverage**: ~40% test coverage. Core config, auth, and services have tests; integration coverage is thin.

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+ (for web/dashboard)
- Google Drive service account JSON
- Folderfort account credentials

### Backend

```bash
# Install Python dependencies
pip install -r requirements.txt

# Set required environment variables
export OMNIDRIVE_JWT_SECRET="your-random-secret-min-32-chars"
export OMNIDRIVE_ADMIN_EMAIL="admin@example.com"
export OMNIDRIVE_ADMIN_PASSWORD="your-admin-password"
export GOOGLE_SERVICE_ACCOUNT_JSON='{"type":"service_account",...}'
export FOLDERFORT_EMAIL="your@email.com"
export FOLDERFORT_PASSWORD="your-password"

# Start the API
cd omnidrive-web/api && uvicorn app.main:app --reload
```

### Web Dashboard

```bash
cd omnidrive-web/omnidrive-web
# Copy and fill environment variables
cp .env.example .env.local
# Edit .env.local with your API URL

npm install
npm run dev
```

### Desktop App

```bash
cd omnidrive-desktop
npm install
npm run build
# Output: release/OmniDrive-1.0.0-arm64-mac.zip
```

## Testing

```bash
# Python tests
pytest tests/ -v

# Python linting
ruff check omnidrive/ tests/ omnidrive-web/api/app

# Web lint
npm --prefix omnidrive-web/omnidrive-web run lint

# Web build
npm --prefix omnidrive-web/omnidrive-web run build

# Desktop build
npm --prefix omnidrive-desktop run build
```

## Architecture

```
omnidrive/
├── cli.py                    # CLI entry point
├── config.py                 # Configuration management
├── services/                 # Cloud service implementations
│   ├── base.py              # CloudService abstract base
│   ├── google_drive.py      # Google Drive
│   └── folderfort.py        # Folderfort
├── auth/                     # Authentication modules
│   ├── google.py
│   └── folderfort.py
├── rag/                      # RAG system (partial)
│   ├── embeddings.py
│   ├── vector_store.py
│   └── indexer.py
├── memory/                   # Session persistence
│   └── serena_client.py
└── workflows/                # Workflow engine (stubbed)
    └── graphs.py

omnidrive-web/
├── api/app/                  # FastAPI backend
│   ├── api/routes/          # Auth, files, sync, search
│   ├── auth/jwt.py          # JWT utilities
│   └── main.py
└── omnidrive-web/           # Next.js frontend
    ├── app/dashboard/       # Files, upload, sync, search pages
    ├── lib/api.ts           # API client
    └── lib/websocket.ts     # Real-time updates

omnidrive-desktop/
├── electron/main.ts         # Electron main process
├── package.json             # Electron builder config
└── dist-electron/           # Build output
```

## Environment Variables

See `.env.omnidrive.template` for the full list. The most important ones:

| Variable | Required For | Description |
|----------|-------------|-------------|
| `OMNIDRIVE_JWT_SECRET` | Web API | Signing key for JWT tokens (min 32 chars) |
| `OMNIDRIVE_ADMIN_EMAIL` | Web API | Admin login email |
| `OMNIDRIVE_ADMIN_PASSWORD` | Web API | Admin login password |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Google Drive | Service account JSON (single-line) |
| `FOLDERFORT_EMAIL` | Folderfort | Login email |
| `FOLDERFORT_PASSWORD` | Folderfort | Login password |
| `NEXT_PUBLIC_API_URL` | Web frontend | Backend URL (e.g. http://localhost:8000) |
| `NEXT_PUBLIC_WS_URL` | Web frontend | WebSocket URL |

## Security Notes

- JWT secret must be strong and unique per deployment
- Admin credentials are read from environment variables only (no hardcoded defaults in production)
- Google service account JSON is stored in config; handle it as a credential
- Folderfort password is exchanged for a token on auth; token is stored, password is not

## License

MIT
