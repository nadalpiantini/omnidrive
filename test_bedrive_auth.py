#!/usr/bin/env python3
"""Probar autenticación de BeDrive con el token"""
import requests
import json
import os

TOKEN = os.getenv("FOLDERFORT_TOKEN", "")
BASE_URL = "https://na3.folderfort.com"  # Usar NA3 en lugar de NA2

if not TOKEN:
    print("❌ Set FOLDERFORT_TOKEN before running.")
    raise SystemExit(1)

print("🔍 Probando autenticación BeDrive...\n")

# BeDrive usa un formato diferente de autenticación
# El token probablemente necesita ser usado como Bearer token o directamente

methods = [
    {
        "name": "Método 1: Bearer token",
        "headers": {
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/json"
        }
    },
    {
        "name": "Método 2: Token directo (sin Bearer)",
        "headers": {
            "Authorization": TOKEN,
            "Accept": "application/json"
        }
    },
    {
        "name": "Método 3: X-Access-Token header",
        "headers": {
            "X-Access-Token": TOKEN,
            "Accept": "application/json"
        }
    },
    {
        "name": "Método 4: Cookie de sesión",
        "headers": {
            "Accept": "application/json"
        },
        "cookies": {
            "folder_fort_auth_token": TOKEN
        }
    }
]

for method in methods:
    print(f"{method['name']}")

    try:
        kwargs = {
            "headers": method["headers"],
            "params": {"perPage": 1}
        }

        if "cookies" in method:
            kwargs["cookies"] = method["cookies"]

        response = requests.get(
            f"{BASE_URL}/drive/file-entries",
            timeout=10,
            **kwargs
        )

        print(f"  Status: {response.status_code}")
        print(f"  Content-Type: {response.headers.get('Content-Type')}")

        if response.status_code == 200:
            try:
                data = response.json()
                print(f"  ✅ ÉXITO!")
                if isinstance(data, list):
                    print(f"  📁 Archivos encontrados: {len(data)}")
                    if len(data) > 0:
                        print(f"  📄 Primer archivo: {data[0].get('name', 'N/A')}")
                elif isinstance(data, dict):
                    print(f"  🔑 Keys: {list(data.keys())}")
                break
            except:
                if "text/html" not in response.headers.get('Content-Type', ''):
                    print(f"  ✅ Respuesta no HTML:")
                    print(f"  {response.text[:200]}")
                else:
                    print(f"  ❌ Devuelve HTML")
        else:
            print(f"  ❌ Error: {response.text[:100]}")

    except Exception as e:
        print(f"  ❌ Excepción: {e}")

    print()

print("\n💡 Nota: BeDrive puede requerir estar autenticado vía web primero.")
print("   Si ningún método funciona, puede que necesitemos usar Selenium/Playwright")
print("   para simular el login web y obtener las cookies de sesión.")
