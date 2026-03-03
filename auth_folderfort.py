#!/usr/bin/env python3
"""Script temporal para autenticar Folderfort"""
import sys
sys.path.insert(0, '/Users/nadalpiantini/omnidrive-cli')

from omnidrive.auth.folderfort import authenticate_folderfort

# Credenciales
email = "nadalpiantini@gmail.com"
password = "Teclados#13f"

# Autenticar
try:
    token = authenticate_folderfort(email=email, password=password)
    print(f"\n✅ Autenticación exitosa!")
    print(f"Token: {token[:20]}...")
except Exception as e:
    print(f"\n❌ Error: {e}")
    sys.exit(1)
