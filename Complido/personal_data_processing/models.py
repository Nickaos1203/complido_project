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


    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    entity = models.CharField(max_length=100, choices=User.Entity.choices, default=User.Entity.COMPLIDO)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.DRAFT)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="data_processings", null=True, blank=True)
    purpose = models.CharField(max_length=255, blank=True)
    subpurpose = models.CharField(max_length=255, blank=True)
    description_purpose = models.TextField(blank=True)
    legal_basis = models.ManyToManyField(LegalBasis, through="ProcessingLegalBasis", related_name="data_processings", blank=True)
    
    # durée de conservation
    retention_period = models.CharField(max_length=255, blank=True)

    # transferts internationaux
    international_transfer = models.BooleanField(default=False)

    # analyse d'impact requis
    aipd_required = models.BooleanField(default=False)

    # Relations N,N simples
    data_categories = models.ManyToManyField(DataCategory, through="ProcessingDataCategory", related_name="data_processings", blank=True)
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


class ProcessingDataCategory(models.Model):
    """
    Association entre un traitement et une catégorie de données.

    Permet de préciser les données effectivement traitées
    au sein de chaque catégorie.
    """

    processing = models.ForeignKey(DataProcessing, on_delete=models.CASCADE, related_name="processing_data_categories")
    data_category = models.ForeignKey(DataCategory, on_delete=models.PROTECT, related_name="processing_data_categories")
    data_enumeration = models.TextField(verbose_name="Énumération des données", blank=True)

    class Meta:
        verbose_name = "Description de la catégorie de données"
        verbose_name_plural = "Descriptions de la catégories de données"

        constraints = [
            models.UniqueConstraint(
                fields=["processing", "data_category"],
                name="unique_processing_data_category"
            )
        ]

    def __str__(self):
        return f"{self.processing} - {self.data_category}"


class ProcessingLegalBasis(models.Model):
    """
    Association entre un traitement et sa base légale.
    """
    processing = models.ForeignKey(DataProcessing, on_delete=models.CASCADE, related_name="processing_legal_basis")
    legal_basis = models.ForeignKey(LegalBasis, on_delete=models.PROTECT, related_name="processing_legal_basis")
    justification = models.TextField(verbose_name="Justification", blank=True)

    class Meta:
        verbose_name = "Base légale du traitement"
        verbose_name_plural = "Bases légales des traitements"

        constraints = [
            models.UniqueConstraint(
                fields=["processing"],
                name="unique_processing_legal_basis"
            )
        ]

    def __str__(self):
        return f"{self.processing} - {self.legal_basis}"