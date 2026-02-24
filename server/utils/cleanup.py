from datetime import datetime, timedelta
from models import db
from models.user import User
from models.category import Category
from models.task import Task

def permanently_delete_users():

    threshold = datetime.utcnow() - timedelta(days=15)

    users = User.query.filter(
        User.is_deleted == True,
        User.deleted_at <= threshold
    ).all()

    for user in users:

        # ===== Lấy category của user =====
        categories = Category.query.filter_by(user_id=user.id).all()

        for category in categories:

            # ===== Xóa task thuộc category =====
            Task.query.filter_by(category_id=category.id).delete()

            # ===== Xóa category =====
            db.session.delete(category)

        # ===== Xóa user =====
        db.session.delete(user)

    db.session.commit()