import pytest

from models import User


def test_user_hashes_password_and_authenticates(database):
    user = User(username='test-user', email='test@example.com')
    user.password_hash = 'TestPassword123'

    assert user._password_hash != 'TestPassword123'
    assert user.authenticate('TestPassword123') is True
    assert user.authenticate('WrongPassword') is False


def test_password_hash_cannot_be_read(database):
    user = User(username='test-user', email='test@example.com')
    user.password_hash = 'TestPassword123'

    with pytest.raises(AttributeError, match='not a readable attribute'):
        _ = user.password_hash


def test_username_cannot_be_empty(database):
    with pytest.raises(ValueError, match='Username cannot be empty'):
        User(username='   ', email='test@example.com')


def test_email_must_be_valid(database):
    with pytest.raises(ValueError, match='A valid email is required'):
        User(username='test-user', email='invalid-email')
