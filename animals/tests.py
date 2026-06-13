"""Testy aplikacji animals (zwierzęta, gatunki, historia notatek).

Poziomy testów:
- AnimalModelUnitTest – JEDNOSTKOWE,
- AnimalModuleTest    – MODUŁOWE (model + formularz + relacje, w tym NFR-05),
- AnimalFunctionalTest – FUNKCJONALNE (widoki, role, dodawanie notatek).
"""
from datetime import timedelta

from django.db.models import ProtectedError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from users.models import User
from buildings.models import Building
from animals.models import Animal, Species, AnimalNote
from animals.forms import AnimalForm


def goat():
    species, _ = Species.objects.get_or_create(name="Koza")
    return species


class AnimalModelUnitTest(TestCase):
    """JEDNOSTKOWE: reprezentacje tekstowe i metoda latest_note."""

    def test_str_prefers_name_then_identifier(self):
        sp = goat()
        self.assertIn("Bella", str(Animal(name="Bella", identifier="PL1", species=sp)))
        self.assertIn("PL2", str(Animal(name="", identifier="PL2", species=sp)))

    def test_species_str(self):
        self.assertEqual(str(Species(name="Owca")), "Owca")

    def test_latest_note_none_when_empty(self):
        a = Animal.objects.create(identifier="N0", species=goat())
        self.assertIsNone(a.latest_note())


class AnimalModuleTest(TestCase):
    """MODUŁOWE: walidacja formularza, kasowanie powiązań, historia notatek."""

    def test_form_requires_identifier(self):
        form = AnimalForm(data={"identifier": "", "species": goat().id,
                                "sex": "F", "health_status": "HEALTHY"})
        self.assertFalse(form.is_valid())
        self.assertIn("identifier", form.errors)

    def test_form_valid_minimal(self):
        form = AnimalForm(data={"name": "", "identifier": "X1", "species": goat().id,
                                "sex": "F", "building": "", "health_status": "HEALTHY",
                                "birth_date": ""})
        self.assertTrue(form.is_valid(), form.errors)

    def test_deleting_location_keeps_animal_nfr05(self):
        b = Building.objects.create(name="Stajnia", type=Building.Type.STABLE)
        a = Animal.objects.create(identifier="K1", species=goat(), building=b)
        b.delete()
        a.refresh_from_db()
        self.assertTrue(Animal.objects.filter(pk=a.pk).exists())
        self.assertIsNone(a.building)

    def test_species_protected_when_in_use(self):
        sp = Species.objects.create(name="Lama")
        Animal.objects.create(identifier="L1", species=sp)
        with self.assertRaises(ProtectedError):
            sp.delete()

    def test_note_history_order_and_latest(self):
        a = Animal.objects.create(identifier="H1", species=goat())
        old = AnimalNote.objects.create(animal=a, content="stara")
        AnimalNote.objects.filter(pk=old.pk).update(
            created_at=timezone.now() - timedelta(hours=1))
        new = AnimalNote.objects.create(animal=a, content="nowa")
        self.assertEqual(list(a.note_history.all())[0], new)
        self.assertEqual(a.latest_note(), new)


class AnimalFunctionalTest(TestCase):
    """FUNKCJONALNE: dostęp, renderowanie listy, role, notatki przez HTTP."""

    @classmethod
    def setUpTestData(cls):
        cls.manager = User.objects.create_user("mgr", password="pass12345", role=User.Role.MANAGER)
        cls.worker = User.objects.create_user("wrk", password="pass12345", role=User.Role.WORKER)
        cls.sp = goat()

    def test_list_requires_login(self):
        self.assertEqual(self.client.get(reverse("animal-list")).status_code, 302)

    def test_list_renders_animals(self):
        Animal.objects.create(identifier="A1", species=self.sp, name="Bella")
        self.client.login(username="mgr", password="pass12345")
        self.assertContains(self.client.get(reverse("animal-list")), "Bella")

    def test_worker_cannot_create(self):
        self.client.login(username="wrk", password="pass12345")
        self.assertEqual(self.client.get(reverse("animal-create")).status_code, 403)

    def test_manager_can_create(self):
        self.client.login(username="mgr", password="pass12345")
        resp = self.client.post(reverse("animal-create"), {
            "name": "Rogal", "identifier": "R1", "species": self.sp.id,
            "sex": "M", "building": "", "health_status": "HEALTHY", "birth_date": ""})
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Animal.objects.filter(identifier="R1").exists())

    def test_add_note_appears_in_history_with_author(self):
        a = Animal.objects.create(identifier="A2", species=self.sp)
        self.client.login(username="mgr", password="pass12345")
        self.client.post(reverse("animal-note-create", args=[a.pk]), {"content": "Zdrowa"})
        a.refresh_from_db()
        self.assertEqual(a.note_history.count(), 1)
        self.assertEqual(a.note_history.first().author, self.manager)
        self.assertContains(self.client.get(reverse("animal-detail", args=[a.pk])), "Zdrowa")
