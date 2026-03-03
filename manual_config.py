#!/usr/bin/env python3
"""
Configuración manual de Folderfort con un token existente

INSTRUCCIONES:
1. Si encuentras cómo crear un API token en Folderfort, cópialo aquí
2. Ejecuta este script para guardarlo en la configuración
"""

import json
import os

# Token API de Folderfort (pégalo aquí si lo obtienes)
FOLDERFORT_TOKEN = "TU_TOKEN_AQUI"  # <-- Pega el token aquí
FOLDERFORT_EMAIL = "nadalpiantini@gmail.com"

def save_config():
    """Guardar token en configuración"""
    config_dir = os.path.expanduser("~/.omnidrive")
    config_file = os.path.join(config_dir, "config.json")

    # Crear directorio
    os.makedirs(config_dir, exist_ok=True)

    # Cargar config existente
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
    else:
        config = {}

    # Actualizar
    config['folderfort_token'] = FOLDERFORT_TOKEN
    config['folderfort_email'] = FOLDERFORT_EMAIL

    # Guardar
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"✅ Configuración guardada en: {config_file}")
    print(f"\n📁 Contenido:")
    print(json.dumps(config, indent=2))

    # Verificar
    print("\n🔍 Verificando token...")
    if FOLDERFORT_TOKEN != "TU_TOKEN_AQUI":
        print(f"Token: {FOLDERFORT_TOKEN[:30]}...")
        print("✅ Token configurado correctamente")
    else:
        print("⚠️  Debes pegar el token primero en la variable FOLDERFORT_TOKEN")

if __name__ == "__main__":
    save_config()
