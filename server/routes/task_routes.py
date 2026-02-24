from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.task import Task
from models.category import Category
from models import db
from datetime import datetime, date
from sqlalchemy import func

task_bp = Blueprint("task", __name__)

# =========================================================
# GET /api/categories/<category_id>/tasks
# =========================================================
@task_bp.route("/categories/<int:category_id>/tasks", methods=["GET"])
@jwt_required()
def get_tasks_by_category(category_id):

    user_id = get_jwt_identity()

    # Check category ownership
    category = Category.query.filter_by(
        id=category_id,
        user_id=user_id,
        is_deleted=False
    ).first()

    if not category:
        return jsonify({"message": "Danh mục không tồn tại"}), 404

    today = date.today()

    # Get all tasks
    tasks = (
        Task.query
        .filter_by(category_id=category_id, is_deleted=False)
        .order_by(Task.id.desc())
        .all()
    )

    # Summary (gom query lại cho gọn)
    total = len(tasks)
    completed = sum(1 for t in tasks if t.completed)
    pending = total - completed
    today_count = sum(
        1 for t in tasks
        if t.deadline and t.deadline.date() == today
    )

    return jsonify({
        "message": "Lấy danh sách công việc thành công",
        "summary": {
            "total": total,
            "today": today_count,
            "completed": completed,
            "pending": pending
        },
        "tasks": [
            {
                "id": t.id,
                "task_name": t.task_name,
                "completed": t.completed,
                "deadline": t.deadline.isoformat() if t.deadline else None,
                "is_overdue": (
                    not t.completed and
                    t.deadline and
                    t.deadline.date() < today
                )
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

    task_name = data.get("task_name", "").strip() if data else ""

    if not task_name:
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
        task_name=task_name,
        is_deleted=False
    ).first()

    if existing_task:
        return jsonify({
            "message": "Tên công việc đã tồn tại trong danh mục này"
        }), 400

    deadline = None
    if data.get("deadline"):
        try:
            deadline = datetime.fromisoformat(
                data["deadline"].replace("Z", "+00:00")
            )
        except ValueError:
            return jsonify({
                "message": "Định dạng ngày hết hạn không hợp lệ"
            }), 400

    task = Task(
        task_name=task_name,
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

    # Update task name
    if "task_name" in data:
        new_name = data["task_name"].strip()

        if not new_name:
            return jsonify({
                "message": "Tên công việc không được để trống"
            }), 400

        existing_task = Task.query.filter(
            Task.category_id == task.category_id,
            Task.task_name == new_name,
            Task.is_deleted == False,
            Task.id != task.id
        ).first()

        if existing_task:
            return jsonify({
                "message": "Tên công việc đã tồn tại trong danh mục này"
            }), 400

        task.task_name = new_name

    # Update completed
    if "completed" in data:
        task.completed = bool(data["completed"])

    # Update deadline
    if "deadline" in data:
        if data["deadline"]:
            try:
                task.deadline = datetime.fromisoformat(
                    data["deadline"].replace("Z", "+00:00")
                )
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
        "message": "Xóa công việc thành công"
    }), 200