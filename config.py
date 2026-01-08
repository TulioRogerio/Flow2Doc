import os
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env (se existir)
load_dotenv()

# --- CAMINHOS DE PASTAS ---
# Garante que a raiz seja a pasta onde este arquivo config.py está
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# Pasta onde os manuais serão salvos
DOCS_ROOT = os.path.join(BASE_PATH, "docs")

# Pasta de assets (onde fica o tracker.js)
ASSETS_PATH = os.path.join(BASE_PATH, "assets")

# --- CONFIGURAÇÕES DE REDE / PROXY ---
# Tenta pegar do .env, senão usa o padrão (cuidado com senhas aqui)
PROXY_CONFIG = {
    "server": os.getenv("PROXY_SERVER", "sedu2.proxy.dcpr.es.gov.br:1282"),
    "username": os.getenv("PROXY_USER", "tprogerio"),
    "password": os.getenv("PROXY_PASS", "Athene2025!")
}

# Se não tiver usuário/senha configurado, retorna None para o Playwright não tentar autenticar
if not PROXY_CONFIG["server"]:
    PROXY_CONFIG = None