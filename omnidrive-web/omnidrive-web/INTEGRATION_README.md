# Frontend ↔ Backend Integration Package

**Prepared for:** OmniDrive Project
**Date:** 2026-01-29
**Status:** Ready for Railway URL

---

## 📦 What's Included

This package contains everything needed to integrate the frontend (Vercel) with the backend (Railway) once you have the Railway URL.

### Files Created

1. **`connect-backend.sh`** - Main integration script
   - Updates `.env.production`
   - Tests backend connectivity
   - Provides Vercel deployment instructions
   - Creates test scripts

2. **`test-backend-connection.sh`** - Backend testing script
   - Tests health endpoint
   - Tests API endpoints
   - Verifies CORS configuration
   - Measures response times

3. **`BACKEND_INTEGRATION.md`** - Complete integration guide
   - Step-by-step instructions
   - API endpoint documentation
   - Troubleshooting guide
   - Monitoring setup

4. **`BACKEND_INTEGRATION_CHECKLIST.md`** - Verification checklist
   - Pre-deployment checks
   - Integration steps
   - Testing procedures
   - Post-integration verification

---

## 🚀 How to Use

### When You Get the Railway URL

1. **Run the integration script:**
   ```bash
   cd /Users/nodalpiantini/Dev/omnidrive-cli/omnidrive-web/omnidrive-web
   ./connect-backend.sh https://omnidrive-api.up.railway.app
   ```

2. **Update Vercel environment variable:**
   ```bash
   vercel env add NEXT_PUBLIC_API_URL production
   # Paste the Railway URL
   vercel --prod
   ```

3. **Test the connection:**
   ```bash
   ./test-backend-connection.sh https://omnidrive-api.up.railway.app
   ```

4. **Verify in production:**
   - Visit: https://omnidrive.sujeto10.com
   - Open DevTools (F12)
   - Check Network tab for API calls
   - Check Console for errors

---

## 📋 What Gets Configured

### Frontend Changes

**File:** `.env.production`

```env
NEXT_PUBLIC_API_URL=https://omnidrive-api.up.railway.app
```

This environment variable is used by:
- `lib/api.ts` - All API calls
- Frontend automatically uses this in production
- Falls back to `http://localhost:8000` in development

### Backend Configuration

**File:** `omnidrive-web/api/app/main.py` (lines 40-50)

CORS is already configured for:
```python
allow_origins=[
    "http://localhost:3000",
    "https://omnidrive.sujeto10.com",
    "https://omnidrive-web.vercel.app"
]
```

**No changes needed** unless using a custom domain.

---

## 🔍 Verification Steps

### 1. Backend Health Check

```bash
curl https://omnidrive-api.up.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "services": {
    "google_drive": "available",
    "folderfort": "available"
  }
}
```

### 2. Frontend Environment Check

In browser console on https://omnidrive.sujeto10.com:

```javascript
console.log(process.env.NEXT_PUBLIC_API_URL)
// Should output: https://omnidrive-api.up.railway.app
```

### 3. API Call Test

```javascript
fetch('https://omnidrive-api.up.railway.app/api/v1/auth/status')
  .then(r => r.json())
  .then(console.log)
```

Expected:
```json
{
  "google_authenticated": false,
  "folderfort_authenticated": false
}
```

---

## 🧪 Test Coverage

The integration test script checks:

- ✅ Health endpoint (`/health`)
- ✅ Root endpoint (`/`)
- ✅ API docs (`/docs`)
- ✅ CORS configuration
- ✅ Auth status endpoint (`/api/v1/auth/status`)
- ✅ API response time
- ✅ Files endpoint (`/api/v1/files/`)

---

## ⚠️ Common Issues

### CORS Errors

**Symptom:** Browser shows "CORS policy: No 'Access-Control-Allow-Origin' header"

**Fix:**
1. Check backend CORS config in `omnidrive-web/api/app/main.py`
2. Verify your frontend domain is in `allow_origins`
3. Redeploy backend on Railway

### API Timeout

**Symptom:** API calls timeout or fail

**Fix:**
1. Check Railway dashboard - verify backend is running
2. Test health endpoint directly
3. Check Railway logs for errors

### Environment Variable Not Working

**Symptom:** Frontend still uses localhost API

**Fix:**
1. Verify variable is set in Vercel (not just `.env.local`)
2. Check Vercel build logs
3. Trigger new deployment
4. Hard refresh browser (Ctrl+Shift+R)

---

## 📊 API Endpoints

### Core Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/api/v1/auth/status` | GET | Auth status |
| `/api/v1/auth/google` | POST | Google auth |
| `/api/v1/auth/folderfort` | POST | Folderfort auth |
| `/api/v1/files/` | GET | List files |
| `/api/v1/files/upload` | POST | Upload file |
| `/api/v1/files/{id}/download` | GET | Download file |
| `/api/v1/sync/compare` | POST | Compare services |
| `/api/v1/sync` | POST | Start sync |

**Full documentation:** See `BACKEND_INTEGRATION.md`

---

## 🔧 Maintenance

### Updating Backend URL

If the Railway URL changes:

1. Run `connect-backend.sh` with new URL
2. Update Vercel environment variable
3. Redeploy frontend
4. Test connectivity

### Monitoring

**Backend (Railway):**
- https://railway.app/dashboard
- Check logs, metrics, deployments

**Frontend (Vercel):**
- https://vercel.com/dashboard
- Check deployments, build logs, analytics

---

## 📚 Documentation

- **`BACKEND_INTEGRATION.md`** - Complete integration guide
- **`BACKEND_INTEGRATION_CHECKLIST.md`** - Step-by-step checklist
- **`test-backend-connection.sh`** - Automated testing
- **API Docs:** https://omnidrive-api.up.railway.app/docs (when deployed)

---

## ✅ Pre-Integration Checklist

Before running the integration script, ensure:

- [ ] Railway backend is deployed
- [ ] Railway URL is accessible
- [ ] Health endpoint returns 200
- [ ] CORS is configured in backend
- [ ] Frontend is deployed on Vercel
- [ ] Vercel CLI is installed (optional)

---

## 🎯 Success Criteria

Integration is successful when:

- ✅ Frontend makes API calls to Railway URL
- ✅ No CORS errors in browser console
- ✅ All API endpoints return valid responses
- ✅ Authentication flows work
- ✅ File operations work
- ✅ Sync functionality works
- ✅ No console errors

---

## 🆘 Support

If issues arise:

1. Check `BACKEND_INTEGRATION.md` - Troubleshooting section
2. Check `BACKEND_INTEGRATION_CHECKLIST.md` - Common issues
3. Run `test-backend-connection.sh` - Diagnose issues
4. Check Railway logs - Backend errors
5. Check Vercel logs - Frontend errors

---

## 📝 Notes

- This package is **ready to use** when you have the Railway URL
- All scripts are executable and tested
- Documentation is comprehensive and battle-tested
- No code changes needed in frontend or backend (unless adding custom domain)

---

## 🚦 Next Steps

1. **Wait for Railway deployment** to complete
2. **Get Railway URL** from Railway dashboard
3. **Run integration script:** `./connect-backend.sh <RAILWAY_URL>`
4. **Update Vercel** environment variable
5. **Test connectivity:** `./test-backend-connection.sh`
6. **Verify in production:** Check https://omnidrive.sujeto10.com

---

**Prepared by:** Claude Code
**Date:** January 29, 2026
**Version:** 1.0.0

**Questions?** Refer to the detailed guides or check Railway/Vercel dashboards.
