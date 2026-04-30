document.addEventListener("DOMContentLoaded", () => {
  const themeSelect = document.getElementById("theme-select");
  const runBtn = document.getElementById("run-btn");
  const codeInput = document.getElementById("code-input");
  const analysisContainer = document.getElementById("analysis-container");
  const outputContainer = document.getElementById("analysis-output");

  const floatingBtn = document.getElementById("floating-chat-btn");
  const closeChatBtn = document.getElementById("close-chat-btn");
  const sidebar = document.getElementById("chat-sidebar");
  const chatInput = document.getElementById("chat-input");
  const sendBtn = document.getElementById("send-btn");
  const chatMessages = document.getElementById("chat-messages");

  const tabOutputBtn = document.getElementById("tab-output-btn");
  const tabDiagramBtn = document.getElementById("tab-diagram-btn");
  const tabRawBtn = document.getElementById("tab-raw-btn");
  const copyBtn = document.getElementById("copy-btn");
  const rawOutput = document.getElementById("raw-output");
  const regenerateAnalysisBtn = document.getElementById(
    "regenerate-analysis-btn",
  );

  const diagramContainer = document.getElementById("diagram-container");
  const generateDiagramBtn = document.getElementById("generate-diagram-btn");
  const regenerateDiagramBtn = document.getElementById(
    "regenerate-diagram-btn",
  );
  const diagramOutput = document.getElementById("diagram-output");

  // Select options
  const actionSelect = document.getElementById("action-select");
  const levelSelect = document.getElementById("level-select");
  const langSelect = document.getElementById("lang-select");
  const agentModeToggle = document.getElementById("agent-mode-toggle");

  let currentAnalysisRaw = "";
  let currentDiagramRaw = "";
  let lastActiveTab = "output";
  let currentB64Img = null;
  let isGenerating = false;
  let renderTimeout = null;

  // Initialize icons
  lucide.createIcons();

  // Debounced markdown render for streaming
  function debouncedRender(container, text, delay = 80) {
    clearTimeout(renderTimeout);
    renderTimeout = setTimeout(() => {
      container.innerHTML = marked.parse(text);
    }, delay);
  }

  // Theme toggle
  themeSelect.addEventListener("change", (e) => {
    document.documentElement.setAttribute("data-theme", e.target.value);
    const hljsLink = document.getElementById("hljs-theme");
    if (e.target.value === "light") {
      hljsLink.href =
        "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-light.min.css";
    } else {
      hljsLink.href =
        "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css";
    }
  });

  // Configure marked.js to use highlight.js
  marked.setOptions({
    highlight: function (code, lang) {
      if (lang && hljs.getLanguage(lang)) {
        return hljs.highlight(code, { language: lang }).value;
      }
      return hljs.highlightAuto(code).value;
    },
  });

  // Tab key support for textarea
  codeInput.addEventListener("keydown", function (e) {
    if (e.key === "Tab") {
      e.preventDefault();
      const start = this.selectionStart;
      const end = this.selectionEnd;
      this.value =
        this.value.substring(0, start) + "    " + this.value.substring(end);
      this.selectionStart = this.selectionEnd = start + 4;
    }
  });

  // Run Analysis
  async function executeAnalysis(actionOverride = null) {
    if (isGenerating) return;
    isGenerating = true;

    const code = codeInput.value;
    const repoUrlInput = document.getElementById("repo-url-input");
    const repoUrl = repoUrlInput ? repoUrlInput.value.trim() : "";
    const currentAction = actionOverride || actionSelect.value;
    const isVisualizing = currentAction === "Visualize Architecture";
    const targetContainer = isVisualizing ? diagramOutput : outputContainer;

    // Auto-switch to correct tab
    if (isVisualizing) {
      switchTab("diagram");
    } else {
      switchTab("output");
    }

    if (!code.trim() && !repoUrl) {
      targetContainer.innerHTML =
        '<div style="color: #ef4444; text-align: center; margin-top: 2rem;">Paste some code or provide a URL first.</div>';
      isGenerating = false;
      return;
    }

    runBtn.disabled = true;
    if (generateDiagramBtn) generateDiagramBtn.disabled = true;
    if (regenerateDiagramBtn) regenerateDiagramBtn.disabled = true;
    if (regenerateAnalysisBtn) regenerateAnalysisBtn.disabled = true;

    const loaderHtml = `
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; width: 100%; margin-top: 2rem;">
                <div class="spinner"></div>
                <div style="color: var(--text-muted); margin-top: 1rem;">${isVisualizing ? "Generating Diagram via AI..." : "Analyzing code architecture..."}</div>
            </div>
        `;

    if (isVisualizing) {
      const placeholder = document.getElementById("diagram-placeholder");
      if (placeholder) placeholder.style.display = "none";
      const regenBtn = document.getElementById("regenerate-diagram-btn");
      const downBtn = document.getElementById("download-img-btn");
      if (regenBtn) regenBtn.style.display = "none";
      if (downBtn) downBtn.style.display = "none";
      diagramOutput.innerHTML = loaderHtml;
    } else {
      if (regenerateAnalysisBtn) regenerateAnalysisBtn.style.display = "none";
      runBtn.innerHTML = '<i data-lucide="loader"></i> Processing...';
      outputContainer.innerHTML = loaderHtml;
    }
    lucide.createIcons();

    try {
      if (isVisualizing) {
        // Diagram: use regular fetch
        const res = await fetch("/api/analyze", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            code: code,
            action: currentAction,
            level: levelSelect.value,
            language: langSelect.value,
            agent_mode: agentModeToggle.checked,
            repo_url: repoUrl,
          }),
        });
        const data = await res.json();
        currentDiagramRaw = data.result;
        diagramOutput.innerHTML = marked.parse(data.result);

        const regenBtn = document.getElementById("regenerate-diagram-btn");
        if (regenBtn) regenBtn.style.display = "inline-flex";

        const match = currentDiagramRaw.match(
          /data:image\/jpeg;base64,([a-zA-Z0-9+/=]+)/,
        );
        if (match) {
          currentB64Img = match[1];
          const downloadBtn = document.getElementById("download-img-btn");
          if (downloadBtn) downloadBtn.style.display = "inline-flex";
        }
        lucide.createIcons();
      } else if (agentModeToggle.checked) {
        // Agent mode: use regular fetch
        const res = await fetch("/api/analyze", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            code: code,
            action: currentAction,
            level: levelSelect.value,
            language: langSelect.value,
            agent_mode: true,
            repo_url: repoUrl,
          }),
        });
        const data = await res.json();
        currentAnalysisRaw = data.result;
        outputContainer.innerHTML = marked.parse(currentAnalysisRaw);
        if (regenerateAnalysisBtn)
          regenerateAnalysisBtn.style.display = "inline-flex";
      } else {
        // Standard analysis: use streaming
        const res = await fetch("/api/analyze/stream", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            code: code,
            action: currentAction,
            level: levelSelect.value,
            language: langSelect.value,
            agent_mode: false,
            repo_url: repoUrl,
          }),
        });

        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let fullText = "";
        outputContainer.innerHTML = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          const text = decoder.decode(value, { stream: true });
          const lines = text.split("\n");
          for (const line of lines) {
            if (line.startsWith("data: ")) {
              try {
                const parsed = JSON.parse(line.slice(6));
                if (parsed.chunk) {
                  fullText += parsed.chunk;
                  debouncedRender(outputContainer, fullText);
                } else if (parsed.error) {
                  outputContainer.innerHTML = `<div style="color: #ef4444;">Error: ${parsed.error}</div>`;
                }
              } catch (e) {}
            }
          }
        }
        currentAnalysisRaw = fullText;
        // Final render (non-debounced) to ensure complete output
        clearTimeout(renderTimeout);
        outputContainer.innerHTML = marked.parse(fullText);
        if (regenerateAnalysisBtn)
          regenerateAnalysisBtn.style.display = "inline-flex";
        lucide.createIcons();
      }
    } catch (err) {
      targetContainer.innerHTML = `<div style="color: #ef4444;">Error: ${err.message}</div>`;
      if (isVisualizing) {
        const placeholder = document.getElementById("diagram-placeholder");
        if (placeholder) placeholder.style.display = "flex";
      }
    }

    isGenerating = false;
    runBtn.disabled = false;
    if (generateDiagramBtn) generateDiagramBtn.disabled = false;
    if (regenerateDiagramBtn) regenerateDiagramBtn.disabled = false;
    if (regenerateAnalysisBtn) regenerateAnalysisBtn.disabled = false;
    runBtn.innerHTML = '<i data-lucide="play"></i> Run Analysis';
    lucide.createIcons();
  }

  runBtn.addEventListener("click", () => {
    if (actionSelect.value === "Visualize Architecture") {
      switchTab("diagram");
    } else {
      switchTab("output");
    }
    executeAnalysis();
  });

  if (generateDiagramBtn)
    generateDiagramBtn.addEventListener("click", () =>
      executeAnalysis("Visualize Architecture"),
    );
  if (regenerateDiagramBtn)
    regenerateDiagramBtn.addEventListener("click", () =>
      executeAnalysis("Visualize Architecture"),
    );
  if (regenerateAnalysisBtn)
    regenerateAnalysisBtn.addEventListener("click", () =>
      executeAnalysis(actionSelect.value),
    );

  // Tab Switching Logic
  function switchTab(tabId) {
    if (tabId === "output") lastActiveTab = "output";
    if (tabId === "diagram") lastActiveTab = "diagram";

    if (analysisContainer)
      analysisContainer.style.display = tabId === "output" ? "flex" : "none";
    if (diagramContainer)
      diagramContainer.style.display = tabId === "diagram" ? "flex" : "none";

    if (tabId === "raw") {
      rawOutput.style.display = "block";
      rawOutput.value =
        lastActiveTab === "diagram" ? currentDiagramRaw : currentAnalysisRaw;
    } else {
      rawOutput.style.display = "none";
    }

    if (tabOutputBtn)
      tabOutputBtn.style.color =
        tabId === "output" ? "var(--hl-color)" : "var(--text-muted)";
    if (tabDiagramBtn)
      tabDiagramBtn.style.color =
        tabId === "diagram" ? "var(--hl-color)" : "var(--text-muted)";
    if (tabRawBtn)
      tabRawBtn.style.color =
        tabId === "raw" ? "var(--hl-color)" : "var(--text-muted)";
  }

  if (tabOutputBtn)
    tabOutputBtn.addEventListener("click", () => switchTab("output"));
  if (tabDiagramBtn)
    tabDiagramBtn.addEventListener("click", () => switchTab("diagram"));
  if (tabRawBtn) tabRawBtn.addEventListener("click", () => switchTab("raw"));

  // Set default tab
  switchTab("output");

  copyBtn.addEventListener("click", () => {
    let textToCopy =
      rawOutput.style.display === "block"
        ? rawOutput.value
        : lastActiveTab === "diagram"
          ? currentDiagramRaw
          : currentAnalysisRaw;
    navigator.clipboard.writeText(textToCopy);
    const originalHtml = copyBtn.innerHTML;
    copyBtn.innerHTML = '<i data-lucide="check"></i> Copied';
    lucide.createIcons();
    setTimeout(() => {
      copyBtn.innerHTML = originalHtml;
      lucide.createIcons();
    }, 2000);
  });

  const downloadImgBtn = document.getElementById("download-img-btn");
  if (downloadImgBtn) {
    downloadImgBtn.addEventListener("click", () => {
      if (currentB64Img) {
        const link = document.createElement("a");
        link.href = `data:image/jpeg;base64,${currentB64Img}`;
        link.download = "architecture_diagram.jpg";
        link.click();
      }
    });
  }

  // Chat Sidebar Toggle
  const sidebarOverlay = document.getElementById("sidebar-overlay");

  function openSidebar() {
    sidebar.classList.add("open");
    sidebarOverlay.classList.add("visible");
  }
  function closeSidebar() {
    sidebar.classList.remove("open");
    sidebarOverlay.classList.remove("visible");
  }

  floatingBtn.addEventListener("click", openSidebar);
  closeChatBtn.addEventListener("click", closeSidebar);
  sidebarOverlay.addEventListener("click", closeSidebar);

  // Chat Send
  async function sendChat() {
    const text = chatInput.value.trim();
    if (!text) return;

    chatInput.value = "";

    const userMsg = document.createElement("div");
    userMsg.className = "msg user";
    userMsg.innerText = text;
    chatMessages.appendChild(userMsg);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    const loadingMsg = document.createElement("div");
    loadingMsg.className = "msg assistant";
    loadingMsg.innerHTML =
      '<span class="loading-dots">Thinking<span>.</span><span>.</span><span>.</span></span>';
    chatMessages.appendChild(loadingMsg);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_input: text,
          context_code: codeInput.value,
        }),
      });
      const data = await res.json();

      // Remove loading indicator
      loadingMsg.remove();

      const botMsg = document.createElement("div");
      botMsg.className = "msg assistant markdown-body";
      botMsg.innerHTML = marked.parse(data.reply);
      chatMessages.appendChild(botMsg);
      chatMessages.scrollTop = chatMessages.scrollHeight;
    } catch (err) {
      loadingMsg.remove();
      const errorMsg = document.createElement("div");
      errorMsg.className = "msg assistant";
      errorMsg.style.color = "#ef4444";
      errorMsg.innerText = `Error: ${err.message}`;
      chatMessages.appendChild(errorMsg);
    }
  }

  sendBtn.addEventListener("click", sendChat);
  chatInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendChat();
  });
});
