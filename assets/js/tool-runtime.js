/* DataConverter Forge tool runtime — wires the common workspace UI to a per-tool
   `transform(inputText, opts) -> outputText` function set on
   `window.AMForgeTool.run`. Kept generic so every tool page only has to
   define its own transform + a couple of DOM ids.

   Files are read with the Streams API (ReadableStream + TextDecoderStream)
   in chunks rather than loaded in one blocking FileReader call, so large
   files don't lock up the tab while reading. Only the first PREVIEW_LINES
   lines are ever shown in the input/output boxes — the full content is
   kept in memory (on `_fullText`) and used for the actual conversion and
   for the downloaded file, so nothing is lost, just not all displayed. */
(function () {
  "use strict";

  const PREVIEW_LINES = 100;

  function showStatus(el, msg, kind) {
    if (!el) return;
    el.textContent = msg;
    el.className = "status-msg show " + kind;
  }

  // Splits text into a preview of the first N lines + metadata about how
  // much was cut off, without ever holding more than one extra copy of it.
  function previewOf(text, n) {
    const lines = text.split("\n");
    if (lines.length <= n) return { preview: text, truncated: false, total: lines.length };
    return { preview: lines.slice(0, n).join("\n"), truncated: true, total: lines.length };
  }

  function withPreviewNote(text, n, forWhat) {
    const p = previewOf(text, n);
    if (!p.truncated) return p.preview;
    return p.preview + "\n\n… " + (p.total - n) + " more lines not shown (showing first " + n + " of " + p.total + "). " + forWhat;
  }

  // Reads a File using the Streams API, decoding chunks as they arrive
  // instead of blocking on one giant FileReader.readAsText call.
  function readFileStreaming(file) {
    return new Promise((resolve, reject) => {
      if (file.stream && window.TextDecoderStream) {
        const reader = file.stream().pipeThrough(new TextDecoderStream()).getReader();
        let text = "";
        (function pump() {
          reader.read().then(({ done, value }) => {
            if (done) { resolve(text); return; }
            text += value;
            pump();
          }).catch(reject);
        })();
      } else {
        // Fallback for browsers without stream support on File objects.
        const fr = new FileReader();
        fr.onload = (e) => resolve(e.target.result);
        fr.onerror = reject;
        fr.readAsText(file);
      }
    });
  }

  function init(config) {
    const { Usage } = window.AMForge;
    const input = document.getElementById(config.inputId || "input");
    const output = document.getElementById(config.outputId || "output");
    const convertBtn = document.getElementById(config.convertBtnId || "convertBtn");
    const downloadBtn = document.getElementById(config.downloadBtnId);
    const status = document.getElementById(config.statusId || "status");
    const counterEl = document.getElementById(config.counterId || "usageCounter");
    const dropzone = document.getElementById(config.dropzoneId || "dropzone");
    const fileInput = document.getElementById(config.fileInputId || "fileInput");

    if (counterEl) Usage.renderCounter(counterEl);

    // If the person edits the visible (possibly-truncated) text by hand,
    // the cached full version from a loaded file is no longer trustworthy.
    if (input) {
      input.addEventListener("input", () => { delete input._fullText; });
    }

    function loadFile(file) {
      if (!file) return;
      if (!Usage.checkFileSize(file.size)) {
        showStatus(status, `File is larger than the ${window.AMForge.Plan.limits.maxFileSizeMB}MB free limit. Upgrade to DataConverter Forge Pro for files up to 1GB.`, "limit");
        return;
      }
      showStatus(status, "Reading file…", "ok");
      readFileStreaming(file).then((text) => {
        input._fullText = text;
        input.value = withPreviewNote(text, PREVIEW_LINES, "The full file will still be used when you convert.");
        status.classList.remove("show");
        if (dropzone) {
          const p = dropzone.querySelector("p");
          if (p) p.innerHTML = `Loaded <span class="fname">${file.name}</span> — click Convert`;
          dropzone.classList.add("drag-over");
          setTimeout(() => dropzone.classList.remove("drag-over"), 500);
        }
      }).catch(() => showStatus(status, "Couldn't read that file.", "err"));
    }

    if (dropzone) {
      dropzone.addEventListener("click", () => fileInput && fileInput.click());
      dropzone.addEventListener("dragover", (e) => { e.preventDefault(); dropzone.classList.add("drag-over"); });
      dropzone.addEventListener("dragleave", () => dropzone.classList.remove("drag-over"));
      dropzone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropzone.classList.remove("drag-over");
        loadFile(e.dataTransfer.files[0]);
      });
    }
    if (fileInput) fileInput.addEventListener("change", (e) => loadFile(e.target.files[0]));

    if (convertBtn) {
      convertBtn.addEventListener("click", () => {
        if (!Usage.canRun()) {
          showStatus(status, "You have reached today's free limit. More powerful features will be available in DataConverter Forge Pro.", "limit");
          return;
        }
        try {
          const rawInput = input._fullText !== undefined ? input._fullText : input.value;
          const result = window.AMForgeTool.run(rawInput);
          if (output.tagName === "TEXTAREA" || output.tagName === "INPUT") {
            output._fullText = result;
            output.value = withPreviewNote(result, PREVIEW_LINES, "Download to get the complete result.");
          } else {
            delete output._fullText;
            output.innerHTML = result;
          }
          Usage.record();
          if (counterEl) Usage.renderCounter(counterEl);
          showStatus(status, "Done. Your result is ready below.", "ok");
          convertBtn.classList.add("striking");
          setTimeout(() => convertBtn.classList.remove("striking"), 450);
          if (downloadBtn) downloadBtn.disabled = false;
        } catch (err) {
          showStatus(status, "Error: " + err.message, "err");
        }
      });
    }

    if (downloadBtn) {
      downloadBtn.addEventListener("click", () => {
        const text = output._fullText !== undefined
          ? output._fullText
          : (output.tagName === "TEXTAREA" ? output.value : output.textContent);
        const blob = new Blob([text], { type: config.mime || "text/plain" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = config.filename || "amforge-output.txt";
        a.click();
        URL.revokeObjectURL(url);
      });
    }
  }

  window.AMForgeRuntime = { init, readFileStreaming, previewOf, withPreviewNote, PREVIEW_LINES };
})();
