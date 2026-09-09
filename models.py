from extensions import db, bcrypt
from sqlalchemy.orm import validates
from sqlalchemy.sql import func


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    _password_hash = db.Column('password_hash', db.String(128), nullable=False)

    expenses = db.relationship('Expense', back_populates='user', cascade='all, delete-orphan')

    @property
    def password_hash(self):
        raise AttributeError('password_hash is not a readable attribute')

    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password)

    @validates('username')
    def validate_username(self, key, value):
        if not value or len(value.strip()) == 0:
            raise ValueError('Username cannot be empty')
        return value

    def __repr__(self):
        return f'<User {self.id}: {self.username}>'


class Expense(db.Model):
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(60), nullable=False)
    note = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, server_default=func.now())

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', back_populates='expenses')

    @validates('title')
    def validate_title(self, key, value):
        if not value or len(value.strip()) == 0:
            raise ValueError('Title cannot be empty')
        return value

    @validates('amount')
    def validate_amount(self, key, value):
        if value is None or value <= 0:
            raise ValueError('Amount must be a positive number')
        return value

    @validates('category')
    def validate_category(self, key, value):
        if not value or len(value.strip()) == 0:
            raise ValueError('Category cannot be empty')
        return value

    def __repr__(self):
        return f'<Expense {self.id}: {self.title} ${self.amount} (user_id={self.user_id})>'
