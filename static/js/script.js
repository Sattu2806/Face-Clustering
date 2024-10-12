// script.js

document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.querySelector('input[type="file"]');
    const fileLabel = document.querySelector('.file-label');

    fileInput.addEventListener('change', (e) => {
        const fileName = e.target.files.length > 1 
            ? `${e.target.files.length} files selected` 
            : e.target.files[0].name;
        fileLabel.innerText = fileName;
    });
});
