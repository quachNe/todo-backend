
from .db import db

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)

    completed = db.Column(db.Boolean, default=False)
    deadline = db.Column(db.DateTime)

    user_id = db.Column(db.Integer, nullable=False)
    category_id = db.Column(db.Integer, nullable=False)

    is_deleted = db.Column(db.Boolean, default=False) # true: đã xóa, false: đang hoạt động