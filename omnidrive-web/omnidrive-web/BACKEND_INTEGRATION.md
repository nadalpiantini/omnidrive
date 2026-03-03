# Backend ↔ Frontend Integration Guide

## Overview

This guide covers connecting the OmniDrive frontend (Vercel) with the backend API (Railway).

## Prerequisites

✅ Backend deployed on Railway
✅ Frontend deployed on Vercel
✅ Railway URL obtained (e.g., `https://omnidrive-api.up.railway.app`)

---

## Quick Start

### 1. Run Integration Script

```bash
cd /Users/nadalpiantini/Dev/omnidrive-cli/omnidrive-web/omnidrive-web
./connect-backend.sh https://omnidrive-api.up.railway.app
```

This script:
- ✅ Updates `.env.production` with Railway URL
- ✅ Tests backend connectivity
- ✅ Creates test scripts
- ✅ Provides deployment instructions

### 2. Update Vercel Environment Variables

**Option A: Vercel CLI**
```bash
vercel env add NEXT_PUBLIC_API_URL production
# Paste: https://omnidrive-api.up.railway.app
vercel --prod
```

**Option B: Vercel Dashboard**
1. Go to https://vercel.com/dashboard
2. Select `omnidrive-web` project
3. Settings → Environment Variables
4. Update `NEXT_PUBLIC_API_URL` with Railway URL
5. Save and redeploy

### 3. Verify Integration

```bash
./test-backend-connection.sh https://omnidrive-api.up.railway.app
```

### 4. Test in Production

Visit: https://omnidrive.sujeto10.com

Open DevTools (F12):
- **Network Tab**: Check API calls to Railway URL
- **Console Tab**: Verify no CORS errors

---

## Files Modified

### Frontend

**`.env.production`**
```env
NEXT_PUBLIC_API_URL=https://omnidrive-api.up.railway.app
```

**`lib/api.ts`** (No changes needed)
- Uses `process.env.NEXT_PUBLIC_API_URL` automatically
- Falls back to `http://localhost:8000` for development

### Backend (if CORS update needed)

**`omnidrive-web/api/app/main.py`** (lines 40-50)

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://omnidrive.sujeto10.com",
        "https://omnidrive-web.vercel.app",
        # Add your custom domain if different
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## API Endpoints

### Health & Status

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Backend health check |
| `/` | GET | API info and docs link |
| `/docs` | GET | Swagger UI documentation |

### Authentication

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/status` | GET | Get current auth status |
| `/api/v1/auth/google` | POST | Authenticate Google Drive |
| `/api/v1/auth/folderfort` | POST | Authenticate Folderfort |
| `/api/v1/auth/logout` | POST | Logout from all services |

### Files

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/files/` | GET | List files from service |
| `/api/v1/files/upload` | POST | Upload file to service |
| `/api/v1/files/{id}/download` | GET | Download file |
| `/api/v1/files/{id}` | DELETE | Delete file |

### Sync

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/sync/compare` | POST | Compare two services |
| `/api/v1/sync` | POST | Start sync operation |
| `/api/v1/sync/status/{id}` | GET | Get sync job status |

### Search

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/search` | POST | Semantic search |
| `/api/v1/index` | POST | Index files for search |

### Workflows

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/workflows` | GET | List available workflows |
| `/api/v1/workflows/{name}/run` | POST | Run workflow |
| `/api/v1/workflows/{name}/status/{id}` | GET | Get workflow status |

---

## Testing Examples

### Test Health Endpoint

```bash
curl https://omnidrive-api.up.railway.app/health
```

Expected:
```json
{
  "status": "healthy",
  "services": {
    "google_drive": "available",
    "folderfort": "available"
  }
}
```

### Test Auth Status

```bash
curl https://omnidrive-api.up.railway.app/api/v1/auth/status
```

Expected:
```json
{
  "google_authenticated": false,
  "folderfort_authenticated": false
}
```

### Test with Frontend

```javascript
// In browser console on https://omnidrive.sujeto10.com
fetch(`${process.env.NEXT_PUBLIC_API_URL}/health`)
  .then(r => r.json())
  .then(console.log)
