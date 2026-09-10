# Testing Guide

## Scope

This test suite is intentionally independent of the route implementation. It
checks the current `User` and `Expense` model behavior and the schema contracts
that routes can use when they are added or updated.

## Test layout

- `tests/test_user_model.py` checks password hashing, authentication, and user
  validation.
- `tests/test_expense_model.py` checks valid persistence and expense field
  validation.
- `tests/test_relationships.py` checks ownership and cascade deletion.
- `tests/test_schemas.py` checks JSON serialization and input validation.
- `tests/conftest.py` provides an isolated in-memory SQLite database.

## Running tests

From the repository root:

```bash
python -m pytest -q
```

No real account password, production database, or seeded data is required.
Test passwords are dummy values created inside each test.
