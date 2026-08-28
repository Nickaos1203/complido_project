from django.db import models
from django.conf import settings

from entities.models import Entity
from users.models import User


class LegalBasis(models.Model):
    """
    Base légale d'un traitement de données personnelles.
    Un traitement possède une seule base légale.
    Une base légale peut être utilisée par plusieurs traitements.
    """

    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Base légale"
        verbose_name_plural = "Bases légales"
        ordering = ["name"]

    def __str__(self):
        return self.name


class DataCategory(models.Model):
    """
    Catégorie de données personnelles.

    La description permet à l'utilisateur de préciser
    librement les données appartenant à cette catégorie.
    """

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Catégorie de données"
        verbose_name_plural = "Catégories de données"
        ordering = ["name"]

    def __str__(self):
        return self.name


class DataSubjectCategory(models.Model):
    """
    Catégorie de personnes concernées par le traitement.
    """

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Catégorie de personnes concernées"
        verbose_name_plural = "Catégories de personnes concernées"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Recipient(models.Model):
    """
    Destinataire des données personnelles.
    """

    class RecipientType(models.TextChoices):
        INTERNAL = "INTERNAL", "Interne"
        EXTERNAL = "EXTERNAL", "Externe"
        PUBLIC = "PUBLIC", "Autorité publique"

    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=RecipientType.choices)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Destinataire"
        verbose_name_plural = "Destinataires"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Subprocessor(models.Model):
    """
    Sous-traitant intervenant dans un ou plusieurs traitements.
    """

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    contact = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Sous-traitant"
        verbose_name_plural = "Sous-traitants"
        ordering = ["name"]

    def __str__(self):
        return self.name


class OperationType(models.Model):
    """
    Type d'opération réalisée sur les données personnelles.
    """

    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Type d'opération"
        verbose_name_plural = "Types d'opération"
        ordering = ["name"]

    def __str__(self):
        return self.name


class SecurityMeasure(models.Model):
    """
    Mesure de sécurité applicable à un traitement.
    """
    class Category(models.TextChoices):
        ORGANIZATIONAL = "ORGANIZATIONAL", "Organisationnelle"
        TECHNICAL = "TECHNICAL", "Technique"
        PHYSICAL = "PHYSICAL", "Physique"

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=Category.choices)

    class Meta:
        verbose_name = "Mesure de sécurité"
        verbose_name_plural = "Mesures de sécurité"
        ordering = ["name"]

    def __str__(self):
        return self.name


class DataProcessing(models.Model):
    """
    Traitement de données personnelles.

    Cette classe constitue le cœur du registre des traitements
    de Complido.
    """

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Brouillon"
        ACTIVE = "ACTIVE", "Actif"
        ARCHIVED = "ARCHIVED", "Archivé"

    # nom du traitement
    name = models.CharField(max_length=255)

    # précision sur le traitement et le contexte
    description = models.TextField(blank=True)

    # Organisation propriétaire du traitement
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name="data_processings")

    # status du traitement
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.DRAFT)

    # utilisateur
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="data_processings", null=True, blank=True)

    # une finalité pour un traitement
    purpose = models.CharField(max_length=255, blank=True)

    # Sous-finalité facultative
    subpurpose = models.CharField(max_length=255, blank=True)

    # Description de la finalité
    description_purpose = models.TextField(blank=True)

    # Une seule base légale par traitement
    legal_basis = models.ForeignKey(LegalBasis, on_delete=models.PROTECT, related_name="data_processings")
    

    # durée de conservation
    retention_period = models.CharField(max_length=255, blank=True)

    # transferts internationaux
    international_transfer = models.BooleanField(default=False)

    # analyse d'impact requis
    aipd_required = models.BooleanField(default=False)

    # Relations N,N simples
    data_categories = models.ManyToManyField(DataCategory, related_name="data_processings", blank=True)
    data_subject_categories = models.ManyToManyField(DataSubjectCategory, related_name="data_processings", blank=True)
    recipients = models.ManyToManyField(Recipient, related_name="data_processings", blank=True)
    subprocessors = models.ManyToManyField(Subprocessor, related_name="data_processings", blank=True)

    # Relations N,N avec modèle intermédiaire
    security_measures = models.ManyToManyField(SecurityMeasure, through="ProcessingSecurityMeasure", related_name="data_processings", blank=True)
    operations = models.ManyToManyField(OperationType, through="ProcessingOperation", related_name="data_processings", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Traitement"
        verbose_name_plural = "Traitements"
        ordering = ["name"]

    def __str__(self):
        return self.name


class ProcessingOperation(models.Model):
    """
    Association entre un traitement et un type d'opération.

    Cette table permet notamment de conserver l'ordre
    des opérations et une description spécifique.
    """

    processing = models.ForeignKey(DataProcessing, on_delete=models.CASCADE, related_name="processing_operations")
    operation_type = models.ForeignKey(OperationType, on_delete=models.PROTECT, related_name="processing_operations")
    display_order = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Opération du traitement"
        verbose_name_plural = "Opérations du traitement"
        ordering = ["display_order"]

        constraints = [
            models.UniqueConstraint(
                fields=["processing", "operation_type"],
                name="unique_processing_operation"
            )
        ]

    def __str__(self):
        return f"{self.processing} - {self.operation_type}"


class ProcessingSecurityMeasure(models.Model):
    """
    Association entre un traitement et une mesure de sécurité.

    La relation possède des informations supplémentaires :
    - état de mise en œuvre
    - commentaire
    """

    class Status(models.TextChoices):
        PLANNED = "PLANNED", "Prévue"
        PARTIAL = "PARTIAL", "Partiellement mise en œuvre"
        IMPLEMENTED = "IMPLEMENTED", "Mise en œuvre"
        NOT_APPLICABLE = "NOT_APPLICABLE", "Non applicable"

    processing = models.ForeignKey(DataProcessing, on_delete=models.CASCADE, related_name="processing_security_measures")
    security_measure = models.ForeignKey(SecurityMeasure, on_delete=models.PROTECT, related_name="processing_security_measures")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLANNED)
    comment = models.TextField(blank=True)

    class Meta:
        verbose_name = "Mesure de sécurité du traitement"
        verbose_name_plural = "Mesures de sécurité du traitement"

        constraints = [
            models.UniqueConstraint(
                fields=["processing", "security_measure"],
                name="unique_processing_security_measure"
            )
        ]

    def __str__(self):
        return f"{self.processing} - {self.security_measure}"