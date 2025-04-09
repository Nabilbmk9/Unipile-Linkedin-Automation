from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, ProspectionSession


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("username", "email")


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ("username", "email")


class NewProspectionForm(forms.ModelForm):
    class Meta:
        model = ProspectionSession
        fields = ["name", "search_url", "note_template", "daily_limit"]
        widgets = {
            "note_template": forms.Textarea(attrs={"rows": 4}),
        }
        labels = {
            "name": "Nom de la campagne",
            "search_url": "Lien de recherche LinkedIn",
            "note_template": "Message personnalisé (ex: Bonjour {{first_name}})",
            "daily_limit": "Nombre max d'invitations par jour"
        }