# Configurações globais (caminhos, credenciais, constantes)

import os
from dotenv import load_dotenv # Sugestão: use python-dotenv para segurança

load_dotenv()

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
DOCS_ROOT = os.path.join(BASE_PATH, "docs")

# Configurações de Proxy (Idealmente via variáveis de ambiente)
PROXY_CONFIG = {
    "server": os.getenv("PROXY_SERVER", "sedu2.proxy.dcpr.es.gov.br:1282"),
    "username": os.getenv("PROXY_USER", "tprogerio"),
    "password": os.getenv("PROXY_PASS", "Athene2025!") # Cuidado com senhas hardcoded!
}