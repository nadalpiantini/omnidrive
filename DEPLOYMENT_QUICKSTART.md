# 🚀 OmniDrive Deployment Quick Start

## Overview

Deploy OmniDrive hybrid CLI + Web Dashboard to **omnidrive.sujeto10.com**

**Architecture:**
- 🎨 **Frontend**: Next.js (Vercel)
- ⚙️ **Backend**: FastAPI (Railway)
- 🗄️ **Database**: Supabase (PostgreSQL)
- 🌐 **DNS**: Cloudflare

---

## ⚡ Quick Deploy (Automated)

### Prerequisites

1. **Supabase Account** (free tier OK)
   - Create at: https://supabase.com
   - Get: URL, Anon Key, Service Key

2. **OpenAI API Key** (required for RAG)
   - Get from: https://platform.openai.com
   - Cost: ~$5 for testing

3. **Google Service Account** (for Google Drive)
   - Create at: https://console.cloud.google.com
   - Enable Drive API
   - Download JSON key

4. **Railway Account** (backend hosting)
   - Create at: https://railway.app
   - Free tier: $5 credit/month

5. **Vercel Account** (frontend hosting)
   - Create at: https://vercel.com
   - Free tier available

### One-Command Deployment

```bash
cd /Users/nadalpiantini/omnidrive-cli

# Run automated deployment script
./scripts/deploy-omnidrive.sh
```

The script will:
- ✅ Collect all credentials and tokens
- ✅ Create environment files
- ✅ Deploy backend to Railway
- ✅ Deploy frontend to Vercel
- ✅ Provide SQL schema for Supabase
- ✅ Guide DNS configuration

---

## 📋 Manual Deployment Steps

If you prefer manual deployment or need to troubleshoot:

### Step 1: Database Setup (Supabase)

```sql
-- Run in Supabase SQL Editor
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

CREATE TABLE IF NOT EXISTS omnidrive_files (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  service VARCHAR(50) NOT NULL,
  file_id VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(500) NOT NULL,
  mime_type VARCHAR(100),
  size BIGINT,
  parent_id VARCHAR(255),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  modified_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  metadata JSONB
);

-- See DEPLOYMENT_PREPARATION.md for complete schema
```

### Step 2: Backend Deployment (Railway)

```bash
cd omnidrive-web/api

# Install Railway CLI
npm install -g @railway/cli
railway login

# Initialize project
railway init
# Project name: omnidrive-api

# Set environment variables
railway variables set PYTHON_VERSION=3.10
railway variables set SUPABASE_URL=https://your-project.supabase.co
railway variables set SUPABASE_ANON_KEY=your-anon-key
railway variables set SUPABASE_SERVICE_KEY=your-service-key
railway variables set OPENAI_API_KEY=sk-your-key
railway variables set FRONTEND_URL=https://omnidrive.sujeto10.com

# Deploy
railway up

# Get deployment URL
railway domain
```

### Step 3: Frontend Deployment (Vercel)

```bash
cd omnidrive-web/omnidrive-web

# Install Vercel CLI
npm install -g vercel
vercel login

# Install dependencies
npm install

# Deploy
vercel --prod

# Set custom domain
vercel domains add omnidrive.sujeto10.com
```

### Step 4: DNS Configuration (Cloudflare)

Add these records to **sujeto10.com** zone:

```
Type: CNAME
Name: omnidrive
Content: cname.vercel.net
Proxy: Proxied (Orange cloud)

Type: CNAME
Name: api
Content: railway.app
Proxy: DNS only (Grey cloud)
```

---

## ✅ Verification

### Health Checks

```bash
# Backend health
curl https://api.omnidrive.sujeto10.com/health

# Frontend
curl https://omnidrive.sujeto10.com/

# API Docs (open in browser)
open https://api.omnidrive.sujeto10.com/docs
```

### Manual Testing

1. **Open Dashboard**: https://omnidrive.sujeto10.com/dashboard
2. **Connect Google Drive**: Upload service account JSON
3. **List Files**: View files from Google Drive
4. **Upload Test**: Upload a small file
5. **Test Search**: Try semantic search

---

## 🔑 Configuration Templates

### Fill in your values:

