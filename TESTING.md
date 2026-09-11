# Testing Guide

## Scope

This test suite checks the current `User` and `Expense` model behavior, schema
contracts, authentication routes, and expense resource routes.

## Test layout

- `tests/test_user_model.py` checks password hashing, authentication, email,
  and user validation.
- `tests/test_expense_model.py` checks valid persistence and expense field
  validation.
- `tests/test_relationships.py` checks ownership and cascade deletion.
- `tests/test_schemas.py` checks serialization, input validation, and server-
  owned expense fields.
- `tests/test_auth_routes.py` checks registration, login, `/me`, and JWT error
  responses.
- `tests/test_expense_routes.py` checks JWT-required expense CRUD, pagination,
  ownership protection, server-owned IDs, and invalid updates.
- `tests/conftest.py` provides an isolated in-memory SQLite database and a
  dedicated JWT secret for each test run.

## Running tests

From the repository root:

```bash
python -m pytest -q
```

No real account password, production database, or seeded data is required.
Test passwords are dummy values created inside each test. The suite uses bearer
tokens and does not depend on the seeded development database.

The model tests target the shared model contract from `feature/models` and
`feature/auth`. The route tests target the current resource implementation
from `feature/resource-crud` after it is merged into the integration branch.
