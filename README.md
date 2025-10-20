# 🏰 WEB BÁN HÀNG ĐIỆN TỬ (DJANGO PROJECT)
Truy cập tại: 👉 https://web-banhang-django.onrender.com
## 🧭 Giới thiệu
Dự án Web Bán Hàng Điện Tử được xây dựng bằng Django – một framework mạnh mẽ của Python.  
Website có các chức năng cơ bản của một hệ thống thương mại điện tử:  
- Quản lý sản phẩm, danh mục  
- Giỏ hàng, thanh toán  
- Đăng nhập / đăng ký người dùng  
- Hệ thống gợi ý sản phẩm bằng AI (Recommendation System)
- Tích hợp API gemini để gợi ý sản phẩm cho người dùng thông qua chatbot

---

## ⚙️ Cấu trúc thư mục chính
```
WEBBANHANGDIENTU/
│
├── app/                       # Ứng dụng chính
│   ├── migrations/            # Lưu thay đổi database
│   ├── static/                # File CSS, JS, hình ảnh
│   ├── templates/             # Giao diện HTML
│   ├── templatetags/          # Thẻ template tùy chỉnh
│   ├── admin.py               # Cấu hình trang admin
│   ├── apps.py                # Khai báo ứng dụng
│   ├── models.py              # Định nghĩa các model
│   ├── recommend.py           # File xử lý gợi ý sản phẩm (AI)
│   ├── tests.py               # Unit test
│   ├── urls.py                # Định tuyến URL
│   ├── utils.py               # Hàm tiện ích
│   └── views.py               # Xử lý logic hiển thị
│
├── webbanhangdientu/          # Thư mục cấu hình Django gốc
│   ├── settings.py            # Cấu hình toàn hệ thống
│   ├── urls.py                # URL gốc
│   ├── wsgi.py                # Chạy server thật (Deploy)
│   ├── asgi.py                # Cấu hình async
│   └── __init__.py
│
├── manage.py                  # File chạy chính của Django
├── .env                       # Biến môi trường (không public)
├── .gitignore                 # File loại trừ khi push GitHub
└── README.md                  # Tập tin hướng dẫn
```

---

## 🪄 Cài đặt & Chạy Dự án

### 1️⃣ Tạo môi trường ảo
```bash
python -m venv venv
```

### 2️⃣ Kích hoạt môi trường ảo
- Windows
  ```bash
  venv\Scripts\activate
  ```
- macOS/Linux
  ```bash
  source venv/bin/activate
  ```

### 3️⃣ Cài đặt thư viện cần thiết
```bash
pip install -r requirements.txt
```

> Nếu chưa có `requirements.txt`, tạo nhanh bằng lệnh:
> ```bash
> pip freeze > requirements.txt
> ```

### 4️⃣ Cấu hình cơ sở dữ liệu
Mở file `.env` (nếu có) hoặc `settings.py`, chỉnh lại phần:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```
> Nếu dùng MySQL / PostgreSQL thì cập nhật thông tin tương ứng.

### 5️⃣ Chạy migrate database
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6️⃣ Tạo tài khoản admin
```bash
python manage.py createsuperuser
```

### 7️⃣ Chạy server
```bash
python manage.py runserver
```

Truy cập tại: 👉 http://127.0.0.1:8000/

---

## 🧑‍💻 Liên hệ & Ghi chú
- Tác giả: Hung dep trai 💎  
- Framework: Django  
- Ngôn ngữ: Python  

---

## Tạo thêm file .env gồm

SECRET_KEY=django-insecure-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
SENDER_EMAIL=name your email
APP_PASSWORD=your email pass word
GEMINI_API_KEY=your gemini api key
-- 3 cái này phải tạo tài khoản cloudinary(cái này để lưu ảnh upload lên cloud) để lấy--
CLOUDINARY_CLOUD_NAME=xxxx
CLOUDINARY_API_KEY=xxxxx
CLOUDINARY_API_SECRET=xxxxx
### Để lấy secret key chạy dòng lệnh sau rồi thay vào xxxxxx
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

