# OmniDrive Hybrid Architecture - Implementation Plan

## 🎯 Vision: CLI + Web Dashboard Unificado

**Arquitectura Híbrida:**
```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Layer                            │
├─────────────────────────────────────────────────────────────┤
│  CLI (Python)           │     Web Dashboard (Next.js)        │
│  • Click Framework      │     • React + TailwindCSS          │
│  • Terminal UI          │     • Modern UI/UX                 │
│  • Scripts/automation   │     • Drag & drop                   │
│  • Power users          │     • Visual feedback              │
└──────────┬──────────────┴──────────────┬────────────────────┘
           │                            │
           │    REST API + WebSocket    │
           └────────────┬───────────────┘
                        │
┌────────────────────────▼────────────────────────────────────┐
│                  Backend API (FastAPI)                       │
├─────────────────────────────────────────────────────────────┤
│  • Authentication (JWT)                                      │
│  • File operations (list, upload, download)                  │
│  • Cross-service sync                                       │
│  • Semantic search (RAG)                                     │
│  • Workflows execution                                      │
│  • Session management                                       │
│  • WebSocket (real-time updates)                            │
└────────────────────────┬────────────────────────────────────┘
                         │
    ┌────────────────────┼────────────────────┐
    │                    │                    │
┌───▼────┐         ┌────▼─────┐      ┌──────▼──────┐
│Google  │         │Folderfort│      │Vector Store  │
│Drive   │         │          │      │  (ChromaDB)  │
└────────┘         └──────────┘      └─────────────┘
```

---

## 📋 Phase 1: FastAPI Backend (Week 1)

### 1.1 Project Structure
```
omnidrive-api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app
│   ├── config.py               # Settings
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── jwt.py              # JWT auth
│   │   └── middleware.py       # Auth middleware
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── files.py        # File operations
│   │   │   ├── auth.py         # Authentication
│   │   │   ├── sync.py         # Cross-service sync
│   │   │   ├── search.py       # Semantic search
│   │   │   └── workflows.py    # Workflow execution
│   │   └── websocket/
│   │       └── handler.py      # WebSocket handler
│   ├── services/
│   │   ├── __init__.py
│   │   └── cloud_service.py    # Service factory
│   └── models/
│       ├── __init__.py
│       ├── requests.py         # Request models
│       └── responses.py        # Response models
├── tests/
├── requirements.txt
├── Dockerfile
└── railway.json                # Railway deployment
```

### 1.2 API Endpoints

**Authentication:**
```python
POST   /api/v1/auth/google         # Google OAuth
POST   /api/v1/auth/folderfort    # Folderfort OAuth
GET    /api/v1/auth/status        # Auth status
POST   /api/v1/auth/logout        # Logout
```

**Files:**
```python
GET    /api/v1/files              # List files
POST   /api/v1/files/upload       # Upload file
GET    /api/v1/files/{file_id}    # Get file metadata
DELETE /api/v1/files/{file_id}    # Delete file
GET    /api/v1/files/{file_id}/download  # Download file
```

**Sync:**
```python
POST   /api/v1/sync               # Sync between services
GET    /api/v1/sync/compare       # Compare services
GET    /api/v1/sync/status/{job_id}  # Sync job status
```

**Search:**
```python
POST   /api/v1/search             # Semantic search
POST   /api/v1/index              # Index files
```

**Workflows:**
```python
GET    /api/v1/workflows          # List workflows
POST   /api/v1/workflows/{name}/run  # Run workflow
GET    /api/v1/workflows/{name}/status/{job_id}  # Status
```

**WebSocket:**
```python
WS     /ws/updates                # Real-time updates
```

### 1.3 Technology Stack

**Backend:**
- FastAPI 0.104+ - Modern Python web framework
- uvicorn - ASGI server
- pydantic v2 - Data validation
- python-jose - JWT handling
- passlib[bcrypt] - Password hashing
- python-multipart - File uploads
- websockets - Real-time updates

**Database (Future):**
- PostgreSQL - User accounts, sessions, sync jobs
- Redis - Job queue, caching

---

## 📋 Phase 2: Next.js Frontend (Week 1-2)

