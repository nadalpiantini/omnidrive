# OmniDrive — Deployment Guide

> **Phase 3** — Railway (backend) + Vercel (frontend)

---

## Architecture Overview

```
  omnidrive.sujeto10.com  ──►  Vercel (Next.js frontend)
  api.omnidrive.sujeto10.com ──►  Railway (FastAPI backend)
```

---

## 1 · Railway — Backend (FastAPI)

### 1.1 Prerequisites

- [Railway account](https://railway.app) linked to the GitHub repo
- Railway CLI installed: `npm i -g @railway/cli`

### 1.2 Environment Variables (set in Railway dashboard)

| Variable | Description | Example |
|---|---|---|
| `OMNIDRIVE_JWT_SECRET` | JWT signing key | `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to service-account JSON (mount as volume or paste JSON) | `/app/credentials/gdrive-sa.json` |
| `FOLDERFORT_TOKEN` | Folderfort API token | `312\|QiTA...` |
| `FOLDERFORT_EMAIL` | Folderfort account email | `user@example.com` |
| `ALLOWED_ORIGINS` | Comma-separated CORS origins | `https://omnidrive.sujeto10.com` |
| `OMNIDRIVE_LOG_LEVEL` | Log verbosity | `INFO` |
| `OMNIDRIVE_LOG_FORMAT` | `json` or `text` | `json` |
| `PORT` | *(auto-injected by Railway)* | — |

### 1.3 Deploy

```bash
# From repo root
cd omnidrive-web/api

# Option A — via Railway CLI
railway login
railway init          # link to existing project or create new
railway up            # deploy using Dockerfile

# Option B — via GitHub integration
# Push to main → Railway auto-deploys (if connected)
git push origin main
```

### 1.4 Health Check

Railway will hit `GET /health` which returns:

```json
{ "status": "healthy", "services": { "google_drive": "available", "folderfort": "available" } }
```

### 1.5 Custom Domain (Railway)

1. Railway Dashboard → Service → Settings → **Custom Domain**
2. Add: `api.omnidrive.sujeto10.com`
3. In your DNS provider, create a **CNAME**:
   ```
   api.omnidrive.sujeto10.com  →  <your-service>.up.railway.app
   ```

---

## 2 · Vercel — Frontend (Next.js)

### 2.1 Prerequisites

- [Vercel account](https://vercel.com) linked to the GitHub repo
- Vercel CLI: `npm i -g vercel`

### 2.2 Environment Variables (set in Vercel dashboard)

| Variable | Description | Example |
|---|---|---|
| `NEXT_PUBLIC_API_BASE` | Backend URL | `https://api.omnidrive.sujeto10.com` |
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL | `https://nqzhxukuvmdlpewqytpv.supabase.co` |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase anon key | `eyJ...` |

> The `vercel.json` references `@omnidrive_api_base` as a Vercel **Shared Environment Variable**. Create it in **Vercel Dashboard → Settings → Environment Variables** with the name `omnidrive_api_base` and the Railway backend URL as its value.

### 2.3 Deploy

```bash
# From repo root
cd omnidrive-web/omnidrive-web

# Option A — via Vercel CLI
vercel login
vercel --prod

# Option B — via GitHub integration
# Push to main → Vercel auto-deploys
git push origin main
```

### 2.4 Custom Domain (Vercel)

1. Vercel Dashboard → Project → Settings → **Domains**
2. Add: `omnidrive.sujeto10.com`
3. In your DNS provider:
   ```
   omnidrive.sujeto10.com  →  CNAME  →  cname.vercel-dns.com
   ```

---

## 3 · DNS Configuration Summary

| Record | Type | Name | Value |
|---|---|---|---|
| CNAME | `api.omnidrive.sujeto10.com` | `api` | `<service>.up.railway.app` |
| CNAME | `omnidrive.sujeto10.com` | `@` or `www` | `cname.vercel-dns.com` |

> **Note:** If your DNS provider does not support CNAME at the root (`@`), use an **A record** pointing to Vercel's IP (`76.76.21.21`) or use their proxy/ALIAS record type.

---

## 4 · Rollback Procedure

### Railway (Backend)

```bash
# List deployments
railway status

# Redeploy a previous commit
railway up --detached  # or re-deploy from Railway Dashboard → Deployments → "Redeploy" on a previous successful deploy

# Via Dashboard: Service → Deployments → click ⋮ on the target deploy → "Redeploy"
```

### Vercel (Frontend)

```bash
# List deployments
vercel ls

# Promote a previous deployment to production
vercel --prod <deployment-url>

# Via Dashboard: Project → Deployments → ⋮ → "Promote to Production"
```

### Emergency: Both

1. `git revert HEAD` on the offending commit(s)
2. `git push origin main` — both platforms auto-deploy the revert
3. Verify `/health` on backend and homepage on frontend

---

## 5 · File Reference

| File | Purpose |
|---|---|
| `omnidrive-web/api/Dockerfile` | Container image for Railway |
| `omnidrive-web/api/railway.json` | Railway build + deploy config |
| `omnidrive-web/api/.env.example` | Backend env var documentation |
| `omnidrive-web/omnidrive-web/vercel.json` | Vercel build + deploy config |
| `omnidrive-web/omnidrive-web/.env.example` | Frontend env var documentation |