```

---

## Troubleshooting

### CORS Errors

**Symptoms:** Browser shows "CORS policy: No 'Access-Control-Allow-Origin' header"

**Solution:**
1. Check backend CORS configuration in `main.py`
2. Verify `https://omnidrive.sujeto10.com` is in `allow_origins`
3. Redeploy backend on Railway
4. Clear browser cache

**Test CORS:**
```bash
curl -X OPTIONS https://omnidrive-api.up.railway.app/api/v1/auth/status \
  -H "Origin: https://omnidrive.sujeto10.com" \
  -H "Access-Control-Request-Method: GET" -v
```

### API Timeout

**Symptoms:** API calls timeout or fail

**Solution:**
1. Check Railway dashboard for backend status
2. Test health endpoint directly
3. Check backend logs in Railway
4. Verify URL is correct

**Test Health:**
```bash
curl https://omnidrive-api.up.railway.app/health
```

### Environment Variable Not Working

**Symptoms:** Frontend still uses localhost API

**Solution:**
1. Verify variable is set in Vercel (not just `.env.local`)
2. Check Vercel build logs
3. Trigger new deployment
4. Hard refresh browser (Ctrl+Shift+R)

**Check Vercel Env:**
```bash
vercel env ls
```

### WebSocket Connection Issues

**Symptoms:** WebSocket errors in console

**Solution:**
1. Verify WebSocket URL format: `wss://` (not `https://`)
2. Test WebSocket connection

**Test WebSocket:**
```javascript
const ws = new WebSocket('wss://omnidrive-api.up.railway.app/ws');
ws.onopen = () => console.log('✅ Connected');
ws.onerror = (e) => console.error('❌ Error:', e);
ws.onmessage = (e) => console.log('📨:', e.data);
```

---

## Monitoring

### Backend (Railway)
- **Dashboard**: https://railway.app/dashboard
- **Metrics**: CPU, Memory, Network usage
- **Logs**: Real-time application logs
- **Deployments**: Deployment history and status

### Frontend (Vercel)
- **Dashboard**: https://vercel.com/dashboard
- **Deployments**: Build logs and deployment history
- **Analytics**: Page views, visitors, geography
- **Speed Insights**: Core Web Vitals and performance

---

## Performance Targets

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Initial page load | < 3s | Lighthouse / WebPageTest |
| API response time | < 500ms (p95) | Railway metrics |
| File list load | < 1s | Browser DevTools |
| File upload | Real-time progress | Frontend UI |

---

## Security Checklist

- [ ] HTTPS enabled on both domains
- [ ] CORS properly configured
- [ ] Environment variables not exposed
- [ ] API rate limiting configured (future)
- [ ] Input validation on backend
- [ ] Authentication tokens secured
- [ ] Secrets managed in Railway/Vercel

---

## Next Steps

1. ✅ Complete integration
2. ✅ Run connectivity tests
3. ✅ Verify all API endpoints
4. ✅ Test authentication flows
5. ✅ Test file operations
6. ✅ Test sync functionality
7. ✅ Load testing and optimization
8. ✅ Monitor production metrics

---

## Support

- **API Documentation**: https://omnidrive-api.up.railway.app/docs
- **Backend Logs**: Railway dashboard
- **Frontend Logs**: Vercel dashboard
- **Issue Tracker**: GitHub Issues

---

## Rollback Procedure

If integration causes issues:

### Frontend Rollback
```bash
# Revert to previous Vercel deployment
vercel rollback
```

### Backend Rollback
1. Go to Railway dashboard
2. Select backend project
3. Click on "Deployments"
4. Find previous working deployment
5. Click "Redeploy"

---

## Additional Resources

- **Vercel Docs**: https://vercel.com/docs
- **Railway Docs**: https://docs.railway.app
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Next.js Docs**: https://nextjs.org/docs
