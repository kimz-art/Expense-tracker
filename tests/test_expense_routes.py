import pytest

from app import app


@pytest.fixture()
def client(database):
    return app.test_client()


def register_and_login(client, username, email):
    client.post('/register', json={
        'username': username,
        'email': email,
        'password': 'TestPassword123',
    })
    response = client.post('/login', json={
        'email': email,
        'password': 'TestPassword123',
    })
    return {'Authorization': f"Bearer {response.json['access_token']}"}


def expense_payload(title='Lunch', amount=15.25, category='Food'):
    return {
        'title': title,
        'amount': amount,
        'category': category,
        'note': 'Team meal',
    }


def test_expense_routes_require_authentication(client):
    assert client.get('/expenses').status_code == 401
    assert client.post('/expenses', json=expense_payload()).status_code == 401


def test_expense_create_list_update_and_delete_flow(client):
    headers = register_and_login(client, 'expense-user', 'expense@example.com')

    first = client.post('/expenses', json=expense_payload(), headers=headers)
    second = client.post(
        '/expenses',
        json=expense_payload('Bus fare', 4.50, 'Transport'),
        headers=headers,
    )

    assert first.status_code == 201
    assert second.status_code == 201
    assert 'user_id' in first.json
    assert 'created_at' in first.json

    listing = client.get('/expenses?page=1&per_page=1', headers=headers)
    assert listing.status_code == 200
    assert listing.json['total'] == 2
    assert listing.json['pages'] == 2
    assert listing.json['current_page'] == 1
    assert listing.json['per_page'] == 1

    expense_id = first.json['id']
    updated = client.patch(
        f'/expenses/{expense_id}',
        json={'amount': 20, 'note': 'Updated meal'},
        headers=headers,
    )
    assert updated.status_code == 200
    assert updated.json['amount'] == 20.0
    assert updated.json['note'] == 'Updated meal'

    deleted = client.delete(f'/expenses/{expense_id}', headers=headers)
    assert deleted.status_code == 200
    assert client.get(f'/expenses/{expense_id}', headers=headers).status_code == 404


def test_expense_routes_protect_user_ownership(client):
    owner_headers = register_and_login(client, 'owner', 'owner@example.com')
    other_headers = register_and_login(client, 'other', 'other@example.com')

    created = client.post(
        '/expenses', json=expense_payload(), headers=owner_headers
    )
    expense_id = created.json['id']

    update = client.patch(
        f'/expenses/{expense_id}',
        json={'amount': 99},
        headers=other_headers,
    )
    delete = client.delete(f'/expenses/{expense_id}', headers=other_headers)

    assert update.status_code == 403
    assert delete.status_code == 403


def test_expense_create_rejects_client_owned_user_id(client):
    headers = register_and_login(client, 'trusted-user', 'trusted@example.com')

    response = client.post(
        '/expenses',
        json={**expense_payload(), 'user_id': 999},
        headers=headers,
    )

    assert response.status_code == 400
    assert 'user_id' in response.json['errors']


def test_expense_update_rejects_invalid_model_values(client):
    headers = register_and_login(client, 'validation-user', 'validation@example.com')
    created = client.post(
        '/expenses', json=expense_payload(), headers=headers
    )

    response = client.patch(
        f"/expenses/{created.json['id']}",
        json={'amount': 0},
        headers=headers,
    )

    assert response.status_code == 400
    assert response.json['error'] == 'Amount must be a positive number'
