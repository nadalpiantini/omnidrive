#!/usr/bin/env python3
"""Script final de autenticación con credenciales correctas"""
import sys
sys.path.insert(0, '/Users/nadalpiantini/omnidrive-cli')

from omnidrive.auth.folderfort import authenticate_folderfort

# Credenciales cargadas desde variables de entorno (evitar hardcodear)
import os
email = os.getenv("FOLDERFORT_EMAIL", "")
password = os.getenv("FOLDERFORT_PASSWORD", "")

if not email or not password:
    print("❌ Set FOLDERFORT_EMAIL and FOLDERFORT_PASSWORD environment variables before running.")
    sys.exit(1)

print("🔐 Autenticando con Folderfort...")
print(f"📧 Email: {email}")
print()

try:
    token = authenticate_folderfort(email=email, password=password)
    print(f"\n✅ ¡Autenticación exitosa!")
    print(f"Token: {token[:30]}...")
    print(f"\n💾 Configuración guardada en: ~/.omnidrive/config.json")
except Exception as e:
    print(f"\n❌ Error: {e}")
    sys.exit(1)
