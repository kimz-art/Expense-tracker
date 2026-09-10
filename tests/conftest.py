import pytest

from app import app
from extensions import db


@pytest.fixture()
def database():
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
    )

    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()
