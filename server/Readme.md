# 📌 Todo List Backend – Flask REST API

## 1. Giới thiệu
**Todo List Backend** là hệ thống Backend cho ứng dụng Todo List Mobile, được xây dựng theo mô hình **Frontend – Backend tách rời**.  
Backend cung cấp các **RESTful API** cho phép quản lý người dùng, danh mục công việc (Category) và các công việc cá nhân (Task).

Hệ thống sử dụng **JWT Authentication** để xác thực người dùng, đảm bảo mỗi tài khoản chỉ truy cập và thao tác trên dữ liệu của chính mình.

---

## 2. Công nghệ sử dụng
- **Python 3**
- **Flask**
- **Flask SQLAlchemy**
- **Flask JWT Extended**
- **Flask CORS**
- **SQLite**
- **RESTful API**

---

## 3. Kiến trúc hệ thống
- Frontend và Backend được **tách rời hoàn toàn**
- Backend hoạt động như một **REST API Server**
- Giao tiếp giữa Client và Server thông qua **HTTP + JSON**
- Xác thực và phân quyền bằng **JWT Access Token**
- Dữ liệu được lưu trữ bằng **SQLite (local database)**

---

## 4. Cấu trúc thư mục
```plaintext
server/
│
├── app.py                 # File khởi chạy Flask server
├── config.py              # Cấu hình ứng dụng
├── requirements.txt       # Danh sách thư viện
│
├── models/                # Định nghĩa database models
│   ├── __init__.py
│   ├── user.py
│   ├── category.py
│   └── task.py
│
├── routes/                # Định nghĩa API endpoints
│   ├── __init__.py
│   ├── auth.py
│   ├── category.py
│   └── task.py
│
├── instance/
│   └── todo.db            # SQLite database
│
└── venv/                  # Virtual environment
```

---

## 5. API Endpoints

### 🔐 Authentication
| Method | Endpoint             | Mô tả                 |
|--------|----------------------|-----------------------|
| POST   | `/api/auth/register` | Đăng ký tài khoản     |
| POST   | `/api/auth/login`    | Đăng nhập, trả về JWT |

---

### 📂 Category
| Method | Endpoint          | Mô tả                           |
|--------|-------------------|---------------------------------|
| GET    | `/api/categories` | Lấy danh sách category của user |
| POST   | `/api/categories` | Tạo category mới                |

---

### ✅ Task
| Method | Endpoint                     | Mô tả                               |
|--------|------------------------------|------                               |
| GET    | `/api/categories/{id}/tasks` | Lấy danh sách task theo category    |
| POST   | `/api/categories/{id}/tasks` | Tạo task trong category             |
| PUT    | `/api/tasks/{id}`            | Cập nhật trạng thái / nội dung task |
| DELETE | `/api/tasks/{id}`            | Xóa task                            |

---

## 6. Hướng dẫn chạy Backend

### 6.1. Tạo môi trường ảo
```bash
python -m venv venv
pip install -r requirements.txt
python app.py 
```
