# 👑 Django Web Project — by Hung

Xin chào, đây là project web được xây dựng bằng **Django Framework (Python)**.  
Mục tiêu của dự án: Xây dựng Website bán hàng tích hợp content-based filtering và collaborative-filtering để gợi ý
sản phẩm dựa vào tương tác của người dùng và các đánh giá từ sản phẩm đồng thời tích hợp api của gemini để xây dựng 
chatbot tương tác với người dùng


## 🌟 Tính năng chính

- 🧭 Trang chủ hiển thị sản phẩm
- 🛍️ Xem chi tiết sản phẩm
- ❤️ Gợi ý sản phẩm tương tự (recommend system)
- 👤 Đăng nhập / Đăng ký người dùng
- 🧩 Quản trị dữ liệu qua Django Admin
- 📊 Module `recommend.py` hỗ trợ gợi ý thông minh dựa trên hành vi người dùng
- 🖼️ Quản lý static và template đầy đủ

---

## ⚙️ Cấu trúc thư mục dự án

WEBBANHANGDIENTU/
│
├── app/ # Ứng dụng chính
│ ├── migrations/
│ ├── static/ # CSS, JS, images...
│ ├── templates/ # Giao diện HTML
│ ├── templatetags/ # Custom template tags
│ ├── admin.py
│ ├── apps.py
│ ├── models.py
│ ├── recommend.py # Hệ thống gợi ý
│ ├── tests.py
│ ├── urls.py
│ ├── utils.py
│ └── views.py
│
├── webbanhangdientu/ # Cấu hình Django chính
│ ├── init.py
│ ├── asgi.py
│ ├── settings.py
│ ├── urls.py
│ └── wsgi.py
│
├── .env # File cấu hình môi trường (ẩn)
├── .gitignore
├── manage.py
├── README.md
└── requirements.txt

## 🧩 Yêu cầu hệ thống

| Thành phần | Phiên bản |
|-------------|------------|
| Python | 3.10 – 3.12 |
| Django | 5.x |
| pip | Mới nhất |
| Virtualenv | Khuyến khích sử dụng |

## 🚀 Cách cài đặt và chạy dự án

### 1️⃣ Clone project
```bash
git clone https://github.com/<your-username>/WEBBANHANGDIENTU.git
cd WEBBANHANGDIENTU


