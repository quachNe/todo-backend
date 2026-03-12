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

    user = db.relationship('User', backref='categories')

    __table_args__ = (
        db.UniqueConstraint(
            'user_id',
            'category_name',
            name='uq_user_category'
        ),
    )