### 2.1 Project Structure
```
omnidrive-web/
├── src/
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── login/
│   │   │   └── layout.tsx
│   │   ├── dashboard/
│   │   │   ├── page.tsx          # Main dashboard
│   │   │   ├── files/
│   │   │   │   └── page.tsx      # File browser
│   │   │   ├── upload/
│   │   │   │   └── page.tsx      # Upload interface
│   │   │   ├── sync/
│   │   │   │   └── page.tsx      # Sync interface
│   │   │   ├── search/
│   │   │   │   └── page.tsx      # Semantic search
│   │   │   └── workflows/
│   │   │       └── page.tsx      # Workflow management
│   │   ├── api/
│   │   │   └── [...proxy]        # API proxy to backend
│   │   ├── layout.tsx            # Root layout
│   │   └── page.tsx              # Home/landing
│   ├── components/
│   │   ├── ui/
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── input.tsx
│   │   │   └── modal.tsx
│   │   ├── files/
│   │   │   ├── FileList.tsx
│   │   │   ├── FileCard.tsx
│   │   │   └── FileIcon.tsx
│   │   ├── upload/
│   │   │   ├── DropZone.tsx
│   │   │   └── UploadProgress.tsx
│   │   ├── sync/
│   │   │   ├── SyncInterface.tsx
│   │   │   └── SyncProgress.tsx
│   │   └── search/
│   │       ├── SearchBar.tsx
│   │       └── SearchResult.tsx
│   ├── lib/
│   │   ├── api.ts                # API client
│   │   ├── auth.ts               # Auth utilities
│   │   └── websocket.ts          # WebSocket client
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useFiles.ts
│   │   └── useWebSocket.ts
│   └── types/
│       └── index.ts              # TypeScript types
├── public/
├── tailwind.config.ts
├── next.config.js
└── package.json
```

### 2.2 UI Components

**Dashboard:**
- Service selector (Google Drive, Folderfort)
- File browser with grid/list views
- Quick actions (upload, sync, search)
- Recent activity
- Storage usage

**File Browser:**
- Folder navigation
- File cards with icons
- Bulk selection
- Context menu (download, delete, move)
- Search/filter

**Upload Interface:**
- Drag & drop zone
- File picker
- Progress bars
- Upload queue
- Auto-retry on failure

**Sync Interface:**
- Visual service comparison
- File diff view
- Sync direction selector
- Progress tracking
- Conflict resolution

**Search Interface:**
- Search bar
- Filter by service
- Results with relevance score
- Content preview
- Open in cloud storage

### 2.3 Technology Stack

**Frontend:**
- Next.js 14 (App Router)
- React 18+
- TypeScript 5+
- TailwindCSS 3+
- shadcn/ui components
- React Query (TanStack Query)
- Zustand (state management)
- React Hook Form
- Zod (validation)

**Styling:**
- TailwindCSS
- shadcn/ui
- Framer Motion (animations)

---

## 📋 Phase 3: Deployment (Week 2)

### 3.1 Backend Deployment

**Railway:**
1. Create Railway project
2. Link GitHub repo
3. Configure build command
4. Set environment variables
5. Deploy

**Environment Variables:**
```bash
# Railway
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
JWT_SECRET=your-secret-key
OPENAI_API_KEY=sk-...
GOOGLE_APPLICATION_CREDENTIALS=/app/secrets/google-key.json
```

### 3.2 Frontend Deployment

**Vercel:**
1. Connect GitHub repo
2. Configure build settings
3. Set environment variables
4. Deploy

**Environment Variables:**
```bash
# Vercel
NEXT_PUBLIC_API_URL=https://omnidrive-api.sujeto10.com
NEXT_PUBLIC_WS_URL=wss://omnidrive-api.sujeto10.com
```

### 3.3 DNS Configuration

**omnidrive.sujeto10.com:**
```
A Record: omnidrive → 76.76.21.21 (Vercel)
CNAME: api → railway.app
```

---

## 📋 Phase 4: Testing & Launch (Week 2)

### 4.1 Testing Checklist

**Backend:**
- ✅ All API endpoints tested
- ✅ WebSocket connection stable
- ✅ File upload/download works
- ✅ Authentication flow works
- ✅ Error handling comprehensive

**Frontend:**
- ✅ All UI components working
- ✅ Responsive design (mobile/tablet/desktop)
- ✅ Browser compatibility (Chrome, Firefox, Safari)
- ✅ Accessibility (WCAG 2.1 AA)
- ✅ Performance (<3s LCP)

**Integration:**
- ✅ End-to-end user flows
- ✅ Real file operations
- ✅ Cross-service sync
- ✅ Semantic search
- ✅ Workflow execution

### 4.2 Launch Checklist

**Pre-launch:**
- ✅ SSL certificates configured
- ✅ Monitoring setup (Sentry)
- ✅ Analytics ready (PostHog)
- ✅ Documentation complete
- ✅ Support email configured

**Launch:**
- ✅ DNS propagation complete
- ✅ Backend deployed
- ✅ Frontend deployed
- ✅ Smoke tests passing
- ✅ Monitoring alerts configured

---

## 🔑 Authentication Flow

