const birdNameInput = document.getElementById('bird-name-input');
const searchButton = document.getElementById('search-button');
const birdInfoDiv = document.getElementById('bird-info');
const imageGalleryDiv = document.getElementById('image-gallery');
const loadingDiv = document.getElementById('loading');
const errorMessageDiv = document.getElementById('error-message');

// URL của backend Flask
const BACKEND_URL = 'http://127.0.0.1:5000/search'; // Thay đổi nếu backend chạy ở địa chỉ khác

// Hàm hiển thị thông báo lỗi
function showErrorMessage(message) {
    errorMessageDiv.textContent = message;
    errorMessageDiv.classList.remove('hidden');
}

// Hàm ẩn thông báo lỗi
function hideErrorMessage() {
    errorMessageDiv.classList.add('hidden');
    errorMessageDiv.textContent = '';
}

// Hàm hiển thị loading
function showLoading() {
    loadingDiv.classList.remove('hidden');
    searchButton.disabled = true; // Tắt nút tìm kiếm khi đang xử lý
}

// Hàm ẩn loading
function hideLoading() {
    loadingDiv.classList.add('hidden');
    searchButton.disabled = false; // Bật lại nút tìm kiếm
}

// Hàm xóa kết quả cũ
function clearResults() {
    birdInfoDiv.innerHTML = ''; // Xóa thông tin
    imageGalleryDiv.innerHTML = ''; // Xóa ảnh
    hideErrorMessage();
}

// Hàm xử lý sự kiện click nút tìm kiếm
async function handleSearch() {
    const birdName = birdNameInput.value.trim(); // Lấy tên chim và loại bỏ khoảng trắng dư thừa

    if (!birdName) {
        showErrorMessage("Vui lòng nhập tên loài chim.");
        return; // Dừng lại nếu input rỗng
    }

    clearResults(); // Xóa kết quả cũ trước khi tìm kiếm mới
    showLoading(); // Hiển thị trạng thái loading

    try {
        // Gửi yêu cầu POST đến backend
        const response = await fetch(BACKEND_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ bird_name: birdName }) // Gửi tên chim dưới dạng JSON
        });

        // Kiểm tra mã trạng thái HTTP
        if (!response.ok) {
            const errorData = await response.json(); // Thử đọc lỗi từ body
            throw new Error(`Lỗi từ server: ${response.status} ${response.statusText}${errorData.error ? ' - ' + errorData.error : ''}`);
        }

        // Parse dữ liệu JSON nhận được
        const data = await response.json();

        // Hiển thị thông tin chim
        if (data.bird_info) {
            // Sử dụng textContent để ngăn chặn XSS, nhưng nếu Gemini trả về HTML (không mong muốn)
            // thì cách này sẽ hiển thị cả tag. Với Gemini thường trả text thuần.
            // Nếu muốn giữ định dạng xuống dòng, có thể thay bằng innerHTML và xử lý text trước (ví dụ: replace \n bằng <br>)
            // Hoặc dùng CSS white-space: pre-wrap như trong style.css
            birdInfoDiv.textContent = data.bird_info;
        } else {
            birdInfoDiv.textContent = "Không tìm thấy thông tin chi tiết cho loài chim này.";
        }


        // Hiển thị hình ảnh
        if (data.image_urls && data.image_urls.length > 0) {
            data.image_urls.forEach(url => {
                const imgElement = document.createElement('img');
                imgElement.src = url;
                imgElement.alt = `Hình ảnh của ${birdName}`; // Thêm alt text cho accessibility
                imageGalleryDiv.appendChild(imgElement); // Thêm ảnh vào gallery
            });
        } else {
             const noImageMessage = document.createElement('p');
             noImageMessage.textContent = "Không tìm thấy hình ảnh nào cho loài chim này.";
             imageGalleryDiv.appendChild(noImageMessage);
        }

    } catch (error) {
        console.error("Lỗi khi tìm kiếm:", error);
        showErrorMessage(`Đã xảy ra lỗi khi tìm kiếm. Vui lòng thử lại. Chi tiết: ${error.message}`);
        // Có thể hiển thị thông báo lỗi cụ thể hơn tùy thuộc vào loại lỗi
    } finally {
        hideLoading(); // Luôn ẩn loading bất kể thành công hay thất bại
    }
}

// Gán sự kiện click cho nút tìm kiếm
searchButton.addEventListener('click', handleSearch);

// Cho phép tìm kiếm khi nhấn Enter trong input
birdNameInput.addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        event.preventDefault(); // Ngăn form submit mặc định nếu có
        handleSearch();
    }
});