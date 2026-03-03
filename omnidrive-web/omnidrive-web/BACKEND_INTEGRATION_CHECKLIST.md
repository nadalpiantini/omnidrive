# Backend ↔ Frontend Integration Checklist

## Quick Reference

**Backend URL:** https://omnidrive-api.up.railway.app (example)
**Frontend URL:** https://omnidrive.sujeto10.com

---

## Integration Steps

### Step 1: Run Integration Script

```bash
cd /Users/nadalpiantini/Dev/omnidrive-cli/omnidrive-web/omnidrive-web
./connect-backend.sh https://omnidrive-api.up.railway.app
```

### Step 2: Update Vercel Environment Variables

```bash
# Using Vercel CLI
vercel env add NEXT_PUBLIC_API_URL production
# Paste: https://omnidrive-api.up.railway.app
vercel --prod
```

**Or use Vercel Dashboard:**
1. Go to Settings → Environment Variables
2. Update `NEXT_PUBLIC_API_URL`
3. Save and redeploy

### Step 3: Test Connectivity

```bash
./test-backend-connection.sh https://omnidrive-api.up.railway.app
```

---

## API Endpoints to Test

### Health & Status
- [ ] `GET /health` - Backend health check
- [ ] `GET /` - API root info
- [ ] `GET /docs` - API documentation

### Authentication
- [ ] `GET /api/v1/auth/status` - Get auth status
- [ ] `POST /api/v1/auth/google` - Google auth
- [ ] `POST /api/v1/auth/folderfort` - Folderfort auth
- [ ] `POST /api/v1/auth/logout` - Logout

### Files
- [ ] `GET /api/v1/files/?service=google_drive` - List files
- [ ] `POST /api/v1/files/upload` - Upload file
- [ ] `GET /api/v1/files/{id}/download` - Download file
- [ ] `DELETE /api/v1/files/{id}` - Delete file

### Sync
- [ ] `POST /api/v1/sync/compare` - Compare services
- [ ] `POST /api/v1/sync` - Start sync
- [ ] `GET /api/v1/sync/status/{id}` - Get sync status

### Search
- [ ] `POST /api/v1/search` - Semantic search
- [ ] `POST /api/v1/index` - Index files

### Workflows
- [ ] `GET /api/v1/workflows` - List workflows
- [ ] `POST /api/v1/workflows/{name}/run` - Run workflow
- [ ] `GET /api/v1/workflows/{name}/status/{id}` - Get status

---

## Verification Checklist

### Backend (Railway)
- [ ] Backend deployed successfully
- [ ] Health endpoint returns 200
- [ ] API docs accessible
- [ ] CORS configured for frontend domains

### Frontend (Vercel)
- [ ] Environment variable updated
- [ ] Production deployed
- [ ] API calls use Railway URL
- [ ] No CORS errors in browser

### Integration Tests
- [ ] Auth flow works (Google + Folderfort)
- [ ] File listing works
- [ ] File upload works with progress
- [ ] File download works
- [ ] File deletion works
- [ ] Sync compare works
- [ ] Sync execution works
- [ ] Search functionality works

---

## Troubleshooting

### CORS Errors
1. Check backend CORS config in `main.py`
2. Verify frontend domain in `allow_origins`
3. Redeploy backend

### API Timeout
1. Check Railway backend is running
2. Test health endpoint directly
3. Check Railway logs

### Environment Variable Not Working
1. Verify set in Vercel (not .env.local)
2. Trigger new deployment
3. Hard refresh browser (Ctrl+Shift+R)

---

## Monitoring

**Backend:** https://railway.app/dashboard
**Frontend:** https://vercel.com/dashboard
**API Docs:** https://omnidrive-api.up.railway.app/docs
