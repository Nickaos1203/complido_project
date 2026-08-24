from django.db import models
from django.conf import settings


# finalités
class Purpose(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Nom",)
    description = models.TextField(blank=True, verbose_name="Description",)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Finalité"
        verbose_name_plural = "Finalités"
        ordering = ["name"]


# bases légales
class LegalBasis(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Nom",)
    description = models.TextField(blank=True, verbose_name="Description",)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Base légale"
        verbose_name_plural = "Bases légales"
        ordering = ["name"]


# catégories de données
class DataCategory(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Nom",)
    description = models.TextField(blank=True, verbose_name="Description",)
    is_sensitive = models.BooleanField(default=False, verbose_name="Donnée particulière", help_text="Indique si la catégorie contient des données particulières.",)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Catégorie de données"
        verbose_name_plural = "Catégories de données"
        ordering = ["name"]


# catégories de personnes concernées
class DataSubjectCategory(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Nom",)
    description = models.TextField(blank=True, verbose_name="Description",)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Catégorie de personnes concernées"
        verbose_name_plural = "Catégories de personnes concernées"
        ordering = ["name"]


# destinataires
class Recipient(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Nom",)
    description = models.TextField(blank=True, verbose_name="Description",)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Destinataire"
        verbose_name_plural = "Destinataires"
        ordering = ["name"]


# sous-traitants
class SubProcessor(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nom",)
    description = models.TextField(blank=True, verbose_name="Description",)
    contact_email = models.EmailField(blank=True, verbose_name="Email de contact",)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Sous-traitant"
        verbose_name_plural = "Sous-traitants"
        ordering = ["name"]


# mesures de sécurité
class SecurityMeasure(models.Model):

    class Category(models.TextChoices):
        ORGANIZATIONAL = ("ORGANIZATIONAL", "Organisationnelle",)
        TECHNICAL = ("TECHNICAL", "Technique",)
        PHYSICAL = ("PHYSICAL", "Physique",)

    name = models.CharField(max_length=255, unique=True, verbose_name="Nom",)
    description = models.TextField(blank=True, verbose_name="Description",)
    category = models.CharField(max_length=20, choices=Category.choices, verbose_name="Catégorie",)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Mesure de sécurité"
        verbose_name_plural = "Mesures de sécurité"
        ordering = ["category", "name"]


# traitements de données
class PersonalDataProcessing(models.Model):

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Brouillon"
        ACTIVE = "ACTIVE", "Actif"
        ARCHIVED = "ARCHIVED", "Archivé"

    name = models.CharField(max_length=255, verbose_name="Nom du traitement",)
    description = models.TextField(blank=True, verbose_name="Description générale du traitement",)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, verbose_name="Statut",)
    # Finalités
    purposes = models.ManyToManyField(Purpose, related_name="processings", blank=True,verbose_name="Finalités",)
    # Bases légales
    legal_bases = models.ManyToManyField(LegalBasis, related_name="processings", blank=True, verbose_name="Bases légales",)
    # Catégories de données personnelles
    data_categories = models.ManyToManyField(DataCategory, related_name="processings", blank=True,verbose_name="Catégories de données",)
    # Catégories de personnes concernées
    data_subject_categories = models.ManyToManyField(DataSubjectCategory, related_name="processings", blank=True, verbose_name="Catégories de personnes concernées",)
    # Destinataires
    recipients = models.ManyToManyField(Recipient, related_name="processings", blank=True, verbose_name="Destinataires",)
    # Sous-traitants
    sub_processors = models.ManyToManyField(SubProcessor, related_name="processings", blank=True, verbose_name="Sous-traitants",)
    # Mesures de sécurité
    security_measures = models.ManyToManyField(SecurityMeasure, related_name="processings", blank=True, verbose_name="Mesures de sécurité",)
    # Conservation
    retention_period = models.CharField(max_length=255, blank=True, verbose_name="Durée de conservation",)
    # Transferts internationaux
    international_transfer = models.BooleanField(default=False, verbose_name="Transfert international",)
    international_transfer_details = models.TextField(blank=True, verbose_name="Détails du transfert international",)

    # AIPD
    dpia_required = models.BooleanField(default=False, verbose_name="AIPD nécessaire",)
    dpia_date = models.DateField(null=True, blank=True, verbose_name="Date de l'AIPD",)

    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création",)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de modification",)

    # utilisateur
    responsible_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="personal_data_processings", null=True, blank=True, verbose_name="Responsable",)


    class Meta:
        verbose_name = "Traitement de données personnelles"
        verbose_name_plural = "Traitements de données personnelles"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


# Opérations de traitement
class ProcessingOperation(models.Model):

    class OperationType(models.TextChoices):
        COLLECTION = "COLLECTION", "Collecte"
        RECORDING = "RECORDING", "Enregistrement"
        STORAGE = "STORAGE", "Stockage"
        CONSULTATION = "CONSULTATION", "Consultation"
        USE = "USE", "Utilisation"
        TRANSMISSION = "TRANSMISSION", "Transmission"
        MODIFICATION = "MODIFICATION", "Modification"
        ARCHIVING = "ARCHIVING", "Archivage"
        DELETION = "DELETION", "Suppression"

    processing = models.ForeignKey(PersonalDataProcessing, on_delete=models.CASCADE, related_name="operations", verbose_name="Traitement",)
    operation_type = models.CharField(max_length=20, choices=OperationType.choices, verbose_name="Type d'opération",)
    description = models.TextField(blank=True, verbose_name="Description de l'opération de traitement",)
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre", help_text="Ordre chronologique de l'opération.",)

    class Meta:
        verbose_name = "Opération de traitement"
        verbose_name_plural = "Opérations de traitement"
        ordering = ["order"]

    def __str__(self):
        return f"{self.processing.name} - {self.get_operation_type_display()}"