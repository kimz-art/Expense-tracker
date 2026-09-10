import pytest

from models import Expense, User


def make_user():
    user = User(username='expense-owner')
    user.password_hash = 'TestPassword123'
    return user


def test_expense_accepts_valid_values(database):
    user = make_user()
    expense = Expense(
        title='Groceries',
        amount=54.30,
        category='Food',
        note='Weekly shop',
        user=user,
    )

    database.session.add(expense)
    database.session.commit()

    assert expense.id is not None
    assert expense.user.username == 'expense-owner'


def test_expense_rejects_non_positive_amount(database):
    with pytest.raises(ValueError, match='Amount must be a positive number'):
        Expense(title='Invalid', amount=0, category='Food', user_id=1)


def test_expense_rejects_empty_title(database):
    with pytest.raises(ValueError, match='Title cannot be empty'):
        Expense(title='   ', amount=10, category='Food', user_id=1)


def test_expense_rejects_empty_category(database):
    with pytest.raises(ValueError, match='Category cannot be empty'):
        Expense(title='Lunch', amount=10, category='  ', user_id=1)
