import sys
import os
import asyncio

# Evita criação de arquivos .pyc / __pycache__
sys.dont_write_bytecode = True 

from playwright.async_api import async_playwright
from config import PROXY_CONFIG
from core.generator import DocGenerator

async def run():
    # Inicializa o orquestrador (Engine)
    doc = DocGenerator()
    
    print("🚀 Iniciando Flow2Doc v2.1...")

    try:
        async with async_playwright() as p:
            # 1. Configuração do Navegador
            launch_args = {
                "headless": False,
                "args": ["--start-maximized"],
                "proxy": PROXY_CONFIG if PROXY_CONFIG and PROXY_CONFIG.get("server") else None
            }

            # Tenta usar o Chrome instalado (melhor compatibilidade de vídeo/codecs)
            try:
                browser = await p.chromium.launch(channel="chrome", **launch_args)
            except Exception:
                print("⚠️ Chrome não encontrado. Usando Chromium padrão.")
                browser = await p.chromium.launch(**launch_args)
            
            # Contexto com viewport zerado para pegar o tamanho total da janela
            context = await browser.new_context(no_viewport=True)
            page = await context.new_page()

            # 2. Ponte de Comunicação (Python <-> JS)
            # Quando o JS chamar window.pythonNotify(), essa função roda
            await page.expose_function("pythonNotify", lambda info: doc.handle_event(info, page))

            # 3. Função de Injeção de Interface
            async def inject_interface():
                # Se o sistema estiver ocupado tirando print, NÃO mexe na tela
                if doc.is_capturing: 
                    return 

                try:
                    if not page.is_closed():
                        # Obtém o script combinado (Config + Tracker.js)
                        js_code = doc.get_js()
                        if js_code:
                            await page.evaluate(js_code)
                except Exception:
                    pass # Ignora erros se a página estiver fechando/navegando

            # Injeta ao carregar nova página
            await page.add_init_script(doc.get_js())
            page.on("framenavigated", lambda _: asyncio.create_task(inject_interface()))

            # 4. Abertura Inicial
            print("✅ Sistema Pronto! Navegue para começar.")
            try:
                # Pode alterar para a URL que desejar iniciar
                await page.goto("https://conecta.sedu.es.gov.br")
                await asyncio.sleep(1)
                await inject_interface()
            except Exception as e:
                print(f"⚠️ Aviso ao carregar página inicial: {e}")

            # 5. Loop Principal (Mantém o programa vivo)
            while not doc.finished:
                try:
                    # Verifica se o navegador foi fechado pelo usuário
                    if not browser.is_connected() or page.is_closed():
                        print("\n❌ Navegador encerrado.")
                        break

                    # Loop de verificação (Heartbeat)
                    await asyncio.sleep(1.0)
                    
                    # Re-injeta a interface se necessário (garante que o menu não suma)
                    # A condição "not is_capturing" é vital para não estragar os prints
                    if not doc.is_capturing:
                        await inject_interface()
                        
                except Exception:
                    break

    except Exception as e:
        print(f"\n⚠️ Erro crítico: {e}")

    finally:
        # 6. Encerramento Seguro
        print("\n🛑 Encerrando aplicação...")
        # Se sobraram logs na memória (crash ou fechamento forçado), salva agora
        if doc.logs: 
            print("💾 Salvando trabalho pendente de emergência...")
            await doc.save_manual()
        
        print("👋 Até logo!")

if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        pass