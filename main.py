import sys
import os

sys.dont_write_bytecode = True 

import asyncio
from playwright.async_api import async_playwright
from config import PROXY_CONFIG
from core.generator import DocGenerator

async def run():
    doc = DocGenerator()
    
    # Bloco principal de execução
    try:
        async with async_playwright() as p:
            print("🌍 Iniciando Browser Maximizado...")
            
            # Tenta lançar o Chrome, se não der, usa o padrão
            try:
                browser = await p.chromium.launch(
                    headless=False, 
                    proxy=PROXY_CONFIG,
                    channel="chrome", 
                    args=["--start-maximized"]
                )
            except:
                # Fallback caso não tenha chrome instalado
                browser = await p.chromium.launch(
                    headless=False, 
                    proxy=PROXY_CONFIG,
                    args=["--start-maximized"]
                )
            
            context = await browser.new_context(no_viewport=True)
            page = await context.new_page()

            # Conecta Python <-> JS
            await page.expose_function("pythonNotify", lambda info: doc.handle_event(info, page))

            async def inject_interface():
                if doc.is_capturing: return 
                try:
                    # Verifica explicitamente se a página ainda existe
                    if not page.is_closed():
                        await page.evaluate(doc.get_js())
                except Exception:
                    pass # Ignora erros de injeção se o browser estiver fechando

            await page.add_init_script(doc.get_js())
            page.on("framenavigated", lambda _: asyncio.create_task(inject_interface()))

            print("🚀 Sistema Pronto! Navegue para começar.")
            
            try:
                await page.goto("https://conecta.sedu.es.gov.br")
                await asyncio.sleep(1)
                await inject_interface()
            except:
                print("⚠️ Aviso: Navegador iniciado sem página padrão.")

            # --- LOOP PRINCIPAL ---
            while not doc.finished:
                try:
                    # Se o navegador desconectou, força a saída do loop
                    if not browser.is_connected():
                        print("\n❌ Navegador fechado.")
                        break
                    
                    # Verifica se a página específica foi fechada
                    if page.is_closed():
                        print("\n❌ Aba fechada.")
                        break

                    await asyncio.sleep(1.0)
                    
                    # Tenta injetar a interface (mantém o menu vivo)
                    if (doc.is_recording or doc.is_paused) and not doc.is_capturing:
                        await inject_interface()
                        
                except Exception:
                    # Qualquer erro fatal dentro do loop (ex: janela fechada à força) quebra o loop
                    break

    except Exception as e:
        print(f"\n⚠️ Ocorreu uma interrupção: {e}")

    finally:
        # --- BLOCO DE SEGURANÇA FINAL ---
        # Este código RODARÁ SEMPRE, mesmo se o navegador crashar ou for fechado.
        print("\n🛑 Encerrando sistema...")
        
        if doc.logs: # Se tiver algo na memória...
            print("💾 Salvando trabalho pendente antes de sair...")
            # Como o navegador já fechou, save_manual vai apenas escrever o arquivo de texto
            # Não vai tentar tirar novos prints.
            await doc.save_manual()
        
        print("👋 Aplicação concluída com sucesso.")

if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        # Captura Ctrl+C no terminal
        pass