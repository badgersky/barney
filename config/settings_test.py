"""Ustawienia do szybkiego, lokalnego uruchamiania testów na SQLite (w pamięci),
bez potrzeby stawiania PostgreSQL. Użycie:

    DJANGO_SETTINGS_MODULE=config.settings_test python manage.py test

W CI oraz w Dockerze testy uruchamiane są na PostgreSQL (config.settings).
"""
from .settings import *  # noqa

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
