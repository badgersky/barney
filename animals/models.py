from django.db import models
from buildings.models import Building


class Animal(models.Model):

    class Species(models.TextChoices):
        COW = "COW", "Cow"
        PIG = "PIG", "Pig"
        HORSE = "HORSE", "Horse"
        CHICKEN = "CHICKEN", "Chicken"
        GOAT = "GOAT", "Goat"
        DUCK = "DUCK", "Duck"
        GOOSE = "GOOSE", "Goose"

    name = models.CharField(
        max_length=100,
        blank=True    
    )

    species = models.CharField(
        max_length=20,
        choices=Species.choices
    )

    building = models.ForeignKey(
        Building,
        on_delete=models.CASCADE,
        related_name="animals"
    )

    birth_date = models.DateField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.name} ({self.get_species_display()})"