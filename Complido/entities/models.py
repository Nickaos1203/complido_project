from django.db import models


class Entity(models.Model):
    name = models.CharField(max_length=255)
    siret = models.CharField(max_length=14, blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Entité"
        verbose_name_plural = "Entités"
        ordering = ["name"]

    def __str__(self):
        return self.name