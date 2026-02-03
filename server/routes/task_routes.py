from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.task import Task
from models.category import Category
from models import db
from datetime import datetime

task_bp = Blueprint("task", __name__)

# =========================
# LẤY TASK THEO CATEGORY
# =========================
# GET /api/categories/<id>/tasks
@task_bp.route("/categories/<int:category_id>/tasks", methods=["GET"])
@jwt_required()
def get_tasks_by_category(category_id):
    user_id = get_jwt_identity()

    # Check category thuộc user & chưa bị xóa
    category = Category.query.filter_by(
        id=category_id,
        user_id=user_id,
        is_deleted=False
    ).first()

    if not category:
        return jsonify({"msg": "Category not found"}), 404

    tasks = Task.query.filter_by(
        category_id=category_id,
        user_id=user_id,
        is_deleted=False
    ).all()

    return jsonify([
        {
            "id": t.id,
            "task_name": t.task_name,
            "completed": t.completed,
            "deadline": t.deadline.isoformat() if t.deadline else None
        }
        for t in tasks
    ]), 200


# =========================
# TẠO TASK TRONG CATEGORY
# =========================
# POST /api/categories/<id>/tasks
@task_bp.route("/categories/<int:category_id>/tasks", methods=["POST"])
@jwt_required()
def create_task(category_id):
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data or "task_name" not in data:
        return jsonify({"msg": "Task name is required"}), 400

    category = Category.query.filter_by(
        id=category_id,
        user_id=user_id,
        is_deleted=False
    ).first()

    if not category:
        return jsonify({"msg": "Category not found"}), 404

    deadline = None
    if data.get("deadline"):
        deadline = datetime.fromisoformat(data["deadline"])

    task = Task(
        task_name=data["task_name"],
        user_id=user_id,
        category_id=category_id,
        deadline=deadline
    )

    db.session.add(task)
    db.session.commit()

    return jsonify({
        "msg": "Task created",
        "task": {
            "id": task.id,
            "task_name": task.task_name
        }
    }), 201


# =========================
# CẬP NHẬT TASK
# =========================
# PUT /api/tasks/<id>
@task_bp.route("/tasks/<int:id>", methods=["PUT"])
@jwt_required()
def update_task(id):
    user_id = get_jwt_identity()
    data = request.get_json()

    task = Task.query.filter_by(
        id=id,
        user_id=user_id,
        is_deleted=False
    ).first()

    if not task:
        return jsonify({"msg": "Task not found"}), 404

    if "task_name" in data:
        task.task_name = data["task_name"]

    if "completed" in data:
        task.completed = data["completed"]

    if "deadline" in data:
        task.deadline = (
            datetime.fromisoformat(data["deadline"])
            if data["deadline"]
            else None
        )

    db.session.commit()

    return jsonify({"msg": "Task updated"}), 200


# =========================
# XOÁ TASK (XOÁ MỀM)
# =========================
# DELETE /api/tasks/<id>
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

    task.is_deleted = True
    db.session.commit()

    return jsonify({"msg": "Task deleted"}), 200
