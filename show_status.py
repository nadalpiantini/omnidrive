#!/usr/bin/env python3
"""Verificar configuración actual de OmniDrive"""
import json
import os

config_file = os.path.expanduser("~/.omnidrive/config.json")

if os.path.exists(config_file):
    with open(config_file, 'r') as f:
        config = json.load(f)

    print("📋 Configuración Actual de OmniDrive")
    print("=" * 50)
    print()

    if 'folderfort_token' in config:
        print("✅ Folderfort: CONFIGURADO")
        print(f"   Email: {config.get('folderfort_email', 'N/A')}")
        print(f"   Token: {config['folderfort_token'][:30]}...")
        print()

    if 'google_key_path' in config:
        print("✅ Google Drive: CONFIGURADO")
        print(f"   Key Path: {config['google_key_path']}")
        print()
    else:
        print("⏳ Google Drive: NO CONFIGURADO")
        print()

    print("=" * 50)
    print()
    print("🚀 Comandos Disponibles:")
    print()

    if 'folderfort_token' in config:
        print("📁 Folderfort:")
        print("   python3 -m omnidrive list --drive folderfort --limit 10")
        print("   python3 -m omnidrive upload <archivo> folderfort")
        print()

    if 'google_key_path' not in config:
        print("⚠️  Google Drive:")
        print("   Para configurar: necesitas un Service Account JSON")
        print("   del proyecto FreeJack en Google Cloud Console")
        print()

    print("🔍 Buscar Semántica (opcional):")
    print("   export DEEPSEEK_API_KEY='sk-...'")
    print("   python3 -m omnidrive index folderfort")
    print("   python3 -m omnidrive search \"mis fotos\"")
    print()

    print("💾 Gestión de Sesiones:")
    print("   python3 -m omnidrive session save mi-trabajo")
    print("   python3 -m omnidrive session resume mi-trabajo")
    print("   python3 -m omnidrive session list")

else:
    print("❌ No hay configuración guardada")
    print()
    print("Configura un servicio:")
    print("   python3 -m omnidrive auth folderfort")
    print("   python3 -m omnidrive auth google")
