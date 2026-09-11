# Schema Integration Notes

Route owners can use the shared schema instances from `schemas.py` when wiring
responses and request validation:

```python
from schemas import (
	expense_create_schema,
	expense_schema,
	expense_update_schema,
	expenses_schema,
)

payload = expense_create_schema.load(request.json)
response_body = expense_schema.dump(expense)
list_body = expenses_schema.dump(expenses)
changes = expense_update_schema.load(request.json)
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

The route contract tested by `tests/test_auth_routes.py` is:

- `POST /register` returns status `201` and a public `user` object.
- `POST /login` returns status `200`, an `access_token`, and a public `user`.
- `GET /me` returns status `200` and the authenticated public user.

Each public user object contains only `id`, `username`, and `email`.

`ExpenseCreateSchema` and `ExpenseUpdateSchema` validate client-supplied
fields. The authenticated user ID should be assigned by the route or service
layer rather than accepted from untrusted request data. `ExpenseSchema`
includes `user_id` and `created_at` for response data only. The current
resource route uses `expense_schema.load` for creation, which also rejects
those server-owned fields.

Expense list responses should serialize the paginated items with
`expenses_schema` and preserve the pagination metadata returned by the route.

These notes describe the current model and auth branch schema contract. If the
team changes field names or authentication behavior, update the schema tests
and README in the same pull request.
