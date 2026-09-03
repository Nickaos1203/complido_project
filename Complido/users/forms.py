from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class UserRegisterForm(UserCreationForm):

    class Meta:
        model = User

        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "entity",
            "department",
            "role",
            "password1",
            "password2",
        ]

        widgets = {
            "first_name": forms.TextInput(attrs={
                "class": "form-control",
                "autocomplete": "given-name",
                "maxlength": 150,
            }),
            "last_name": forms.TextInput(attrs={
                "class": "form-control",
                "autocomplete": "family-name",
                "maxlength": 150,
            }),
            "username": forms.TextInput(attrs={
                "class": "form-control",
                "autocomplete": "username",
                "maxlength": 150,
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "autocomplete": "email",
                "maxlength": 254,
            }),
            "entity": forms.Select(attrs={
                "class": "form-select",
            }),
            "department": forms.TextInput(attrs={
                "class": "form-control",
                "maxlength": 30,
            }),
            "role": forms.Select(attrs={
                "class": "form-select",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Un administrateur ne peut pas être créé depuis
        # le formulaire utilisateur.
        self.fields["role"].choices = [
            (User.Role.DPO, "DPO"),
            (User.Role.REFERENT, "Référent"),
        ]

        self.fields["password1"].widget.attrs.update({
            "class": "form-control",
            "autocomplete": "new-password",
        })

        self.fields["password2"].widget.attrs.update({
            "class": "form-control",
            "autocomplete": "new-password",
        })

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "Cette adresse e-mail est déjà utilisée."
            )

        return email