import asyncio
import datetime
import re
from dataclasses import dataclass, field
from typing import List, Optional

from utils.formatter import MarkdownFormatter
from utils.file_manager import FileManager
from core.browser_js import get_injection_script

@dataclass
class DocState:
    """Armazena o estado atual da gravação."""
    is_recording: bool = False
    is_paused: bool = False
    is_capturing: bool = False  # Trava para não tirar 2 prints ao mesmo tempo
    step_counter: int = 0
    base_filename: Optional[str] = None
    start_time: Optional[datetime.datetime] = None
    pending_comment: Optional[str] = None
    logs: List[str] = field(default_factory=list)

class DocGenerator:
    def __init__(self):
        self.state = DocState()
        self.file_manager = None
        self.finished = False  # Controla o loop do main.py

    def reset(self):
        """Reseta o estado para um novo projeto."""
        self.state = DocState()
        self.file_manager = None
        self.finished = False
        print("🔄 Estado resetado. Pronto para novo projeto.")

    def _sanitize_filename(self, filename):
        if not filename: return "Projeto_Sem_Nome"
        # Remove caracteres inválidos
        clean = re.sub(r'[<>:"/\\|?*]', '', filename).strip()
        # Substitui espaços por underline
        return clean.replace(' ', '_')

    def _init_project(self, raw_name):
        """Inicializa gerenciador de arquivos e cronômetro."""
        clean_name = self._sanitize_filename(raw_name)
        self.state.base_filename = clean_name
        self.state.start_time = datetime.datetime.now()
        self.file_manager = FileManager(clean_name)
        print(f"\n📂 PROJETO INICIADO: {clean_name}")

    async def handle_event(self, info, page):
        """Recebe eventos do JavaScript (tracker.js)."""
        event_type = info.get('event', '').upper()
        
        # --- COMANDOS DE CONTROLE ---
        if event_type == 'START':
            self._init_project(info.get('filename'))
            self.state.is_recording = True
            self.state.is_paused = False
            # Atualiza a UI imediatamente para mostrar botões de controle
            try:
                await page.evaluate(self.get_js())
            except Exception:
                pass

        elif event_type == 'STOP':
            print("⏹️ Finalizando projeto...")
            self.state.is_recording = False
            await self.save_manual()
            self.reset() # Reseta para permitir novo projeto

        elif event_type == 'PAUSE':
            self.state.is_paused = not self.state.is_paused
            status = "PAUSADO" if self.state.is_paused else "GRAVANDO"
            print(f"⏸️ {status}")

        elif event_type == 'UNDO':
            await self._handle_undo()

        # --- COMANDOS DE DADOS ---
        elif event_type == 'COMMENT':
            self.state.pending_comment = info.get('text', '')
            print(f"💬 Comentário pendente: {self.state.pending_comment}")

        elif event_type in ['LOG', 'MANUAL_NOTE']:
            # Só captura se estiver gravando e não estiver pausado
            if self.state.is_recording and not self.state.is_paused:
                await self._capture_action(info, page, is_manual=(event_type == 'MANUAL_NOTE'))

    async def _capture_action(self, info, page, is_manual=False):
        """Lógica central de captura de tela."""
        if not self.file_manager:
            self._init_project("Recuperado_Crash")

        # TRAVA: Impede conflitos de captura
        self.state.is_capturing = True
        
        try:
            self.state.step_counter += 1
            step_num = self.state.step_counter
            
            # Nome do arquivo da imagem formatado (Projeto01.png)
            img_name = f"{self.state.base_filename}{step_num:02d}.png"
            full_path = self.file_manager.get_image_full_path(img_name)
            
            print(f"📸 Capturando Passo {step_num}...")

            # 1. Esconde o menu para a foto
            await page.evaluate("const p=document.getElementById('doc-panel'); if(p) p.style.display='none';")
            
            # 2. Pequeno delay para garantir renderização (bolinha/destaque)
            if not is_manual:
                await asyncio.sleep(0.15) 
            
            # 3. Tira o print
            await page.screenshot(path=full_path)
            
            # 4. Mostra o menu de volta
            await page.evaluate("const p=document.getElementById('doc-panel'); if(p) p.style.display='flex';")

            # 5. Obtém o link relativo correto (Projeto/Imagem.png)
            relative_link = self.file_manager.get_relative_path(img_name)

            if is_manual:
                log_entry = MarkdownFormatter.format_manual_note(
                    step_num, info.get('text', ''), relative_link
                )
            else:
                log_entry = MarkdownFormatter.format_step(
                    step_num, info, relative_link, self.state.pending_comment
                )
                self.state.pending_comment = None # Limpa comentário após uso

            self.state.logs.append(log_entry)

        except Exception as e:
            print(f"❌ Erro na captura: {e}")
            self.state.step_counter -= 1 # Reverte contador em caso de erro
        
        finally:
            self.state.is_capturing = False

    async def _handle_undo(self):
        """Desfaz o último passo e apaga a imagem."""
        if self.state.logs and self.state.step_counter > 0:
            # Recria o nome da imagem que deve ser deletada
            img_name = f"{self.state.base_filename}{self.state.step_counter:02d}.png"
            
            # Deleta arquivo físico
            if self.file_manager.delete_image(img_name):
                print(f"🗑️ Imagem deletada: {img_name}")
            
            # Remove log da memória
            self.state.logs.pop()
            self.state.step_counter -= 1
            print(f"↩️ Passo desfeito. Total: {self.state.step_counter}")
        else:
            print("⚠️ Nada para desfazer.")

    async def save_manual(self):
        """Compila e salva o manual final."""
        if not self.state.logs:
            print("⚠️ Projeto vazio. Nada salvo.")
            if self.file_manager:
                self.file_manager.cleanup()
            return

        full_content = []
        # Header
        full_content.append(MarkdownFormatter.format_header(
            self.state.base_filename, 
            self.state.step_counter, 
            self.state.start_time
        ))
        # Steps
        full_content.extend(self.state.logs)
        # Footer
        full_content.append(MarkdownFormatter.format_footer())

        path = self.file_manager.save_markdown(full_content)
        if path:
            print(f"✅ MANUAL SALVO COM SUCESSO EM:\n   -> {path}")

    # Exposição de propriedades para o main.py
    @property
    def is_capturing(self):
        return self.state.is_capturing
    
    @property
    def is_recording(self):
        return self.state.is_recording
    
    @property
    def is_paused(self):
        return self.state.is_paused
    
    @property
    def logs(self):
        return self.state.logs

    def get_js(self):
        """Gera o script de injeção com o estado atual."""
        return get_injection_script(
            self.state.is_recording, 
            self.state.is_paused, 
            self.state.step_counter, 
            self.state.base_filename
        )