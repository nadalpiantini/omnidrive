#!/usr/bin/env python3
"""Configurar Folderfort con el token API encontrado"""
import json
import os
import requests

# Token API de Folderfort (desde entorno)
FOLDERFORT_TOKEN = os.getenv("FOLDERFORT_TOKEN", "")
FOLDERFORT_EMAIL = os.getenv("FOLDERFORT_EMAIL", "")

# Nota: La URL de la API puede ser na3 en lugar de na2
BASE_URL_NA2 = "https://na2.folderfort.com"
BASE_URL_NA3 = "https://na3.folderfort.com"

if not FOLDERFORT_TOKEN or not FOLDERFORT_EMAIL:
    print("❌ Set FOLDERFORT_TOKEN and FOLDERFORT_EMAIL before running.")
    raise SystemExit(1)

print("🔧 Configurando Folderfort...")
print(f"📧 Email: {FOLDERFORT_EMAIL}")
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

print(f"✅ Configuración guardada en: {config_file}")
print()

# Probar el token con ambas URLs
print("🔍 Verificando token con diferentes servidores...\n")

for base_url, name in [(BASE_URL_NA2, "NA2"), (BASE_URL_NA3, "NA3")]:
    try:
        print(f"Probando {name}: {base_url}")

        response = requests.get(
            f"{base_url}/drive/file-entries",
            headers={
                "Authorization": f"Bearer {FOLDERFORT_TOKEN}",
                "Accept": "application/json"
            },
            params={"perPage": 1},
            timeout=10
        )

        print(f"  Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                print(f"  ✅ ¡Token funciona en {name}!")
                print(f"  📁 Tienes {len(data)} archivos (mostrando primeros 1)")
            elif isinstance(data, dict) and 'data' in data:
                print(f"  ✅ ¡Token funciona en {name}!")
                print(f"  📁 Respuesta: {list(data.keys())}")
            else:
                print(f"  ⚠️  Respuesta inesperada")
        elif response.status_code == 401:
            print(f"  ❌ Token no válido o expirado en {name}")
        else:
            print(f"  ❌ Error: {response.text[:100]}")
        print()

    except Exception as e:
        print(f"  ❌ Excepción: {e}")
        print()

print("💾 Configuración final:")
print(json.dumps(config, indent=2))
