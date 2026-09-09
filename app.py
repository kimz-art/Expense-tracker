import os
from flask import Flask
from dotenv import load_dotenv
from extensions import db, migrate, bcrypt, ma, cors

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change-me')

db.init_app(app)
migrate.init_app(app, db)
bcrypt.init_app(app)
ma.init_app(app)
cors.init_app(app)

from models import User, Expense  # noqa: E402,F401
from flask import request, jsonify, session
from marshmallow import ValidationError
from schemas import expense_schema, expenses_schema


def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.get(user_id)


@app.route('/expenses', methods=['GET'])
def get_expenses():
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Unauthorized'}), 401

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    pagination = (
        Expense.query
        .filter_by(user_id=current_user.id)
        .order_by(Expense.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    return jsonify({
        'expenses': expenses_schema.dump(pagination.items),
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page,
        'per_page': pagination.per_page
    }), 200


@app.route('/expenses', methods=['POST'])
def create_expense():
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No input data provided'}), 400

    try:
        validated = expense_schema.load(data)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400

    try:
        new_expense = Expense(
            title=validated['title'],
            amount=validated['amount'],
            category=validated['category'],
            note=validated.get('note'),
            user_id=current_user.id
        )
        db.session.add(new_expense)
        db.session.commit()
    except ValueError as err:
        db.session.rollback()
        return jsonify({'error': str(err)}), 400

    return jsonify(expense_schema.dump(new_expense)), 201


@app.route('/expenses/<int:id>', methods=['PATCH'])
def update_expense(id):
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Unauthorized'}), 401

    expense = Expense.query.get(id)
    if not expense:
        return jsonify({'error': 'Expense not found'}), 404

    if expense.user_id != current_user.id:
        return jsonify({'error': 'Forbidden: you do not own this resource'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No input data provided'}), 400

    try:
        for field in ('title', 'amount', 'category', 'note'):
            if field in data:
                setattr(expense, field, data[field])
        db.session.commit()
    except ValueError as err:
        db.session.rollback()
        return jsonify({'error': str(err)}), 400

    return jsonify(expense_schema.dump(expense)), 200


@app.route('/expenses/<int:id>', methods=['DELETE'])
def delete_expense(id):
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Unauthorized'}), 401

    expense = Expense.query.get(id)
    if not expense:
        return jsonify({'error': 'Expense not found'}), 404

    if expense.user_id != current_user.id:
        return jsonify({'error': 'Forbidden: you do not own this resource'}), 403

    db.session.delete(expense)
    db.session.commit()

    return jsonify({'message': 'Expense deleted successfully'}), 200


if __name__ == '__main__':
    app.run(port=5555, debug=True)


