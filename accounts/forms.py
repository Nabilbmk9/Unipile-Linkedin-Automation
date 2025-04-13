from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, ProspectionSession


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )


class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class LoginForm(forms.Form):
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label=_("Mot de passe"),
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    remember_me = forms.BooleanField(
        label=_("Se souvenir de moi"),
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class NewProspectionForm(forms.ModelForm):
    class Meta:
        model = ProspectionSession
        fields = ["name", "search_url", "note_template", "daily_limit"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex: Développeurs Python Paris"
            }),
            "search_url": forms.URLInput(attrs={
                "class": "form-control",
                "placeholder": "https://www.linkedin.com/search/results/people/..."
            }),
            "note_template": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Bonjour {{first_name}},\nJ'aimerais vous ajouter à mon réseau professionnel..."
            }),
            "daily_limit": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "1",
                "max": "100"
            })
        }
        labels = {
            "name": "Nom de la campagne",
            "search_url": "Lien de recherche LinkedIn",
            "note_template": "Message personnalisé",
            "daily_limit": "Nombre max d'invitations par jour"
        }