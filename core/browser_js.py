import os

def get_injection_script(is_recording, is_paused, step_count, project_name):
    # 1. Define o estado atual (Lógica Python)
    if is_recording and not is_paused:
        status_color, status_text = "#ff0000", "GRAVANDO"
    elif is_paused:
        status_color, status_text = "#ffa500", "PAUSADO"
    else:
        status_color, status_text = "#bbb", "PRONTO"

    js_project_name = project_name if (project_name and str(project_name) != "None") else ""
    display_name = js_project_name if js_project_name else "Novo Projeto"

    # Define visibilidade CSS
    if is_recording or is_paused:
        styles = {
            "startBtn": "none",
            "nameInput": "none",
            "controls": "flex",
            "comment": "flex"
        }
    else:
        styles = {
            "startBtn": "block",
            "nameInput": "none",
            "controls": "none",
            "comment": "none"
        }

    # 2. Cria o objeto de configuração JS
    config_script = f"""
    window.DocGenState = {{
        statusColor: '{status_color}',
        statusText: '{status_text}',
        stepCount: {step_count},
        projectName: '{js_project_name}',
        displayTitle: '{display_name}',
        styles: {{
            startBtn: '{styles["startBtn"]}',
            nameInput: '{styles["nameInput"]}',
            controls: '{styles["controls"]}',
            comment: '{styles["comment"]}'
        }}
    }};
    """

    # 3. Lê os arquivos JS (Blur + Tracker)
    try:
        # AQUI ESTA A CORREÇÃO: Lemos também o blur_tool.js
        tracker_path = os.path.join("assets", "tracker.js")
        blur_path = os.path.join("assets", "blur_tool.js")
        
        js_code_combined = ""

        # Primeiro lê a ferramenta de blur (se existir)
        if os.path.exists(blur_path):
            with open(blur_path, "r", encoding="utf-8") as f:
                js_code_combined += f.read() + "\n"
        else:
            print(f"⚠️ Aviso: {blur_path} não encontrado.")

        # Depois lê o tracker principal
        if os.path.exists(tracker_path):
            with open(tracker_path, "r", encoding="utf-8") as f:
                js_code_combined += f.read()
        else:
            print(f"❌ ERRO CRÍTICO: {tracker_path} não encontrado!")
            return ""

    except Exception as e:
        print(f"❌ Erro ao ler scripts JS: {e}")
        return ""

    # 4. Retorna a combinação (Config + Blur + Tracker)
    return config_script + "\n" + js_code_combined