#!/usr/bin/env python3
"""Probar con /api/v1 en la URL"""
import requests

TOKEN = "312|QiTAhcxsVMmzJkUvbPQlBorcINER4TFBmpiv5PCUcf44574d"
BASE_URL = "https://na3.folderfort.com/api/v1"

print("🔍 Probando endpoints de /api/v1\n")

endpoints = [
    "/drive/file-entries",
    "/files",
    "/file-entries",
    "/uploads",
]

for endpoint in endpoints:
    url = f"{BASE_URL}{endpoint}"
    print(f"Probando: {url}")

    try:
        response = requests.get(
            url,
            headers={
                "Authorization": f"Bearer {TOKEN}",
                "Accept": "application/json"
            },
            params={"perPage": 1} if "file-entries" in endpoint else None,
            timeout=10
        )

        print(f"  Status: {response.status_code}")

        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            if 'application/json' in content_type:
                print(f"  ✅ JSON!")
                data = response.json()
                print(f"  📊 Tipo: {type(data)}")
                if isinstance(data, list):
                    print(f"  📁 Archivos: {len(data)}")
                elif isinstance(data, dict):
                    print(f"  🔑 Keys: {list(data.keys())[:5]}")
                print()
                break
            else:
                print(f"  ❌ No es JSON: {content_type}")
        elif response.status_code == 404:
            print(f"  ❌ No encontrado")
        elif response.status_code == 401:
            print(f"  ❌ No autorizado")
        else:
            print(f"  ❌ Error: {response.text[:100]}")
        print()

    except Exception as e:
        print(f"  ❌ Excepción: {e}")
        print()

print("\n💡 Si ningún endpoint funciona, Folderfort puede requerir:")
print("   1. Estar autenticado vía web (cookies de sesión)")
print("   2. Usar su SDK de JavaScript en lugar de REST")
print("   3. O puede que la API solo esté disponible para planes pagos")
