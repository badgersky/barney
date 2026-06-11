from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        MANAGER = "MANAGER", "Manager"
        WORKER = "WORKER", "Worker"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.WORKER
    )

    def __str__(self):
        return self.username
    
    def is_admin(self):
        return self.role == self.Role.ADMIN

    def is_manager(self):
        return self.role == self.Role.MANAGER

    def is_worker(self):
        return self.role == self.Role.WORKER