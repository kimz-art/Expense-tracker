from app import app, db
from models import User, Expense

with app.app_context():
    db.drop_all()
    db.create_all()

    amina = User(username='amina', email='amina@example.com')
    amina.password_hash = 'password123'
    brian = User(username='brian', email='brian@example.com')
    brian.password_hash = 'password456'
    db.session.add_all([amina, brian])
    db.session.commit()

    expenses = [
        Expense(title='Groceries', amount=54.30, category='Food', note='Weekly shop', user_id=amina.id),
        Expense(title='Uber to airport', amount=22.00, category='Transport', user_id=amina.id),
        Expense(title='Netflix', amount=15.99, category='Subscriptions', user_id=amina.id),
        Expense(title='Gym membership', amount=40.00, category='Health', user_id=brian.id),
        Expense(title='Coffee', amount=4.50, category='Food', user_id=brian.id),
    ]
    db.session.add_all(expenses)
    db.session.commit()
    print(f'Seeded 2 users and {len(expenses)} expenses.')
