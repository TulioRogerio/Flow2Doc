import datetime

class MarkdownFormatter:
    @staticmethod
    def format_header(title, total_steps, start_time):
        """Gera o cabeçalho do documento."""
        return (
            f"# 📘 {title}\n\n"
            f"**📅 Data:** {start_time.strftime('%d/%m/%Y')}\n"
            f"**⏰ Início:** {start_time.strftime('%H:%M:%S')}\n"
            f"**📊 Total de Passos:** {total_steps}\n\n"
            "---\n\n"
            "## 📋 Detalhamento do Processo\n\n"
        )

    @staticmethod
    def format_step(step_num, info, img_path, pending_comment=None):
        """Formata um passo padrão (clique, input)."""
        entry = f"### Passo {step_num}\n\n"
        
        # Se houver instrução pendente, adiciona antes da imagem
        if pending_comment:
            entry += f"📄 **Instrução:** {pending_comment}\n\n"
        
        # Se for um input de texto, mostra o valor digitado
        if info.get('value'):
            entry += f"**✍️ Preenchimento:** `{info.get('value')}`\n\n"
        
        # Link da imagem formatado para compatibilidade
        # O uso de < > ajuda com espaços no nome, embora tenhamos removido espaços
        entry += f"![Passo {step_num}](<{img_path}>)\n\n---\n\n"
        return entry

    @staticmethod
    def format_manual_note(note_num, note_text, img_path):
        """Formata uma nota manual (botão 'Nota')."""
        return (
            f"### 📌 Nota {note_num}\n\n"
            f"**💡 Observação:** {note_text}\n\n"
            f"![Nota {note_num}](<{img_path}>)\n\n---\n\n"
        )

    @staticmethod
    def format_footer():
        """Gera o rodapé do documento."""
        return (
            "\n---\n\n"
            "## ✅ Conclusão\n\n"
            "Documentação gerada automaticamente pelo **Flow2Doc**.\n"
        )