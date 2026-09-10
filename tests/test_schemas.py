import pytest
from marshmallow import ValidationError

from models import Expense, User
from schemas import ExpenseCreateSchema, ExpenseSchema, UserSchema


def test_user_schema_does_not_expose_password_hash(database):
    user = User(username='schema-user')
    user.password_hash = 'TestPassword123'
    database.session.add(user)
    database.session.commit()

    payload = UserSchema().dump(user)

    assert payload == {'id': user.id, 'username': 'schema-user'}
    assert 'password_hash' not in payload


def test_expense_schema_serializes_public_fields(database):
    user = User(username='schema-owner')
    user.password_hash = 'TestPassword123'
    expense = Expense(
        title='Train ticket',
        amount=12.5,
        category='Transport',
        note=None,
        user=user,
    )
    database.session.add(expense)
    database.session.commit()

    payload = ExpenseSchema().dump(expense)

    assert payload['id'] == expense.id
    assert payload['title'] == 'Train ticket'
    assert payload['amount'] == 12.5
    assert payload['category'] == 'Transport'
    assert payload['note'] is None
    assert payload['user_id'] == user.id
    assert isinstance(payload['created_at'], str)


def test_expense_create_schema_requires_expected_fields():
    payload = ExpenseCreateSchema().load({
        'title': 'Lunch',
        'amount': 15.25,
        'category': 'Food',
    })

    assert payload == {'title': 'Lunch', 'amount': 15.25, 'category': 'Food'}


def test_expense_create_schema_rejects_invalid_amount():
    with pytest.raises(ValidationError):
        ExpenseCreateSchema().load({
            'title': 'Invalid',
            'amount': 0,
            'category': 'Food',
        })
