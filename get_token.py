#!/usr/bin/env python3
"""Obtener token de Folderfort via API"""
import requests
import json
import os

EMAIL = "nadalpiantini@gmail.com"
PASSWORD = "Teclados#13"
BASE_URL = "https://na3.folderfort.com"

print("🔐 Obteniendo token de Folderfort...")
print(f"📧 Email: {EMAIL}")
print(f"📍 URL: {BASE_URL}/api/v1/auth/login")
print()

try:
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={
            "email": EMAIL,
            "password": PASSWORD,
            "token_name": "omnidrive-cli"
        },
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    )

    print(f"Status: {response.status_code}")
    print()

    if response.status_code == 200:
        data = response.json()

        if data.get('status') == 'success':
            token = data['user']['access_token']

            print("✅ ¡Login exitoso!")
            print(f"🎫 Token: {token}")
            print(f"👤 Usuario: {data['user'].get('display_name', 'N/A')}")
            print()

            # Guardar en config
            config_dir = os.path.expanduser("~/.omnidrive")
            config_file = os.path.join(config_dir, "config.json")
            os.makedirs(config_dir, exist_ok=True)

            # Cargar config existente
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
            else:
                config = {}

            # Actualizar
            config['folderfort_token'] = token
            config['folderfort_email'] = EMAIL

            # Guardar
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)

            print(f"💾 Token guardado en: {config_file}")
            print()

            # Verificar token
            print("🔍 Verificando token...")
            verify_response = requests.get(
                f"{BASE_URL}/drive/file-entries",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/json"
                },
                params={"perPage": 1}
            )

            if verify_response.status_code == 200:
                files = verify_response.json()
                if isinstance(files, list):
                    print(f"✅ Token funciona! Tienes {len(files)} archivos")
                else:
                    print(f"✅ Token funciona! Respuesta: {list(files.keys())[:5]}")
            else:
                print(f"⚠️  Token guardado pero verificación falló: {verify_response.status_code}")
        else:
            print("❌ Login falló")
            print(json.dumps(data, indent=2))
    else:
        print("❌ Error de autenticación")
        print(response.text)

except Exception as e:
    print(f"❌ Excepción: {e}")
    import traceback
    traceback.print_exc()
