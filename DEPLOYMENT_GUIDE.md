# OmniDrive Web Deployment Guide

## 🚀 Deployment to omnidrive.sujeto10.com

### Backend Deployment (Railway)

1. **Push code to GitHub:**
```bash
cd /Users/nadalpiantini/omnidrive-cli
git add omnidrive-web/api/
git commit -m "feat: add FastAPI backend"
git push
```

2. **Deploy on Railway:**
- Go to https://railway.app/new
- Select "Deploy from GitHub repo"
- Choose: `omnidrive-cli/omnidrive-web/api`
- Settings:
  - Root Directory: `omnidrive-web/api`
  - Build Command: `pip install -r requirements.txt`
  - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Environment Variables:**
```
JWT_SECRET=your-secret-key-here
OPENAI_API_KEY=sk-your-openai-key
FRONTEND_URL=https://omnidrive.sujeto10.com
```

4. **Get domain:**
- Railway will provide: `omnidrive-api.railway.app`
- Or configure custom domain: `api.omnidrive.sujeto10.com`

### Frontend Deployment (Vercel)

1. **Push code to GitHub:**
```bash
cd /Users/nadalpiantini/omnidrive-cli
git add omnidrive-web/omnidrive-web/
git commit -m "feat: add Next.js frontend"
git push
```

2. **Deploy on Vercel:**
- Go to https://vercel.com/new
- Import from GitHub
- Root Directory: `omnidrive-web/omnidrive-web`

3. **Environment Variables:**
```
NEXT_PUBLIC_API_URL=https://omnidrive-api.sujeto10.com
NEXT_PUBLIC_WS_URL=wss://omnidrive-api.sujeto10.com/ws
```

4. **Custom Domain:**
- Add domain: `omnidrive.sujeto10.com`
- Vercel will handle SSL automatically

### DNS Configuration (sujeto10.com)

Add these records in your DNS provider:

```
# A Records
omnidrive.sujeto10.com → 76.76.21.21 (Vercel)

# CNAME Records
api.omnidrive.sujeto10.com → railway.app
```

### Testing

Once deployed, test:
1. Backend: https://api.omnidrive.sujeto10.com/health
2. API Docs: https://api.omnidrive.sujeto10.com/docs
3. Frontend: https://omnidrive.sujeto10.com

### Local Development

**Backend:**
```bash
cd omnidrive-web/api
pip install -r requirements.txt
uvicorn app.main:app --reload
# http://localhost:8000
```

**Frontend:**
```bash
cd omnidrive-web/omnidrive-web
npm run dev
# http://localhost:3000
```

---

*Deployment Status: Ready to deploy*
*Target: omnidrive.sujeto10.com*
