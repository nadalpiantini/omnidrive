# OmniDrive Checkpoint - 2026-01-25

## ✅ COMPLETADO

### 1. Supabase (SUJETO10)
- **URL**: `https://nqzhxukuvmdlpewqytpv.supabase.co`
- **Tablas creadas**: omnidrive_files, omnidrive_sync_jobs, omnidrive_auth_configs
- **Datos existentes**: 1 registro en cada tabla

### 2. Frontend Vercel
- **Proyecto**: omnidrive-app
- **URL**: https://omnidrive-cokkyw3fg-nadalpiantini-fcbc2d66.vercel.app
- **Status**: ✅ Deployed (Ready)
- **Env vars configuradas**: SUPABASE_URL, ANON_KEY, SERVICE_ROLE_KEY

### 3. API Routes (Next.js)
- `/api/v1/auth/status` - Creado
- `/api/v1/files` - Creado
- Conectan con Supabase SUJETO10

### 4. Proyecto movido
- De: `~/omnidrive-cli`
- A: `~/Dev/omnidrive-cli`

---

## 🔄 PENDIENTE (PRÓXIMO SPRINT)

### 1. Railway Backend (Python/FastAPI)
**IMPORTANTE**: Usar credenciales correctas de SUJETO10:
```bash
SUPABASE_URL=https://nqzhxukuvmdlpewqytpv.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5xemh4dWt1dm1kbHBld3F5dHB2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY2NTk0MDksImV4cCI6MjA2MjIzNTQwOX0.9raKtf_MAUoZ7lUOek4lazhWTfmxPvufW1-al82UHmk
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5xemh4dWt1dm1kbHBld3F5dHB2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NjY1OTQwOSwiZXhwIjoyMDYyMjM1NDA5fQ.KUbJb8fCHADnITIhr-x8R49_BsmicsYAzW9qG2YlTFA
```

Pasos:
1. `railway login`
2. `cd ~/Dev/omnidrive-cli/omnidrive-web/api`
3. `railway init` (nombre: omnidrive-api)
4. Configurar variables (SUJETO10, no ClueQuest)
5. `railway up`
6. `railway domain`

### 2. Conectar Frontend con Backend
- Actualizar `NEXT_PUBLIC_API_URL` en Vercel con URL de Railway

### 3. Custom Domain
- Configurar omnidrive.sujeto10.com apuntando a Vercel

### 4. CLI remoto
- Documentar cómo usar OmniDrive CLI desde otra máquina

---

## 📋 CREDENCIALES CORRECTAS

### Supabase SUJETO10 (USAR ESTE)
- Project: nqzhxukuvmdlpewqytpv
- URL: https://nqzhxukuvmdlpewqytpv.supabase.co

### Folderfort
- Email: nadalpiantini@gmail.com
- Token: <REDACTED>

### Google OAuth
- Config en: ~/.omnidrive/oauth/

---

## ⚠️ NO USAR (INCORRECTO)

- ❌ josxxqkdnvqodxvtjgov.supabase.co (esto es ClueQuest)
- ❌ omnidrive-api.up.railway.app (no existe aún)

---

## 📁 Rutas Importantes

```
~/Dev/omnidrive-cli/                    # Proyecto principal
~/Dev/omnidrive-cli/omnidrive/          # CLI Python
~/Dev/omnidrive-cli/omnidrive-web/      # Web apps
~/Dev/omnidrive-cli/omnidrive-web/api/  # Backend FastAPI (para Railway)
~/Dev/omnidrive-cli/omnidrive-web/omnidrive-web/  # Frontend Next.js (en Vercel)
~/.omnidrive/                           # Config local del CLI
```
