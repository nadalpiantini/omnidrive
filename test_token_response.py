#!/usr/bin/env python3
"""Investigar qué devuelve el endpoint de Folderfort"""
import requests

TOKEN = "311|oZQrBtxWdmY0fP8nEtxqtlZChJihMxoZ8z1DxkmZ1208e30c"
BASE_URL_NA3 = "https://na3.folderfort.com"

print("🔍 Investigando respuesta de Folderfort API...\n")

# Test 1: Ver qué devuelve el endpoint
print("Test 1: GET /drive/file-entries")
response = requests.get(
    f"{BASE_URL_NA3}/drive/file-entries",
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/json"
    },
    params={"perPage": 1}
)

print(f"Status: {response.status_code}")
print(f"Content-Type: {response.headers.get('Content-Type')}")
print(f"Response (first 500 chars):")
print(response.text[:500])
print("\n" + "="*60 + "\n")

# Test 2: Intentar con formato diferente de autorización
print("Test 2: Con header 'Authorization: token XXX' (sin Bearer)")
response = requests.get(
    f"{BASE_URL_NA3}/drive/file-entries",
    headers={
        "Authorization": TOKEN,  # Sin "Bearer"
        "Accept": "application/json"
    },
    params={"perPage": 1}
)

print(f"Status: {response.status_code}")
print(f"Response (first 300 chars):")
print(response.text[:300])
print("\n" + "="*60 + "\n")

# Test 3: Verificar documentación de API
print("Test 3: Revisar /api-docs en NA3")
response = requests.get(
    f"{BASE_URL_NA3}/api-docs",
    headers={"Accept": "application/json"}
)

print(f"Status: {response.status_code}")
print(f"Content-Type: {response.headers.get('Content-Type')}")

if response.status_code == 200:
    # Guardar para revisar
    with open("/Users/nadalpiantini/omnidrive-cli/api_docs_response.html", "w") as f:
        f.write(response.text)
    print("✅ Documentación guardada en: api_docs_response.html")
    print("🔍 Buscando patrones de autenticación...")

    # Buscar patrones comunes de auth
    text = response.text
    if "Bearer" in text:
        print("  🔎 Encontrado: 'Bearer'")
    if "token" in text.lower():
        print("  🔎 Encontrado: 'token'")
    if "authorization" in text.lower():
        print("  🔎 Encontrado: 'authorization'")
    if "/api/v1" in text:
        print("  🔎 Encontrado: '/api/v1'")
