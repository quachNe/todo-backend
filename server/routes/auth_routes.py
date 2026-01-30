from flask import Blueprint, request, jsonify
from models.user import User
from models import db
from utils.hash import hash_password, verify_password
from utils.auth import generate_token

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"msg": "User exists"}), 400

    user = User(
        username=data["username"],
        password=hash_password(data["password"])
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"msg": "Register success"})

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(username=data["username"]).first()

    if not user or not verify_password(user.password, data["password"]):
        return jsonify({"msg": "Invalid credentials"}), 401

    token = generate_token(user.id)
    return jsonify(access_token=token)
