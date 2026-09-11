# Schema Integration Notes

Route owners can use the shared schema instances from `schemas.py` when wiring
responses and request validation:

```python
from schemas import expense_create_schema, expense_schema, expenses_schema

payload = expense_create_schema.load(request.json)
response_body = expense_schema.dump(expense)
list_body = expenses_schema.dump(expenses)
```

`UserSchema` intentionally serializes only the public user identifier,
username, and email. It must not expose `_password_hash`.

Auth route owners can use the authentication schemas as follows:

```python
from schemas import auth_user_schema, login_schema, register_schema

registration = register_schema.load(request.json)
credentials = login_schema.load(request.json)
user_body = auth_user_schema.dump(user)
```

`RegisterSchema` accepts `username`, `email`, and `password`. `LoginSchema`
accepts `email` and `password`. Password fields are load-only and cannot be
serialized into a response.

`ExpenseCreateSchema` validates client-supplied fields. The authenticated user
ID should be assigned by the route or service layer rather than accepted from
untrusted request data. `ExpenseSchema` includes `user_id` for response data.

These notes describe the current model and auth branch schema contract. If the
team changes field names or authentication behavior, update the schema tests
and README in the same pull request.
