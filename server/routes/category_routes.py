from sqlalchemy.exc import IntegrityError
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.category import Category
from models.task import Task
from models import db
from sqlalchemy import func

category_bp = Blueprint("category", __name__)

# =========================
# GET /api/categories/user
# =========================
from sqlalchemy import func

@category_bp.route("/user", methods=["GET"])
@jwt_required()
def get_my_categories():
    user_id = get_jwt_identity()

    results = (
        db.session.query(
            Category.id,
            Category.category_name,
            func.count(Task.id).label("task_count")
        )
        .outerjoin(
            Task,
            (Task.category_id == Category.id) &
            (Task.is_deleted == False)
        )
        .filter(
            Category.user_id == user_id,
            Category.is_deleted == False
        )
        .group_by(Category.id)
        .all()
    )

    return jsonify([
        {
            "id": r.id,
            "category_name": r.category_name,
            "task_count": r.task_count
        }
        for r in results
    ]), 200



# =========================
# POST /api/categories
# =========================

@category_bp.route("", methods=["POST"])
@jwt_required()
def create_category():
    user_id = get_jwt_identity()
    data = request.get_json()

    category = Category(
        category_name=data.get("category_name"),
        user_id=user_id
    )

    db.session.add(category)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "message": "Danh mục đã tồn tại"
        }), 409

    return jsonify({
        "id": category.id,
        "category_name": category.category_name
    }), 201

# =========================
# PUT /api/categories/<id>
# =========================
@category_bp.route("/<int:id>", methods=["PUT"])
@jwt_required()
def update_category(id):
    user_id = get_jwt_identity()
    data = request.get_json()

    category_name = data.get("category_name")

    category = Category.query.filter(
        Category.id == id,
        Category.user_id == user_id,
        Category.is_deleted == False
    ).first()

    if not category:
        return jsonify({"message": "Category not found"}), 404

    # ✅ CHECK TRÙNG (loại trừ chính nó)
    exists = Category.query.filter(
        Category.user_id == user_id,
        Category.category_name == category_name,
        Category.is_deleted == False,
        Category.id != id
    ).first()

    if exists:
        return jsonify({
            "message": "Danh mục đã tồn tại"
        }), 409

    category.category_name = category_name

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "message": "Danh mục đã tồn tại"
        }), 409

    return jsonify({
        "id": category.id,
        "category_name": category.category_name
    }), 200

# =========================
# DELETE /api/categories/<id>
# =========================
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
