# accounts/tests/test_callback.py

import json
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.models import LinkedAccount

User = get_user_model()


@pytest.mark.django_db
def test_callback_creates_linked_account(client):
    """Test qu'on crée un LinkedAccount quand tout est ok."""
    user = User.objects.create_user(username="testuser", password="123")
    payload = {
        "account_id": "linkedin_123",
        "name": str(user.id),  # name = str(user.id)
        "provider": "LINKEDIN"
    }

    response = client.post(
        "/unipile-callback/",  # ou reverse("unipile_callback")
        data=json.dumps(payload),
        content_type="application/json"
    )

    assert response.status_code == 200
    linked = LinkedAccount.objects.filter(account_id="linkedin_123", user=user).exists()
    assert linked is True


@pytest.mark.django_db
def test_callback_missing_account_id(client):
    """Test qu'on renvoie une erreur si account_id manque."""
    user = User.objects.create_user(username="testuser", password="123")
    payload = {
        # "account_id": "linkedin_123",  # Oublié exprès
        "name": str(user.id),
        "provider": "LINKEDIN"
    }

    response = client.post(
        "/unipile-callback/",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_callback_unknown_user(client):
    """Test qu'on renvoie 500 si le user n'existe pas."""
    payload = {
        "account_id": "linkedin_123",
        "name": "9999",  # user inexistant
        "provider": "LINKEDIN"
    }

    response = client.post(
        "/unipile-callback/",
        data=json.dumps(payload),
        content_type="application/json"
    )
    # Dans notre code, on catch l'exception => on renvoie 500
    assert response.status_code == 500


def test_callback_invalid_method(client):
    """Test qu'un GET renvoie 405."""
    response = client.get("/unipile-callback/")
    assert response.status_code == 405
