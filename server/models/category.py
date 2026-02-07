from .db import db

class Category(db.Model):
    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), nullable=False)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )

    is_deleted = db.Column(db.Boolean, default=False, nullable=False) # true: đã xóa, false: đang hoạt động
    user = db.relationship('User', backref='categories')

    __table_args__ = (
        db.UniqueConstraint(
            'user_id',
            'category_name',
            'is_deleted',
            name='uq_user_category_active'
        ),
    )