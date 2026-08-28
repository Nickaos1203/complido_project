from django.contrib import admin
from .models import (
    DataProcessing,
    LegalBasis,
    DataCategory,
    DataSubjectCategory,
    Recipient,
    Subprocessor,
    OperationType,
    ProcessingOperation,
    SecurityMeasure,
    ProcessingSecurityMeasure
    )

# Register your models here.
admin.site.register([
    DataProcessing,
    LegalBasis,
    DataCategory,
    DataSubjectCategory,
    Recipient,
    Subprocessor,
    OperationType,
    ProcessingOperation,
    SecurityMeasure,
    ProcessingSecurityMeasure
    ])