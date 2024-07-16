from db import db
from flask_login import UserMixin


# model for permissions
class Role(db.Model):
    __tablename__ = 'user_role'

    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(16), nullable=False, unique=True)
    users = db.relationship('User', backref='role', lazy=True)


# model for user
class User(db.Model, UserMixin):
    __tablename__ = 'user_info'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(320), nullable=False, unique=True)
    user_role = db.Column(db.Integer, db.ForeignKey('user_role.id'), nullable=True)

    def has_role(self, role_name):
        return self.role.role_name == role_name
