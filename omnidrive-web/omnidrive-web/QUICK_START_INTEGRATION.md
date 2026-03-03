# 🚀 Quick Start: Backend Integration

## When You Get the Railway URL

```bash
# 1. Run integration script
./connect-backend.sh https://omnidrive-api.up.railway.app

# 2. Update Vercel (Option A - CLI)
vercel env add NEXT_PUBLIC_API_URL production
vercel --prod

# 3. Or update Vercel (Option B - Dashboard)
# Go to https://vercel.com/dashboard
# Settings → Environment Variables
# Update NEXT_PUBLIC_API_URL

# 4. Test connection
./test-backend-connection.sh https://omnidrive-api.up.railway.app

# 5. Verify in browser
# Visit https://omnidrive.sujeto10.com
# Open DevTools (F12)
# Check Network tab for API calls
```

---

## Quick Test Commands

```bash
# Test health endpoint
curl https://omnidrive-api.up.railway.app/health

# Test auth status
curl https://omnidrive-api.up.railway.app/api/v1/auth/status

# Test API docs (open in browser)
open https://omnidrive-api.up.railway.app/docs
```

---

## What Gets Updated

**File:** `.env.production`
```env
NEXT_PUBLIC_API_URL=https://omnidrive-api.up.railway.app
```

**No code changes needed** - `lib/api.ts` uses the env var automatically.

---

## Verification Checklist

- [ ] Backend deployed on Railway
- [ ] Health endpoint returns 200
- [ ] `.env.production` updated
- [ ] Vercel env var set
- [ ] Frontend redeployed
- [ ] API calls work in production
- [ ] No CORS errors
- [ ] No console errors

---

## Troubleshooting

**CORS errors?** → Check `api/app/main.py` CORS config
**API timeout?** → Check Railway dashboard
**Wrong URL?** → Verify Vercel env var
**Cache issues?** → Hard refresh (Ctrl+Shift+R)

---

## Documentation

- **Full Guide:** `BACKEND_INTEGRATION.md`
- **Checklist:** `BACKEND_INTEGRATION_CHECKLIST.md`
- **Overview:** `INTEGRATION_README.md`
- **API Docs:** https://omnidrive-api.up.railway.app/docs

---

**Status:** ✅ Ready for Railway URL
**Date:** 2026-01-29
