# 🚀 Deployment Script - OmniDrive a omnidrive.sujeto10.com

## 📋 Pre-Deployment Checklist

### 1. Preparar Repositorios GitHub

```bash
# Ir al directorio del proyecto
cd /Users/nodalpiantini/omnidrive-cli

# Inicializar git si no existe
git init
git add .

# Commit inicial
git commit -m "feat: omnidrive hybrid - CLI + Web Dashboard

# Conectar a GitHub (crear repos primero)
# gh repo create omnidrive-cli --public --source
# git remote add origin https://github.com/nadalpiantini/omnidrive-cli.git
```

### 2. Preparar Backend (Railway)

```bash
# Crear directorio API separado si prefieres
mkdir -p /Users/nadalpiantini/omnidrive-api
cp -r omnidrive-web/api/* /Users/nadalpiantini/omnidrive-api/

# O usar el existente
# El backend ya está en omnidrive-web/api/
```

### 3. Preparar Frontend (Vercel)

```bash
# El frontend ya está en omnidrive-web/omnidrive-web/
# Ya tiene vercel.json configurado
# Ya tiene .env.local configurado
```

---

## 🌐 Paso 1: Backend Railway (5 minutos)

### Opción A: Via CLI Railway

```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login
railway login

# Crear proyecto desde GitHub
railway import
# Selecciona: omnidrive-cli (omnidrive-web/api)
# Root directory: omnidrive-web/api
# Variables de entorno:
#   - JWT_SECRET (generar uno)
#   - OPENAI_API_KEY (opcional)

# Deploy
railway up
```

### Opción B: Via Dashboard Railway

1. Ir a https://railway.app
2. "New Project" → "Deploy from GitHub repo"
3. Seleccionar repositorio GitHub
4. Configurar:
   - **Root:** `omnidrive-web/api`
   - **Name:** `omnidrive-api`
   - **Region:** US East
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. **Environment Variables:**
```bash
PYTHON_VERSION=3.10
JWT_SECRET=generar-con-openssl-rand-hex-32
OPENAI_API_KEY=sk-tu-key
FRONTEND_URL=https://omnidrive.sujeto10.com
```

6. **Deploy!**

---

## 🎨 Paso 2: Frontend Vercel (3 minutos)

### Via CLI Vercel

```bash
# Instalar Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy desde directorio
cd omnidrive-web/omnidrive-web
vercel

# Primera vez te preguntará:
# - Set up and deploy? → Y
# - Which scope? → Y (full)
# - Link to existing project? → N (nuevo proyecto)
# - Project name? → omnidrive-web
# - Directory? → (actual directorio)
# - Override settings? → N

# Configurar dominio custom
vercel domains add omnidrive.sujeto10.com
```

### Variables de Entorno Vercel:

```
NEXT_PUBLIC_API_URL=https://omnidrive-api.railway.app
NEXT_PUBLIC_WS_URL=wss://omnidrive-api.railway.app/ws
NEXT_PUBLIC_APP_NAME=OmniDrive
NEXT_PUBLIC_APP_URL=https://omnidrive.sujeto10.com
```

---

## 🔧 Paso 3: Configurar DNS (2 minutos)

### En tu proveedor de DNS (sujeto10.com)

Agregar estos records:

```
# Type: A
Name: omnidrive
Content: 76.76.21.21

# Type: CNAME
Name: api
Content: railway.app
```

O si usas Cloudflare:

```
omnidrive.sujeto10.com → 76.76.21.21
api.omnidrive.sujeto10.com → railway.app
```

---

## ✅ Verificación Post-Deployment

### Test URLs

```bash
# Backend health check
curl https://api.omnidrive.sujeto10.com/health

# Backend API docs
open https://api.omnidrive.sujeto10.com/docs

# Frontend
open https://omnidrive.sujeto10.com/dashboard
```

### Health Check

```bash
# Backend
curl https://api.omnidrive.sujeto10.com/health
# Debería retornar: {"status": "healthy", ...}

# Frontend
curl https://omnidrive.sujeto10.com/
# Debería cargar el dashboard
```

---

## 🧪 Testing Manual

1. **Autenticación Google:**
   - Ir a `/dashboard`
   - Click "Connect Google Drive"
   - Subir service account JSON
   - Ver archivos listados

2. **Upload File:**
   - Ir a `/dashboard/files`
   - Seleccionar Google Drive
   - Arrastrar archivo para upload
   - Ver progress bar

3. **Sync Services:**
   - Ir a `/dashboard/sync`
   - Seleccionar Google → Folderfort
   - Ver archivos a sync
   - Ejecutar sync

4. **Semantic Search:**
   - Set `OPENAI_API_KEY` en Railway
   - Indexar archivos
   - Buscar "documento importante"
   - Ver resultados

---

## 🚨 Troubleshooting

### Error: "Not authenticated"

**Frontend:**
- Verificar que backend URL es correcta en `.env.local`
- Verificar CORS headers

**Backend:**
- Verificar JWT_SECRET está configurado
- Verificar tokens en config

### Error: "CORS"

**Backend:**
- Agregar frontend URL a CORS origins
- Verificar `FRONTEND_URL` env var

### Error: "WebSocket connection"

**Frontend:**
- Verificar WS_URL usa wss://
- Verificar firewall permite WS

**Backend:**
- Verificar WebSocket endpoint habilitado

---

## 📊 URLs Finales

```
Frontend:    https://omnidrive.sujeto10.com
Backend API: https://api.omnidrive.sujeto10.com
API Docs:   https://api.omnidrive.sujeto10.com/docs
WebSocket:  wss://api.omnidrive.sujeto10.com/ws
CLI:        pip install omnidrive-cli (PyPI)
```

---

## 🔐 Variables de Entorno Necesarias

### Railway (Backend):
```bash
PYTHON_VERSION=3.10
JWT_SECRET=<generar con: openssl rand -hex 32>
OPENAI_API_KEY=sk-...
FRONTEND_URL=https://omnidrive.sujeto10.com
```

### Vercel (Frontend):
```bash
NEXT_PUBLIC_API_URL=https://omnidrive-api.railway.app
NEXT_PUBLIC_WS_URL=wss://omnidrive-api.railway.app/ws
NEXT_PUBLIC_APP_NAME=OmniDrive
```

### Local (Desarrollo):
```bash
# Backend
cd omnidrive-web/api
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...
uvicorn app.main:app --reload

# Frontend
cd omnidrive-web/omnidrive-web
npm run dev
```

---

## 🎯 Proximos Pasos Post-Deployment

1. **Testing Completo:**
   - Test todas las operaciones core
   - Verificar WebSockets funcionan
   - Test file upload/download
   - Verificar sync funciona

2. **Monitoring:**
   - Configurar Sentry para errores
   - Configurar Vercel Analytics
   - Configurar Railway monitoring

3. **Documentación:**
   - Actualizar README con URLs
   - Crear guía de usuario
   - Demo video del web app

4. **Marketing:**
   - Anunciar en communities
   - Publicar en Product Hunt
   - Compartir en redes

---

*Status: ✅ Ready to deploy*
*Target: omnidrive.sujeto10.com*
*Methodology: Edward Honour SaaS Blueprint*
