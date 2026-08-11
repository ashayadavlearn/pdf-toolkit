/**
 * PDF Toolkit - Frontend JavaScript Logic
 */

document.addEventListener('DOMContentLoaded', function () {
    initDragAndDrop();
    initPdfInfoFetcher();
    initMultiFileUploader();
    initFormSubmissions();
    initCopyToClipboard();
});

/**
 * Format bytes to readable string (KB / MB)
 */
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

/**
 * Drag and Drop File Zone Handler
 */
function initDragAndDrop() {
    const dropzones = document.querySelectorAll('.dropzone');

    dropzones.forEach(dropzone => {
        const fileInput = dropzone.querySelector('input[type="file"]');
        if (!fileInput) return;

        dropzone.addEventListener('click', (e) => {
            if (e.target !== fileInput) {
                fileInput.click();
            }
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.remove('dragover');
            }, false);
        });

        dropzone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files && files.length > 0) {
                fileInput.files = files;
                // Dispatch change event manually
                const event = new Event('change', { bubbles: true });
                fileInput.dispatchEvent(event);
            }
        });
    });
}

/**
 * Single File PDF Info & Preview Fetcher
 */
function initPdfInfoFetcher() {
    const singleFileInputs = document.querySelectorAll('.single-pdf-input');

    singleFileInputs.forEach(input => {
        input.addEventListener('change', function () {
            const file = this.files[0];
            const infoContainer = document.getElementById('pdf-info-container');
            const previewFilename = document.getElementById('preview-filename');
            const previewFilesize = document.getElementById('preview-filesize');
            const previewPagecount = document.getElementById('preview-pagecount');

            if (!file) return;

            if (!file.name.toLowerCase().endswith?.('.pdf') && !file.name.toLowerCase().endsWith('.pdf')) {
                alert('Please select a valid .pdf file.');
                this.value = '';
                if (infoContainer) infoContainer.style.display = 'none';
                return;
            }

            if (previewFilename) previewFilename.textContent = file.name;
            if (previewFilesize) previewFilesize.textContent = formatBytes(file.size);

            if (infoContainer) infoContainer.style.display = 'block';

            // Send metadata request to backend API
            const formData = new FormData();
            formData.append('file', file);

            fetch('/api/pdf-info', {
                method: 'POST',
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if (data.success && previewPagecount) {
                    previewPagecount.textContent = data.info.page_count + ' Pages';
                    
                    // Populate page inputs if present
                    const maxPageHelp = document.querySelectorAll('.max-page-help');
                    maxPageHelp.forEach(el => el.textContent = `Total pages: ${data.info.page_count}`);
                }
            })
            .catch(err => console.log('Could not fetch PDF info', err));
        });
    });
}

/**
 * Multi-file Uploader with List Reordering & Removal (Merge Tool)
 */
let multiFilesArray = [];

function initMultiFileUploader() {
    const multiInput = document.getElementById('multi-pdf-input');
    const fileListContainer = document.getElementById('multi-file-list');
    const mergeSubmitBtn = document.getElementById('merge-submit-btn');

    if (!multiInput || !fileListContainer) return;

    multiInput.addEventListener('change', function () {
        const newFiles = Array.from(this.files);
        
        newFiles.forEach(file => {
            if (file.name.toLowerCase().endsWith('.pdf')) {
                multiFilesArray.push(file);
            }
        });

        renderMultiFileList();
    });
}

function renderMultiFileList() {
    const fileListContainer = document.getElementById('multi-file-list');
    const mergeSubmitBtn = document.getElementById('merge-submit-btn');
    const multiInput = document.getElementById('multi-pdf-input');
    
    if (!fileListContainer) return;
    fileListContainer.innerHTML = '';

    if (multiFilesArray.length === 0) {
        fileListContainer.innerHTML = '<div class="text-center text-muted py-3">No PDF files selected yet.</div>';
        if (mergeSubmitBtn) mergeSubmitBtn.disabled = true;
        return;
    }

    if (mergeSubmitBtn) mergeSubmitBtn.disabled = multiFilesArray.length < 2;

    // Sync files array back to DataTransfer object for form submission
    const dataTransfer = new DataTransfer();

    multiFilesArray.forEach((file, index) => {
        dataTransfer.items.add(file);

        const item = document.createElement('div');
        item.className = 'file-item-badge';
        item.innerHTML = `
            <div class="d-flex align-items-center">
                <span class="badge bg-indigo-light text-primary me-2">${index + 1}</span>
                <span class="file-item-name">${file.name}</span>
            </div>
            <div class="d-flex align-items-center gap-2">
                <span class="file-item-size">${formatBytes(file.size)}</span>
                <button type="button" class="btn btn-sm btn-outline-secondary" onclick="moveFile(${index}, -1)" ${index === 0 ? 'disabled' : ''}><i class="fas fa-arrow-up"></i></button>
                <button type="button" class="btn btn-sm btn-outline-secondary" onclick="moveFile(${index}, 1)" ${index === multiFilesArray.length - 1 ? 'disabled' : ''}><i class="fas fa-arrow-down"></i></button>
                <button type="button" class="btn btn-sm btn-outline-danger" onclick="removeMultiFile(${index})"><i class="fas fa-trash"></i></button>
            </div>
        `;
        fileListContainer.appendChild(item);
    });

    if (multiInput) multiInput.files = dataTransfer.files;
}

function removeMultiFile(index) {
    multiFilesArray.splice(index, 1);
    renderMultiFileList();
}

function moveFile(index, direction) {
    const targetIndex = index + direction;
    if (targetIndex >= 0 && targetIndex < multiFilesArray.length) {
        const temp = multiFilesArray[index];
        multiFilesArray[index] = multiFilesArray[targetIndex];
        multiFilesArray[targetIndex] = temp;
        renderMultiFileList();
    }
}

/**
 * Form Submissions and Spinner Handling
 */
function initFormSubmissions() {
    const pdfForms = document.querySelectorAll('.pdf-action-form');
    const overlay = document.getElementById('spinner-overlay');
    const spinnerText = document.getElementById('spinner-text');

    pdfForms.forEach(form => {
        form.addEventListener('submit', function (e) {
            const fileInput = this.querySelector('input[type="file"]');
            if (fileInput && fileInput.files.length === 0) {
                e.preventDefault();
                alert('Please select a PDF file before proceeding.');
                return;
            }

            if (overlay) {
                overlay.style.display = 'flex';
                if (spinnerText) {
                    const actionName = this.getAttribute('data-action-name') || 'Processing PDF';
                    spinnerText.textContent = `${actionName}, please wait...`;
                }
            }
        });
    });
}

/**
 * Copy Extracted Text to Clipboard
 */
function initCopyToClipboard() {
    const copyBtn = document.getElementById('copy-text-btn');
    const textBox = document.getElementById('extracted-text-content');

    if (copyBtn && textBox) {
        copyBtn.addEventListener('click', function () {
            const text = textBox.textContent || textBox.innerText;
            navigator.clipboard.writeText(text).then(() => {
                const originalHtml = copyBtn.innerHTML;
                copyBtn.innerHTML = '<i class="fas fa-check me-1"></i> Copied!';
                copyBtn.classList.replace('btn-outline-primary', 'btn-success');

                setTimeout(() => {
                    copyBtn.innerHTML = originalHtml;
                    copyBtn.classList.replace('btn-success', 'btn-outline-primary');
                }, 2500);
            }).catch(err => {
                alert('Could not copy text automatically: ' + err);
            });
        });
    }
}

/**
 * Confirm deletion action
 */
function confirmAction(message) {
    return confirm(message || 'Are you sure you want to proceed with this action?');
}
