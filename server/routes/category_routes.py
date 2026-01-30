from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.category import Category
from models import db

category_bp = Blueprint("category", __name__)

# GET /api/categories
@category_bp.route("/", methods=["GET"])
@jwt_required()
def get_categories():
    user_id = get_jwt_identity()
    categories = Category.query.filter_by(user_id=user_id).all()

    return jsonify([
        {
            "id": c.id,
            "name": c.name
        } for c in categories
    ]), 200


# POST /api/categories
@category_bp.route("/", methods=["POST"])
@jwt_required()
def create_category():
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data or "name" not in data:
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
