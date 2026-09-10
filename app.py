import os
from flask import Flask
from dotenv import load_dotenv
from extensions import db, migrate, bcrypt, ma, cors

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change-me')

db.init_app(app)
migrate.init_app(app, db)
bcrypt.init_app(app)
ma.init_app(app)
cors.init_app(app)

from models import User, Expense  # noqa: E402,F401

if __name__ == '__main__':
    app.run(port=5555, debug=True)

from datetime import timedelta
from flask import Flask,request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models import db, bcrypt, User, Expense
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'a_very_long_and_secure_random_jwt_secret_key_32bytes'  # Change this to a random secret key in production

migrate = Migrate(app, db)
db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)

#jwt custom error handlers
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
#Endpoint for user registration
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'error': 'Username, email, and password are required'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400


    new_user = User(username=username, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        'message': 'User registered successfully.',
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email
        }
    }), 201
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401

    access_token = create_access_token(identity=str(user.id))
    return jsonify({
                    "message": "Login successful.",
                    "access_token": access_token,
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email
                    }
                }), 200
@app.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)  # Using session.get for better performance and to avoid deprecation warnings

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({
        "id": user.id,
        'username': user.username,
        'email': user.email
    }), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    app.run(debug=True)