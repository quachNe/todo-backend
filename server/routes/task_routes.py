from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.task import Task
from models.category import Category
from models import db
from datetime import datetime

task_bp = Blueprint("task", __name__)


# =========================================================
# GET /api/categories/<category_id>/tasks
# =========================================================
from datetime import date
from sqlalchemy import func
from flask_jwt_extended import jwt_required, get_jwt_identity

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
        return jsonify({
            "message": "Danh mục không tồn tại"
        }), 404

    today = date.today()

    # ======================
    # TASK LIST
    # ======================
    tasks = (
        Task.query
        .filter_by(category_id=category_id, is_deleted=False)
        .order_by(Task.id.desc())
        .all()
    )

    # ======================
    # SUMMARY COUNT
    # ======================

    # Tổng = tất cả chưa xoá
    total_count = (
        Task.query
        .filter_by(category_id=category_id, is_deleted=False)
        .count()
    )

    # Hôm nay
    today_count = (
        Task.query
        .filter(
            Task.category_id == category_id,
            Task.is_deleted == False,
            func.date(Task.deadline) == today
        )
        .count()
    )

    # Đã hoàn thành
    completed_count = (
        Task.query
        .filter_by(
            category_id=category_id,
            is_deleted=False,
            completed=True
        )
        .count()
    )

    # Chưa hoàn thành
    pending_count = (
        Task.query
        .filter_by(
            category_id=category_id,
            is_deleted=False,
            completed=False
        )
        .count()
    )

    return jsonify({
        "message": "Lấy danh sách công việc thành công",
        "summary": {
            "total": total_count,
            "today": today_count,
            "completed": completed_count,
            "pending": pending_count
        },
        "tasks": [
            {
                "id": t.id,
                "task_name": t.task_name,
                "completed": t.completed,
                "deadline": t.deadline.isoformat() if t.deadline else None
            }
            for t in tasks
        ]
    }), 200


# =========================================================
# POST /api/categories/<category_id>/tasks
# =========================================================
@task_bp.route("/categories/<int:category_id>/tasks", methods=["POST"])
@jwt_required()
def create_task(category_id):
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data or not data.get("task_name"):
        return jsonify({
            "message": "Tên công việc không được để trống"
        }), 400

    category = Category.query.filter_by(
        id=category_id,
        user_id=user_id,
        is_deleted=False
    ).first()

    if not category:
        return jsonify({
            "message": "Danh mục không tồn tại"
        }), 404

    existing_task = Task.query.filter_by(
        category_id=category_id,
        task_name=data["task_name"],
        is_deleted=False
    ).first()

    if existing_task:
        return jsonify({
            "message": "Tên công việc đã tồn tại trong danh mục này"
        }), 400

    deadline = None
    if data.get("deadline"):
        try:
            deadline = datetime.fromisoformat(data["deadline"])
        except ValueError:
            return jsonify({
                "message": "Định dạng ngày hết hạn không hợp lệ"
            }), 400

    task = Task(
        task_name=data["task_name"],
        category_id=category_id,
        deadline=deadline
    )

    db.session.add(task)
    db.session.commit()

    return jsonify({
        "message": "Tạo công việc thành công",
        "task": {
            "id": task.id,
            "task_name": task.task_name,
            "completed": task.completed,
            "deadline": task.deadline.isoformat() if task.deadline else None
        }
    }), 201


# =========================================================
# PUT /api/tasks/<task_id>
# =========================================================
@task_bp.route("/tasks/<int:task_id>", methods=["PUT"])
@jwt_required()
def update_task(task_id):
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data:
        return jsonify({
            "message": "Không có dữ liệu được cung cấp"
        }), 400

    task = (
        Task.query
        .join(Category)
        .filter(
            Task.id == task_id,
            Task.is_deleted == False,
            Category.user_id == user_id,
            Category.is_deleted == False
        )
        .first()
    )

    if not task:
        return jsonify({
            "message": "Công việc không tồn tại"
        }), 404

    if "task_name" in data:
        existing_task = Task.query.filter(
            Task.category_id == task.category_id,
            Task.task_name == data["task_name"],
            Task.is_deleted == False,
            Task.id != task.id
        ).first()

        if existing_task:
            return jsonify({
                "message": "Tên công việc đã tồn tại trong danh mục này"
            }), 400

        task.task_name = data["task_name"]

    if "completed" in data:
        task.completed = data["completed"]

    if "deadline" in data:
        if data["deadline"]:
            try:
                task.deadline = datetime.fromisoformat(data["deadline"])
            except ValueError:
                return jsonify({
                    "message": "Định dạng ngày hết hạn không hợp lệ"
                }), 400
        else:
            task.deadline = None

    db.session.commit()

    return jsonify({
        "message": "Cập nhật công việc thành công",
        "task": {
            "id": task.id,
            "task_name": task.task_name,
            "completed": task.completed,
            "deadline": task.deadline.isoformat() if task.deadline else None
        }
    }), 200


# =========================================================
# DELETE /api/tasks/<task_id>
# =========================================================
@task_bp.route("/tasks/<int:task_id>", methods=["DELETE"])
@jwt_required()
def delete_task(task_id):
    user_id = get_jwt_identity()

    task = (
        Task.query
        .join(Category)
        .filter(
            Task.id == task_id,
            Task.is_deleted == False,
            Category.user_id == user_id,
            Category.is_deleted == False
        )
        .first()
    )

    if not task:
        return jsonify({
            "message": "Công việc không tồn tại"
        }), 404

    task.is_deleted = True
    db.session.commit()

    return jsonify({
        "message": "Xóa công việc thành công",
        "task": {
            "id": task.id,
            "task_name": task.task_name,
            "completed": task.completed,
            "deadline": task.deadline.isoformat() if task.deadline else None
        }
    }), 200
