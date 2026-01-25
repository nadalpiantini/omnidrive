# 🚀 OmniDrive Deployment Preparation - omnidrive.sujeto10.com

## 📋 Configuration Sources

Deployment patterns extracted from existing sujeto10.com projects:
- **PromptSmith MCP** (prompsmith.sujeto10.com) - MCP server pattern
- **ClueQuest** (cluequest.app) - Next.js full-stack pattern
- **Reeldoctor** - Railway Python backend pattern

---

## 🔑 Required Tokens & Configurations

### 1. Supabase Configuration (Database)

**Source Pattern**: PromptSmith MCP, ClueQuest

```bash
# Required Variables
SUPABASE_URL=https://YOUR-PROJECT.supabase.co
SUPABASE_ANON_KEY=YOUR-ANON-KEY
SUPABASE_SERVICE_ROLE_KEY=YOUR-SERVICE-ROLE-KEY

# OmniDrive Specific
SUPABASE_DATABASE_PASSWORD=YOUR-DB-PASSWORD
PROJECT_PREFIX=omnidrive_  # Multi-tenant isolation
```

**Action Items**:
- [ ] Create Supabase project at supabase.com
- [ ] Get project URL and keys from Settings > API
- [ ] Set database password
- [ ] Note: Use `omnidrive_` prefix for all tables

### 2. OpenAI API (RAG System)

**Required for**: Semantic search, embeddings

```bash
OPENAI_API_KEY=sk-your-openai-api-key-here
```

**Action Items**:
- [ ] Get API key from platform.openai.com
- [ ] Set up billing (minimum $5 for testing)
- [ ] Verify API key works: `curl https://api.openai.com/v1/models`

### 3. Google Drive Credentials

**Required for**: Google Drive integration

```bash
GOOGLE_SERVICE_ACCOUNT_JSON='{"type": "service_account", ...}'
```

**Action Items**:
- [ ] Create service account at console.cloud.google.com
- [ ] Enable Drive API
- [ ] Download JSON key file
- [ ] Add JSON content to environment variable

### 4. Folderfort Credentials

**Required for**: Folderfort integration

```bash
FOLDERFORT_EMAIL=your-email@example.com
FOLDERFORT_PASSWORD=your-password
FOLDERFORT_API_URL=https://na2.folderfort.com
```

**Action Items**:
- [ ] Create Folderfort account at folderfort.com
- [ ] Generate API token in settings
- [ ] Store credentials securely

### 5. Railway Token (Backend Deployment)

**Required for**: Deploying Python FastAPI backend

```bash
RAILWAY_TOKEN=your-railway-token
RAILWAY_PROJECT_ID=your-project-id
```

**Action Items**:
- [ ] Create Railway account at railway.app
- [ ] Install Railway CLI: `npm install -g @railway/cli`
- [ ] Login: `railway login`
- [ ] Create new project: `railway init`
- [ ] Note project ID from Railway dashboard

### 6. Vercel Token (Frontend Deployment)

**Required for**: Deploying Next.js frontend

```bash
VERCEL_TOKEN=your-vercel-token
VERCEL_ORG_ID=your-org-id
VERCEL_PROJECT_ID=your-project-id
```

**Action Items**:
- [ ] Create Vercel account at vercel.com
- [ ] Install Vercel CLI: `npm install -g vercel`
- [ ] Login: `vercel login`
- [ ] Create project: `vercel link`
- [ ] Note org and project IDs from `.vercel/project.json`

### 7. Cloudflare Configuration (DNS)

**Required for**: Custom domain omnidrive.sujeto10.com

```bash
CLOUDFLARE_ACCOUNT_ID=your-account-id
CLOUDFLARE_API_TOKEN=your-api-token
CLOUDFLARE_ZONE_ID=your-zone-id
```

**Action Items**:
- [ ] Get Account ID from Cloudflare dashboard
- [ ] Create API token with Zone:DNS:Edit permission
- [ ] Get Zone ID for sujeto10.com domain
- [ ] Configure DNS records (see DNS section below)

---

## 📁 Configuration Files

