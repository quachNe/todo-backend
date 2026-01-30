from flask import Blueprint, request, jsonify
from models.user import User
from models import db
from utils.hash import hash_password, verify_password
from utils.auth import generate_token

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json

    # Validate dữ liệu
    if not data.get("username") or not data.get("password"):
        return jsonify({"msg": "Missing username or password"}), 400

    # Kiểm tra username đã tồn tại chưa
    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"msg": "User already exists"}), 400

    # Tạo user mới
    user = User(
        username=data["username"],
        password=hash_password(data["password"]),
        full_name=data.get("full_name"),   # optional
        gender=data.get("gender")           # optional
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"msg": "Register success"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(username=data["username"]).first()

    if not user or not verify_password(user.password, data["password"]):
        return jsonify({"msg": "Invalid credentials"}), 401

    token = generate_token(user.id)
    return jsonify(access_token=token)
