from django.db import models
from buildings.models import Building


class Species(models.Model):
    """Gatunek zwierzęcia — osobna, zarządzalna encja."""

    name = models.CharField("Nazwa gatunku", max_length=100, unique=True)

    class Meta:
        verbose_name = "Gatunek"
        verbose_name_plural = "Gatunki"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Animal(models.Model):

    class Sex(models.TextChoices):
        FEMALE = "F", "Samica"
        MALE = "M", "Samiec"
        UNKNOWN = "U", "Nieznana"

    class HealthStatus(models.TextChoices):
        HEALTHY = "HEALTHY", "Zdrowe"
        TREATMENT = "TREATMENT", "W trakcie leczenia"
        SICK = "SICK", "Chore"

    name = models.CharField("Nazwa", max_length=100, blank=True)

    identifier = models.CharField(
        "Identyfikator",
        max_length=50,
        unique=True,
        help_text="Unikalny numer / oznaczenie zwierzęcia.",
    )

    species = models.ForeignKey(
        Species,
        on_delete=models.PROTECT,
        related_name="animals",
        verbose_name="Gatunek",
    )

    sex = models.CharField(
        "Płeć",
        max_length=1,
        choices=Sex.choices,
        default=Sex.UNKNOWN,
    )

    building = models.ForeignKey(
        Building,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="animals",
        verbose_name="Lokalizacja",
    )

    health_status = models.CharField(
        "Stan zdrowia",
        max_length=20,
        choices=HealthStatus.choices,
        default=HealthStatus.HEALTHY,
    )

    birth_date = models.DateField("Data urodzenia", null=True, blank=True)

    created_at = models.DateTimeField("Data dodania", auto_now_add=True)

    class Meta:
        verbose_name = "Zwierzę"
        verbose_name_plural = "Zwierzęta"
        ordering = ["name", "identifier"]

    def __str__(self):
        label = self.name or self.identifier
        return f"{label} ({self.species})"

    def latest_note(self):
        """Najnowsza notatka (lub None)."""
        return self.note_history.first()


class AnimalNote(models.Model):
    """Wpis w historii notatek zwierzęcia (z datą dodania)."""

    animal = models.ForeignKey(
        Animal,
        on_delete=models.CASCADE,
        related_name="note_history",
        verbose_name="Zwierzę",
    )

    content = models.TextField("Treść notatki")

    author = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        verbose_name="Autor",
    )

    created_at = models.DateTimeField("Data aktualizacji", auto_now_add=True)

    class Meta:
        verbose_name = "Notatka zwierzęcia"
        verbose_name_plural = "Notatki zwierzęcia"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.animal} – {self.created_at:%d.%m.%Y}"
