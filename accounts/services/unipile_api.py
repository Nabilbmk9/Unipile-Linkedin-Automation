import time
import requests
from decouple import config

API_URL = "https://api9.unipile.com:13973"
HEADERS = {
    "X-API-KEY": config("UNIPILE_API_KEY"),
    "accept": "application/json",
    "content-type": "application/json"
}


def send_invitation(account_id: str, provider_id: str, message: str = "") -> tuple[bool, str]:
    url = f"{API_URL}/api/v1/users/invite"
    payload = {
        "account_id": account_id,
        "provider_id": provider_id,
        "message": message
    }

    response = requests.post(url, headers=HEADERS, json=payload)

    if response.status_code in (200, 201):  # ✅ on accepte aussi 201 maintenant
        return True, ""
    else:
        return False, f"{response.status_code} - {response.text}"


def get_profiles_from_search(account_id: str, search_url: str) -> list[dict]:
    """Exécute une recherche LinkedIn à partir d'une URL et retourne les profils trouvés."""
    url = f"{API_URL}/api/v1/linkedin/search?account_id={account_id}"
    payload = {"url": search_url}

    response = requests.post(url, headers=HEADERS, json=payload)

    if response.status_code == 200:
        return response.json().get("items", [])
    else:
        print("Erreur:", response.status_code, response.text)
        return []


def get_raw_data(resource_id: str) -> list[dict]:
    """Récupère les résultats d’une recherche via son resource_id."""
    time.sleep(5)  # attente minimale recommandée
    response = requests.get(f"{API_URL}/api/v1/raw-data/{resource_id}", headers=HEADERS)

    if response.status_code == 200:
        return response.json().get("items", [])
    return []


def check_account_exists(account_id: str) -> bool:
    """Vérifie si un compte LinkedIn est toujours actif dans Unipile."""
    response = requests.get(f"{API_URL}/api/v1/accounts", headers=HEADERS)

    if response.status_code == 200:
        accounts = response.json().get("items", [])
        return any(acc.get("id") == account_id for acc in accounts)
    return False
