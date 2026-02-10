from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from models import db
from utils.hash import hash_password, verify_password
import os
from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename


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
        "avatar": BASE_URL + "static/uploads/avatars/" + user.avatar
        }
    }), 200


# =========================
# CẬP NHẬT THÔNG TIN USER
# =========================
# PUT /api/users
@user_bp.route("/", methods=["PATCH"])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"msg": "User not found"}), 404

    data = request.form  # nhận text + file

    # ===== Update text fields =====
    if "full_name" in data and data["full_name"].strip():
        user.full_name = data["full_name"]

    if "gender" in data and data["gender"].strip():
        user.gender = data["gender"]

    # ===== Handle avatar =====
    if "avatar" in request.files:
        file = request.files["avatar"]

        if file and file.filename:
            filename = secure_filename(file.filename)

            upload_folder = os.path.join(
                current_app.root_path,
                "static/uploads/avatars"
            )
            os.makedirs(upload_folder, exist_ok=True)

            # xóa avatar cũ nếu không phải default
            if user.avatar and user.avatar != DEFAULT_AVATAR:
                old_path = os.path.join(upload_folder, user.avatar)
                if os.path.exists(old_path):
                    os.remove(old_path)

            # lưu avatar mới
            new_filename = f"user_{user.id}_{filename}"
            file.save(os.path.join(upload_folder, new_filename))

            user.avatar = new_filename

    db.session.commit()

    return jsonify({
        "msg": "Profile updated",
        "user": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "gender": user.gender,
            "avatar": user.avatar,
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
        return jsonify({"msg": "Missing password"}), 400

    user = User.query.get(user_id)

    if not verify_password(user.password, data["old_password"]):
        return jsonify({"msg": "Old password incorrect"}), 401

    user.password = hash_password(data["new_password"])
    db.session.commit()

    return jsonify({"msg": "Password updated"}), 200
