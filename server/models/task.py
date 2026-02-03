
from .db import db

class Task(db.Model):
    __tablename__ = 'task'

    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(200), nullable=False)

    completed = db.Column(db.Boolean, default=False)
    deadline = db.Column(db.DateTime)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )

    category_id = db.Column(
        db.Integer,
        db.ForeignKey('category.id'),
        nullable=False
    )

    is_deleted = db.Column(db.Boolean, default=False) # true: đã xóa, false: đang hoạt động
    user = db.relationship('User', backref='tasks')
    category = db.relationship('Category', backref='tasks')