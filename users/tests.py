"""Testy aplikacji users.

Poziomy testów:
- UserModelUnitTest  – JEDNOSTKOWE (logika modelu w izolacji od HTTP/DB),
- AuthFunctionalTest – FUNKCJONALNE (logowanie i rejestracja przez warstwę HTTP).
"""
from django.test import TestCase
from django.urls import reverse

from users.models import User


class UserModelUnitTest(TestCase):
    """JEDNOSTKOWE: metody i wartości domyślne modelu User."""

    def test_default_role_is_worker(self):
        self.assertEqual(User(username="x").role, User.Role.WORKER)

    def test_role_helper_methods(self):
        self.assertTrue(User(username="a", role=User.Role.ADMIN).is_admin())
        self.assertTrue(User(username="m", role=User.Role.MANAGER).is_manager())
        self.assertTrue(User(username="w", role=User.Role.WORKER).is_worker())
        self.assertFalse(User(username="w", role=User.Role.WORKER).is_admin())

    def test_str_returns_username(self):
        self.assertEqual(str(User(username="kowalski")), "kowalski")


class AuthFunctionalTest(TestCase):
    """FUNKCJONALNE: dostęp wymaga logowania, rejestracja tworzy konto."""

    def test_protected_view_redirects_anonymous_to_login(self):
        resp = self.client.get(reverse("task-list"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/login/", resp.url)

    def test_register_creates_worker_and_authenticates(self):
        resp = self.client.post(reverse("register"), {
            "username": "nowy",
            "password1": "TrudneHaslo123",
            "password2": "TrudneHaslo123",
        })
        self.assertEqual(resp.status_code, 302)
        user = User.objects.get(username="nowy")
        self.assertEqual(user.role, User.Role.WORKER)
        self.assertIn("_auth_user_id", self.client.session)
