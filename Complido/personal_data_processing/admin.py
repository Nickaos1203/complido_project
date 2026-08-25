from django.contrib import admin
from .models import (
    DataProcessing,
    LegalBasis,
    Purpose,
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
    Purpose,
    DataCategory,
    DataSubjectCategory,
    Recipient,
    Subprocessor,
    OperationType,
    ProcessingOperation,
    SecurityMeasure,
    ProcessingSecurityMeasure
    ])