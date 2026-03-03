#!/usr/bin/env python3
"""Probar diferentes endpoints de autenticación de Folderfort"""
import requests
import json

BASE_URL = "https://na2.folderfort.com"
email = "nadalpiantini@gmail.com"
password = "Teclados#13f"

endpoints = [
    "/api/v1/auth/login",
    "/api/auth/login",
    "/v1/auth/login",
    "/auth/api/login",
    "/api/login",
    "/auth/token",
    "/api/token",
    "/oauth/token",
]

print("🔍 Probando diferentes endpoints de autenticación...\n")

for endpoint in endpoints:
    url = f"{BASE_URL}{endpoint}"
    print(f"Probando: {url}")

    try:
        response = requests.post(
            url,
            json={
                "email": email,
                "password": password
            },
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            timeout=10
        )

        print(f"  Status: {response.status_code}")
        print(f"  Content-Type: {response.headers.get('Content-Type')}")

        # Try to parse as JSON
        try:
            data = response.json()
            print(f"  ✅ JSON Response:")
            print(f"  {json.dumps(data, indent=2)[:200]}")

            # If we got a success response with token, we're done!
            if 'status' in data and data['status'] == 'success':
                print("\n  🎉 ¡ENCONTRADO! Este endpoint funciona")
                break
        except:
            # Not JSON, show first 200 chars of text
            print(f"  ❌ No es JSON: {response.text[:200]}")

        print()

    except requests.exceptions.RequestException as e:
        print(f"  ❌ Error: {e}")
        print()

print("\n📝 Nota: Si ninguno funciona, es posible que Folderfort no tenga API pública")
print("y requiera autenticación vía navegador web.")
