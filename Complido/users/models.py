from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrateur"
        DPO = "DPO", "DPO"
        REFERENT = "REFERENT", "Référent"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.REFERENT,
        verbose_name="Rôle",
    )

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"