import asyncio
import datetime
import re
from utils.formatter import MarkdownFormatter
from utils.file_manager import FileManager
from core.browser_js import get_injection_script

class DocGenerator:
    def __init__(self):
        self.reset_state()

    def reset_state(self):
        self.is_recording = False
        self.is_paused = False
        self.finished = False
        self.is_capturing = False
        self.logs = []
        self.step_counter = 0
        self.pending_comment = None
        self.base_filename = None
        self.file_manager = None
        self.start_time = None
        print("🔄 Estado resetado.")

    def sanitize_filename(self, filename):
        if not filename: return "Projeto_Sem_Nome"
        clean = re.sub(r'[<>:"/\\|?*]', '_', filename)
        return clean.strip()

    def initialize_file_manager(self, filename):
        clean_name = self.sanitize_filename(filename)
        self.base_filename = clean_name
        self.file_manager = FileManager(clean_name)
        self.start_time = datetime.datetime.now()
        print(f"\n📂 PROJETO DEFINIDO: {clean_name}")

    async def handle_event(self, info, page):
        event_type = info.get('event', '').upper()
        
        if event_type == 'START':
            raw_name = info.get('filename')
            if not self.base_filename:
                if not raw_name: raw_name = "Projeto_Sem_Nome"
                self.initialize_file_manager(raw_name)
            self.is_recording = True
            self.is_paused = False
            await page.evaluate(self.get_js())
            print(f"🔴 GRAVAÇÃO INICIADA")
        
        elif event_type == 'STOP':
            print("⏹️ Finalizando...")
            self.is_recording = False
            await self.save_manual()
            self.reset_state()
            
        elif event_type == 'PAUSE':
            self.is_paused = not self.is_paused
            print(f"⏸️ Status: {'PAUSADO' if self.is_paused else 'RETOMADO'}")

        elif event_type == 'COMMENT':
            self.pending_comment = info.get('text', '')
            print(f"💬 Comentário: {self.pending_comment}")

        elif event_type == 'UNDO':
            # --- CORREÇÃO DA LÓGICA DE DESFAZER ---
            if self.logs and self.step_counter > 0:
                # 1. Reconstrói o nome da imagem que será apagada
                img_to_delete = f"{self.base_filename}({self.step_counter:02d}).png"
                
                # 2. Apaga o arquivo físico
                if self.file_manager:
                    deleted = self.file_manager.delete_image(img_to_delete)
                    msg_file = " (Imagem apagada)" if deleted else ""

                # 3. Remove do log e recua o contador
                self.logs.pop()
                print(f"↩️ Passo {self.step_counter} desfeito.{msg_file}")
                self.step_counter -= 1
            else:
                print("⚠️ Nada para desfazer (Lista vazia).")

        elif event_type in ['LOG', 'MANUAL_NOTE']:
            if self.is_recording and not self.is_paused:
                await self.capture_action(info, page, is_manual=(event_type=='MANUAL_NOTE'))

    async def capture_action(self, info, page, is_manual=False):
        if not self.file_manager:
            self.initialize_file_manager("Recuperado")

        self.is_capturing = True 
        
        self.step_counter += 1
        img_filename = f"{self.base_filename}({self.step_counter:02d}).png"
        img_full_path = self.file_manager.get_image_path(img_filename)
        print(f"📸 Passo {self.step_counter}")

        try:
            # 1. ESCONDE O MENU
            await page.evaluate("const p = document.getElementById('doc-panel'); if(p) p.style.display = 'none';")
            
            # 2. PEQUENO DELAY
            if not is_manual: 
                await asyncio.sleep(0.2) 
            
            # 3. TIRA O PRINT
            await page.screenshot(path=img_full_path, full_page=False)
            
            # 4. MOSTRA O MENU DE VOLTA
            await page.evaluate("const p = document.getElementById('doc-panel'); if(p) p.style.display = 'flex';")

            relative_img_path = f"{self.base_filename}/{img_filename}"

            if is_manual:
                entry = MarkdownFormatter.format_manual_note(
                    self.step_counter, info.get('text', ''), relative_img_path
                )
            else:
                entry = MarkdownFormatter.format_step(
                    self.step_counter, info, relative_img_path, self.pending_comment
                )
                self.pending_comment = None

            self.logs.append(entry)

        except Exception as e:
            print(f"❌ Erro: {e}")
            self.step_counter -= 1
        
        finally:
             self.is_capturing = False

    async def save_manual(self):
        if not self.logs:
            print("⚠️ Nada gravado.")
            self.file_manager.cleanup()
            return
        full_content = []
        start_t = self.start_time or datetime.datetime.now()
        full_content.append(MarkdownFormatter.format_header(
            self.base_filename, self.step_counter, start_t
        ))
        full_content.extend(self.logs)
        full_content.append(MarkdownFormatter.format_footer())
        path = self.file_manager.save_markdown(full_content)
        if path:
            print(f"✅ Manual salvo em: {path}")

    def get_js(self):
        return get_injection_script(self.is_recording, self.is_paused, self.step_counter, self.base_filename)