from django import forms
from .models import DataProcessing


class PersonalDataProcessingForm(forms.ModelForm):

    class Meta:
        model = DataProcessing
        fields = "__all__"