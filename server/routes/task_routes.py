from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.task import Task
from models.category import Category
from models import db
from datetime import datetime

task_bp = Blueprint("task", __name__)


# =========================
# GET /api/categories/<category_id>/tasks
# =========================
@task_bp.route("/categories/<int:category_id>/tasks", methods=["GET"])
@jwt_required()
def get_tasks_by_category(category_id):
    user_id = get_jwt_identity()

    category = Category.query.filter_by(
        id=category_id,
        user_id=user_id,
        is_deleted=False
    ).first()

    if not category:
        return jsonify({"message": "Category not found"}), 404

    tasks = (
        Task.query
        .filter_by(
            category_id=category_id,
            user_id=user_id,
            is_deleted=False
        )
        .order_by(Task.id.desc())
        .all()
    )

    return jsonify([
        {
            "id": t.id,
            "task_name": t.task_name,
            "completed": t.completed,
            "deadline": t.deadline.isoformat() if t.deadline else None,
        }
        for t in tasks
    ]), 200


# =========================
# POST /api/categories/<category_id>/tasks
# =========================
@task_bp.route("/categories/<int:category_id>/tasks", methods=["POST"])
@jwt_required()
def create_task(category_id):
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data or not data.get("task_name"):
        return jsonify({"message": "Task name is required"}), 400

    category = Category.query.filter_by(
        id=category_id,
        user_id=user_id,
        is_deleted=False
    ).first()

    if not category:
        return jsonify({"message": "Category not found"}), 404

    deadline = None
    if data.get("deadline"):
        try:
            deadline = datetime.fromisoformat(data["deadline"])
        except ValueError:
            return jsonify({"message": "Invalid deadline format"}), 400

    task = Task(
        task_name=data["task_name"],
        user_id=user_id,
        category_id=category_id,
        deadline=deadline
    )

    db.session.add(task)
    db.session.commit()

    return jsonify({
        "id": task.id,
        "task_name": task.task_name,
        "completed": task.completed,
        "deadline": task.deadline.isoformat() if task.deadline else None
    }), 201


# =========================
# PUT /api/tasks/<task_id>
# =========================
@task_bp.route("/tasks/<int:task_id>", methods=["PUT"])
@jwt_required()
def update_task(task_id):
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data:
        return jsonify({"message": "No data provided"}), 400

    task = Task.query.filter_by(
        id=task_id,
        user_id=user_id,
        is_deleted=False
    ).first()

    if not task:
        return jsonify({"message": "Task not found"}), 404

    if "task_name" in data:
        task.task_name = data["task_name"]

    if "completed" in data:
        task.completed = data["completed"]

    if "deadline" in data:
        if data["deadline"]:
            try:
                task.deadline = datetime.fromisoformat(data["deadline"])
            except ValueError:
                return jsonify({"message": "Invalid deadline format"}), 400
        else:
            task.deadline = None

    db.session.commit()

    return jsonify({
        "id": task.id,
        "task_name": task.task_name,
        "completed": task.completed,
        "deadline": task.deadline.isoformat() if task.deadline else None
    }), 200


# =========================
# DELETE /api/tasks/<task_id>
# =========================
@task_bp.route("/tasks/<int:task_id>", methods=["DELETE"])
@jwt_required()
def delete_task(task_id):
    user_id = get_jwt_identity()

    task = Task.query.filter_by(
        id=task_id,
        user_id=user_id,
        is_deleted=False
    ).first()

    if not task:
        return jsonify({"message": "Task not found"}), 404

    task.is_deleted = True
    db.session.commit()

    return jsonify({"message": "Task deleted successfully"}), 200
