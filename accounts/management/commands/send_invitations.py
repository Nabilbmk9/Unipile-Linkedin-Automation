import time
import random
from django.core.management.base import BaseCommand
from django.utils.timezone import now
from accounts.models import ProspectionSession, ProspectionTarget
from decouple import config
import requests
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Envoie automatique de demandes de connexion LinkedIn via Unipile"

    def handle(self, *args, **kwargs):
        headers = {
            "X-API-KEY": config("UNIPILE_API_KEY"),
            "accept": "application/json",
            "content-type": "application/json"
        }

        active_sessions = ProspectionSession.objects.filter(is_active=True)

        for session in active_sessions:
            print(f"📤 Traitement de la campagne : {session.name}")

            # Sélectionne les cibles en attente, limité au quota
            targets = session.targets.filter(status="pending")[:session.daily_limit]

            for target in targets:
                try:
                    payload = {
                        "account_id": session.user.linkedaccount.account_id,
                        "profile_id": target.profile_id,
                        "note": session.note_template.replace("{{first_name}}", target.full_name.split(" ")[0])
                    }

                    response = requests.post(
                        "https://api9.unipile.com:13973/api/v1/linkedin/invitations",
                        headers=headers,
                        json=payload
                    )

                    if response.status_code == 200:
                        target.status = "sent"
                        target.sent_at = now()
                        print(f"✅ Invitation envoyée à {target.full_name}")
                    else:
                        target.status = "error"
                        target.error_message = f"HTTP {response.status_code}: {response.text}"
                        print(f"❌ Erreur pour {target.full_name}: {response.status_code}")

                    target.save()
                    session.last_sent_at = now()
                    session.save()

                    # Délai aléatoire entre 9 et 29 sec
                    delay = random.randint(9, 29)
                    print(f"⏱️ Pause de {delay}s...")
                    time.sleep(delay)

                except Exception as e:
                    target.status = "error"
                    target.error_message = str(e)
                    target.save()
                    print(f"❌ Exception pour {target.full_name}: {e}")
