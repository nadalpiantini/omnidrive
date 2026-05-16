#!/usr/bin/env python3
"""Script temporal para autenticar Folderfort"""
import sys
sys.path.insert(0, '/Users/nadalpiantini/omnidrive-cli')

from omnidrive.auth.folderfort import authenticate_folderfort
import os

# Credenciales via entorno (no hardcode)
email = os.getenv("FOLDERFORT_EMAIL", "")
password = os.getenv("FOLDERFORT_PASSWORD", "")

if not email or not password:
    print("❌ Set FOLDERFORT_EMAIL and FOLDERFORT_PASSWORD before running.")
    sys.exit(1)

# Autenticar
try:
    token = authenticate_folderfort(email=email, password=password)
    print(f"\n✅ Autenticación exitosa!")
    print(f"Token: {token[:20]}...")
except Exception as e:
    print(f"\n❌ Error: {e}")
    sys.exit(1)
