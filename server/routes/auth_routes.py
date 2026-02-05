from flask import Blueprint, request, jsonify
from models.user import User
from models import db
from utils.hash import hash_password, verify_password
from utils.auth import generate_token

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json

    # Kiểm tra username đã tồn tại chưa
    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"message": "Tên đăng nhập đã tồn tại"}), 400

    # Tạo user mới
    user = User(
        username=data["username"],
        password=hash_password(data["password"]),
        full_name=data.get("full_name"),
        gender=data.get("gender"),
        avatar="default_user.png"   
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"success": True,"message": "Register success"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json

    user = User.query.filter_by(username=data.get("username")).first()

    if not user or not verify_password(user.password, data.get("password")):
        return jsonify({
            "success": False,
            "message": "Sai tài khoản hoặc mật khẩu"
        }), 401

    token = generate_token(user.id)

    avatar_url = request.host_url + "static/uploads/avatars/" + user.avatar

    return jsonify({
        "success": True,
        "message": "Đăng nhập thành công",
        "token": token,
        "user": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "gender": user.gender,
            "avatar": user.avatar,
            "avatar_url": avatar_url   # 👈 CỰC KỲ QUAN TRỌNG
        }
    }), 200