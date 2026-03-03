#!/usr/bin/env python3
"""Configurar Folderfort con el token obtenido"""
import requests
import json
import os

# Token obtenido
FOLDERFORT_TOKEN = "312|QiTAhcxsVMmzJkUvbPQlBorcINER4TFBmpiv5PCUcf44574d"
FOLDERFORT_EMAIL = "nadalpiantini@gmail.com"
BASE_URL = "https://na3.folderfort.com"

print("🔧 Configurando Folderfort...")
print(f"🎫 Token: {FOLDERFORT_TOKEN[:30]}...")
print()

# Crear directorio de configuración
config_dir = os.path.expanduser("~/.omnidrive")
config_file = os.path.join(config_dir, "config.json")
os.makedirs(config_dir, exist_ok=True)

# Cargar config existente
if os.path.exists(config_file):
    with open(config_file, 'r') as f:
        config = json.load(f)
else:
    config = {}

# Actualizar configuración
config['folderfort_token'] = FOLDERFORT_TOKEN
config['folderfort_email'] = FOLDERFORT_EMAIL

# Guardar
with open(config_file, 'w') as f:
    json.dump(config, f, indent=2)

print(f"✅ Token guardado en: {config_file}")
print()

# Verificar token
print("🔍 Verificando token con la API...")
try:
    response = requests.get(
        f"{BASE_URL}/drive/file-entries",
        headers={
            "Authorization": f"Bearer {FOLDERFORT_TOKEN}",
            "Accept": "application/json"
        },
        params={"perPage": 5}
    )

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        files = response.json()

        if isinstance(files, list) and len(files) > 0:
            print(f"✅ ¡Token funciona perfectamente!")
            print(f"📁 Tienes {len(files)} archivos en Folderfort")
            print()
            print("Archivos recientes:")
            for i, file in enumerate(files[:5], 1):
                name = file.get('name', 'N/A')
                size = file.get('file_size', 0)
                size_mb = size / (1024*1024) if size else 0
                print(f"  {i}. {name} ({size_mb:.2f} MB)")

            print()
            print("🎉 ¡Configuración completada!")
            print()
            print("📝 Ahora puedes usar OmniDrive CLI:")
            print("   python3 -m omnidrive list --drive folderfort")
            print("   python3 -m omnidrive upload <archivo> folderfort")
            print("   python3 -m omnidrive sync folderfort google")
        elif isinstance(files, dict):
            print(f"✅ ¡Token funciona!")
            print(f"📁 Respuesta: {list(files.keys())}")
        else:
            print(f"⚠️  Respuesta inesperada: {type(files)}")
    else:
        print(f"❌ Error verificando token")
        print(f"Response: {response.text[:300]}")

except Exception as e:
    print(f"❌ Excepción: {e}")
    import traceback
    traceback.print_exc()

print()
print("💾 Configuración final:")
print(json.dumps(config, indent=2))
