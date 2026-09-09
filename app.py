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
