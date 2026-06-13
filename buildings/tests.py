"""Testy aplikacji buildings (lokalizacje + historia notatek).

Poziomy testów:
- BuildingModelUnitTest – JEDNOSTKOWE,
- BuildingModuleTest    – MODUŁOWE,
- BuildingFunctionalTest – FUNKCJONALNE.
"""
from django.test import TestCase
from django.urls import reverse

from users.models import User
from buildings.models import Building, BuildingNote
from animals.models import Animal, Species


def goat():
    species, _ = Species.objects.get_or_create(name="Koza")
    return species


class BuildingModelUnitTest(TestCase):
    """JEDNOSTKOWE."""

    def test_str_contains_type_label(self):
        b = Building(name="Boks 1", type=Building.Type.STALL)
        self.assertIn("Boks 1", str(b))
        self.assertIn("Boks", str(b))

    def test_latest_note_none_when_empty(self):
        b = Building.objects.create(name="L", type=Building.Type.PEN)
        self.assertIsNone(b.latest_note())


class BuildingModuleTest(TestCase):
    """MODUŁOWE: notatki i zachowanie przy kasowaniu (NFR-05)."""

    def test_note_history_records_entries(self):
        b = Building.objects.create(name="Zagroda", type=Building.Type.PEN)
        BuildingNote.objects.create(building=b, content="Wymiana ściółki")
        self.assertEqual(b.note_history.count(), 1)
        self.assertEqual(b.latest_note().content, "Wymiana ściółki")

    def test_delete_location_does_not_delete_animals(self):
        b = Building.objects.create(name="Stajnia", type=Building.Type.STABLE)
        sp = goat()
        a = Animal.objects.create(identifier="B1", species=sp, building=b)
        b.delete()
        a.refresh_from_db()
        self.assertTrue(Animal.objects.filter(pk=a.pk).exists())
        self.assertIsNone(a.building)


class BuildingFunctionalTest(TestCase):
    """FUNKCJONALNE."""

    @classmethod
    def setUpTestData(cls):
        cls.manager = User.objects.create_user("mgr", password="pass12345", role=User.Role.MANAGER)
        cls.worker = User.objects.create_user("wrk", password="pass12345", role=User.Role.WORKER)

    def test_list_requires_login(self):
        self.assertEqual(self.client.get(reverse("building-list")).status_code, 302)

    def test_manager_can_create_location(self):
        self.client.login(username="mgr", password="pass12345")
        resp = self.client.post(reverse("building-create"),
                                {"name": "Wybieg A", "type": "PADDOCK"})
        self.assertEqual(resp.status_code, 302)
        b = Building.objects.get(name="Wybieg A")
        self.assertEqual(b.created_by, self.manager)

    def test_worker_cannot_create_location(self):
        self.client.login(username="wrk", password="pass12345")
        self.assertEqual(self.client.get(reverse("building-create")).status_code, 403)

    def test_add_note_visible_in_detail(self):
        b = Building.objects.create(name="Boks 7", type=Building.Type.STALL)
        self.client.login(username="mgr", password="pass12345")
        self.client.post(reverse("building-note-create", args=[b.pk]), {"content": "Naprawiono bramkę"})
        self.assertEqual(b.note_history.count(), 1)
        self.assertContains(self.client.get(reverse("building-detail", args=[b.pk])), "Naprawiono bramkę")
