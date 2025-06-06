// Wrap everything to avoid leaking variables to the global scope
document.addEventListener('DOMContentLoaded', () => {
    const fileInput        = document.getElementById('fileInput');
    const fileInputWrapper = document.getElementById('fileInputWrapper');
    const fileInfo         = document.getElementById('fileInfo');
    const fileName         = document.getElementById('fileName');
    const fileSize         = document.getElementById('fileSize');
    const submitBtn        = document.getElementById('submitBtn');
    const uploadForm       = document.getElementById('uploadForm');
    const progressBar      = document.getElementById('progressBar');
    const progressFill     = document.getElementById('progressFill');

    /* ---------- Helpers ---------- */
    const formatFileSize = bytes => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024, sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return (bytes / Math.pow(k, i)).toFixed(2) + ' ' + sizes[i];
    };

    const displayFileInfo = file => {
        fileName.textContent = file.name;
        fileSize.textContent = formatFileSize(file.size);
        fileInfo.classList.add('show');
    };

    const hideFileInfo = () => fileInfo.classList.remove('show');

    /* ---------- File picker ---------- */
    fileInput.addEventListener('change', e => {
        const file = e.target.files[0];
        if (file) {
            displayFileInfo(file);
            submitBtn.disabled = false;
        } else {
            hideFileInfo();
            submitBtn.disabled = true;
        }
    });

    /* ---------- Drag & drop ---------- */
    ['dragover', 'dragleave', 'drop'].forEach(evt =>
        fileInputWrapper.addEventListener(evt, e => e.preventDefault())
    );

    fileInputWrapper.addEventListener('dragover', () =>
        fileInputWrapper.classList.add('dragover')
    );
    fileInputWrapper.addEventListener('dragleave', () =>
        fileInputWrapper.classList.remove('dragover')
    );
    fileInputWrapper.addEventListener('drop', e => {
        fileInputWrapper.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
            displayFileInfo(e.dataTransfer.files[0]);
            submitBtn.disabled = false;
        }
    });

    /* ---------- Form submit ---------- */
    uploadForm.addEventListener('submit', () => {
        submitBtn.textContent = 'Uploading…';
        submitBtn.disabled = true;
        progressBar.style.display = 'block';

        // Dummy progress animation
        let progress = 0;
        const timer = setInterval(() => {
            progress = Math.min(progress + 10, 90);
            progressFill.style.width = progress + '%';
            if (progress === 90) clearInterval(timer);
        }, 100);
    });
});