### Backend: `omnidrive-web/api/Railway.json`

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Frontend: `omnidrive-web/omnidrive-web/vercel.json`

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "regions": ["iad1"],
  "functions": {
    "app/api/**/*.ts": {
      "maxDuration": 30
    }
  },
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "Referrer-Policy",
          "value": "strict-origin-when-cross-origin"
        },
        {
          "key": "Permissions-Policy",
          "value": "camera=(), microphone=(), geolocation=()"
        },
        {
          "key": "Strict-Transport-Security",
          "value": "max-age=31536000; includeSubDomains; preload"
        },
        {
          "key": "Content-Security-Policy",
          "value": "default-src 'self' 'unsafe-eval' 'unsafe-inline' omnidrive.sujeto10.com *.sujeto10.com https://*.vercel.app; img-src 'self' data: https: blob:; font-src 'self' data:; style-src 'unsafe-inline';"
        }
      ]
    },
    {
      "source": "/static/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ]
}
```

---

## 🌐 DNS Configuration (Cloudflare)

### DNS Records for omnidrive.sujeto10.com

```
# Frontend (Next.js on Vercel)
Type: CNAME
Name: omnidrive
Content: cname.vercel.net
Proxy: Proxied (Orange cloud)

# Backend (FastAPI on Railway)
Type: CNAME
Name: api
Content: railway.app
Proxy: DNS only (Grey cloud)

# Alternative: A Record for Vercel
Type: A
Name: omnidrive
Content: 76.76.21.21
Proxy: Proxied (Orange cloud)
```

**Action Items**:
- [ ] Log in to Cloudflare dashboard
- [ ] Select sujeto10.com zone
- [ ] Add CNAME record for `omnidrive` → `cname.vercel.net`
- [ ] Add CNAME record for `api` → `railway.app`
- [ ] Wait for DNS propagation (5-10 minutes)

---

## 🔧 Environment Variables Setup

### Railway (Backend) Environment Variables

```bash
# Python
PYTHON_VERSION=3.10
PORT=8000

# Database
SUPABASE_URL=https://YOUR-PROJECT.supabase.co
SUPABASE_ANON_KEY=YOUR-ANON-KEY
SUPABASE_SERVICE_KEY=YOUR-SERVICE-KEY

# AI Services
OPENAI_API_KEY=sk-your-openai-key

# Cloud Services
GOOGLE_APPLICATION_CREDENTIALS=/tmp/service_account.json
FOLDERFORT_API_URL=https://na2.folderfort.com

# Frontend URL (for CORS)
FRONTEND_URL=https://omnidrive.sujeto10.com

# App Config
APP_NAME=OmniDrive
APP_VERSION=1.0.0
ENVIRONMENT=production
LOG_LEVEL=info
```

### Vercel (Frontend) Environment Variables

```bash
# API Endpoints
NEXT_PUBLIC_API_URL=https://api.omnidrive.sujeto10.com
NEXT_PUBLIC_WS_URL=wss://api.omnidrive.sujeto10.com/ws

# App Config
NEXT_PUBLIC_APP_NAME=OmniDrive
NEXT_PUBLIC_APP_URL=https://omnidrive.sujeto10.com
NEXT_PUBLIC_VERSION=1.0.0

# Database (Supabase Client)
NEXT_PUBLIC_SUPABASE_URL=https://YOUR-PROJECT.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=YOUR-ANON-KEY
```

---

## 🚀 Deployment Steps

### Phase 1: Backend (Railway)

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Navigate to API directory
cd omnidrive-web/api

# 4. Initialize project
railway init
# Project name: omnidrive-api

# 5. Set environment variables
railway variables set PYTHON_VERSION=3.10
railway variables set SUPABASE_URL=https://YOUR-PROJECT.supabase.co
railway variables set SUPABASE_ANON_KEY=YOUR-ANON-KEY
railway variables set SUPABASE_SERVICE_KEY=YOUR-SERVICE-KEY
railway variables set OPENAI_API_KEY=sk-your-openai-key
railway variables set FRONTEND_URL=https://omnidrive.sujeto10.com

# 6. Deploy
railway up

# 7. Get deployment URL
railway domain
# Example: https://omnidrive-api.railway.app
```

### Phase 2: Frontend (Vercel)

```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Login
vercel login

# 3. Navigate to frontend directory
cd omnidrive-web/omnidrive-web

# 4. Install dependencies
npm install

# 5. Deploy
vercel --prod

# 6. Set custom domain
vercel domains add omnidrive.sujeto10.com

# 7. Configure environment variables in Vercel dashboard
# Go to: https://vercel.com/dashboard > omnidrive-web > Settings > Environment Variables
```

