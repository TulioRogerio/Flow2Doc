def get_injection_script(is_recording, is_paused, step_count, project_name):
    # Cores e Variáveis
    if is_recording and not is_paused:
        status_color, status_text = "#ff0000", "GRAVANDO"
    elif is_paused:
        status_color, status_text = "#ffa500", "PAUSADO"
    else:
        status_color, status_text = "#bbb", "PRONTO"

    display_name = project_name if (project_name and str(project_name) != "None") else "Novo Projeto"
    js_project_name = project_name if (project_name and str(project_name) != "None") else ""

    # Controle de visibilidade dos botões
    if is_recording or is_paused:
        style_start_btn = "none"
        style_name_input = "none"
        style_controls = "flex"
        style_comment = "flex"
    else:
        style_start_btn = "block"
        style_name_input = "none"
        style_controls = "none"
        style_comment = "none"

    return f"""
    (() => {{
        // Variável para controlar o "Debounce" (evita duplicidade Change + Click)
        let changeTimer = null;

        // --- 1. GESTÃO DO PAINEL (UI) ---
        const existingPanel = document.getElementById('doc-panel');
        
        if (existingPanel) {{
            const dot = document.getElementById('doc-dot');
            const status = document.getElementById('doc-status');
            const counter = document.getElementById('step-counter');
            const title = document.getElementById('doc-title');
            const btnStart = document.getElementById('btn-start');
            const nameArea = document.getElementById('name-input-area');
            const controls = document.getElementById('recording-controls');
            const commentBox = document.getElementById('comment-box');
            
            if (dot) {{ dot.style.background = '{status_color}'; dot.style.boxShadow = '0 0 8px {status_color}'; }}
            if (status) status.innerText = '{status_text}';
            if (counter) counter.innerText = 'Passos: {step_count}';
            if (title && '{js_project_name}') title.innerText = '{js_project_name}';
            
            const isLocalTyping = nameArea && nameArea.style.display !== 'none' && '{status_text}' === 'PRONTO';

            if (!isLocalTyping) {{
                if (btnStart) btnStart.style.display = '{style_start_btn}';
                if (nameArea) nameArea.style.display = '{style_name_input}';
            }}
            
            if (controls) controls.style.display = '{style_controls}';
            if (commentBox) commentBox.style.display = '{style_comment}';
            return;
        }}

        // --- CRIAÇÃO DO PAINEL ---
        const panel = document.createElement('div');
        panel.id = 'doc-panel';
        Object.assign(panel.style, {{
            position: 'fixed', top: '10px', left: '50%', transform: 'translateX(-50%)',
            zIndex: '2147483647', background: '#222', color: '#fff', padding: '10px 20px',
            borderRadius: '30px', display: 'flex', gap: '10px', alignItems: 'center',
            boxShadow: '0 6px 25px rgba(0,0,0,0.5)', fontFamily: 'Segoe UI, sans-serif', 
            border: '1px solid #444', flexWrap: 'wrap', maxWidth: '95vw', fontSize: '13px'
        }});

        panel.innerHTML = `
            <div style='display:flex; flex-direction:column; border-right: 1px solid #555; padding-right: 10px; margin-right: 5px'>
                <span style='font-size:9px; color:#aaa; text-transform:uppercase; font-weight:bold'>PROJETO</span>
                <strong id='doc-title' style='color:#fff; max-width:140px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap'>
                    {display_name}
                </strong>
            </div>
            <div style='display:flex; align-items:center; gap:6px; border-right: 1px solid #555; padding-right: 10px'>
                <div id='doc-dot' style='width:10px; height:10px; background:{status_color}; border-radius:50%; box-shadow: 0 0 8px {status_color}'></div>
                <span id='doc-status' style='font-weight:bold; letter-spacing:0.5px'>{status_text}</span>
            </div>
            <span id='step-counter' style='color:#aaa; border-right: 1px solid #555; padding-right: 10px; margin-right: 5px'>Passos: {step_count}</span>
            
            <button id='btn-start' style='display:{style_start_btn}; background:#28a745; color:white; border:none; padding:6px 14px; border-radius:20px; cursor:pointer; font-weight:bold'>▶ Iniciar</button>

            <div id='name-input-area' style='display:{style_name_input}; align-items:center; gap:5px'>
                <input id='project-name-input' type='text' placeholder='Nome do Projeto...' 
                    style='padding:5px 10px; border-radius:15px; border:none; background:#444; color:white; outline:none; width:150px'>
                <button id='btn-confirm-start' style='background:#28a745; color:white; border:none; padding:6px 12px; border-radius:20px; cursor:pointer; font-weight:bold'>OK</button>
            </div>

            <div id='recording-controls' style='display:{style_controls}; align-items:center; gap:5px'>
                <button id='btn-pause' style='background:#ffa500; color:white; border:none; padding:6px 14px; border-radius:20px; cursor:pointer; font-weight:bold'>⏸ Pausar</button>
                <button id='btn-note' style='background:#17a2b8; color:white; border:none; padding:6px 14px; border-radius:20px; cursor:pointer; font-weight:bold'>📸 Nota</button>
                <button id='btn-undo' style='background:#6c757d; color:white; border:none; padding:6px 14px; border-radius:20px; cursor:pointer; font-weight:bold'>↩ Desfazer</button>
                <button id='btn-stop' style='background:#dc3545; color:white; border:none; padding:6px 14px; border-radius:20px; cursor:pointer; font-weight:bold'>⏹ Finalizar</button>
            </div>
            
            <div id='comment-box' style='display:{style_comment}; width:100%; margin-top:8px; border-top: 1px solid #444; padding-top: 8px'>
                <input id='comment-input' type='text' placeholder='Instrução para o próximo passo...' 
                       style='flex-grow:1; padding:6px 10px; border-radius:15px; border:1px solid #555; background:#333; color:#fff; font-size:12px; outline:none'>
                <button id='btn-save-comment' style='background:#007bff; color:white; border:none; padding:6px 12px; border-radius:15px; cursor:pointer; font-weight:bold; margin-left:8px; font-size:11px'>💾</button>
            </div>
        `;
        document.body.appendChild(panel);

        // --- LISTENERS DE BOTÕES ---
        const btnStart = document.getElementById('btn-start');
        const nameInput = document.getElementById('project-name-input');
        const btnConfirmStart = document.getElementById('btn-confirm-start');
        const commentInput = document.getElementById('comment-input');
        const btnSaveComment = document.getElementById('btn-save-comment');
        
        const startRecording = () => {{
            const name = nameInput.value.trim() || 'Projeto_Sem_Nome';
            window.pythonNotify({{event: 'START', filename: name}});
            document.getElementById('name-input-area').style.display = 'none';
            document.getElementById('doc-title').innerText = name;
        }};

        btnStart.onclick = (e) => {{ e.stopPropagation(); btnStart.style.display='none'; document.getElementById('name-input-area').style.display='flex'; nameInput.focus(); }};
        btnConfirmStart.onclick = (e) => {{ e.stopPropagation(); startRecording(); }};
        nameInput.onkeypress = (e) => {{ if (e.key === 'Enter') {{ e.preventDefault(); startRecording(); }} }};

        document.getElementById('btn-pause').onclick = (e) => {{ e.stopPropagation(); window.pythonNotify({{event: 'PAUSE'}}); }};
        document.getElementById('btn-note').onclick = (e) => {{ e.stopPropagation(); const t = prompt('Nota:')||'Nota'; window.pythonNotify({{event:'MANUAL_NOTE', text:t}}); }};
        document.getElementById('btn-undo').onclick = (e) => {{ e.stopPropagation(); if (confirm('Desfazer?')) window.pythonNotify({{event:'UNDO'}}); }};
        document.getElementById('btn-stop').onclick = (e) => {{ e.stopPropagation(); window.pythonNotify({{event:'STOP'}}); document.getElementById('doc-panel')?.remove(); }};

        btnSaveComment.onclick = (e) => {{
            e.stopPropagation();
            const val = commentInput.value.trim();
            if (val) {{
                window.pythonNotify({{event: 'COMMENT', text: val}});
                commentInput.value = '';
                commentInput.placeholder = '✓ Salvo!';
                setTimeout(() => {{ commentInput.placeholder = 'Instrução para o próximo passo...'; }}, 1500);
            }}
        }};

        // --- 2. LÓGICA DE CAPTURA (CLIQUES) ---
        window.addEventListener('click', async (e) => {{
            if (e.target.closest('#doc-panel')) return;

            const el = e.target;
            const isInput = ['INPUT', 'TEXTAREA'].includes(el.tagName) || el.isContentEditable;
            if (isInput) return; 

            // SE HOUVER UM CLICK, CANCELA QUALQUER "CHANGE" PENDENTE
            // Isso evita o print duplo (Preenchimento + Clique no Botão)
            if (changeTimer) {{
                clearTimeout(changeTimer);
                changeTimer = null;
            }}

            if (el.getAttribute('data-doc-bypass') === 'true') {{
                el.removeAttribute('data-doc-bypass');
                return;
            }}

            e.preventDefault();
            e.stopPropagation();

            const h = document.createElement('div');
            Object.assign(h.style, {{
                position: 'absolute',
                left: (e.pageX - 25) + 'px',
                top: (e.pageY - 25) + 'px',
                width: '50px',
                height: '50px',
                border: '4px solid #ffeb3b', 
                borderRadius: '50%',
                backgroundColor: 'rgba(255, 235, 59, 0.4)', 
                zIndex: '2147483646',
                pointerEvents: 'none',
                transform: 'scale(0.5)',
                opacity: '1',
                transition: 'transform 0.3s ease-out'
            }});
            document.body.appendChild(h);
            
            requestAnimationFrame(() => {{ h.style.transform = 'scale(1.4)'; }});

            const text = el.innerText?.substring(0,30) || el.value || 'Elemento';

            await window.pythonNotify({{
                event: 'LOG', 
                type: 'Clique', 
                tag: el.tagName, 
                text: text
            }});

            h.remove(); 
            el.setAttribute('data-doc-bypass', 'true');
            el.click(); 
        }}, true);

        // --- 3. LÓGICA DE CAPTURA (INPUTS/TEXTO) COM DELAY ---
        window.addEventListener('change', async (e) => {{
            if (e.target.closest('#doc-panel')) return;
            const el = e.target;
            
            if (['INPUT','TEXTAREA','SELECT'].includes(el.tagName)) {{
                // Limpa timer anterior se houver
                if (changeTimer) clearTimeout(changeTimer);

                const border = el.style.border;
                el.style.border = '3px solid #4caf50';
                
                // ATRASO DE 400ms PARA VERIFICAR SE O USUÁRIO VAI CLICAR EM ALGO
                changeTimer = setTimeout(async () => {{
                    const val = el.type==='password'?'******':el.value;
                    
                    // Se o timer sobreviveu até aqui, tira o print do preenchimento
                    await window.pythonNotify({{
                        event:'LOG', 
                        type:'Preenchimento', 
                        tag:el.tagName, 
                        text:el.name||'Campo', 
                        value:val
                    }});

                    setTimeout(() => el.style.border = border, 800);
                    changeTimer = null;
                }}, 400); // 400ms de tolerância
            }}
        }}, true);
    }})();
    """