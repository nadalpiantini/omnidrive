#!/usr/bin/env python3
"""
Autenticar con Folderfort usando Playwright
Simula el login web y obtiene las cookies de sesión
"""
import asyncio
import json
import os
from playwright.async_api import async_playwright

EMAIL = "nadalpiantini@gmail.com"
PASSWORD = "Teclados#13"

async def login_and_get_cookies():
    """Hacer login y obtener cookies"""
    print("🔐 Iniciando login con Playwright...")
    print(f"📧 Email: {EMAIL}")
    print()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # headless=True para modo invisible
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # Ir a la página de login
            print("📍 Navegando a: https://na3.folderfort.com/login")
            await page.goto("https://na3.folderfort.com/login")

            # Esperar a que cargue el formulario
            await page.wait_for_selector('input[name="email"]', timeout=10000)
            print("✅ Página de login cargada")

            # Llenar formulario
            print("📝 Llenando formulario...")
            await page.fill('input[name="email"]', EMAIL)
            await page.fill('input[name="password"]', PASSWORD)

            # Hacer clic en login
            print("🔒 Haciendo clic en login...")
            await page.click('button[type="submit"]')

            # Esperar a que redirija
            await page.wait_for_url("**/drive", timeout=15000)
            print("✅ Login exitoso - Redirigido a /drive")

            # Obtener cookies
            cookies = await context.cookies()
            print(f"\n🍪 Cookies obtenidas: {len(cookies)}")

            # Buscar la cookie de sesión
            session_cookie = None
            for cookie in cookies:
                if cookie['name'] in ['folder_fort_auth_token', 'folder_fort_affordable_cloud_storage_session', 'session']:
                    session_cookie = cookie
                    print(f"✅ Cookie de sesión encontrada: {cookie['name']}")
                    print(f"   Valor: {cookie['value'][:50]}...")
                    break

            if not session_cookie:
                print("⚠️  No se encontró cookie de sesión específica")
                print("📁 Todas las cookies:")
                for cookie in cookies:
                    print(f"   - {cookie['name']}: {cookie['value'][:30]}...")

            # Guardar cookies en archivo
            cookies_file = "/Users/nadalpiantini/omnidrive-cli/folderfort_cookies.json"
            with open(cookies_file, 'w') as f:
                json.dump(cookies, f, indent=2)
            print(f"\n💾 Cookies guardadas en: {cookies_file}")

            # Probar hacer una request a la API con las cookies
            print("\n🔍 Probando API con cookies...")
            api_response = await page.request.get(
                "https://na3.folderfort.com/drive/file-entries",
                params={"perPage": 5}
            )

            if api_response.ok:
                data = await api_response.json()
                print(f"✅ API funciona con cookies!")
                print(f"📁 Respuesta: {json.dumps(data, indent=2)[:500]}...")
            else:
                print(f"❌ Error en API: {api_response.status}")

        except Exception as e:
            print(f"❌ Error durante login: {e}")
            import traceback
            traceback.print_exc()

        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(login_and_get_cookies())
