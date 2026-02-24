document.addEventListener("DOMContentLoaded", () => {
    const tabs = document.querySelectorAll(".tab");
    const panels = document.querySelectorAll(".panel");
    const urlInput = document.getElementById("url-input");
    const btnScrape = document.getElementById("btn-scrape");
    const fileInput = document.getElementById("file-input");
    const dropZone = document.getElementById("drop-zone");
    const fileName = document.getElementById("file-name");
    const btnConvert = document.getElementById("btn-convert");
    const loading = document.getElementById("loading");
    const error = document.getElementById("error");
    const errorMessage = document.getElementById("error-message");
    const result = document.getElementById("result");
    const resultTitle = document.getElementById("result-title");
    const previewContent = document.getElementById("preview-content");
    const btnDownload = document.getElementById("btn-download");
    const btnCopy = document.getElementById("btn-copy");
    const btnClear = document.getElementById("btn-clear");

    let currentMarkdown = "";
    let currentFilename = "output.md";

    // Tab switching
    tabs.forEach(tab => {
        tab.addEventListener("click", () => {
            tabs.forEach(t => t.classList.remove("active"));
            panels.forEach(p => p.classList.remove("active"));
            tab.classList.add("active");
            document.getElementById(`panel-${tab.dataset.tab}`).classList.add("active");
            hideError();
        });
    });

    // URL scraping
    btnScrape.addEventListener("click", () => scrapeUrl());
    urlInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") scrapeUrl();
    });

    async function scrapeUrl() {
        const url = urlInput.value.trim();
        if (!url) return;

        showLoading();
        hideError();
        hideResult();

        try {
            const res = await fetch("/api/scrape", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url }),
            });
            const data = await res.json();

            if (!res.ok) {
                showError(data.error || "Scraping failed");
                return;
            }

            currentMarkdown = data.markdown;
            currentFilename = sanitizeFilename(data.title || url) + ".md";
            showResult(data.title || url, data.markdown);
        } catch (err) {
            showError("Network error. Please try again.");
        } finally {
            hideLoading();
        }
    }

    // File upload - drag & drop
    dropZone.addEventListener("click", (e) => {
        // Don't double-trigger when clicking the Browse Files label
        if (e.target.closest('label[for="file-input"]')) return;
        fileInput.click();
    });

    dropZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropZone.classList.add("dragover");
    });

    dropZone.addEventListener("dragleave", () => {
        dropZone.classList.remove("dragover");
    });

    dropZone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropZone.classList.remove("dragover");
        if (e.dataTransfer.files.length > 0) {
            fileInput.files = e.dataTransfer.files;
            onFileSelected();
        }
    });

    fileInput.addEventListener("change", onFileSelected);

    function onFileSelected() {
        if (fileInput.files.length > 0) {
            fileName.textContent = fileInput.files[0].name;
            btnConvert.disabled = false;
        }
    }

    // File conversion
    btnConvert.addEventListener("click", () => convertFile());

    async function convertFile() {
        if (!fileInput.files.length) return;

        showLoading();
        hideError();
        hideResult();

        const formData = new FormData();
        formData.append("file", fileInput.files[0]);

        try {
            const res = await fetch("/api/convert", {
                method: "POST",
                body: formData,
            });
            const data = await res.json();

            if (!res.ok) {
                showError(data.error || "Conversion failed");
                return;
            }

            currentMarkdown = data.markdown;
            currentFilename = data.filename || "output.md";
            showResult(data.title || fileInput.files[0].name, data.markdown);
        } catch (err) {
            showError("Network error. Please try again.");
        } finally {
            hideLoading();
        }
    }

    // Download
    btnDownload.addEventListener("click", () => {
        const blob = new Blob([currentMarkdown], { type: "text/markdown;charset=utf-8" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = currentFilename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });

    // Copy
    btnCopy.addEventListener("click", async () => {
        try {
            await navigator.clipboard.writeText(currentMarkdown);
            const originalText = btnCopy.textContent;
            btnCopy.textContent = "Copied!";
            setTimeout(() => { btnCopy.textContent = originalText; }, 1500);
        } catch {
            // Fallback for older browsers
            const textarea = document.createElement("textarea");
            textarea.value = currentMarkdown;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand("copy");
            document.body.removeChild(textarea);
            btnCopy.textContent = "Copied!";
            setTimeout(() => { btnCopy.textContent = "Copy"; }, 1500);
        }
    });

    // Clear
    btnClear.addEventListener("click", () => {
        hideResult();
        currentMarkdown = "";
        currentFilename = "output.md";
    });

    // Helpers
    function showLoading() { loading.hidden = false; }
    function hideLoading() { loading.hidden = true; }

    function showError(msg) {
        errorMessage.textContent = msg;
        error.hidden = false;
    }
    function hideError() { error.hidden = true; }

    function showResult(title, markdown) {
        resultTitle.textContent = title;
        previewContent.textContent = markdown;
        result.hidden = false;
    }
    function hideResult() { result.hidden = true; }

    function sanitizeFilename(name) {
        return name
            .replace(/[<>:"/\\|?*]/g, "")
            .replace(/\s+/g, "_")
            .substring(0, 100);
    }
});
