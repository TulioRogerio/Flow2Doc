import os
import shutil
from config import DOCS_ROOT

class FileManager:
    def __init__(self, project_name):
        self.project_name = project_name
        
        # A pasta de imagens continua sendo uma subpasta: docs/NomeDoProjeto
        self.project_images_folder = os.path.join(DOCS_ROOT, self.project_name)
        
        # Garante que a pasta de imagens exista
        self._ensure_folders_exist()

    def _ensure_folders_exist(self):
        os.makedirs(self.project_images_folder, exist_ok=True)

    def get_image_full_path(self, filename):
        """Retorna o caminho absoluto para SALVAR o arquivo de imagem no disco."""
        return os.path.join(self.project_images_folder, filename)

    def get_relative_path(self, filename):
        """
        Retorna o link relativo para ser escrito no Markdown.
        
        Como o .md ficará em 'docs/' e a imagem em 'docs/Projeto/',
        o link precisa incluir o nome da pasta do projeto.
        Ex: MeuProjeto/passo_01.png
        """
        return f"{self.project_name}/{filename}"

    def delete_image(self, filename):
        """Remove fisicamente uma imagem (usado no Desfazer)."""
        try:
            file_path = self.get_image_full_path(filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception as e:
            print(f"⚠️ Erro ao deletar imagem {filename}: {e}")
        return False

    def save_markdown(self, content_lines):
        """
        Salva o arquivo .md na raiz 'docs/', um nível ACIMA das imagens.
        """
        md_filename = f"{self.project_name}.md"
        
        # CORREÇÃO/GARANTIA: Usa DOCS_ROOT diretamente, não a pasta de imagens
        output_path = os.path.join(DOCS_ROOT, md_filename)

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.writelines(content_lines)
            return output_path
        except Exception as e:
            print(f"❌ Erro ao salvar Markdown: {e}")
            return None

    def cleanup(self):
        """Limpa a pasta de imagens se o projeto for cancelado ou vazio."""
        try:
            if os.path.exists(self.project_images_folder):
                shutil.rmtree(self.project_images_folder)
                print(f"🗑️ Pasta limpa: {self.project_images_folder}")
        except Exception as e:
            print(f"Erro ao limpar: {e}")