### Phase 3: DNS Configuration

```bash
# 1. Log in to Cloudflare
# 2. Select sujeto10.com zone
# 3. Add DNS records (see DNS section above)
# 4. Wait for propagation
```

---

## ✅ Verification Checklist

### Backend Health Check

```bash
# Check API health
curl https://api.omnidrive.sujeto10.com/health

# Expected response:
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected",
  "services": {
    "google_drive": "configured",
    "folderfort": "configured"
  }
}
```

### Frontend Health Check

```bash
# Check frontend
curl https://omnidrive.sujeto10.com/

# Check API docs
curl https://api.omnidrive.sujeto10.com/docs
```

### DNS Propagation

```bash
# Check DNS propagation
dig omnidrive.sujeto10.com
dig api.omnidrive.sujeto10.com

# Or use online tool:
# https://dnschecker.org/
```

---

## 🔒 Security Checklist

- [ ] All API keys stored as environment variables (never in code)
- [ ] CORS configured for omnidrive.sujeto10.com only
- [ ] CSP headers configured (already in vercel.json)
- [ ] Database RLS policies enabled in Supabase
- [ ] HTTPS enforced (SSL via Vercel/Railway automatic)
- [ ] Rate limiting configured (TODO: implement)
- [ ] Input validation on all API endpoints
- [ ] Security headers configured (already in vercel.json)

---

## 📊 Monitoring & Analytics

### Recommended Services

1. **Sentry** (Error Tracking)
   ```bash
   SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
   ```

2. **Vercel Analytics** (Frontend Performance)
   - Enabled in Vercel dashboard automatically

3. **Railway Monitoring** (Backend Performance)
   - Available in Railway dashboard automatically

4. **Supabase Logs** (Database Performance)
   - Available in Supabase dashboard

---

## 🆘 Troubleshooting

### Common Issues

**Issue 1: CORS Errors**
```
Solution:
1. Verify FRONTEND_URL in Railway env vars
2. Check CORS origins in app/main.py
3. Clear browser cache and retry
```

**Issue 2: Database Connection Failed**
```
Solution:
1. Verify Supabase credentials
2. Check Supabase project is active
3. Test connection: curl https://YOUR-PROJECT.supabase.co
```

**Issue 3: DNS Not Propagating**
```
Solution:
1. Wait 10-15 minutes after DNS change
2. Clear DNS cache: sudo dscacheutil -flushcache (Mac)
3. Check propagation: https://dnschecker.org/
```

**Issue 4: API Returns 404**
```
Solution:
1. Verify Railway deployment is successful
2. Check Railway logs for errors
3. Verify healthcheck path is correct
```

---

## 📝 Post-Deployment Tasks

1. **Test Authentication Flow**
   - [ ] Google Drive auth works
   - [ ] Folderfort auth works
   - [ ] Tokens stored securely

2. **Test File Operations**
   - [ ] List files from both services
   - [ ] Upload file to Google Drive
   - [ ] Upload file to Folderfort
   - [ ] Download file from both services

3. **Test Sync Operations**
   - [ ] Compare services
   - [ ] Sync Google → Folderfort
   - [ ] Sync Folderfort → Google

4. **Test RAG Search**
   - [ ] Index files from Google Drive
   - [ ] Semantic search works
   - [ ] Results are relevant

5. **Monitor Performance**
   - [ ] Check Railway logs
   - [ ] Check Vercel Analytics
   - [ ] Check Supabase performance

---

## 🎯 Success Criteria

- ✅ Frontend accessible at https://omnidrive.sujeto10.com
- ✅ Backend API accessible at https://api.omnidrive.sujeto10.com
- ✅ All health checks return 200 OK
- ✅ Authentication works for both services
- ✅ File operations (list, upload, download) work
- ✅ DNS resolves correctly for all subdomains
- ✅ HTTPS/SSL valid for all domains
- ✅ No console errors in browser
- ✅ No errors in Railway/Vercel logs

---

**Status**: Ready for deployment
**Target Domain**: omnidrive.sujeto10.com
**Backend**: Railway (FastAPI/Python)
**Frontend**: Vercel (Next.js)
**Database**: Supabase (PostgreSQL)
**DNS**: Cloudflare

**Last Updated**: 2025-01-24
**Configuration Source**: PromptSmith MCP, ClueQuest, Reeldoctor deployment patterns
