# 🚀 Railway Setup Instructions

## Paso 1: Instalar Railway CLI

```bash
npm install -g @railway/cli
```

## Paso 2: Login y Obtener Token

```bash
railway login
```

Esto abrirá tu navegador. Después de login:

### Obtener tu Railway Token:

1. Ve a: https://railway.app/account/tokens
2. Click en "New Token"
3. Dale un nombre: "omnidrive-deployment"
4. Copia el token (se ve como: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)

## Paso 3: Crear Proyecto OmniDrive

### Opción A: Via CLI (Recomendado)

```bash
cd /Users/nadalpiantini/omnidrive-cli/omnidrive-web/api

# Inicializar proyecto
railway init

# Nombre del proyecto: omnidrive-api
# O selecciona "Create New Project"
```

### Opción B: Via Dashboard

1. Ve a: https://railway.app/new
2. Click en "Deploy from GitHub repo"
3. O selecciona "Empty Project" si vas a subir código manualmente
4. Nombre: `omnidrive-api`

## Paso 4: Configurar Variables de Entorno

### Via CLI:

```bash
# Dentro del directorio del proyecto
cd omnidrive-web/api

# Variables básicas
railway variables set PYTHON_VERSION=3.10
railway variables set PORT=8000

# Supabase (del repo sujeto10)
railway variables set SUPABASE_URL=https://TU-PROYECTO.supabase.co
railway variables set SUPABASE_ANON_KEY=TU-ANON-KEY
railway variables set SUPABASE_SERVICE_KEY=TU-SERVICE-KEY
railway variables set PROJECT_PREFIX=omnidrive_

# OpenAI
railway variables set OPENAI_API_KEY=sk-e2537cbaff974532ac35cb20a7177ca1

# Frontend URL
railway variables set FRONTEND_URL=https://omnidrive.sujeto10.com

# App config
railway variables set APP_NAME=OmniDrive
railway variables set ENVIRONMENT=production
railway variables set LOG_LEVEL=info
```

### Via Dashboard:

1. Ve a: https://railway.app/project/omnidrive-api
2. Click en "Variables" tab
3. Agrega todas las variables arriba

## Paso 5: Deploy

```bash
railway up
```

## Paso 6: Obtener URL del Backend

```bash
railway domain
```

Esto te dará una URL como:
- `https://omnidrive-api.railway.app`
- O `https://omnidrive-api.up.railway.app`

## Paso 7: Verificar Health Check

```bash
# Reemplaza con tu URL real
curl https://omnidrive-api.railway.app/health
```

Debería retornar:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

## 📋 Resumen de Variables Necesarias

```bash
# Python
PYTHON_VERSION=3.10
PORT=8000

# Supabase (buscar en repo sujeto10)
SUPABASE_URL=https://XXXXX.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_KEY=eyJ...
PROJECT_PREFIX=omnidrive_

# OpenAI (proporcionaste)
OPENAI_API_KEY=sk-e2537cbaff974532ac35cb20a7177ca1

# Frontend
FRONTEND_URL=https://omnidrive.sujeto10.com

# App
APP_NAME=OmniDrive
ENVIRONMENT=production
LOG_LEVEL=info
```

---

## ⚡ Quick Start (Todo Junto)

```bash
# 1. Instalar CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Crear proyecto
cd /Users/nadalpiantini/omnidrive-cli/omnidrive-web/api
railway init

# 4. Configurar variables (reemplazar con valores reales)
railway variables set PYTHON_VERSION=3.10
railway variables set SUPABASE_URL=TU_URL
railway variables set SUPABASE_ANON_KEY=TU_KEY
railway variables set SUPABASE_SERVICE_KEY=TU_SERVICE_KEY
railway variables set PROJECT_PREFIX=omnidrive_
railway variables set OPENAI_API_KEY=sk-e2537cbaff974532ac35cb20a7177ca1
railway variables set FRONTEND_URL=https://omnidrive.sujeto10.com

# 5. Deploy
railway up

# 6. Obtener URL
railway domain
```

---

## 🆘 Troubleshooting

### Error: "No Railway project found"
```bash
railway init
# Selecciona "Create New Project"
```

### Error: "Environment variable not set"
```bash
# Verifica variables
railway variables list
# Agrega la faltante
railway variables set NOMBRE=valor
```

### Error: "Build failed"
```bash
# Verifica logs
railway logs
# Asegúrate que requirements.txt existe
cat omnidrive-web/api/requirements.txt
```

---

## ✅ Checklist

- [ ] Railway CLI instalado
- [ ] Login completado
- [ ] Proyecto creado: `omnidrive-api`
- [ ] Variables de entorno configuradas
- [ ] Deploy exitoso (`railway up`)
- [ ] URL obtenida (`railway domain`)
- [ ] Health check funcionando

---

**Siguiente paso**: Una vez Railway esté listo, continuamos con Vercel frontend deployment.
