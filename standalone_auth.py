#!/usr/bin/env python3
"""Script standalone de autenticación Folderfort"""
import requests
import json
import os

# Credenciales
email = "nadalpiantini@gmail.com"
password = "Teclados#13"

BASE_URL = "https://na2.folderfort.com"

print("🔐 Autenticando con Folderfort...")
print(f"📧 Email: {email}")
print(f"📍 Endpoint: {BASE_URL}/api/v1/auth/login")
print()

try:
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
            "token_name": "omnidrive-cli"
        },
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    )

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()

        if data.get('status') == 'success':
            token = data['user']['access_token']

            print("✅ ¡Autenticación exitosa!")
            print(f"🎫 Token: {token[:50]}...")
            print()

            # Guardar en config
            config_dir = os.path.expanduser("~/.omnidrive")
            config_file = os.path.join(config_dir, "config.json")

            # Crear directorio si no existe
            os.makedirs(config_dir, exist_ok=True)

            # Cargar config existente o crear nueva
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
            else:
                config = {}

            # Actualizar config
            config['folderfort_token'] = token
            config['folderfort_email'] = email

            # Guardar config
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)

            print(f"💾 Configuración guardada en: {config_file}")
            print(f"📁 Contenido:")
            print(json.dumps(config, indent=2))
        else:
            print("❌ Error en la respuesta:")
            print(json.dumps(data, indent=2))
    else:
        print("❌ Error de autenticación:")
        print(response.text)

except Exception as e:
    print(f"❌ Excepción: {e}")
    import traceback
    traceback.print_exc()
