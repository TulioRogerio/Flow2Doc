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
        
        # channel="chrome" é recomendado se tiver Chrome instalado
        browser = await p.chromium.launch(
            headless=False, 
            proxy=PROXY_CONFIG, # Se não usar proxy, remova ou comente esta linha
            channel="chrome",   # Remove se der erro e use apenas o padrão
            args=["--start-maximized"]
        )
        
        context = await browser.new_context(no_viewport=True)
        page = await context.new_page()

        # Conecta o Python ao JS
        await page.expose_function("pythonNotify", lambda info: doc.handle_event(info, page))

        async def inject_interface():
            # Se estiver capturando (print), não injeta interface
            if doc.is_capturing: 
                return 

            try:
                # Só tenta injetar se a página ainda estiver aberta
                if not page.is_closed():
                    js_code = doc.get_js()
                    await page.evaluate(js_code)
            except Exception:
                pass

        await page.add_init_script(doc.get_js())
        page.on("framenavigated", lambda _: asyncio.create_task(inject_interface()))

        print("🚀 Sistema Pronto! Navegue para começar.")
        
        try:
            await page.goto("https://www.google.com")
            await asyncio.sleep(1)
            await inject_interface()
        except Exception as e:
            print(f"⚠️ Aviso: {e}")

        # --- LOOP PRINCIPAL ---
        while not doc.finished:
            # 1. VERIFICA SE O NAVEGADOR FOI FECHADO
            if not browser.is_connected():
                print("\n❌ Navegador fechado pelo usuário.")
                break # Sai do loop imediatamente
            
            await asyncio.sleep(1.0)
            
            # 2. ATUALIZA A INTERFACE (Se necessário)
            if (doc.is_recording or doc.is_paused) and not doc.is_capturing:
                await inject_interface()

        # --- ENCERRAMENTO SEGURO ---
        # Se o loop acabou mas o doc não foi finalizado (ex: navegador fechou no X)
        # e existem logs gravados, salva agora para não perder o trabalho.
        if not doc.finished and doc.logs:
            print("💾 Salvando trabalho pendente antes de sair...")
            await doc.save_manual()
        
        print("👋 Aplicação concluída com sucesso.")

if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\n👋 Programa interrompido.")