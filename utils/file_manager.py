import os
import shutil
from config import DOCS_ROOT

class FileManager:
    def __init__(self, project_name):
        self.project_name = project_name
        
        # 1. Define o caminho da PASTA (que conterá as imagens)
        # Ex: docs/MeuManual
        self.images_folder_path = os.path.join(DOCS_ROOT, self.project_name)
        
        # 2. Garante que essa pasta existe
        os.makedirs(self.images_folder_path, exist_ok=True)

    def get_image_path(self, filename):
        """Retorna o caminho completo para salvar a imagem dentro da pasta"""
        return os.path.join(self.images_folder_path, filename)

    def save_markdown(self, content_lines):
        """Salva o arquivo .md FORA da pasta de imagens (na raiz de docs)"""
        # Ex: docs/MeuManual.md
        filename = f"{self.project_name}.md"
        output_path = os.path.join(DOCS_ROOT, filename)
        
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.writelines(content_lines)
            return output_path
        except Exception as e:
            print(f"❌ Erro ao salvar Markdown: {e}")
            return None

    def cleanup(self):
        """Remove a pasta de imagens e o arquivo MD se existirem (limpeza)"""
        try:
            # Remove a pasta de imagens
            if os.path.exists(self.images_folder_path):
                shutil.rmtree(self.images_folder_path)
                print(f"🗑️ Pasta removida: {self.images_folder_path}")
            
            # Remove o arquivo .md se tiver sido criado parcialmente
            md_path = os.path.join(DOCS_ROOT, f"{self.project_name}.md")
            if os.path.exists(md_path):
                os.remove(md_path)
        except Exception as e:
            print(f"Erro ao limpar arquivos: {e}")