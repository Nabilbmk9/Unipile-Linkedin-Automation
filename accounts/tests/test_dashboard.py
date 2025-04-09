# accounts/tests/test_dashboard.py

import pytest
from unittest.mock import patch
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.models import LinkedAccount

User = get_user_model()

@pytest.mark.django_db
def test_dashboard_no_account(client):
    """Si aucun compte n'est lié, on affiche le bouton."""
    user = User.objects.create_user(username="testuser", password="pwd123")
    client.login(username="testuser", password="pwd123")

    response = client.get("/dashboard/")
    assert response.status_code == 200
    assert b"Connecter mon compte LinkedIn" in response.content


@pytest.mark.django_db
@patch("accounts.views.is_linkedin_account_still_valid", return_value=False)
def test_dashboard_deleted_if_not_valid(mock_check, client):
    """Si le compte n'est pas valide, on le supprime localement."""
    user = User.objects.create_user(username="bob", password="pwd123")
    LinkedAccount.objects.create(user=user, account_id="linkedin_def", provider="LINKEDIN")

    client.login(username="bob", password="pwd123")
    response = client.get("/dashboard/")
    assert response.status_code == 200
    # On a mocké la fonction => renvoie False => doit delete le linked_account
    # => On affiche le bouton de connexion
    assert b"Connecter mon compte LinkedIn" in response.content

    # Vérifie qu'il est bien supprimé en base
    assert not LinkedAccount.objects.filter(user=user).exists()
