from django.contrib import admin
from .models import PersonalDataProcessing, SecurityMeasure, SubProcessor, Recipient, DataSubjectCategory, DataCategory, LegalBasis, Purpose, ProcessingOperation

# Register your models here.
admin.site.register(PersonalDataProcessing)