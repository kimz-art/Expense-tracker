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