**1. Google Drive OAuth:**
```
User clicks "Connect Google"
→ Redirect to Google OAuth consent screen
→ User approves
→ Callback to frontend with code
→ Frontend sends code to backend
→ Backend exchanges for token
→ Backend stores token securely
→ Backend returns JWT to frontend
→ Frontend stores JWT in httpOnly cookie
```

**2. Folderfort Email/Password:**
```
User enters email/password
→ Frontend sends to backend (HTTPS)
→ Backend validates with Folderfort API
→ Backend stores token
→ Backend returns JWT to frontend
→ Frontend stores JWT in httpOnly cookie
```

**3. JWT Validation:**
```
Every API request includes JWT
→ Backend validates JWT
→ Extracts user/service info
→ Proceeds with request
```

---

## 🔄 Real-time Updates (WebSocket)

**Events:**
```python
# Server → Client
{
  "type": "upload_progress",
  "data": {
    "file_id": "abc123",
    "progress": 45,
    "status": "uploading"
  }
}

{
  "type": "sync_complete",
  "data": {
    "job_id": "xyz789",
    "files_synced": 23,
    "status": "completed"
  }
}

{
  "type": "file_added",
  "data": {
    "file": {...}
  }
}
```

---

## 📊 Key Features Implementation

### 1. File Upload with Progress

**Backend:**
```python
@app.post("/api/v1/files/upload")
async def upload_file(
    file: UploadFile,
    service: str,
    background_tasks: BackgroundTasks
):
    # Stream upload to cloud service
    # Broadcast progress via WebSocket
    # Return file metadata
```

**Frontend:**
```tsx
const { mutate, progress } = useUpload();

<DropZone onUpload={(files) => mutate(files)} />
<ProgressBar value={progress} />
```

### 2. Cross-Service Sync

**Backend:**
```python
@app.post("/api/v1/sync")
async def sync_services(
    source: str,
    target: str,
    background_tasks: BackgroundTasks
):
    job_id = create_job()
    background_tasks.add_task(run_sync, job_id, source, target)
    return {"job_id": job_id}
```

**Frontend:**
```tsx
const sync = () => {
  mutate({ source: 'google', target: 'folderfort' })
}

useEffect(() => {
  // Subscribe to WebSocket updates
  ws.on('sync_progress', (data) => {
    setSyncProgress(data)
  })
}, [])
```

### 3. Semantic Search

**Backend:**
```python
@app.post("/api/v1/search")
async def semantic_search(query: str, service: str = None):
    # Generate query embedding
    # Search vector store
    # Return ranked results
```

**Frontend:**
```tsx
<SearchBar
  onSearch={(query) => search(query)}
  placeholder="Search in file contents..."
/>
<SearchResults results={data} />
```

---

## 🎨 UI/UX Design Principles

**1. Simplicity First:**
- Clean, minimal interface
- Clear visual hierarchy
- Intuitive navigation

**2. Visual Feedback:**
- Loading states
- Progress indicators
- Success/error messages
- Hover effects

**3. Accessibility:**
- Keyboard navigation
- Screen reader support
- High contrast mode
- Focus indicators

**4. Responsive:**
- Mobile-first design
- Breakpoints: 640px, 768px, 1024px, 1280px
- Touch-friendly targets (44px min)

**5. Performance:**
- Code splitting
- Lazy loading
- Image optimization
- API response caching

---

## 📈 Success Metrics

**Technical:**
- API response time: <200ms (p95)
- WebSocket latency: <100ms
- Frontend LCP: <2.5s
- Uptime: >99.9%

**User:**
- Time to first upload: <2 minutes
- Sync success rate: >99%
- Search relevance: >80%
- User satisfaction: >4.5/5

**Business:**
- Monthly active users: >100 (Month 1)
- Files uploaded: >1,000 (Month 1)
- Sync operations: >500 (Month 1)
- Searches performed: >200 (Month 1)

---

## 🚀 Getting Started

**Prerequisites:**
- Node.js 18+
- Python 3.10+
- Google account (for testing)
- Folderfort account (for testing)

**Local Development:**
```bash
# Backend
cd omnidrive-api
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd omnidrive-web
npm install
npm run dev
```

Access:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 📝 Next Steps

1. ✅ Create FastAPI backend structure
2. ✅ Implement authentication endpoints
3. ✅ Create file operation endpoints
4. ✅ Implement WebSocket handler
5. ✅ Create Next.js project
6. ✅ Build dashboard UI
7. ✅ Implement file upload UI
8. ✅ Create sync interface
9. ✅ Deploy to Railway + Vercel
10. ✅ Configure DNS
11. ✅ Test end-to-end
12. ✅ Launch! 🚀

---

*Last Updated: 2025-01-24*
*Status: Planning Complete - Ready to Build*
