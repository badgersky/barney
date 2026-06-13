"""Testy aplikacji tasks (zadania, typy, przypomnienia).

Poziomy testów:
- TaskUnitTest       – JEDNOSTKOWE (logika statusów liczonych z terminu),
- TaskModuleTest     – MODUŁOWE (formularz + relacje + dane zasiane migracjami),
- TaskFunctionalTest – FUNKCJONALNE (role, przepływ dodawania i podglądu).
"""
from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from users.models import User
from animals.models import Animal, Species
from buildings.models import Building
from tasks.models import Task, TaskType, Reminder
from tasks.forms import TaskForm


def goat():
    species, _ = Species.objects.get_or_create(name="Koza")
    return species


class TaskUnitTest(TestCase):
    """JEDNOSTKOWE: display_status / status_code / target bez bazy."""

    def test_done_and_cancelled_labels(self):
        self.assertEqual(Task(status=Task.Status.DONE).display_status(), "Wykonane")
        self.assertEqual(Task(status=Task.Status.CANCELLED).display_status(), "Anulowane")

    def test_planned_without_due_date(self):
        self.assertEqual(Task(status=Task.Status.PLANNED).display_status(), "Zaplanowane")

    def test_overdue_when_due_date_in_past(self):
        t = Task(status=Task.Status.PLANNED, due_date=timezone.localdate() - timedelta(days=1))
        self.assertEqual(t.display_status(), "Zaległe")
        self.assertEqual(t.status_code(), "overdue")

    def test_upcoming_when_due_soon(self):
        t = Task(status=Task.Status.PLANNED, due_date=timezone.localdate() + timedelta(days=2))
        self.assertEqual(t.display_status(), "Nadchodzące")

    def test_far_future_stays_planned(self):
        t = Task(status=Task.Status.PLANNED, due_date=timezone.localdate() + timedelta(days=30))
        self.assertEqual(t.display_status(), "Zaplanowane")

    def test_target_none_when_unset(self):
        self.assertIsNone(Task().target)


class TaskModuleTest(TestCase):
    """MODUŁOWE: walidacja celu zadania, relacje, dane referencyjne."""

    def setUp(self):
        self.sp = goat()
        self.tt, _ = TaskType.objects.get_or_create(
            name="Leczenie",
            category=TaskType.Category.HEALTH
        )
        self.animal = Animal.objects.create(identifier="C1", species=self.sp)
        self.building = Building.objects.create(name="Boks", type=Building.Type.STALL)

    def _data(self, **kw):
        data = {"title": "T", "description": "", "task_type": self.tt.id,
                "assigned_to": "", "animal": "", "building": "",
                "status": "PLANNED", "due_date": ""}
        data.update(kw)
        return data

    def test_form_invalid_without_target(self):
        self.assertFalse(TaskForm(data=self._data()).is_valid())

    def test_form_valid_with_animal(self):
        form = TaskForm(data=self._data(animal=self.animal.id))
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_valid_with_building(self):
        form = TaskForm(data=self._data(building=self.building.id))
        self.assertTrue(form.is_valid(), form.errors)

    def test_target_prefers_animal_then_building(self):
        t1 = Task.objects.create(title="A", task_type=self.tt, animal=self.animal)
        self.assertEqual(t1.target, self.animal)
        t2 = Task.objects.create(title="B", task_type=self.tt, building=self.building)
        self.assertEqual(t2.target, self.building)

    def test_reminder_related_to_task(self):
        t = Task.objects.create(title="R", animal=self.animal)
        Reminder.objects.create(task=t, date=timezone.localdate(), message="m")
        self.assertEqual(t.reminders.count(), 1)

    def test_seed_reference_data_present(self):
        self.assertTrue(Species.objects.exists())
        self.assertTrue(TaskType.objects.filter(category=TaskType.Category.HEALTH).exists())


class TaskFunctionalTest(TestCase):
    """FUNKCJONALNE: role, przepływ dodawania zadania, podgląd, przypomnienia."""

    @classmethod
    def setUpTestData(cls):
        cls.manager = User.objects.create_user("mgr", password="pass12345", role=User.Role.MANAGER)
        cls.worker = User.objects.create_user("wrk", password="pass12345", role=User.Role.WORKER)
        cls.other = User.objects.create_user("wrk2", password="pass12345", role=User.Role.WORKER)
        cls.sp = goat()
        cls.tt, _ = TaskType.objects.get_or_create(
            name="Leczenie",
            category=TaskType.Category.HEALTH
        )
        cls.animal = Animal.objects.create(identifier="F1", species=cls.sp)

    def test_worker_sees_only_assigned_tasks(self):
        Task.objects.create(title="moje", assigned_to=self.worker, animal=self.animal, task_type=self.tt)
        Task.objects.create(title="cudze", assigned_to=self.other, animal=self.animal, task_type=self.tt)
        self.client.login(username="wrk", password="pass12345")
        resp = self.client.get(reverse("task-list"))
        self.assertContains(resp, "moje")
        self.assertNotContains(resp, "cudze")

    def test_manager_sees_all_tasks(self):
        Task.objects.create(title="t1", assigned_to=self.worker, animal=self.animal, task_type=self.tt)
        self.client.login(username="mgr", password="pass12345")
        self.assertContains(self.client.get(reverse("task-list")), "t1")

    def test_create_redirects_to_detail(self):
        self.client.login(username="mgr", password="pass12345")
        resp = self.client.post(reverse("task-create"), {
            "title": "Nowe", "description": "", "task_type": self.tt.id,
            "assigned_to": self.worker.id, "animal": self.animal.id,
            "building": "", "status": "PLANNED", "due_date": ""})
        t = Task.objects.get(title="Nowe")
        self.assertRedirects(resp, reverse("task-detail", args=[t.pk]))

    def test_create_rejected_without_target(self):
        self.client.login(username="mgr", password="pass12345")
        resp = self.client.post(reverse("task-create"), {
            "title": "Bez celu", "description": "", "task_type": self.tt.id,
            "assigned_to": "", "animal": "", "building": "",
            "status": "PLANNED", "due_date": ""})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "zwierzęcia albo lokalizacji")
        self.assertFalse(Task.objects.filter(title="Bez celu").exists())

    def test_worker_cannot_create(self):
        self.client.login(username="wrk", password="pass12345")
        self.assertEqual(self.client.get(reverse("task-create")).status_code, 403)

    def test_worker_can_update_own_task_status(self):
        t = Task.objects.create(title="s", assigned_to=self.worker, animal=self.animal, task_type=self.tt)
        self.client.login(username="wrk", password="pass12345")
        resp = self.client.post(reverse("task-status", args=[t.pk]), {"status": "DONE"})
        self.assertEqual(resp.status_code, 302)
        t.refresh_from_db()
        self.assertEqual(t.status, Task.Status.DONE)

    def test_reminder_added_and_visible_in_detail(self):
        t = Task.objects.create(title="r", assigned_to=self.worker, animal=self.animal, task_type=self.tt)
        self.client.login(username="mgr", password="pass12345")
        self.client.post(reverse("reminder-create", args=[t.pk]), {"date": "2030-01-01", "message": "Pamiętaj"})
        self.assertEqual(t.reminders.count(), 1)
        self.assertContains(self.client.get(reverse("task-detail", args=[t.pk])), "Pamiętaj")
