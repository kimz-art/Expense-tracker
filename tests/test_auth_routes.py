import pytest

from app import app
from extensions import db
from models import User


@pytest.fixture()
def client(database):
    return app.test_client()


def test_register_returns_public_user_data(client):
    response = client.post('/register', json={
        'username': 'route-user',
        'email': 'route@example.com',
        'password': 'TestPassword123',
    })

    assert response.status_code == 201
    assert response.json['user'] == {
        'id': 1,
        'username': 'route-user',
        'email': 'route@example.com',
    }
    assert 'password' not in response.json['user']
    assert 'password_hash' not in response.json['user']


def test_login_returns_token_and_public_user_data(client, database):
    user = User(username='login-user', email='login@example.com')
    user.password_hash = 'TestPassword123'
    database.session.add(user)
    database.session.commit()

    response = client.post('/login', json={
        'email': 'login@example.com',
        'password': 'TestPassword123',
    })

    assert response.status_code == 200
    assert response.json['access_token']
    assert response.json['user'] == {
        'id': user.id,
        'username': 'login-user',
        'email': 'login@example.com',
    }


def test_me_returns_authenticated_public_user_data(client, database):
    user = User(username='me-user', email='me@example.com')
    user.password_hash = 'TestPassword123'
    database.session.add(user)
    database.session.commit()

    login_response = client.post('/login', json={
        'email': 'me@example.com',
        'password': 'TestPassword123',
    })
    token = login_response.json['access_token']

    response = client.get('/me', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 200
    assert response.json == {
        'id': user.id,
        'username': 'me-user',
        'email': 'me@example.com',
    }


def test_auth_routes_reject_incomplete_credentials(client):
    register = client.post('/register', json={'username': 'missing-email'})
    login = client.post('/login', json={'email': 'missing@example.com'})

    assert register.status_code == 400
    assert login.status_code == 400


def test_me_rejects_missing_and_invalid_tokens(client, database):
    assert client.get('/me').status_code == 401
    response = client.get(
        '/me', headers={'Authorization': 'Bearer definitely-invalid'}
    )

    assert response.status_code == 401
    assert response.json['error'] == 'Invalid token'
