(() => {
  // 1. CONFIGURAÇÃO (Recebida do Python)
  const state = window.DocGenState || {
    statusColor: "#bbb",
    statusText: "DESCONECTADO",
    stepCount: 0,
    projectName: "",
    displayTitle: "Novo Projeto",
    styles: {
      startBtn: "block",
      nameInput: "none",
      controls: "none",
      comment: "none",
    },
  };

  let changeTimer = null;

  // --- 2. GESTÃO DO PAINEL (UI) ---
  const existingPanel = document.getElementById("doc-panel");

  if (existingPanel) {
    const dot = document.getElementById("doc-dot");
    const status = document.getElementById("doc-status");
    const counter = document.getElementById("step-counter");
    const title = document.getElementById("doc-title");
    const btnStart = document.getElementById("btn-start");
    const nameArea = document.getElementById("name-input-area");
    const controls = document.getElementById("recording-controls");
    const commentBox = document.getElementById("comment-box");
    // Referência ao botão blur
    const btnBlur = document.getElementById("btn-blur");

    if (dot) {
      dot.style.background = state.statusColor;
      dot.style.boxShadow = `0 0 8px ${state.statusColor}`;
    }
    if (status) status.innerText = state.statusText;
    if (counter) counter.innerText = `Passos: ${state.stepCount}`;
    if (title && state.projectName) title.innerText = state.projectName;

    const isLocalTyping =
      nameArea &&
      nameArea.style.display !== "none" &&
      state.statusText === "PRONTO";

    if (!isLocalTyping) {
      if (btnStart) btnStart.style.display = state.styles.startBtn;
      if (nameArea) nameArea.style.display = state.styles.nameInput;
    }

    if (controls) controls.style.display = state.styles.controls;
    if (commentBox) commentBox.style.display = state.styles.comment;

    // --- CORREÇÃO AQUI ---
    // Verifica o estado REAL da ferramenta antes de atualizar o botão
    if (btnBlur && window.BlurTool) {
      if (window.BlurTool.isActive()) {
        // Se estiver desenhando, mantém o visual de "Cancelar"
        btnBlur.style.border = "2px solid #fff";
        btnBlur.innerText = "Cancelar";
      } else {
        // Se estiver parado, volta ao normal
        btnBlur.style.border = "none";
        btnBlur.innerText = "👁️‍🗨️ Blur";
      }
    }
    return;
  }

  // --- 3. CRIAÇÃO DO PAINEL (Primeira vez) ---
  const panel = document.createElement("div");
  panel.id = "doc-panel";
  Object.assign(panel.style, {
    position: "fixed",
    top: "10px",
    left: "50%",
    transform: "translateX(-50%)",
    zIndex: "2147483647",
    background: "#222",
    color: "#fff",
    padding: "10px 20px",
    borderRadius: "30px",
    display: "flex",
    gap: "10px",
    alignItems: "center",
    boxShadow: "0 6px 25px rgba(0,0,0,0.5)",
    fontFamily: "Segoe UI, sans-serif",
    border: "1px solid #444",
    flexWrap: "wrap",
    maxWidth: "95vw",
    fontSize: "13px",
  });

  panel.innerHTML = `
        <div style='display:flex; flex-direction:column; border-right: 1px solid #555; padding-right: 10px; margin-right: 5px'>
            <span style='font-size:9px; color:#aaa; text-transform:uppercase; font-weight:bold'>PROJETO</span>
            <strong id='doc-title' style='color:#fff; max-width:140px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap'>
                ${state.displayTitle}
            </strong>
        </div>
        <div style='display:flex; align-items:center; gap:6px; border-right: 1px solid #555; padding-right: 10px'>
            <div id='doc-dot' style='width:10px; height:10px; background:${state.statusColor}; border-radius:50%; box-shadow: 0 0 8px ${state.statusColor}'></div>
            <span id='doc-status' style='font-weight:bold; letter-spacing:0.5px'>${state.statusText}</span>
        </div>
        <span id='step-counter' style='color:#aaa; border-right: 1px solid #555; padding-right: 10px; margin-right: 5px'>Passos: ${state.stepCount}</span>
        
        <button id='btn-start' style='display:${state.styles.startBtn}; background:#28a745; color:white; border:none; padding:6px 14px; border-radius:20px; cursor:pointer; font-weight:bold'>▶ Iniciar</button>

        <div id='name-input-area' style='display:${state.styles.nameInput}; align-items:center; gap:5px'>
            <input id='project-name-input' type='text' placeholder='Nome do Projeto...' 
                style='padding:5px 10px; border-radius:15px; border:none; background:#444; color:white; outline:none; width:150px'>
            <button id='btn-confirm-start' style='background:#28a745; color:white; border:none; padding:6px 12px; border-radius:20px; cursor:pointer; font-weight:bold'>OK</button>
        </div>

        <div id='recording-controls' style='display:${state.styles.controls}; align-items:center; gap:5px'>
            <button id='btn-pause' style='background:#ffa500; color:white; border:none; padding:6px 14px; border-radius:20px; cursor:pointer; font-weight:bold'>⏸ Pausar</button>
            <button id='btn-blur' style='background:#6f42c1; color:white; border:none; padding:6px 14px; border-radius:20px; cursor:pointer; font-weight:bold' title='Selecione e arraste. Botão direito para apagar.'>👁️‍🗨️ Blur</button>
            <button id='btn-note' style='background:#17a2b8; color:white; border:none; padding:6px 14px; border-radius:20px; cursor:pointer; font-weight:bold'>📸 Nota</button>
            <button id='btn-undo' style='background:#6c757d; color:white; border:none; padding:6px 14px; border-radius:20px; cursor:pointer; font-weight:bold'>↩ Desfazer</button>
            <button id='btn-stop' style='background:#dc3545; color:white; border:none; padding:6px 14px; border-radius:20px; cursor:pointer; font-weight:bold'>⏹ Finalizar</button>
        </div>
        
        <div id='comment-box' style='display:${state.styles.comment}; width:100%; margin-top:8px; border-top: 1px solid #444; padding-top: 8px'>
            <input id='comment-input' type='text' placeholder='Instrução para o próximo passo...' 
                   style='flex-grow:1; padding:6px 10px; border-radius:15px; border:1px solid #555; background:#333; color:#fff; font-size:12px; outline:none'>
            <button id='btn-save-comment' style='background:#007bff; color:white; border:none; padding:6px 12px; border-radius:15px; cursor:pointer; font-weight:bold; margin-left:8px; font-size:11px'>💾</button>
        </div>
    `;
  document.body.appendChild(panel);

  // --- 4. LISTENERS DE BOTÕES ---
  const btnStart = document.getElementById("btn-start");
  const nameInput = document.getElementById("project-name-input");
  const btnConfirmStart = document.getElementById("btn-confirm-start");
  const commentInput = document.getElementById("comment-input");
  const btnSaveComment = document.getElementById("btn-save-comment");
  const btnBlur = document.getElementById("btn-blur");

  const startRecording = () => {
    const name = nameInput.value.trim() || "Projeto_Sem_Nome";
    window.pythonNotify({ event: "START", filename: name });
    document.getElementById("name-input-area").style.display = "none";
    document.getElementById("doc-title").innerText = name;
  };

  btnStart.onclick = (e) => {
    e.stopPropagation();
    btnStart.style.display = "none";
    document.getElementById("name-input-area").style.display = "flex";
    nameInput.focus();
  };
  btnConfirmStart.onclick = (e) => {
    e.stopPropagation();
    startRecording();
  };
  nameInput.onkeypress = (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      startRecording();
    }
  };

  document.getElementById("btn-pause").onclick = (e) => {
    e.stopPropagation();
    window.pythonNotify({ event: "PAUSE" });
  };

  // --- Lógica do Botão Blur ---
  btnBlur.onclick = (e) => {
    e.stopPropagation();
    if (window.BlurTool) {
      const isActive = window.BlurTool.toggle();
      if (isActive) {
        btnBlur.style.border = "2px solid #fff";
        btnBlur.innerText = "Cancelar";
        commentInput.placeholder = "Selecione a área para ofuscar...";
      } else {
        btnBlur.style.border = "none";
        btnBlur.innerText = "👁️‍🗨️ Blur";
        commentInput.placeholder = "Instrução para o próximo passo...";
      }
    } else {
      alert("Ferramenta de Blur não carregada! Reinicie a aplicação.");
    }
  };

  // Listener para resetar o botão quando o desenho termina
  window.onBlurToolChange = (isActive) => {
    if (!isActive && btnBlur) {
      btnBlur.style.border = "none";
      btnBlur.innerText = "👁️‍🗨️ Blur";
      commentInput.placeholder = "Instrução para o próximo passo...";
    }
  };

  document.getElementById("btn-note").onclick = (e) => {
    e.stopPropagation();
    const t = prompt("Nota:") || "Nota";
    window.pythonNotify({ event: "MANUAL_NOTE", text: t });
  };

  document.getElementById("btn-stop").onclick = (e) => {
    e.stopPropagation();
    window.pythonNotify({ event: "STOP" });
    document.getElementById("doc-panel")?.remove();
  };

  document.getElementById("btn-undo").onclick = (e) => {
    e.stopPropagation();
    e.preventDefault();
    if (window.BlurTool) window.BlurTool.clear();
    window.pythonNotify({ event: "UNDO" });
  };

  btnSaveComment.onclick = (e) => {
    e.stopPropagation();
    const val = commentInput.value.trim();
    if (val) {
      window.pythonNotify({ event: "COMMENT", text: val });
      commentInput.value = "";
      commentInput.placeholder = "✓ Salvo!";
      setTimeout(() => {
        commentInput.placeholder = "Instrução para o próximo passo...";
      }, 1500);
    }
  };

  // --- 5. LISTENERS GLOBAIS ---
  if (window.docGenListenersAttached) return;
  window.docGenListenersAttached = true;

  window.addEventListener(
    "click",
    async (e) => {
      // 1. IMPEDE PRINT COM BOTÃO DIREITO (Usado para excluir Blur)
      if (e.button !== 0) return;

      // 2. IMPEDE PRINT SE ESTIVER DESENHANDO UM BLUR
      if (window.BlurTool && window.BlurTool.isActive()) {
        e.preventDefault();
        e.stopPropagation();
        return;
      }

      // 3. Ignora cliques no painel ou em blurs já existentes
      if (
        e.target.closest("#doc-panel") ||
        e.target.classList.contains("doc-blur-overlay")
      )
        return;

      const el = e.target;
      const isInput =
        ["INPUT", "TEXTAREA"].includes(el.tagName) || el.isContentEditable;
      if (isInput) return;

      if (changeTimer) {
        clearTimeout(changeTimer);
        changeTimer = null;
      }

      if (el.getAttribute("data-doc-bypass") === "true") {
        el.removeAttribute("data-doc-bypass");
        return;
      }

      e.preventDefault();
      e.stopPropagation();

      const h = document.createElement("div");
      Object.assign(h.style, {
        position: "absolute",
        left: e.pageX - 25 + "px",
        top: e.pageY - 25 + "px",
        width: "50px",
        height: "50px",
        border: "4px solid #ffeb3b",
        borderRadius: "50%",
        backgroundColor: "rgba(255, 235, 59, 0.4)",
        zIndex: "2147483646",
        pointerEvents: "none",
        transform: "scale(0.5)",
        opacity: "1",
        transition: "transform 0.3s ease-out",
      });
      document.body.appendChild(h);

      requestAnimationFrame(() => {
        h.style.transform = "scale(1.4)";
      });

      const text = el.innerText?.substring(0, 30) || el.value || "Elemento";

      await window.pythonNotify({
        event: "LOG",
        type: "Clique",
        tag: el.tagName,
        text: text,
      });

      h.remove();
      el.setAttribute("data-doc-bypass", "true");
      el.click();
    },
    true
  );

  window.addEventListener(
    "change",
    async (e) => {
      if (e.target.closest("#doc-panel")) return;
      const el = e.target;

      if (["INPUT", "TEXTAREA", "SELECT"].includes(el.tagName)) {
        if (changeTimer) clearTimeout(changeTimer);
        const border = el.style.border;
        el.style.border = "3px solid #4caf50";
        changeTimer = setTimeout(async () => {
          const val = el.type === "password" ? "******" : el.value;
          await window.pythonNotify({
            event: "LOG",
            type: "Preenchimento",
            tag: el.tagName,
            text: el.name || "Campo",
            value: val,
          });
          setTimeout(() => (el.style.border = border), 800);
          changeTimer = null;
        }, 400);
      }
    },
    true
  );
})();
