from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from models.user import User
from models import db
from utils.hash import hash_password, verify_password
from utils.auth import generate_token
from datetime import datetime, timedelta
import random
from utils.reset_cache import reset_codes
from utils.mail import send_email
import os, re

auth_bp = Blueprint("auth", __name__)

# =========================
# ĐĂNG KÝ TÀI KHOẢN
# POST /api/auth/register
# =========================
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json

    username = data.get("username", "").strip()
    password = data.get("password")
    email = data.get("email", "").strip()

    if not username or not password or not email:
        return jsonify({"message": "Thiếu username, password hoặc email"}), 400

    # kiểm tra username tồn tại
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Tên đăng nhập đã tồn tại"}), 400

    # kiểm tra email tồn tại
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email đã được sử dụng"}), 400

    # kiểm tra format email
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(email_pattern, email):
        return jsonify({"message": "Email không hợp lệ"}), 400

    # kiểm tra password mạnh
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{6,}$'
    if not re.match(pattern, password):
        return jsonify({
            "message": "Mật khẩu phải có chữ hoa, chữ thường, số và ký tự đặc biệt"
        }), 400

    user = User(
        username=username,
        password=hash_password(password),
        full_name=data.get("full_name"),
        gender=data.get("gender"),
        avatar="default_user.png",
        email=email
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Register success"
    }), 201

# =========================
# ĐĂNG NHẬP TÀI KHOẢN
# POST /api/auth/login
# =========================
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json

    user = User.query.filter_by(username=data.get("username")).first()
    # ===== Sai thông tin =====
    if not user or not verify_password(user.password, data.get("password")):
        return jsonify({
            "success": False,
            "message": "Sai tài khoản hoặc mật khẩu"
        }), 401
    
    # ===== ĐANG CHỜ XÓA =====
    if user.is_deleted:

        expire_time = user.deleted_at + timedelta(days=15)

        # Quá hạn → coi như đã xóa
        if datetime.utcnow() > expire_time:
            return jsonify({
                "success": False,
                "message": "Tài khoản đã bị xóa vĩnh viễn"
            }), 410

        # Trong 15 ngày → cho phép khôi phục
        return jsonify({
            "success": False,
            "message": "Tài khoản đang chờ xóa",
            "can_restore": True,
            "restore_until": expire_time.isoformat(),
            "username": user.username
        }), 403

    # ===== LOGIN BÌNH THƯỜNG =====
    token = create_access_token(identity=str(user.id))
    return jsonify({
        "success": True,
        "message": "Đăng nhập thành công",
        "access_token": token,
        "user": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "gender": user.gender,
            "avatar": user.avatar,
        }
    }), 200


# =========================
# GỬI EMAIL KHÔI PHỤC MẬT KHẨU
# POST /api/auth/forgot-password
# =========================
@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.json
    email = data.get("email")
    username = data.get("username")

    if not username or not email:
        return jsonify({"success": False, "message": "Thiếu dữ liệu"}), 400

    # ===== KIỂM TRA USERNAME + EMAIL =====
    user = User.query.filter_by(username=username, email=email).first()
    if not user:
        return jsonify({
            "success": False,
            "message": "Username hoặc email không đúng"
        }), 404
    
    # ===== TẠO OTP =====
    code = str(random.randint(100000, 999999))

    
    reset_codes[username] = {
        "code": code,
        "expire": datetime.utcnow() + timedelta(minutes=5)
    }

    # ===== GỬI EMAIL =====
    send_email(
        to=user.email,
        subject="Khôi phục mật khẩu",
        content=f"Mã xác nhận của bạn là: {code}\nCó hiệu lực 5 phút."
    )

    return jsonify({
        "success": True,
        "message": "Đã gửi mã xác nhận"
    }), 200

# =========================
# XÁC THỰC MÃ KHÔI PHỤC MẬT KHẨU
# POST /api/auth/verify-reset-code
# =========================
@auth_bp.route("/verify-reset-code", methods=["POST"])
def verify_reset_code():
    data = request.json
    username = data.get("username")
    code = data.get("code")

    cache = reset_codes.get(username)
    if not cache:
        return jsonify({"success": False, "message": "Không có yêu cầu reset"}), 400

    if datetime.utcnow() > cache["expire"]:
        reset_codes.pop(username)
        return jsonify({"success": False, "message": "Mã đã hết hạn"}), 400

    if cache["code"] != code:
        return jsonify({"success": False, "message": "Sai mã"}), 400

    # Đánh dấu đã verify
    cache["verified"] = True

    return jsonify({
        "success": True,
        "message": "Xác thực thành công"
    }), 200

# =========================
# ĐỔI MẬT KHẨU SAU KHI XÁC THỰC OTP
# POST /api/auth/verify-reset-code
# =========================
@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.json
    username = data.get("username")
    new_password = data.get("new_password")

    cache = reset_codes.get(username)

    if not cache or not cache.get("verified"):
        return jsonify({
            "success": False,
            "message": "Chưa xác thực OTP"
        }), 400

    user = User.query.filter_by(username=username).first()
    user.password = hash_password(new_password)
    db.session.commit()

    # Xóa OTP sau khi dùng
    reset_codes.pop(username)

    return jsonify({
        "success": True,
        "message": "Đổi mật khẩu thành công"
    }), 200


# =========================
# KHÔI PHỤC TÀI KHOẢN ĐANG CHỜ XÓA
# POST /api/auth/restore-account
# =========================
@auth_bp.route("/restore-account", methods=["POST"])
def restore_account():
    data = request.json

    user = User.query.filter_by(username=data.get("username")).first()

    if not user:
        return jsonify({
            "success": False,
            "message": "User không tồn tại"
        }), 404

    if not user.is_deleted:
        return jsonify({
            "success": False,
            "message": "Tài khoản không ở trạng thái chờ xóa"
        }), 400

    user.is_deleted = False
    user.deleted_at = None

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Khôi phục tài khoản thành công"
    }), 200