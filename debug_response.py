#!/usr/bin/env python3
"""Investigar respuesta exacta del endpoint"""
import requests
import os

TOKEN = os.getenv("FOLDERFORT_TOKEN", "")
BASE_URL = "https://na3.folderfort.com"

if not TOKEN:
    print("❌ Set FOLDERFORT_TOKEN before running.")
    raise SystemExit(1)

print("🔍 Investigando respuesta de /drive/file-entries\n")

response = requests.get(
    f"{BASE_URL}/drive/file-entries",
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/json"
    },
    params={"perPage": 1}
)

print(f"Status: {response.status_code}")
print(f"Content-Type: {response.headers.get('Content-Type')}")
print(f"Content-Length: {response.headers.get('Content-Length')}")
print()

# Guardar respuesta para inspeccionar
with open("/Users/nadalpiantini/omnidrive-cli/response_debug.txt", "w") as f:
    f.write(f"Status: {response.status_code}\n")
    f.write(f"Headers: {dict(response.headers)}\n")
    f.write(f"\nBody:\n{response.text}\n")

print("💾 Respuesta guardada en: response_debug.txt")
print()

# Mostrar primeros caracteres
print("Primeros 500 caracteres:")
print(response.text[:500])

# Si es JSON, intentar parsear
if response.text.strip().startswith('{'):
    print("\n✅ Parece JSON")
elif response.text.strip().startswith('['):
    print("\n✅ Parece JSON array")
elif response.text.strip().startswith('<!DOCTYPE html>'):
    print("\n❌ Es HTML - El endpoint no está funcionando como API")
    print("💡 Puede que Folderfort no tenga API REST pública")
