"""
All Flask extension objects live here, uninitialized.
Both app.py and models.py import from HERE instead of from each other,
which avoids circular imports entirely.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_marshmallow import Marshmallow
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
ma = Marshmallow()
cors = CORS()