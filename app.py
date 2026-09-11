import os
from datetime import timedelta
from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from dotenv import load_dotenv
from extensions import db, migrate, bcrypt, ma, cors

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URI', 'sqlite:///app.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change-me')
app.config['JWT_SECRET_KEY'] = os.environ.get(
    'JWT_SECRET_KEY', 'dev-jwt-secret-change-me'
)
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

db.init_app(app)
migrate.init_app(app, db)
bcrypt.init_app(app)
ma.init_app(app)
cors.init_app(app)

jwt = JWTManager(app)

# Import models AFTER extensions are initialized
from models import User, Expense  # noqa: E402,F401
from flask import request, jsonify, session
from marshmallow import ValidationError
from schemas import expense_schema, expenses_schema


def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.get(user_id)


@app.route('/expenses', methods=['GET'])
def get_expenses():
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Unauthorized'}), 401

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    pagination = (
        Expense.query
        .filter_by(user_id=current_user.id)
        .order_by(Expense.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    return jsonify({
        'expenses': expenses_schema.dump(pagination.items),
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page,
        'per_page': pagination.per_page
    }), 200


@app.route('/expenses', methods=['POST'])
def create_expense():
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No input data provided'}), 400

    try:
        validated = expense_schema.load(data)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400

    try:
        new_expense = Expense(
            title=validated['title'],
            amount=validated['amount'],
            category=validated['category'],
            note=validated.get('note'),
            user_id=current_user.id
        )
        db.session.add(new_expense)
        db.session.commit()
    except ValueError as err:
        db.session.rollback()
        return jsonify({'error': str(err)}), 400

    return jsonify(expense_schema.dump(new_expense)), 201


@app.route('/expenses/<int:id>', methods=['PATCH'])
def update_expense(id):
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Unauthorized'}), 401

    expense = Expense.query.get(id)
    if not expense:
        return jsonify({'error': 'Expense not found'}), 404

    if expense.user_id != current_user.id:
        return jsonify({'error': 'Forbidden: you do not own this resource'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No input data provided'}), 400

    try:
        for field in ('title', 'amount', 'category', 'note'):
            if field in data:
                setattr(expense, field, data[field])
        db.session.commit()
    except ValueError as err:
        db.session.rollback()
        return jsonify({'error': str(err)}), 400

    return jsonify(expense_schema.dump(expense)), 200


@app.route('/expenses/<int:id>', methods=['DELETE'])
def delete_expense(id):
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Unauthorized'}), 401

    expense = Expense.query.get(id)
    if not expense:
        return jsonify({'error': 'Expense not found'}), 404

    if expense.user_id != current_user.id:
        return jsonify({'error': 'Forbidden: you do not own this resource'}), 403

    db.session.delete(expense)
    db.session.commit()

    return jsonify({'message': 'Expense deleted successfully'}), 200



# --- JWT custom error handlers ---
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({
        'error': 'Token has expired',
        'message': 'The token you provided has expired. Please log in again.'
    }), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'error': 'Invalid token',
        'message': 'The token you provided is invalid. Please log in again.'
    }), 401


@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        'error': 'authorization_required',
        'message': 'Request does not contain an access token. Please log in.'
    }), 401


# --- Auth routes ---
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({
            'error': 'Username, email, and password are required'
        }), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400

    try:
        new_user = User(username=username, email=email)
        new_user.password_hash = password
        db.session.add(new_user)
        db.session.commit()
    except ValueError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

    return jsonify({
        'message': 'User registered successfully.',
        'user': {
            'id': new_user.id,
            'username': new_user.username,
            'email': new_user.email
        }
    }), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({
            'error': 'Email and password are required'
        }), 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.authenticate(password):
        return jsonify({'error': 'Invalid email or password'}), 401

    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        'message': 'Login successful.',
        'access_token': access_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
    }), 200


@app.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email
    }), 200


if __name__ == '__main__':
    app.run(port=5555, debug=True)


