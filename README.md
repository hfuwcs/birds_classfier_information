# 🐦 Bird Detection and Library App

Đây là một ứng dụng web sử dụng Flask để phát hiện, phân loại các loài chim trong ảnh, cung cấp thông tin chi tiết về loài đó thông qua các API bên ngoài, và hoạt động như một thư viện tra cứu về các loài chim.

## ✨ Tính năng chính

*   ✅ **Phát hiện đối tượng:** Sử dụng mô hình YOLO (được train riêng) để phát hiện vị trí của các con chim trong ảnh.
*   ✅ **Phân loại loài:** Sử dụng mô hình EfficientNet (được fine-tuned riêng) để phân loại loài cho từng con chim được phát hiện.
*   ✅ **Thông tin chi tiết:** Gọi Google Gemini API để lấy mô tả và thông tin về loài chim được phân loại.
*   ✅ **Hình ảnh bổ sung:** Gọi Google Custom Search API để tìm kiếm và hiển thị các hình ảnh khác của loài chim được phân loại.
*   ✅ **Tiếng hót:** Gọi Xeno-Canto API để tìm kiếm và hiển thị các bản ghi âm tiếng hót của loài chim.
*   ✅ **Thư viện tra cứu:** Cung cấp một thư viện các loài chim với thông tin chi tiết (tải từ file JSON), có chức năng tìm kiếm và xem chi tiết từng loài.
*   ✅ **Giao diện web:** Giao diện đơn giản để người dùng tải ảnh lên và duyệt thư viện.

## 🛠️ Công nghệ sử dụng

*   ⚙️ **Backend:** Python, Flask
*   🧠 **Machine Learning:** PyTorch, Ultralytics YOLO, EfficientNet
*   👁️ **Computer Vision:** OpenCV
*   🌐 **API:** Google Gemini API, Google Custom Search API, Xeno-Canto API
*   📦 **Dependency Management:** `pip` (khuyến khích sử dụng kèm `venv` hoặc Conda)
*   🎨 **Frontend:** HTML, CSS, JavaScript, Jinja2 templating

## 📋 Yêu cầu (Prerequisites)

*   🐍 Python 3.7+ (Khuyến nghị 3.11+)
*   🐙 Git (để clone repository)
*   📦 Conda hoặc pip (để quản lý môi trường Python)
*   📶 Kết nối Internet (để tải gói, gọi API)
*   🔑 Một tài khoản Google Cloud Platform (GCP) để lấy Google API Key và thiết lập Google Custom Search Engine (hoặc sử dụng Gemini API riêng nếu có).
*   🤖 Mô hình YOLO đã train (`backend/best.pt`).
*   🤖 Mô hình Classifier đã train (`backend/efficientnet_b3_bird_classifier.pth`).
*   📚 File dữ liệu thư viện chim (`backend/static/birds_data.json`).

## 🚀 Cài đặt và Chạy ứng dụng

1.  **Clone Repository:**
    ```bash
    git clone https://github.com/hfuwcs/birds_classfier_information.git
    cd birds_classfier_information
    ```

2.  **Thiết lập Môi trường ảo:**
    Sử dụng `venv` (Built-in Python):
    ```bash
    python -m venv .venv
    # Kích hoạt môi trường ảo:
    # Trên Windows (PowerShell):
    # .\.venv\Scripts\Activate.ps1
    # Trên Windows (Command Prompt):
    # .\.venv\Scripts\activate
    # Trên macOS/Linux:
    # source ./.venv/bin/activate
    ```
    Hoặc sử dụng Conda (Khuyến nghị nếu gặp lỗi biên dịch native):
    ```bash
    conda create -n bird_env python=3.11 # Thay 3.11 bằng phiên bản Python bạn muốn
    conda activate bird_env
    ```
    **(⚠️ Đảm bảo môi trường ảo đã được kích hoạt trước khi tiếp tục.)**

3.  **Cài đặt Thư viện:**
    Với môi trường ảo đã kích hoạt, chạy lệnh sau từ **thư mục gốc của dự án** (nơi có file `requirements.txt`):
    ```bash
    pip install -r requirements.txt
    ```

4.  **Tải và Đặt các File Mô hình và Dữ liệu Thư viện:**
    Bạn cần có các file mô hình đã train (`best.pt`, `efficientnet_b3_bird_classifier.pth`) và file dữ liệu thư viện (`birds_data.json`).
    *   Đặt `best.pt` và `efficientnet_b3_bird_classifier.pth` vào thư mục `backend/`.
    *   Đặt `birds_data.json` vào thư mục `backend/static/`.

