from datetime import timedelta

from django.db import models
from django.conf import settings
from django.utils import timezone

from animals.models import Animal
from buildings.models import Building


class TaskType(models.Model):
    """Typ zadania: HEALTH (zdrowotne) albo MANAGEMENT (zarządcze)."""

    class Category(models.TextChoices):
        HEALTH = "HEALTH", "Zdrowotne"
        MANAGEMENT = "MANAGEMENT", "Zarządcze"

    name = models.CharField("Nazwa", max_length=100)

    category = models.CharField(
        "Kategoria",
        max_length=20,
        choices=Category.choices,
        default=Category.MANAGEMENT,
    )

    description = models.TextField("Opis", blank=True)

    class Meta:
        verbose_name = "Typ zadania"
        verbose_name_plural = "Typy zadań"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class Task(models.Model):

    # Statusy przechowywane w bazie. "Nadchodzące" i "Zaległe" są stanami
    # wyliczanymi na podstawie terminu (patrz metoda display_status).
    class Status(models.TextChoices):
        PLANNED = "PLANNED", "Zaplanowane"
        DONE = "DONE", "Wykonane"
        CANCELLED = "CANCELLED", "Anulowane"

    title = models.CharField("Tytuł", max_length=200)

    description = models.TextField("Opis", blank=True)

    task_type = models.ForeignKey(
        TaskType,
        on_delete=models.SET_NULL,
        null=True,
        related_name="tasks",
        verbose_name="Typ zadania",
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
        verbose_name="Przypisane do",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_tasks",
        verbose_name="Utworzone przez",
    )

    status = models.CharField(
        "Status",
        max_length=20,
        choices=Status.choices,
        default=Status.PLANNED,
    )

    due_date = models.DateField("Termin", null=True, blank=True)

    created_at = models.DateTimeField("Data utworzenia", auto_now_add=True)

    # Zadanie może dotyczyć zwierzęcia ALBO lokalizacji.
    animal = models.ForeignKey(
        Animal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
        verbose_name="Zwierzę",
    )

    building = models.ForeignKey(
        Building,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
        verbose_name="Lokalizacja",
    )

    class Meta:
        verbose_name = "Zadanie"
        verbose_name_plural = "Zadania"
        ordering = ["due_date", "-created_at"]

    def __str__(self):
        return self.title

    def display_status(self):
        """Zwraca stan prezentacyjny zadania (uwzględnia termin)."""
        if self.status != self.Status.PLANNED:
            return self.get_status_display()

        if self.due_date:
            today = timezone.localdate()
            if self.due_date < today:
                return "Zaległe"
            if self.due_date <= today + timedelta(days=3):
                return "Nadchodzące"
        return "Zaplanowane"

    def status_code(self):
        """Krótki kod stanu do stylowania (klasa CSS)."""
        return {
            "Zaległe": "overdue",
            "Nadchodzące": "upcoming",
            "Zaplanowane": "planned",
            "Wykonane": "done",
            "Anulowane": "cancelled",
        }.get(self.display_status(), "planned")

    @property
    def target(self):
        """Czego dotyczy zadanie: zwierzęcia lub lokalizacji."""
        if self.animal:
            return self.animal
        if self.building:
            return self.building
        return None


class Reminder(models.Model):
    """Przypomnienie powiązane z zadaniem."""

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Aktywne"
        SENT = "SENT", "Wysłane"
        CANCELLED = "CANCELLED", "Anulowane"

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="reminders",
        verbose_name="Zadanie",
    )

    date = models.DateField("Data przypomnienia")

    message = models.CharField("Treść", max_length=255)

    status = models.CharField(
        "Status",
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    created_at = models.DateTimeField("Data utworzenia", auto_now_add=True)

    class Meta:
        verbose_name = "Przypomnienie"
        verbose_name_plural = "Przypomnienia"
        ordering = ["date"]

    def __str__(self):
        return f"{self.date} – {self.message}"
