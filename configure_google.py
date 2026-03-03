#!/usr/bin/env python3
"""Configurar Google Drive con Service Account"""
import json
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Ruta al service account
SERVICE_ACCOUNT_FILE = "/Users/nadalpiantini/omnidrive-cli/google-service-account.json"

print("🔧 Configurando Google Drive...")
print(f"📁 Service Account: {SERVICE_ACCOUNT_FILE}")
print(f"📧 Email: google-drive-service@freejack.iam.gserviceaccount.com")
print()

try:
    # Cargar credenciales
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=['https://www.googleapis.com/auth/drive']
    )

    print("✅ Credenciales cargadas correctamente")

    # Crear servicio de Drive
    service = build('drive', 'v3', credentials=credentials)

    # Probar listar archivos
    print("🔍 Probando conexión con Google Drive API...")
    results = service.files().list(
        pageSize=5,
        fields="nextPageToken, files(id, name, size, mimeType)"
    ).execute()

    items = results.get('files', [])

    if items:
        print(f"✅ ¡Google Drive funciona!")
        print(f"📁 Archivos encontrados: {len(items)}")
        print()
        print("Archivos recientes:")
        for i, item in enumerate(items[:5], 1):
            name = item.get('name', 'N/A')
            size = int(item.get('size', 0)) if item.get('size') else 0
            size_mb = size / (1024*1024) if size else 0
            mime = item.get('mimeType', 'N/A')
            print(f"  {i}. {name}")
            print(f"     Size: {size_mb:.2f} MB | Type: {mime}")
    else:
        print("✅ ¡Google Drive funciona!")
        print("📁 No hay archivos (cuenta vacía o nueva)")

    print()

    # Actualizar configuración de omnidrive
    config_dir = os.path.expanduser("~/.omnidrive")
    config_file = os.path.join(config_dir, "config.json")
    os.makedirs(config_dir, exist_ok=True)

    # Cargar config existente
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
    else:
        config = {}

    # Actualizar con Google Drive
    config['google_key_path'] = SERVICE_ACCOUNT_FILE

    # Guardar
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"💾 Configuración guardada en: {config_file}")
    print()
    print("✅ Google Drive configurado exitosamente!")
    print()
    print("📝 Ahora puedes usar:")
    print("   python3 -m omnidrive list --drive google --limit 10")
    print("   python3 -m omnidrive sync google folderfort")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print()
print("💾 Configuración completa:")
with open(config_file, 'r') as f:
    print(json.dumps(json.load(f), indent=2))
