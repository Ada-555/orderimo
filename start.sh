#!/bin/bash
# Plurino startup script — activates venv and runs the dev server

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/venv/bin/activate"

cd "$SCRIPT_DIR"

# Ensure migrations are applied
python manage.py migrate --run-syncdb

# Run tests first
echo "Running tests..."
python -m pytest tests/ -q --tb=short || { echo "Tests failed — fix before continuing"; exit 1; }

# Start dev server
echo "Starting Plurino dev server on 0.0.0.0:8000..."
python manage.py runserver 0.0.0.0:8000
