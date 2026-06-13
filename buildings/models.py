from django.db import models
from django.conf import settings


class Building(models.Model):
    """Lokalizacja: stajnia, boks, zagroda lub wybieg."""

    class Type(models.TextChoices):
        STABLE = "STABLE", "Stajnia"
        STALL = "STALL", "Boks"
        PEN = "PEN", "Zagroda"
        PADDOCK = "PADDOCK", "Wybieg"

    name = models.CharField("Nazwa", max_length=100)

    type = models.CharField(
        "Typ lokalizacji",
        max_length=20,
        choices=Type.choices,
        default=Type.STABLE,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_buildings",
        verbose_name="Utworzona przez",
    )

    created_at = models.DateTimeField("Data utworzenia", auto_now_add=True)

    class Meta:
        verbose_name = "Lokalizacja"
        verbose_name_plural = "Lokalizacje"

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

    def latest_note(self):
        """Najnowsza notatka (lub None)."""
        return self.note_history.first()


class BuildingNote(models.Model):
    """Wpis w historii notatek lokalizacji (z datą dodania)."""

    building = models.ForeignKey(
        Building,
        on_delete=models.CASCADE,
        related_name="note_history",
        verbose_name="Lokalizacja",
    )

    content = models.TextField("Treść notatki")

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        verbose_name="Autor",
    )

    created_at = models.DateTimeField("Data aktualizacji", auto_now_add=True)

    class Meta:
        verbose_name = "Notatka lokalizacji"
        verbose_name_plural = "Notatki lokalizacji"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.building} – {self.created_at:%d.%m.%Y}"
