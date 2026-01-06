import sys
import os

sys.dont_write_bytecode = True 

import asyncio
from playwright.async_api import async_playwright
from config import PROXY_CONFIG
from core.generator import DocGenerator

async def run():
    doc = DocGenerator()
    
    async with async_playwright() as p:
        print("🌍 Iniciando Browser Maximizado...")
        
        # Use channel="chrome" se tiver o Chrome instalado, é mais estável para sites de vídeo
        browser = await p.chromium.launch(
            headless=False, 
            proxy=PROXY_CONFIG,
            args=["--start-maximized"]
        )
        
        context = await browser.new_context(no_viewport=True)
        page = await context.new_page()

        # AQUI É O PONTO CHAVE:
        # Quando o JS chamar window.pythonNotify, ele vai esperar essa função terminar
        await page.expose_function("pythonNotify", lambda info: doc.handle_event(info, page))

        async def inject_interface():
            # Se estiver tirando foto, não injeta nada para não poluir a tela
            if doc.is_capturing: 
                return 

            try:
                js_code = doc.get_js()
                await page.evaluate(js_code)
            except Exception:
                pass

        await page.add_init_script(doc.get_js())
        page.on("framenavigated", lambda _: asyncio.create_task(inject_interface()))

        print("🚀 Sistema Pronto! Navegue para começar.")
        
        try:
            await page.goto("https://conecta.sedu.es.gov.br")
            await asyncio.sleep(1)
            await inject_interface()
        except Exception as e:
            print(f"⚠️ Erro ao carregar página inicial: {e}")

        while not doc.finished:
            if not browser.is_connected():
                print("❌ Navegador fechado pelo utilizador.")
                break
            
            await asyncio.sleep(1.0)
            
            # Só atualiza a UI se estiver gravando E não estiver ocupado tirando foto
            if (doc.is_recording or doc.is_paused) and not doc.is_capturing:
                await inject_interface()

if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\n👋 Programa encerrado.")