from marshmallow import Schema, fields, validate
from flask_marshmallow import Marshmallow

from models import Expense, User


ma = Marshmallow()


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = False
        include_fk = False
        exclude = ('_password_hash',)

    id = fields.Integer(dump_only=True)
    username = fields.String(required=True, validate=validate.Length(min=1, max=80))
    email = fields.Email(required=True, validate=validate.Length(max=120))


class ExpenseSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Expense
        load_instance = False
        include_fk = True

    id = fields.Integer(dump_only=True)
    title = fields.String(required=True, validate=validate.Length(min=1, max=120))
    amount = fields.Float(required=True, validate=validate.Range(min=0.01))
    category = fields.String(required=True, validate=validate.Length(min=1, max=60))
    note = fields.String(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    user_id = fields.Integer(required=True)


class ExpenseCreateSchema(Schema):
    title = fields.String(required=True, validate=validate.Length(min=1, max=120))
    amount = fields.Float(required=True, validate=validate.Range(min=0.01))
    category = fields.String(required=True, validate=validate.Length(min=1, max=60))
    note = fields.String(allow_none=True)


class RegisterSchema(Schema):
    username = fields.String(required=True, validate=validate.Length(min=1, max=80))
    email = fields.Email(required=True, validate=validate.Length(max=120))
    password = fields.String(required=True, load_only=True, validate=validate.Length(min=1))


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True, validate=validate.Length(min=1))


class AuthUserSchema(Schema):
    id = fields.Integer(required=True)
    username = fields.String(required=True)
    email = fields.Email(required=True)


user_schema = UserSchema()
users_schema = UserSchema(many=True)
expense_schema = ExpenseSchema()
expenses_schema = ExpenseSchema(many=True)
expense_create_schema = ExpenseCreateSchema()
register_schema = RegisterSchema()
login_schema = LoginSchema()
auth_user_schema = AuthUserSchema()
