document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('fileInput'); // Lấy input file bên trong drop zone
    const uploadForm = dropZone.closest('form'); // Lấy form chứa drop zone

    if (!dropZone || !fileInput || !uploadForm) {
        console.error("Drop zone, file input, or form element not found!");
        return; // Thoát nếu không tìm thấy các phần tử cần thiết
    }

    // Ngăn chặn hành vi mặc định của trình duyệt khi kéo file vào
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
        // Thêm cho cả body/window để ngăn kéo thả ngoài drop zone nếu cần
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    // Highlight khu vực kéo thả khi file được kéo vào
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
    });

    // Xử lý file khi được thả vào
    dropZone.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;

        // Gán file đầu tiên vào input file
        if (files.length > 0) {
            fileInput.files = files;

            // Tự động submit form sau khi thả file
            uploadForm.submit();

            // Tùy chọn: Hiển thị preview ảnh trước khi submit
            const reader = new FileReader();
            reader.onloadend = () => {
                const img = document.createElement('img');
                img.src = reader.result;
                img.style.maxWidth = '100%';
                dropZone.innerHTML = '';
                dropZone.appendChild(img);
            };
            reader.readAsDataURL(files[0]);
        }
    }

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            uploadForm.submit();
        }
    });
});