```bash
# Copy template
cp .env.omnidrive.template .env

# Edit with your values
code .env
```

**Required variables:**
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_ANON_KEY` - Supabase anonymous key
- `SUPABASE_SERVICE_ROLE_KEY` - Supabase service key
- `OPENAI_API_KEY` - OpenAI API key for RAG
- `GOOGLE_SERVICE_ACCOUNT_JSON` - Google Drive credentials
- `RAILWAY_TOKEN` - Railway deployment token
- `VERCEL_TOKEN` - Vercel deployment token

---

## 📁 Project Structure

```
omnidrive-cli/
├── omnidrive/                          # Python CLI (existing)
│   ├── __main__.py
│   ├── cli.py
│   ├── services/
│   ├── auth/
│   └── commands/
│
├── omnidrive-web/
│   ├── api/                            # FastAPI Backend (new)
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── api/
│   │   │   ├── models/
│   │   │   └── websocket/
│   │   ├── Railway.json
│   │   └── requirements.txt
│   │
│   └── omnidrive-web/                  # Next.js Frontend (new)
│       ├── app/
│       │   ├── dashboard/
│       │   ├── api/
│       │   └── page.tsx
│       ├── components/
│       ├── lib/
│       ├── vercel.json
│       └── package.json
│
├── scripts/
│   └── deploy-omnidrive.sh            # Automated deployment
│
├── .env.omnidrive.template            # Environment template
├── DEPLOYMENT_PREPARATION.md          # Detailed guide
└── DEPLOYMENT_QUICKSTART.md           # This file
```

---

## 🧪 CLI Usage (Local)

The CLI still works locally:

```bash
cd /Users/nadalpiantini/omnidrive-cli

# List files from Google Drive
python3 -m omnidrive list google

# Download a file
python3 -m omnidrive download <file_id> ./

# Upload a file
python3 -m omnidrive upload myfile.txt google

# See all commands
python3 -m omnidrive --help
```

---

## 🌐 URLs After Deployment

| Service | URL |
|---------|-----|
| **Frontend** | https://omnidrive.sujeto10.com |
| **Dashboard** | https://omnidrive.sujeto10.com/dashboard |
| **API Docs** | https://api.omnidrive.sujeto10.com/docs |
| **Health Check** | https://api.omnidrive.sujeto10.com/health |
| **WebSocket** | wss://api.omnidrive.sujeto10.com/ws |

---

## 🆘 Troubleshooting

### Issue: CORS Errors
**Solution**: Verify `FRONTEND_URL` in Railway env vars matches your domain

### Issue: Database Connection Failed
**Solution**: Check Supabase credentials and ensure project is active

### Issue: DNS Not Propagating
**Solution**: Wait 10-15 minutes, check at https://dnschecker.org/

### Issue: API Returns 404
**Solution**: Check Railway logs, verify deployment succeeded

For more troubleshooting, see **DEPLOYMENT_PREPARATION.md**

---

## 📚 Documentation

- **DEPLOYMENT_PREPARATION.md** - Complete deployment guide with all configurations
- **DEPLOYMENT_QUICKSTART.md** - This quick start guide
- **DEPLOY_NOW.md** - Original deployment checklist
- **HYBRID_COMPLETA.md** - Architecture documentation

---

## 🎯 Success Criteria

- ✅ Frontend loads at https://omnidrive.sujeto10.com
- ✅ Backend API responds at https://api.omnidrive.sujeto10.com/health
- ✅ Can authenticate with Google Drive
- ✅ Can list files from Google Drive
- ✅ Can upload/download files
- ✅ Semantic search works (RAG)
- ✅ DNS resolves correctly
- ✅ HTTPS/SSL valid

---

## 🚀 Next Steps

1. **Run deployment script**: `./scripts/deploy-omnidrive.sh`
2. **Configure DNS** in Cloudflare
3. **Test authentication** (Google Drive, Folderfort)
4. **Verify all features** work
5. **Monitor logs** in Railway/Vercel dashboards

---

**Status**: Ready to deploy 🚀
**Target Domain**: omnidrive.sujeto10.com
**Estimated Time**: 15-20 minutes

**Questions?** Check DEPLOYMENT_PREPARATION.md for detailed troubleshooting
