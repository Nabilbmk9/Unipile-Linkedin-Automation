from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    """
    Modèle utilisateur personnalisé avec email unique.
    """
    email = models.EmailField(_('email address'), unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')


class LinkedAccount(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    provider = models.CharField(max_length=50, default="LINKEDIN")
    account_id = models.CharField(max_length=255, unique=True)
    connected_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.provider} - {self.account_id}"


class ProspectionSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    search_url = models.URLField()
    note_template = models.TextField()
    daily_limit = models.PositiveIntegerField(default=20)
    is_active = models.BooleanField(default=True)
    last_sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    current_page = models.PositiveIntegerField(default=1)
    position_in_page = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class ProspectionTarget(models.Model):
    session = models.ForeignKey(ProspectionSession, on_delete=models.CASCADE, related_name="targets")
    profile_id = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=[
        ("pending", "En attente"),
        ("sent", "Envoyée"),
        ("error", "Erreur"),
        ("accepted", "Acceptée")
    ], default="pending")
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.full_name