5.  **Thiết lập Google API Keys và Custom Search Engine:**
    *   Truy cập Google Cloud Console ([https://console.cloud.google.com/](https://console.cloud.google.com/)) để lấy **Google API Key**. Kích hoạt các API cần thiết (Custom Search API, Gemini API - nếu bạn dùng phiên bản từ GCP).
    *   Truy cập Google Programmable Search Engine control panel ([https://programmablesearchengine.google.com](https://programmablesearchengine.google.com)) để tạo một **Custom Search Engine** và lấy **Search Engine ID (cx)** của nó.
    *   Truy cập Google AI Studio ([https://aistudio.google.com/](https://aistudio.google.com/)) nếu bạn sử dụng Gemini API riêng (không qua GCP) để lấy **Gemini API Key**.
    *   *(Lưu ý: Xeno-Canto API hiện tại không yêu cầu API key cho các truy vấn cơ bản mà ứng dụng sử dụng.)*

6.  **Tạo file `.env`:**
    Trong thư mục `backend/`, tạo một file mới có tên `.env` và điền các khóa API và ID bạn đã lấy được. **Thay thế `<YOUR_..._HERE>` bằng giá trị thực tế của bạn.**
    ```dotenv
    # filepath: backend/.env
    GOOGLE_CSE_ID=<YOUR_CUSTOM_SEARCH_ENGINE_ID_HERE>
    GOOGLE_API_KEY=<YOUR_GOOGLE_API_KEY_HERE>
    GEMINI_API_KEY=<YOUR_GEMINI_API_KEY_HERE>
    ```
    **Quan trọng:** 🛡️ Thêm `.env` vào file `.gitignore` của bạn để đảm bảo bạn không vô tình đẩy các khóa bí mật lên Git repository. (File `.gitignore` đã có sẵn trong repo đã clone).

7.  **Chạy Ứng dụng Flask:**
    Mở Terminal hoặc Command Prompt, **kích hoạt lại môi trường ảo** nếu chưa, và điều hướng đến thư mục `backend/`:
    ```bash
    cd backend/
    # Kích hoạt môi trường ảo (ví dụ: source ../.venv/bin/activate hoặc conda activate bird_env)
    python app.py
    ```
    Server Flask sẽ bắt đầu chạy, thường là trên `http://127.0.0.1:5000/`.

## 💻 Sử dụng Ứng dụng

Sau khi server chạy, mở trình duyệt web và truy cập `http://127.0.0.1:5000/`.

*   🏠 **Trang chủ (`/`)**: Giới thiệu về BirdGuide.
*   📚 **Khám phá (`/library`)**: Duyệt qua danh sách các loài chim trong thư viện, có chức năng tìm kiếm. Click vào một loài chim để xem chi tiết.
*   🔎 **Công cụ Phát hiện (`/detection_tool`)**: Tải lên ảnh chứa chim để ứng dụng phát hiện, phân loại và hiển thị thông tin, hình ảnh, tiếng hót (nếu tìm thấy). Từ kết quả, có liên kết đến trang chi tiết trong thư viện.
*   📰 **Tin tức (`/news`)** và ℹ️ **Về chúng tôi (`/about`)**: Các trang thông tin tĩnh (nếu bạn đã tích hợp).

## 📁 Cấu trúc Dự án

Để dễ hình dung, cấu trúc dự án trông như sau:

```
your_project/
├── .gitignore
├── .venv/                 # Môi trường ảo (hoặc thư mục env của Conda)
├── backend/
│   ├── static/            # Các file tĩnh (CSS, JS, JSON, ảnh upload/results)
│   │   ├── uploads/
│   │   ├── results/
│   │   ├── style.css
│   │   ├── script.js         # JS cho trang thư viện
│   │   ├── birds_data.json   # Dữ liệu thư viện
│   │   └── detection_tool_style.css
│   ├── templates/         # Các file HTML template (được render bởi Flask)
│   │   ├── home.html           # Trang chủ
│   │   ├── library_index.html  # Danh sách thư viện
│   │   ├── bird_info.html      # Chi tiết loài chim
│   │   ├── detection_page.html # Công cụ phát hiện (upload/results)
│   │   ├── news.html
│   │   └── about.html
│   ├── app.py             # Backend Flask application
│   └── .env               # Chứa các khóa API
└── requirements.txt       # Danh sách thư viện Python
```

## 📸 Ảnh chụp màn hình (Screenshots)
