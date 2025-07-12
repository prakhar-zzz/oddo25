from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    points = db.Column(db.Integer, default=0)
    is_admin = db.Column(db.Boolean, default=False)

    items = db.relationship('Item', backref='owner', lazy=True)
    swaps = db.relationship('Swap', backref='user', lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))
    type = db.Column(db.String(50))
    size = db.Column(db.String(20))
    condition = db.Column(db.String(50))
    tags = db.Column(db.String(100))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    available = db.Column(db.Boolean, default=True)
    approved = db.Column(db.Boolean, default=False)  # For admin moderation

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    images = db.relationship('Image', backref='item', lazy=True)
    swaps = db.relationship('Swap', backref='item', lazy=True)

    def __repr__(self):
        return f"<Item {self.title}>"


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(200), nullable=False)  # or file path
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)

    def __repr__(self):
        return f"<Image {self.image_url}>"


class Swap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    swap_type = db.Column(db.String(20))  # 'swap' or 'points'
    status = db.Column(db.String(20), default='pending')  # pending, completed, declined
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Swap {self.id} - {self.swap_type}>"


# Optional: use admin flag in User instead of separate Admin table
# class Admin(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     permissions = db.Column(db.String(100))
