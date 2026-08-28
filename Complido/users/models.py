from django.contrib.auth.models import AbstractUser
from django.db import models

from entities.models import Entity


class User(AbstractUser):

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrateur"
        DPO = "DPO", "DPO"
        REFERENT = "REFERENT", "Référent"

    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name="users", null=True, blank=True)
    department = models.CharField(max_length=30, null=True, blank=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.REFERENT)

    def __str__(self):
        return self.get_full_name() or self.username