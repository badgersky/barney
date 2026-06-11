from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        MANAGER = "MANAGER", "Szef"
        WORKER = "WORKER", "Pracownik"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.WORKER
    )

    def __str__(self):
        return self.username