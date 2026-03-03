#!/usr/bin/env python3
"""Test script para verificar la API de Folderfort"""
import requests
import json

BASE_URL = "https://na2.folderfort.com"
email = "nadalpiantini@gmail.com"
password = "Teclados#13f"

print(f"🔍 Probando endpoint: {BASE_URL}/auth/login")
print(f"📧 Email: {email}")
print()

# Test 1: Endpoint actual
try:
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": email,
            "password": password,
            "token_name": "omnidrive-cli"
        }
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Body:")
    print(response.text)
    print()
except Exception as e:
    print(f"Error: {e}")
    print()

# Test 2: Probar endpoint alternativo /api/auth/login
print(f"🔍 Probando endpoint alternativo: {BASE_URL}/api/auth/login")
try:
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "email": email,
            "password": password
        }
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response Body:")
    print(response.text)
    print()
except Exception as e:
    print(f"Error: {e}")
    print()

# Test 3: Verificar si la API requiere un header específico
print(f"🔍 Probando con header User-Agent")
try:
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": email,
            "password": password,
            "token_name": "omnidrive-cli"
        },
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        }
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response Body:")
    print(response.text)
except Exception as e:
    print(f"Error: {e}")
