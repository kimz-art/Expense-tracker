from extensions import ma
from models import User, Expense


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = False

    id = ma.auto_field(dump_only=True)
    username = ma.auto_field(required=True)


class ExpenseSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Expense
        load_instance = False

    id = ma.auto_field(dump_only=True)
    user_id = ma.auto_field(dump_only=True)      # server sets this never the client
    created_at = ma.auto_field(dump_only=True)
    title = ma.auto_field(required=True)
    amount = ma.auto_field(required=True)
    category = ma.auto_field(required=True)
    note = ma.auto_field(required=False, allow_none=True)


expense_schema = ExpenseSchema()
expenses_schema = ExpenseSchema(many=True)