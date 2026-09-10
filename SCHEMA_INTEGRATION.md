# Schema Integration Notes

Route owners can use the shared schema instances from `schemas.py` when wiring
responses and request validation:

```python
from schemas import expense_create_schema, expense_schema, expenses_schema

payload = expense_create_schema.load(request.json)
response_body = expense_schema.dump(expense)
list_body = expenses_schema.dump(expenses)
```

`UserSchema` intentionally serializes only the public user identifier and
username. It must not be changed to expose `_password_hash`.

`ExpenseCreateSchema` validates client-supplied fields. The authenticated user
ID should be assigned by the route or service layer rather than accepted from
untrusted request data. `ExpenseSchema` includes `user_id` for response data.

These notes describe the current model and schema contract. If the team changes
field names or authentication behavior, update the schema tests and README in
the same pull request.
