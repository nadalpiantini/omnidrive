#!/usr/bin/env python3
"""Intentar múltiples métodos de autenticación con Folderfort"""
import requests
import json
import os

BASE_URL = "https://na2.folderfort.com"
email = os.getenv("FOLDERFORT_EMAIL", "")
password = os.getenv("FOLDERFORT_PASSWORD", "")

if not email or not password:
    print("❌ Set FOLDERFORT_EMAIL and FOLDERFORT_PASSWORD before running.")
    raise SystemExit(1)

print("🔍 Probando diferentes métodos de autenticación...\n")

# Método 1: Obtener token CSRF primero
print("Método 1: Obtener token CSRF de la página de login")
try:
    session = requests.Session()
    response = session.get(f"{BASE_URL}/login")

    # Extraer token CSRF de las cookies o del HTML
    csrf_token = None
    if 'XSRF-TOKEN' in session.cookies:
        csrf_token = session.cookies['XSRF-TOKEN']
        print(f"  ✅ Token CSRF encontrado: {csrf_token[:20]}...")

    # Intentar login con el token CSRF
    response = session.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
            "token_name": "omnidrive-cli"
        },
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-XSRF-TOKEN": csrf_token if csrf_token else "",
            "Referer": BASE_URL
        }
    )

    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  ✅ ÉXITO!")
        print(json.dumps(data, indent=2))
    else:
        print(f"  ❌ Falló: {response.text[:200]}")
except Exception as e:
    print(f"  ❌ Error: {e}")

print("\n" + "="*60 + "\n")

# Método 2: Usar API key si existe
print("Método 2: Buscar API key en la interfaz")
try:
    response = requests.get(f"{BASE_URL}/account-settings")
    if response.status_code == 200:
        print("  ✅ Página de configuración accesible")
        # Buscar API keys en el HTML
        if "api" in response.text.lower() or "token" in response.text.lower():
            print("  🔍 Posibles API keys encontradas en la página")
            print("  💡 Revisa: https://na2.folderfort.com/account-settings")
            print("     Busca la sección de API o Tokens")
    else:
        print(f"  Status: {response.status_code}")
except Exception as e:
    print(f"  ❌ Error: {e}")

print("\n" + "="*60 + "\n")

# Método 3: Revisar si hay endpoint para crear token desde la web
print("Método 3: Probar endpoint de tokens de la API")
try:
    session = requests.Session()

    # Primero hacer login web normal
    login_data = {
        "email": email,
        "password": password
    }

    response = session.post(
        f"{BASE_URL}/login",
        data=login_data,
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )

    print(f"  Login web status: {response.status_code}")

    if response.status_code == 200:
        # Intentar crear token de API
        response = session.post(
            f"{BASE_URL}/api/v1/tokens",
            json={
                "name": "omnidrive-cli",
                "abilities": ["read", "write"]
            },
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
        )

        print(f"  Crear token status: {response.status_code}")
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"  ✅ Token creado:")
            print(json.dumps(data, indent=2))
        else:
            print(f"  Response: {response.text[:300]}")
except Exception as e:
    print(f"  ❌ Error: {e}")

print("\n" + "="*60 + "\n")

print("💡 RECOMENDACIONES:")
print("1. Revisa si en Folderfort hay una sección de 'API Keys' o 'Tokens'")
print("2. Busca en: Account Settings → API o Developer")
print("3. Si existe, crea un token manualmente y cópialo")
print("4. Luego podemos configurarlo directamente en ~/.omnidrive/config.json")
