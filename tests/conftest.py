import pytest

from app import app
from extensions import db


@pytest.fixture()
def database():
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_SECRET_KEY='test-jwt-secret-key-with-at-least-32-bytes',
    )

    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()
