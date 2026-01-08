window.BlurTool = (() => {
  let _isActive = false; // Variável interna renomeada para evitar conflitos
  let isDrawing = false;
  let startX = 0;
  let startY = 0;
  let currentBox = null;

  const selectionStyle = `
      position: fixed; z-index: 2147483647; 
      border: 2px dashed #ff0000; background: rgba(255, 0, 0, 0.1);
      pointer-events: none;
  `;

  const blurStyle = `
      position: fixed; z-index: 2147483640;
      backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
      background: rgba(255, 255, 255, 0.1);
      border: 2px solid red;
      cursor: pointer; 
      pointer-events: auto;
  `;

  function init() {
    document.body.addEventListener("mousedown", onMouseDown);
    document.body.addEventListener("mousemove", onMouseMove);
    document.body.addEventListener("mouseup", onMouseUp);
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && _isActive) toggleMode(false);
    });
  }

  function toggleMode(forceState) {
    _isActive = forceState !== undefined ? forceState : !_isActive;
    document.body.style.cursor = _isActive ? "crosshair" : "default";
    return _isActive;
  }

  // --- NOVA FUNÇÃO ---
  // Permite que o tracker.js saiba se estamos no meio de um desenho
  function getIsActive() {
    return _isActive;
  }

  function onMouseDown(e) {
    if (!_isActive) return;
    if (e.target.closest("#doc-panel")) return;

    // Impede que o clique se propague para o site
    e.preventDefault();
    e.stopPropagation();

    isDrawing = true;
    startX = e.clientX;
    startY = e.clientY;

    currentBox = document.createElement("div");
    currentBox.style.cssText = selectionStyle;
    currentBox.style.left = startX + "px";
    currentBox.style.top = startY + "px";
    document.body.appendChild(currentBox);
  }

  function onMouseMove(e) {
    if (!_isActive || !isDrawing || !currentBox) return;

    const currentX = e.clientX;
    const currentY = e.clientY;

    const width = Math.abs(currentX - startX);
    const height = Math.abs(currentY - startY);
    const left = Math.min(currentX, startX);
    const top = Math.min(currentY, startY);

    currentBox.style.width = width + "px";
    currentBox.style.height = height + "px";
    currentBox.style.left = left + "px";
    currentBox.style.top = top + "px";
  }

  function onMouseUp(e) {
    if (!_isActive || !isDrawing) return;
    isDrawing = false;

    if (currentBox) {
      const finalBox = currentBox;
      const rect = finalBox.getBoundingClientRect();

      finalBox.style.cssText = blurStyle;
      finalBox.style.width = rect.width + "px";
      finalBox.style.height = rect.height + "px";
      finalBox.style.left = rect.left + "px";
      finalBox.style.top = rect.top + "px";

      finalBox.classList.add("doc-blur-overlay");
      finalBox.title = "Clique com botão direito para remover";

      // Remove com botão direito
      finalBox.oncontextmenu = (ev) => {
        ev.preventDefault();
        ev.stopPropagation();
        finalBox.remove();
      };

      currentBox = null;
      toggleMode(false); // Desativa modo desenho
      if (window.onBlurToolChange) window.onBlurToolChange(false);
    }
  }

  function clear() {
    document.querySelectorAll(".doc-blur-overlay").forEach((el) => el.remove());
  }

  return {
    init,
    toggle: toggleMode,
    clear,
    isActive: getIsActive, // Exposta para o tracker usar
  };
})();

window.BlurTool.init();
