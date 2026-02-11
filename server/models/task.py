
from .db import db

class Task(db.Model):
    __tablename__ = 'task'

    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(200), nullable=False)

    completed = db.Column(db.Boolean, default=False)
    deadline = db.Column(db.DateTime)

    category_id = db.Column(
        db.Integer,
        db.ForeignKey('category.id'),
        nullable=False
    )

    is_deleted = db.Column(db.Boolean, default=False)

    category = db.relationship('Category', backref='tasks')

    __table_args__ = (
        db.UniqueConstraint(
            'category_id',
            'task_name',
            'is_deleted',
            name='unique_active_task_per_category'
        ),
    )