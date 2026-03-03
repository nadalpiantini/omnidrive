# ⚡ Railway Deploy - Quick Start

**Tiempo estimado: 3-5 minutos**

---

## 🚀 PASO 1: Autenticarse en Railway

```bash
railway login
```

Esto abrirá tu navegador para autenticarte.

---

## 🚀 PASO 2: Ejecutar Script de Deploy

```bash
cd /Users/nadalpiantini/dev/omnidrive-cli/omnidrive-web/api
./deploy-railway.sh
```

**El script hará:**
- ✅ Verificar autenticación
- ✅ Inicializar proyecto Railway
- ✅ Configurar variables SUJETO10
- ✅ Deploy backend
- ✅ Obtener URL pública
- ✅ Testear health endpoint

---

## 📋 OUTPUT ESPERADO

Al final verás:

```
✅ Deploy complete!
======================================

Backend URL: https://omnidrive-api.up.railway.app

📝 Save this URL for the frontend integration:
   NEXT_PUBLIC_API_URL=https://omnidrive-api.up.railway.app

🧪 Testing endpoints...
   Health: https://omnidrive-api.up.railway.app/health
   Docs:   https://omnidrive-api.up.railway.app/docs

✅ Health check passed!
```

---

## ✅ VERIFICACIÓN

```bash
# Test health endpoint
curl https://omnidrive-api.up.railway.app/health

# Abrir API docs
open https://omnidrive-api.up.railway.app/docs
```

---

## 🎯 SIGUIENTE PASO

Una vez tengas la URL del backend, avísame y conectaré el frontend Vercel automáticamente.

---

## ❌ TROUBLESHOOTING

**Error: "Unauthorized"**
```bash
# Re-login
railway login
```

**Error: "Project already exists"**
```bash
# Eliminar y re-crear
rm -rf .railway
railway init --name omnidrive-api
```

**Error: "Variables already set"**
```bash
# Esto es OK, el script lo manejará
```

---

**¿Listo? Ejecuta:**
```bash
railway login && cd /Users/nadalpiantini/dev/omnidrive-cli/omnidrive-web/api && ./deploy-railway.sh
```
