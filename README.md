# Expense Tracker API

A Flask and SQLAlchemy backend for managing users and their expenses.

## Project responsibilities

This branch contains the schemas, automated tests, and documentation for the
Expense Tracker project. The application models, routes, and migrations remain
owned by the relevant team members.

## Requirements

- Python 3.12 or newer
- Flask and SQLAlchemy dependencies from `requirements.txt`

## Setup

Create and activate a virtual environment, then install the dependencies:

```bash
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

Create the database using the existing migration:

```bash
flask --app app db upgrade
```

To load the development records:

```bash
python seed.py
```

Start the Flask application:

```bash
flask --app app run --port 5555
```

The application uses `sqlite:///app.db` by default. Set `DATABASE_URI` in a
`.env` file to use another database. Set `SECRET_KEY` to a private value when
running outside local development.

## Schemas

The schema definitions are in `schemas.py` and are intended to keep API
serialization consistent with the SQLAlchemy models.

### User response

```json
{
  "id": 1,
  "username": "amina",
  "email": "amina@example.com"
}
```

The password hash is never included in serialized user data.

### Expense response

```json
{
	"id": 1,
	"title": "Groceries",
	"amount": 54.3,
	"category": "Food",
	"note": "Weekly shop",
	"created_at": "2026-09-10T12:00:00",
	"user_id": 1
}
```

`ExpenseCreateSchema` accepts `title`, `amount`, `category`, and an optional
`note`. IDs, timestamps, and the owning user ID are assigned by the database
or authenticated application flow.

### Authentication payloads

Registration accepts `username`, `email`, and `password`. Login accepts
`email` and `password`. Both user responses expose only `id`, `username`, and
`email`; password hashes and submitted passwords are never serialized.

The auth branch returns these public user fields from `POST /register`,
`POST /login`, and `GET /me`. Login additionally returns an `access_token`.

## Testing

Run the complete independent test suite from the project root:

```bash
python -m pytest -q
```

The tests use an in-memory SQLite database. They cover password hashing and
authentication, model validation, user-expense relationships, cascade delete,
schema serialization, schema input validation, and the `/register`, `/login`,
and `/me` authentication data flow. They do not require the development
database or seeded records.
