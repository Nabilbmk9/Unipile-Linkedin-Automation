# accounts/tests/test_connect_linkedin.py

import json
import pytest
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


@pytest.mark.django_db
@patch("accounts.views.requests.post")
def test_connect_linkedin_success(mock_post, client):
    """Test qu'on redirige l'utilisateur vers l'URL Unipile en cas de succès."""
    user = User.objects.create_user(username="bob", password="pwd123")
    client.login(username="bob", password="pwd123")

    # Simule la réponse de l'API Unipile
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "error": "{\"object\":\"HostedAuthUrl\",\"url\":\"https://account.unipile.com/fakeurl\"}"
    }

    response = client.post("/connect-linkedin/")
    # Vérifie la redirection
    assert response.status_code == 302
    # Vérifie qu'on appelle l'API Unipile
    mock_post.assert_called_once()


@pytest.mark.django_db
@patch("accounts.views.requests.post")
def test_connect_linkedin_error(mock_post, client):
    """Test qu'on gère une erreur renvoyée par Unipile."""
    user = User.objects.create_user(username="bob", password="pwd123")
    client.login(username="bob", password="pwd123")

    mock_post.return_value.status_code = 400
    mock_post.return_value.text = "Bad request"

    response = client.post("/connect-linkedin/")
    assert response.status_code == 302
    assert response.url == "/dashboard/"
    mock_post.assert_called_once()
