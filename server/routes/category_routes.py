from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.category import Category
from models import db

# Prefix
category_bp = Blueprint("category", __name__, url_prefix="/api/categories")

# =========================
# LẤY CATEGORY THEO USER
# =========================
# GET /api/categories
@category_bp.route("/", methods=["GET"])
@jwt_required()
def get_categories():
    user_id = get_jwt_identity()

    categories = Category.query.filter(
        Category.user_id == user_id,
        Category.is_deleted == False
    ).all()

    return jsonify([
        {
            "id": c.id,
            "name": c.name
        }
        for c in categories
    ]), 200

# =========================
# TẠO CATEGORY MỚI
# =========================
# POST /api/categories
@category_bp.route("/", methods=["POST"])
@jwt_required()
def create_category():
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data or not data.get("name"):
        return jsonify({"msg": "Category name is required"}), 400

    category = Category(
        name=data["name"],
        user_id=user_id
    )

    db.session.add(category)
    db.session.commit()

    return jsonify({
        "msg": "Category created",
        "category": {
            "id": category.id,
            "name": category.name
        }
    }), 201

# =========================
# SỬA CATEGORY
# =========================
# PUT /api/categories/<id>
@category_bp.route("/<int:id>", methods=["PUT"])
@jwt_required()
def update_category(id):
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data or not data.get("name"):
        return jsonify({"msg": "Category name is required"}), 400

    category = Category.query.filter(
        Category.id == id,
        Category.user_id == user_id,
        Category.is_deleted == False
    ).first()

    if not category:
        return jsonify({"msg": "Category not found"}), 404

    category.name = data["name"]
    db.session.commit()

    return jsonify({
        "msg": "Category updated",
        "category": {
            "id": category.id,
            "name": category.name
        }
    }), 200

# =========================
# XÓA CATEGORY XÓA MỀM
# =========================
# DELETE /api/categories
@category_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_category(id):
    user_id = get_jwt_identity()

    category = Category.query.filter(
        Category.id == id,
        Category.user_id == user_id,
        Category.is_deleted == False
    ).first()

    if not category:
        return jsonify({"msg": "Category not found"}), 404

    category.is_deleted = True
    db.session.commit()

    return jsonify({"msg": "Category deleted"}), 200
