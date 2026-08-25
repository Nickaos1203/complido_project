from django.db import models
from django.conf import settings

from personal_data_processing.models import DataProcessing


class Comment(models.Model):
    """
    Commentaire associé à un traitement de données personnelles.
    """

    processing = models.ForeignKey(DataProcessing, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Commentaire"
        verbose_name_plural = "Commentaires"
        ordering = ["created_at"]

    def __str__(self):
        return f"Commentaire de {self.user} - {self.processing}"