# 🎉 OmniDrive CLI - Guía de Uso

## ✅ Servicios Configurados

### 📁 Folderfort (✅ COMPLETO)
- **Email:** nadalpiantini@gmail.com
- **Token:** Configurado y funcionando
- **Archivos:** 4 carpetas visibles

---

## 🚀 Comandos Principales

### 1. **Listar Archivos**
```bash
# Listar archivos de Folderfort
python3 -m omnidrive list --drive folderfort --limit 10

# Con más detalles
python3 -m omnidrive list --drive folderfort --limit 20
```

### 2. **Subir Archivos**
```bash
# Subir un archivo específico
python3 -m omnidrive upload mi_archivo.txt folderfort

# Subir múltiples archivos
python3 -m omnidrive upload *.pdf folderfort
```

### 3. **Descargar Archivos**
```bash
# Descargar a directorio actual (te pedirá ID del archivo)
python3 -m omnidrive download folderfort

# Descargar a ubicación específica
python3 -m omnidrive download folderfort --dest ~/Downloads
```

### 4. **Sincronizar Servicios** (cuando configures Google Drive)
```bash
# Previsualizar sync
python3 -m omnidrive sync folderfort google --dry-run

# Ejecutar sync real
python3 -m omnidrive sync folderfort google

# Sync bidireccional
python3 -m omnidrive sync google folderfort
```

### 5. **Comparar Servicios**
```bash
# Comparar archivos entre servicios
python3 -m omnidrive compare folderfort google
```

---

## 🔍 Búsqueda Semántica (Opcional)

Requiere `DEEPSEEK_API_KEY`:

```bash
# 1. Configurar API key
export DEEPSEEK_API_KEY='sk-...'

# 2. Indexar archivos para búsqueda
python3 -m omnidrive index folderfort

# 3. Buscar por contenido
python3 -m omnidrive search "fotos de navidad"
python3 -m omnidrive search "documentos importantes"
python3 -m omnidrive search "chrome extensions"
```

---

## 💾 Gestión de Sesiones

```bash
# Guardar sesión actual
python3 -m omnidrive session save mi-trabajo

# Reanudar sesión guardada
python3 -m omnidrive session resume mi-trabajo

# Listar todas las sesiones
python3 -m omnidrive session list
```

---

## 🤖 Workflows Automatizados

```bash
# Listar workflows disponibles
python3 -m omnidrive workflow list

# Ejecutar workflow
python3 -m omnidrive workflow run smart-sync
```

---

## 📋 Resumen de Tokens Necesarios

### ✅ Folderfort (CONFIGURADO)
- **Tipo:** Personal Access Token
- **Valor:** `312|QiTAhc...`
- **Ubicación:** `~/.omnidrive/config.json`

### ⏳ Google Drive (OPCIONAL)
Para configurar en el futuro:
1. Ir a Google Cloud Console (proyecto FreeJack)
2. Crear Service Account
3. Habilitar Google Drive API
4. Descargar JSON y ejecutar:
   ```bash
   python3 -m omnidrive auth google
   ```

### ⏳ DeepSeek (OPCIONAL - para búsqueda semántica)
```bash
export DEEPSEEK_API_KEY='sk-...'
```

---

## 🧪 Testing

```bash
cd ~/omnidrive-cli

# Todos los tests
pytest tests/ -v

# Solo Folderfort
pytest tests/test_folderfort.py -v

# Con coverage
pytest tests/ --cov=omnidrive
```

**Estado:** 58/58 tests passing ✅

---

## 📁 Archivos de Configuración

**Ubicación:** `~/.omnidrive/`
```
~/.omnidrive/
├── config.json          # Tokens de autenticación
├── memory/              # Sesiones guardadas
│   └── session_*.json
└── vector_db/           # Base de datos ChromaDB (búsqueda)
    └── chroma.sqlite3
```

---

## 🎯 Próximos Pasos Sugeridos

1. **Probar comandos básicos** con Folderfort
2. **Subir algunos archivos** de prueba
3. **Configurar Google Drive** cuando tengas el service account correcto
4. **Probar sync** entre Folderfort y Google Drive
5. **Configurar búsqueda semántica** si tienes DeepSeek API key

---

## 💡 Tips

- **Usa `--help`** en cualquier comando para ver opciones
- **Session management** mantiene tu contexto entre ejecuciones
- **Dry-run** primero antes de sincronizar (evita sorpresas)
- Los **tokens son privados** - nunca compartir `config.json`

---

**🎉 ¡Disfruta OmniDrive CLI!**
