import datetime

class MarkdownFormatter:
    @staticmethod
    def format_step(step_num, info, img_path, pending_comment=None):
        entry = f"### Passo {step_num}\n\n"
        
        if pending_comment:
            entry += f"📄 **Comentários:** {pending_comment}\n\n"
        
        if info.get('value'):
            entry += f"**✍️ Valor inserido:** `{info.get('value')}`\n\n"
        
        # Link Limpo: apenas o caminho que vem do generator (Pasta/Imagem)
        # O uso de < > ajuda com espaços no nome
        entry += f"![Passo {step_num}](<{img_path}>)\n\n---\n\n"
        
        return entry

    @staticmethod
    def format_manual_note(note_num, note_text, img_path):
        return (
            f"### 📌 Nota {note_num}\n\n"
            f"**💡 Observação:** {note_text}\n\n"
            f"![Nota {note_num}](<{img_path}>)\n\n---\n\n"
        )

    @staticmethod
    def format_header(title, total_steps, start_time):
        return (
            f"# 📘 {title}\n\n"
            f"**📅 Data:** {start_time.strftime('%d/%m/%Y')}\n"
            f"**⏰ Horário:** {start_time.strftime('%H:%M:%S')}\n"
            f"**📊 Passos:** {total_steps}\n\n---\n\n## 📋 Detalhamento\n\n"
        )

    @staticmethod
    def format_footer():
        return "\n---\n\n## ✅ Conclusão\n\nManual finalizado com sucesso! 🎉\n"