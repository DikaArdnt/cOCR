/*
 * cOCR Workbench
 *
 * Copyright (C) 2026 Dika Ardianta
 * Copyright (C) 2026 Hisoka Labs
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License
 * as published by the Free Software Foundation, either version 3
 * of the License, or (at your option) any later version.
 *
 * See LICENSE for details.
 */

document.addEventListener("DOMContentLoaded", () => {
  // Translation helper shortcut
  function t(key, params) {
    if (window.cocrI18n && typeof window.cocrI18n.t === "function") {
      return window.cocrI18n.t(key, params);
    }
    return key;
  }

  // Theme management (light / dark)
  const themeToggleBtn = document.getElementById("btn-theme-toggle");
  const themeColorMeta = document.querySelector('meta[name="theme-color"]');

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("cocr_theme", theme);
    if (themeColorMeta) {
      themeColorMeta.setAttribute("content", theme === "light" ? "#f6f8fa" : "#0d1117");
    }
  }

  const savedTheme = localStorage.getItem("cocr_theme") || "dark";
  applyTheme(savedTheme);

  if (themeToggleBtn) {
    themeToggleBtn.addEventListener("click", () => {
      const currentTheme = document.documentElement.getAttribute("data-theme") || "dark";
      const nextTheme = currentTheme === "dark" ? "light" : "dark";
      applyTheme(nextTheme);
    });
  }

  // Session authentication and HTML escaping
  function escapeHtml(str) {
    if (str === null || str === undefined) return "";
    return String(str).replace(/[&<>'"]/g, (c) => {
      const map = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        "'": "&#39;",
        "\"": "&quot;",
      };
      return map[c] || c;
    });
  }

  function getSessionId() {
    let sid = sessionStorage.getItem("cocr_session_id");
    if (!sid) {
      if (typeof crypto !== "undefined" && crypto.randomUUID) {
        sid = crypto.randomUUID();
      } else {
        sid = "sess_" + Math.random().toString(36).substring(2) + Date.now().toString(36);
      }
      sessionStorage.setItem("cocr_session_id", sid);
    }
    return sid;
  }

  function getAuthHeaders(headers = {}) {
    const sid = getSessionId();
    const h = { ...headers, "X-Session-ID": sid };
    const apiKey = sessionStorage.getItem("cocr_api_key") || "";
    if (apiKey) {
      h["X-API-Key"] = apiKey;
    }
    return h;
  }

  async function authFetch(url, options = {}) {
    const opts = { ...options };
    opts.headers = getAuthHeaders(opts.headers || {});
    const res = await fetch(url, opts);
    if (res.status === 401) {
      const enteredKey = prompt(t("apiKeyPrompt"));
      if (enteredKey && enteredKey.trim()) {
        sessionStorage.setItem("cocr_api_key", enteredKey.trim());
        opts.headers = getAuthHeaders(options.headers || {});
        return fetch(url, opts);
      }
    }
    return res;
  }

  // DOM element references
  const btnSourceFolder = document.getElementById("btn-source-folder");
  const btnSourceUpload = document.getElementById("btn-source-upload");
  const panelSourceFolder = document.getElementById("panel-source-folder");
  const panelSourceUpload = document.getElementById("panel-source-upload");

  const folderInput = document.getElementById("folder-path-input");
  const folderMeta = document.getElementById("folder-scan-meta");
  const outputDirInput = document.getElementById("output-dir-input");
  const btnBrowseFolder = document.getElementById("btn-browse-folder");

  const dropzone = document.getElementById("dropzone");
  const fileUploadInput = document.getElementById("file-upload-input");
  const uploadStatus = document.getElementById("upload-status");

  const layoutModeSelect = document.getElementById("layout-mode-select");
  const deviceSelect = document.getElementById("device-select");
  const optGpu = document.getElementById("opt-gpu");
  const fmtMd = document.getElementById("fmt-md");
  const fmtDocx = document.getElementById("fmt-docx");
  const fmtPdf = document.getElementById("fmt-pdf");
  const btnStart = document.getElementById("btn-start-process");
  const deviceLabel = document.getElementById("device-label");

  const taskBadge = document.getElementById("task-badge");
  const errorBanner = document.getElementById("error-banner");
  const errorDesc = document.getElementById("error-desc");
  const btnCloseError = document.getElementById("btn-close-error");
  const progressSection = document.getElementById("progress-section");
  const progressMessage = document.getElementById("progress-message");
  const progressCounter = document.getElementById("progress-counter");
  const progressBarFill = document.getElementById("progress-bar-fill");
  const timerLabel = document.getElementById("timer-label");

  const statsGrid = document.getElementById("stats-grid");
  const statTotal = document.getElementById("stat-total");
  const statUnique = document.getElementById("stat-unique");
  const statDuplicates = document.getElementById("stat-duplicates");
  const statDuration = document.getElementById("stat-duration");
  const downloadBar = document.getElementById("download-bar");
  const btnDownloadMd = document.getElementById("btn-download-md");
  const btnDownloadDocx = document.getElementById("btn-download-docx");
  const btnDownloadPdf = document.getElementById("btn-download-pdf");

  const tabsContainer = document.getElementById("tabs-container");
  const emptyState = document.getElementById("empty-state");
  const cardsPreviewList = document.getElementById("cards-preview-list");
  const markdownRawText = document.getElementById("markdown-raw-text");
  const filesTableBody = document.getElementById("files-table-body");
  const btnCopyMarkdown = document.getElementById("btn-copy-markdown");

  const tabBtnPreview = document.getElementById("tab-btn-preview");
  const tabBtnMarkdown = document.getElementById("tab-btn-markdown");
  const tabBtnFiles = document.getElementById("tab-btn-files");
  const tabContentPreview = document.getElementById("tab-content-preview");
  const tabContentMarkdown = document.getElementById("tab-content-markdown");
  const tabContentFiles = document.getElementById("tab-content-files");

  // Execution state
  let activeSourceMode = "folder";
  let currentActiveFolder = "";
  let pollInterval = null;
  let activeMarkdownText = "";
  let lastSystemInfo = null;
  let lastCompletedState = null;

  // Query hardware capabilities and server mode
  async function initSystem() {
    try {
      const res = await authFetch("/api/system-info");
      const info = await res.json();
      lastSystemInfo = info;
      updateSystemInfoUI();
    } catch (err) {
      deviceLabel.textContent = t("systemOffline");
    }
  }

  function updateSystemInfoUI() {
    if (!lastSystemInfo) return;
    const info = lastSystemInfo;

    if (info.cloud_mode) {
      switchSourceMode("upload");
      if (btnSourceFolder) btnSourceFolder.style.display = "none";
      const lbl = document.getElementById("label-source-mode");
      if (lbl) lbl.textContent = t("imageSourceCloudLabel");
      if (folderMeta) folderMeta.textContent = t("metaCloudIsolated");
    }

    if (info.gpu_available) {
      deviceLabel.textContent = t("accelDevice", { device: info.device_description });
      optGpu.disabled = false;
      optGpu.textContent = `GPU: ${info.device_description}`;
    } else {
      deviceLabel.textContent = t("computeCpu");
      optGpu.disabled = true;
      optGpu.textContent = t("gpuNotFound");
    }
  }

  // Input source tab switching
  function switchSourceMode(mode) {
    activeSourceMode = mode;
    if (mode === "folder") {
      btnSourceFolder.classList.add("active");
      btnSourceFolder.setAttribute("aria-selected", "true");
      btnSourceUpload.classList.remove("active");
      btnSourceUpload.setAttribute("aria-selected", "false");

      panelSourceFolder.classList.add("active");
      panelSourceUpload.classList.remove("active");

      if (folderInput.value.trim()) {
        currentActiveFolder = folderInput.value.trim();
        scanFolderInput();
      }
    } else {
      btnSourceUpload.classList.add("active");
      btnSourceUpload.setAttribute("aria-selected", "true");
      btnSourceFolder.classList.remove("active");
      btnSourceFolder.setAttribute("aria-selected", "false");

      panelSourceUpload.classList.add("active");
      panelSourceFolder.classList.remove("active");
    }
  }

  btnSourceFolder.addEventListener("click", () => switchSourceMode("folder"));
  btnSourceUpload.addEventListener("click", () => switchSourceMode("upload"));

  // Drag-and-drop and file upload handlers
  dropzone.addEventListener("click", () => fileUploadInput.click());
  dropzone.addEventListener("keydown", (e) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      fileUploadInput.click();
    }
  });

  ["dragenter", "dragover"].forEach((evt) => {
    dropzone.addEventListener(evt, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.add("dragover");
    });
  });

  ["dragleave", "dragend", "drop"].forEach((evt) => {
    dropzone.addEventListener(evt, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.remove("dragover");
    });
  });

  dropzone.addEventListener("drop", (e) => {
    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      handleFilesUpload(files);
    }
  });

  fileUploadInput.addEventListener("change", (e) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFilesUpload(files);
    }
  });

  async function handleFilesUpload(files) {
    if (!files || files.length === 0) return;
    const isSingle = files.length === 1;
    uploadStatus.textContent = isSingle
      ? t("uploadStatusSingle", { name: files[0].name })
      : t("uploadStatusMultiple", { count: files.length });

    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append("files", files[i]);
    }

    try {
      const res = await authFetch("/api/upload-files", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        let errDetail = t("uploadFailed");
        try {
          const errData = await res.json();
          errDetail = errData.detail || errDetail;
        } catch (_) {}
        throw new Error(errDetail);
      }

      const data = await res.json();
      currentActiveFolder = data.folder_path;
      folderInput.value = data.folder_path;

      const fileNames = data.files || [];
      if (data.files_count === 1) {
        uploadStatus.textContent = t("uploadSuccessSingle", { name: fileNames[0] });
        folderMeta.textContent = t("metaUploadSingle", { name: fileNames[0] });
      } else {
        uploadStatus.textContent = t("uploadSuccessMultiple", { count: data.files_count });
        folderMeta.textContent = t("metaUploadMultiple", { count: data.files_count });
      }
      hideError();
    } catch (err) {
      uploadStatus.textContent = "";
      showError(t("uploadError", { error: err.message }));
    }
  }

  let isBrowsingFolder = false;

  async function browseFolder() {
    if (isBrowsingFolder) return;
    isBrowsingFolder = true;
    if (btnBrowseFolder) {
      btnBrowseFolder.disabled = true;
    }
    const previousMeta = folderMeta.textContent;
    folderMeta.textContent = t("metaBrowsingFolder");
    try {
      const res = await authFetch("/api/browse-folder", { method: "POST" });
      const data = await res.json();
      if (!data.cancelled && data.folder_path) {
        folderInput.value = data.folder_path;
        currentActiveFolder = data.folder_path;
        folderMeta.textContent = t("metaDetectedFiles", { count: data.files_count });
        if (data.files_count === 0) {
          showError(t("metaNoImagesFound"));
        } else {
          hideError();
        }
      } else {
        folderMeta.textContent = currentActiveFolder
          ? previousMeta
          : t("metaFolderCancelled");
      }
    } catch (err) {
      showError(t("uploadError", { error: err.message }));
      folderMeta.textContent = t("metaFolderFailed");
    } finally {
      isBrowsingFolder = false;
      if (btnBrowseFolder) {
        btnBrowseFolder.disabled = false;
      }
    }
  }

  async function scanFolderInput() {
    let val = folderInput.value.trim();
    val = val.replace(/^["']|["']$/g, "").trim();
    if (!val) {
      folderMeta.textContent = t("metaFolderNotSpecified");
      return;
    }
    try {
      const res = await authFetch("/api/scan-folder", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ folder_path: val }),
      });
      if (!res.ok) {
        const err = await res.json();
        folderMeta.textContent = err.detail || t("metaFolderInvalid");
        return;
      }
      const data = await res.json();
      currentActiveFolder = data.folder_path;
      folderMeta.textContent = t("metaFolderReady", { count: data.files_count });
      hideError();
    } catch (err) {
      folderMeta.textContent = t("metaFolderVerifyFailed");
    }
  }

  // Error alert helper
  function showError(msg) {
    errorDesc.textContent = msg;
    errorBanner.style.display = "flex";
  }

  function hideError() {
    errorBanner.style.display = "none";
  }

  btnCloseError.addEventListener("click", hideError);

  function resetStartButton() {
    btnStart.disabled = false;
    btnStart.innerHTML = `
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true">
        <polygon points="5 3 19 12 5 21 5 3"/>
      </svg>
      <span id="btn-start-label">${escapeHtml(t("btnStartExtraction"))}</span>
    `;
  }

  // Start OCR processing job
  async function startOCR() {
    let targetFolder = "";
    if (activeSourceMode === "folder") {
      targetFolder = folderInput.value.trim();
    } else {
      targetFolder = currentActiveFolder || folderInput.value.trim();
    }

    targetFolder = targetFolder.replace(/^["']|["']$/g, "").trim();

    if (!targetFolder) {
      showError(t("specifyFolderError"));
      if (activeSourceMode === "folder") folderInput.focus();
      return;
    }

    const formats = [];
    if (fmtMd.checked) formats.push("md");
    if (fmtDocx.checked) formats.push("docx");
    if (fmtPdf.checked) formats.push("pdf");

    if (formats.length === 0) {
      showError(t("selectFormatError"));
      return;
    }

    hideError();
    btnStart.disabled = true;
    btnStart.innerHTML = `
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spin" aria-hidden="true">
        <circle cx="12" cy="12" r="10" stroke-opacity="0.25"/>
        <path d="M12 2a10 10 0 0 1 10 10"/>
      </svg>
      <span>${escapeHtml(t("btnProcessing"))}</span>
    `;

    // Progress panel and status updates
    progressSection.style.display = "flex";
    statsGrid.style.display = "none";
    downloadBar.style.display = "none";
    tabsContainer.style.display = "none";
    emptyState.style.display = "none";

    taskBadge.className = "status-indicator-pill status-running";
    taskBadge.textContent = t("statusProcessing");

    const payload = {
      folder_path: targetFolder,
      output_dir: outputDirInput.value.trim() || null,
      mode: layoutModeSelect.value,
      device: deviceSelect.value,
      formats: formats,
    };

    try {
      const res = await authFetch("/api/start-ocr", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || t("startOcrError"));
      }

      if (pollInterval) clearInterval(pollInterval);
      pollInterval = setInterval(pollTaskStatus, 500);
    } catch (err) {
      showError(err.message);
      taskBadge.className = "status-indicator-pill status-error";
      taskBadge.textContent = t("statusError");
      resetStartButton();
      progressSection.style.display = "none";
      emptyState.style.display = "flex";
    }
  }

  async function pollTaskStatus() {
    try {
      const res = await authFetch("/api/task-status");
      const state = await res.json();

      progressMessage.textContent = state.message || t("progressProcessing");
      timerLabel.textContent = `${state.elapsed_seconds || 0.0}s`;

      const cur = state.current_step || 0;
      const tot = state.total_steps || 1;
      progressCounter.textContent = `${cur} / ${tot}`;

      const pct = Math.min(100, Math.max(0, Math.round((cur / Math.max(tot, 1)) * 100)));
      progressBarFill.style.width = `${pct}%`;
      progressBarFill.parentElement.setAttribute("aria-valuenow", pct);

      if (state.status === "completed") {
        clearInterval(pollInterval);
        handleCompletedState(state);
      } else if (state.status === "error") {
        clearInterval(pollInterval);
        handleErrorState(state.error || t("processFailedInternal"));
      }
    } catch (err) {
      // Suppress transient network polling errors
    }
  }

  function handleCompletedState(state) {
    lastCompletedState = state;
    resetStartButton();

    taskBadge.className = "status-indicator-pill status-done";
    taskBadge.textContent = t("statusCompleted");

    progressSection.style.display = "none";
    statsGrid.style.display = "grid";
    downloadBar.style.display = "flex";
    tabsContainer.style.display = "flex";

    const data = state.data || {};
    statTotal.textContent = data.total_files || 0;
    statUnique.textContent = data.unique_files || 0;
    statDuplicates.textContent = data.duplicate_files || 0;
    statDuration.textContent = `${state.elapsed_seconds || 0.0}s`;

    // Bind document download links
    const sid = getSessionId();
    const apiKey = sessionStorage.getItem("cocr_api_key") || "";
    const authParams = `?session_id=${encodeURIComponent(sid)}${apiKey ? `&api_key=${encodeURIComponent(apiKey)}` : ""}`;

    const files = state.exported_files || {};
    btnDownloadMd.style.display = files.md ? "inline-flex" : "none";
    if (files.md) btnDownloadMd.href = `/api/download/md${authParams}`;

    btnDownloadDocx.style.display = files.docx ? "inline-flex" : "none";
    if (files.docx) btnDownloadDocx.href = `/api/download/docx${authParams}`;

    btnDownloadPdf.style.display = files.pdf ? "inline-flex" : "none";
    if (files.pdf) btnDownloadPdf.href = `/api/download/pdf${authParams}`;

    renderCardsDeck(data.results || []);
    generateMarkdownPreview(data);
    renderFilesTable(data.results || [], data.duplicates || []);
  }

  function handleErrorState(errMsg) {
    resetStartButton();

    taskBadge.className = "status-indicator-pill status-error";
    taskBadge.textContent = t("statusError");

    progressSection.style.display = "none";
    showError(errMsg);
  }

  // Render extracted content cards
  function renderCardsDeck(results) {
    cardsPreviewList.innerHTML = "";
    if (results.length === 0) {
      cardsPreviewList.innerHTML = `<p class='field-helper'>${escapeHtml(t("noItemsExtracted"))}</p>`;
      return;
    }

    let itemNumber = 1;
    results.forEach((res) => {
      const items = res.items || [];
      let currentSection = null;

      items.forEach((it) => {
        if (it.section && it.section !== currentSection) {
          currentSection = it.section;
          const secHeader = document.createElement("div");
          secHeader.className = "question-prompt";
          secHeader.style.cssText = "font-weight: 700; color: var(--accent); border-left: 3px solid var(--accent); margin-top: 1rem;";
          secHeader.textContent = `${t("sectionHeader", { section: it.section })}${it.instruction ? ` ${t("instructionText", { instruction: it.instruction })}` : ""}`;
          cardsPreviewList.appendChild(secHeader);
        }

        const card = document.createElement("article");
        card.className = "question-card";

        const numText = it.number
          ? t("itemNumberLabel", { item: itemNumber, number: escapeHtml(it.number) })
          : t("itemLabel", { item: itemNumber });

        const header = document.createElement("div");
        header.className = "question-card-header";
        header.innerHTML = `
          <span class="badge-question-num">${numText}</span>
          <span class="badge-source-meta">${escapeHtml(t("pageLabel", { page: it.page_number }))} (${escapeHtml(res.filename)})</span>
        `;

        const prompt = document.createElement("div");
        prompt.className = "question-prompt";
        prompt.textContent = it.question || t("textNotDetected");

        card.appendChild(header);
        card.appendChild(prompt);

        if (it.options && it.options.length > 0) {
          const ul = document.createElement("ul");
          ul.className = "options-deck";
          it.options.forEach((opt) => {
            const li = document.createElement("li");
            li.className = "option-row";
            li.textContent = opt;
            ul.appendChild(li);
          });
          card.appendChild(ul);
        }

        cardsPreviewList.appendChild(card);
        itemNumber++;
      });
    });
  }

  function generateMarkdownPreview(data) {
    const lines = [];
    const localeCode = (window.cocrI18n && window.cocrI18n.getCurrentLanguage() === "id") ? "id-ID" : "en-US";
    const dateStr = new Date().toLocaleString(localeCode);

    lines.push(t("mdHeaderTitle"));
    lines.push(t("mdExtractionTime", { time: dateStr }));
    lines.push(t("mdTotalFilesSummary", {
      total: data.total_files || 0,
      unique: data.unique_files || 0,
      duplicates: data.duplicate_files || 0,
    }));
    lines.push(t("mdOcrDevice", { device: data.device_used || "CPU" }));
    lines.push("---\n");

    let count = 1;
    (data.results || []).forEach((res) => {
      lines.push(t("mdFileHeader", { filename: res.filename }));
      let currentSection = null;

      (res.items || []).forEach((it) => {
        if (it.section && it.section !== currentSection) {
          currentSection = it.section;
          lines.push(t("mdSectionHeader", { section: it.section }));
          if (it.instruction) lines.push(`*${it.instruction}*`);
          lines.push("");
        }

        const numLabel = it.number
          ? (window.cocrI18n && window.cocrI18n.getCurrentLanguage() === "id"
            ? `Butir ${count} [Asli: No. ${it.number}]`
            : `Item ${count} [Original: No. ${it.number}]`)
          : (window.cocrI18n && window.cocrI18n.getCurrentLanguage() === "id"
            ? `Butir ${count}`
            : `Item ${count}`);

        lines.push(t("mdItemHeading", { label: numLabel, page: it.page_number }));

        if (it.question) {
          if (it.options && it.options.length > 0) {
            lines.push(t("mdItemPromptQuestion", { text: it.question }));
          } else {
            lines.push(t("mdItemPromptContent", { text: it.question }));
          }
        }
        if (it.options && it.options.length > 0) {
          lines.push(t("mdOptionsHeader"));
          it.options.forEach((o) => lines.push(`- ${o}`));
          lines.push("");
        }
        lines.push("---\n");
        count++;
      });
    });

    activeMarkdownText = lines.join("\n");
    markdownRawText.querySelector("code").textContent = activeMarkdownText;
  }

  function renderFilesTable(results, duplicates) {
    filesTableBody.innerHTML = "";

    results.forEach((r) => {
      const pageStr = r.page > 0 ? t("pageLabel", { page: escapeHtml(r.page) }) : t("pageNA");
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><strong>${escapeHtml(r.filename)}</strong></td>
        <td>${pageStr}</td>
        <td>${escapeHtml(r.width)} x ${escapeHtml(r.height)} px</td>
        <td><span style="color: var(--success); font-weight: 600;">${escapeHtml(t("statusSuccess"))}</span></td>
      `;
      filesTableBody.appendChild(tr);
    });

    duplicates.forEach((d) => {
      const pageStr = d.page > 0 ? t("pageLabel", { page: escapeHtml(d.page) }) : t("pageNA");
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td style="color: var(--text-muted);">${escapeHtml(d.filename)}</td>
        <td>${pageStr}</td>
        <td>-</td>
        <td><span style="color: var(--warning); font-weight: 600;">${escapeHtml(t("statusSkipped", { reason: d.reason }))}</span></td>
      `;
      filesTableBody.appendChild(tr);
    });
  }

  // Result tab navigation with keyboard support
  const resultTabs = [
    { btn: tabBtnPreview, panel: tabContentPreview },
    { btn: tabBtnMarkdown, panel: tabContentMarkdown },
    { btn: tabBtnFiles, panel: tabContentFiles },
  ];

  function switchResultTab(targetIndex) {
    resultTabs.forEach((item, idx) => {
      const isSelected = idx === targetIndex;
      item.btn.classList.toggle("active", isSelected);
      item.btn.setAttribute("aria-selected", isSelected ? "true" : "false");
      item.btn.setAttribute("tabindex", isSelected ? "0" : "-1");
      item.panel.classList.toggle("active", isSelected);
      if (isSelected) {
        item.btn.focus();
      }
    });
  }

  resultTabs.forEach((item, idx) => {
    item.btn.addEventListener("click", () => switchResultTab(idx));
    item.btn.addEventListener("keydown", (e) => {
      if (e.key === "ArrowRight") {
        e.preventDefault();
        const next = (idx + 1) % resultTabs.length;
        switchResultTab(next);
      } else if (e.key === "ArrowLeft") {
        e.preventDefault();
        const prev = (idx - 1 + resultTabs.length) % resultTabs.length;
        switchResultTab(prev);
      }
    });
  });

  // Copy Markdown to clipboard
  btnCopyMarkdown.addEventListener("click", () => {
    if (!activeMarkdownText) return;
    navigator.clipboard.writeText(activeMarkdownText).then(() => {
      const labelSpan = document.getElementById("btn-copy-markdown-text");
      if (labelSpan) {
        labelSpan.textContent = t("copiedToClipboard");
        setTimeout(() => {
          labelSpan.textContent = t("copyMarkdownBtn");
        }, 1600);
      }
    });
  });

  // Re-render dynamic content on locale change
  window.addEventListener("cocr:languageChange", () => {
    updateSystemInfoUI();

    // Update task status label
    if (taskBadge.classList.contains("status-idle")) {
      taskBadge.textContent = t("statusIdle");
    } else if (taskBadge.classList.contains("status-running")) {
      taskBadge.textContent = t("statusProcessing");
    } else if (taskBadge.classList.contains("status-done")) {
      taskBadge.textContent = t("statusCompleted");
    } else if (taskBadge.classList.contains("status-error")) {
      taskBadge.textContent = t("statusError");
    }

    // Re-render cards and summary table if extraction is complete
    if (lastCompletedState && lastCompletedState.data) {
      const data = lastCompletedState.data;
      renderCardsDeck(data.results || []);
      generateMarkdownPreview(data);
      renderFilesTable(data.results || [], data.duplicates || []);
    }
  });

  // Input event listeners
  if (btnBrowseFolder) btnBrowseFolder.addEventListener("click", browseFolder);
  folderInput.addEventListener("change", scanFolderInput);
  btnStart.addEventListener("click", startOCR);

  // Initialization
  initSystem();
});
