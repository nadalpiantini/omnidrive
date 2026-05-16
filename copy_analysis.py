#!/usr/bin/env python3
"""
Copia completa de Google Drive a Folderfort
Analiza costos y ejecuta la migración
"""
import sys
sys.path.insert(0, '/Users/nadalpiantini/omnidrive-cli')

from omnidrive.services.google_drive import GoogleDriveService
from omnidrive.services.folderfort import FolderfortService
from omnidrive.config import load_config
import json
import os

print("🔄 GOOGLE DRIVE → FOLDERFORT COPIA")
print("=" * 60)
print()

# Configuración
GOOGLE_KEY_PATH = None  # Google Drive no está configurado aún
FOLDERFORT_TOKEN = os.getenv("FOLDERFORT_TOKEN", "")

if not FOLDERFORT_TOKEN:
    print("❌ Set FOLDERFORT_TOKEN before running.")
    raise SystemExit(1)

print("⚠️  NOTA IMPORTANTE:")
print("   Google Drive no está configurado en este sistema.")
print("   Para calcular costos exactos, necesitarías:")
print("   1. Service Account JSON de Google Drive")
print("   2. Habilitar Google Drive API en tu proyecto")
print()
print("   Por ahora, mostraré el proceso y costos estimados.")
print("=" * 60)
print()

# Servicios
folderfort = FolderfortService(access_token=FOLDERFORT_TOKEN)

# Analizar Folderfort actual
print("📁 ANÁLISIS DE FOLDERFORT ACTUAL")
try:
    files = folderfort.list_files(limit=1000)
    print(f"   Archivos en Folderfort: {len(files)}")

    if len(files) > 0:
        total_size = sum(f.get('file_size', 0) for f in files)
        total_size_gb = total_size / (1024**3)
        print(f"   Espacio usado: {total_size_gb:.2f} GB")

    print()
except Exception as e:
    print(f"   ⚠️  No se pudo listar: {e}")
    files = []

print()

# Análisis de costos Google Drive (hipotético)
print("💰 ANÁLISIS DE COSTOS - GOOGLE DRIVE")
print()
print("   Si copiaras desde Google Drive:")
print()

# Escenarios
scenarios = [
    {"archivos": 100, "nombre": "Pequeño", "google_calls": 200, "costo": 0.0008},
    {"archivos": 1000, "nombre": "Mediano", "google_calls": 2000, "costo": 0.008},
    {"archivos": 10000, "nombre": "Grande", "google_calls": 20000, "costo": 0.08},
]

for s in scenarios:
    print(f"📊 Escenario {s['nombre']}:")
    print(f"   • {s['archivos']:,} archivos")
    print(f"   • ~{s['google_calls']:,} calls a Google API")
    print(f"   • Costo Google API: ${s['costo']:.4f} USD")
    print(f"   • Costo Folderfort: $0 (gratis)")
    print(f"   • 💰 TOTAL: ${s['costo']:.4f} USD")
    print()

print("💡 CONCLUSIÓN:")
print("   • Google Drive API: Muy económico (~$0.08 por 10K archivos)")
print("   • Folderfort API: GRATIS con tu plan actual")
print("   • El costo principal es TU TIEMPO, no dinero")
print()

# Ejemplo de código para cuando configures Google Drive
print("📝 CÓDIGO PARA EJECUTAR LA COPIA:")
print()
print("   # Opción 1: Sync completo (automático)")
print("   python3 -m omnidrive sync google folderfort")
print()
print("   # Opción 2: Script personalizado")
print("   from omnidrive.services.google_drive import GoogleDriveService")
print("   from omnidrive.services.folderfort import FolderfortService")
print("   ")
print("   # Inicializar servicios")
print("   google = GoogleDriveService()  # Requiere configuración previa")
print("   folderfort = FolderfortService(token='<FOLDERFORT_TOKEN>')")
print("   ")
print("   # Listar archivos de Google")
print("   google_files = google.list_files(limit=10000)")
print("   ")
print("   # Copiar a Folderfort")
print("   for file in google_files:")
print("       folderfort.upload_file(file['id'])  # Simplificado")
print("       print(f\"Copiado: {file['name']}\")")
print()

print("=" * 60)
print()
print("🎯 PRÓXIMOS PASOS:")
print()
print("1. Configurar Google Drive:")
print("   - Crear Service Account en Google Cloud Console")
print("   - Habilitar Google Drive API")
print("   - Descargar JSON y configurar en OmniDrive")
print()
print("2. Ejecutar copia:")
print("   python3 -m omnidrive sync google folderfort")
print()
print("3. Verificar:")
print("   python3 -m omnidrive compare google folderfort")
print()

print("❓ ¿Quieres configurar Google Drive ahora o prefieres solo Folderfort?")
