from models import Expense, User


def test_user_expenses_relationship_returns_owned_expenses(database):
    user = User(username='relationship-user')
    user.password_hash = 'TestPassword123'
    user.expenses = [
        Expense(title='Coffee', amount=4.50, category='Food'),
        Expense(title='Bus fare', amount=2.00, category='Transport'),
    ]

    database.session.add(user)
    database.session.commit()

    assert [expense.title for expense in user.expenses] == ['Coffee', 'Bus fare']
    assert all(expense.user_id == user.id for expense in user.expenses)


def test_deleting_user_deletes_owned_expenses(database):
    user = User(username='delete-user')
    user.password_hash = 'TestPassword123'
    user.expenses = [Expense(title='Coffee', amount=4.50, category='Food')]
    database.session.add(user)
    database.session.commit()

    database.session.delete(user)
    database.session.commit()

    assert database.session.query(Expense).count() == 0
