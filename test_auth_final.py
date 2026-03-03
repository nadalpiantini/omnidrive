#!/usr/bin/env python3
"""Test final de autenticación con el endpoint correcto"""
import requests
import json

BASE_URL = "https://na2.folderfort.com"
email = "nadalpiantini@gmail.com"
password = "Teclados#13f"

print("🔐 Autenticando con Folderfort...")
print(f"📍 Endpoint: {BASE_URL}/api/v1/auth/login")
print(f"📧 Email: {email}")
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
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print()

    if response.status_code == 200:
        data = response.json()
        print("✅ ¡Autenticación exitosa!")
        print(json.dumps(data, indent=2))

        if data.get('status') == 'success':
            token = data['user']['access_token']
            print(f"\n🎉 Token obtenido:")
            print(f"   {token[:50]}...")
            print(f"\n💾 Guardando en ~/.omnidrive/config.json...")
    else:
        print("❌ Error en la autenticación")
        print(response.text)

except Exception as e:
    print(f"❌ Excepción: {e}")
