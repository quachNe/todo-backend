from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.task import Task
from models.category import Category
from models import db

task_bp = Blueprint("task", __name__)

# =========================
# LẤY TASK THEO CATEGORY
# =========================
@task_bp.route("/categories/<int:category_id>/tasks", methods=["GET"])
@jwt_required()
def get_tasks_by_category(category_id):
    user_id = get_jwt_identity()

    # Kiểm tra category có thuộc user không
    category = Category.query.filter_by(
        id=category_id,
        user_id=user_id
    ).first()

    if not category:
        return jsonify({"msg": "Category not found"}), 404

    # Lấy task CHƯA bị xóa
    tasks = Task.query.filter_by(
        category_id=category_id,
        user_id=user_id,
        is_deleted=False
    ).all()

    return jsonify([
        {
            "id": t.id,
            "title": t.title,
            "completed": t.completed
        }
        for t in tasks
    ])



# =========================
# TẠO TASK TRONG CATEGORY
# =========================
@task_bp.route("/categories/<int:category_id>/tasks", methods=["POST"])
@jwt_required()
def create_task(category_id):
    user_id = get_jwt_identity()
    data = request.json

    category = Category.query.filter_by(
        id=category_id,
        user_id=user_id
    ).first()

    if not category:
        return jsonify({"msg": "Category not found"}), 404

    task = Task(
        title=data["title"],
        user_id=user_id,
        category_id=category_id
    )

    db.session.add(task)
    db.session.commit()

    return jsonify({"msg": "Task created"}), 201


# =========================
# CẬP NHẬT TASK
# =========================
@task_bp.route("/tasks/<int:id>", methods=["PUT"])
@jwt_required()
def update_task(id):
    user_id = get_jwt_identity()

    task = Task.query.filter_by(
        id=id,
        user_id=user_id
    ).first()

    if not task:
        return jsonify({"msg": "Task not found"}), 404

    task.completed = request.json.get("completed", task.completed)
    db.session.commit()

    return jsonify({"msg": "Updated"})


# =========================
# XOÁ TASK
# =========================
@task_bp.route("/tasks/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_task(id):
    user_id = get_jwt_identity()

    task = Task.query.filter_by(
        id=id,
        user_id=user_id,
        is_deleted=False
    ).first()

    if not task:
        return jsonify({"msg": "Task not found"}), 404

    # Xóa mềm
    task.is_deleted = True
    db.session.commit()

    return jsonify({"msg": "Task deleted successfully"})

