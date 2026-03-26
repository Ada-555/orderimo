"""Test settings — uses in-memory SQLite, no external dependencies."""

from orderimo.settings import *  # noqa

# Force in-memory SQLite for all test runs
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
