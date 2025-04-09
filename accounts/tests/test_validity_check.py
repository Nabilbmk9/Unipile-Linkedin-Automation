# accounts/tests/test_validity_check.py

import pytest
from unittest.mock import patch
from accounts.views import is_linkedin_account_still_valid

@pytest.mark.django_db
@patch("accounts.views.requests.get")
def test_is_linkedin_account_still_valid_ok(mock_get):
    """Si l'API Unipile renvoie l'account dans items, on renvoie True."""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "object": "AccountList",
        "items": [
            {"id": "linkedin_abc", "provider": "LINKEDIN"}
        ],
        "cursor": None
    }

    assert is_linkedin_account_still_valid("linkedin_abc") is True


@pytest.mark.django_db
@patch("accounts.views.requests.get")
def test_is_linkedin_account_still_valid_absent(mock_get):
    """Si l'API Unipile renvoie une liste vide, on renvoie False."""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "object": "AccountList",
        "items": [],
        "cursor": None
    }

    assert is_linkedin_account_still_valid("linkedin_abc") is False


@pytest.mark.django_db
@patch("accounts.views.requests.get")
def test_is_linkedin_account_still_valid_error(mock_get):
    """Si l'API renvoie un code != 200, on renvoie False."""
    mock_get.return_value.status_code = 500

    assert is_linkedin_account_still_valid("linkedin_abc") is False
