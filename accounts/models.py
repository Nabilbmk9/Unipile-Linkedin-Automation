from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class CustomUser(AbstractUser):
    """
    Modèle utilisateur personnalisé (identique à User de base pour l’instant).
    """
    pass


class LinkedAccount(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    provider = models.CharField(max_length=50, default="LINKEDIN")
    account_id = models.CharField(max_length=255, unique=True)
    connected_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.provider} - {self.account_id}"
