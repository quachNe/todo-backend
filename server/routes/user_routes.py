from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from models import db
from utils.hash import hash_password, verify_password
import os,re
from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from datetime import datetime

user_bp = Blueprint("user", __name__)
DEFAULT_AVATAR = "default_user.png"

# =========================
# LẤY THÔNG TIN USER
# =========================
# GET /api/users
@user_bp.route("", methods=["GET"])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()

    user = User.query.get(user_id)

    if not user:
        return jsonify({"msg": "User not found"}), 404

    BASE_URL = "http://10.0.2.2:5000/"
    return jsonify({
        "user": {
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "gender": user.gender,
        "avatar": BASE_URL + "static/uploads/avatars/" + user.avatar,
        "email": user.email
        }
    }), 200


# =========================
# CẬP NHẬT THÔNG TIN USER
# =========================
# PUT /api/users
@user_bp.route("", methods=["PATCH"])
@jwt_required()
def update_profile():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"msg": "User not found"}), 404

    data = request.form

    # ===== full name =====
    if "full_name" in data and data["full_name"].strip():
        user.full_name = data["full_name"].strip()

    # ===== email =====
    if "email" in data and data["email"].strip():
        email = data["email"].strip()

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({"message": "Email không hợp lệ"}), 400

        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.id != user_id:
            return jsonify({"message": "Email đã được sử dụng"}), 400

        user.email = email

    # ===== gender =====
    if "gender" in data and data["gender"].strip():
        user.gender = data["gender"]

    # ===== avatar =====
    if "avatar" in request.files:
        file = request.files["avatar"]

        if file and file.filename:
            filename = secure_filename(file.filename)

            upload_folder = os.path.join(
                current_app.root_path,
                "static/uploads/avatars"
            )
            os.makedirs(upload_folder, exist_ok=True)

            if user.avatar and user.avatar != DEFAULT_AVATAR:
                old_path = os.path.join(upload_folder, user.avatar)
                if os.path.exists(old_path):
                    os.remove(old_path)

            import time
            new_filename = f"user_{user.id}_{int(time.time())}_{filename}"

            file.save(os.path.join(upload_folder, new_filename))
            user.avatar = new_filename

    db.session.commit()

    return jsonify({
        "message": "Profile updated",
        "user": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "gender": user.gender,
            "avatar": user.avatar,
            "email": user.email
        }
    }), 200


# =========================
# ĐỔI MẬT KHẨU
# =========================
# PUT /api/users/change-password
@user_bp.route("/change-password", methods=["PUT"])
@jwt_required()
def change_password():
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data.get("old_password") or not data.get("new_password"):
        return jsonify({"message": "Missing password"}), 400

    user = User.query.get(user_id)

    if not verify_password(user.password, data["old_password"]):
        return jsonify({"message": "Mật khẩu cũ không đúng"}), 401
    
    if data["old_password"] == data["new_password"]:
        return jsonify({"message": "Mật khẩu mới không được trùng với mật khẩu cũ"}), 400

    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{6,}$'

    if not re.match(pattern, data["new_password"]):
        return jsonify({
            "message": "Mật khẩu phải có ít nhất 6 ký tự, gồm chữ hoa, chữ thường, số và ký tự đặc biệt"
        }), 400

    user.password = hash_password(data["new_password"])
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Cập nhật mật khẩu thành công"}), 200


# =========================
# YÊU CẦU XÓA TÀI KHOẢN
# DELETE /api/users/delete-request
# =========================
@user_bp.route("/delete-request", methods=["DELETE"])
@jwt_required()
def request_delete_account():

    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    # Nếu đã yêu cầu xóa rồi
    if user.is_deleted:
        return jsonify({
            "success": False,
            "message": "Tài khoản đã đang chờ xóa"
        }), 400

    # Đánh dấu chờ xóa
    user.is_deleted = True
    user.deleted_at = datetime.utcnow()

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Tài khoản sẽ bị xóa vĩnh viễn sau 15 ngày"
    }), 200

# =========================
# TEST YÊU CẦU XÓA TÀI KHOẢN
# DELETE /api/users/delete-request
# =========================
# from datetime import datetime, timedelta

# @user_bp.route("/delete-request", methods=["DELETE"])
# @jwt_required()
# def request_delete_account():

#     user_id = get_jwt_identity()
#     user = User.query.get(user_id)

#     if not user:
#         return jsonify({
#             "success": False,
#             "message": "User not found"
#         }), 404

#     if user.is_deleted:
#         return jsonify({
#             "success": False,
#             "message": "Tài khoản đã đang chờ xóa"
#         }), 400

#     # Đánh dấu chờ xóa (để test -> lùi 15 ngày)
#     user.is_deleted = True
#     user.deleted_at = datetime.utcnow() - timedelta(days=15)

#     db.session.commit()

#     return jsonify({
#         "success": True,
#         "message": "Tài khoản test sẽ bị xóa ngay khi chạy cleanup"
#     }), 200