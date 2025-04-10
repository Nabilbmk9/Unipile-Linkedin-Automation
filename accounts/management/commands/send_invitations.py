import time
import random
from django.core.management.base import BaseCommand
from django.utils.timezone import now
from accounts.models import ProspectionSession, ProspectionTarget
from accounts.models import LinkedAccount
from decouple import config
import requests
import logging

from accounts.services.unipile_api import get_profiles_from_search, send_invitation

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Envoie progressive d'invitations LinkedIn via Unipile"

    def handle(self, *args, **kwargs):
        active_sessions = ProspectionSession.objects.filter(is_active=True)

        for session in active_sessions:
            print(f"📤 Campagne : {session.name}")
            account = LinkedAccount.objects.filter(user=session.user).first()
            if not account:
                print("❌ Aucun compte connecté pour cet utilisateur.")
                continue

            daily_limit = session.daily_limit
            sent_today = 0
            current_page = session.current_page
            position = session.position_in_page

            while sent_today < daily_limit:
                print(f"🔎 Lecture de la page {current_page}, à partir du profil {position}")

                # Ajout du paramètre ?page=X dans l’URL
                page_url = _set_page_in_url(session.search_url, current_page)
                profiles = get_profiles_from_search(account.account_id, page_url)

                if not profiles:
                    print("⚠️ Aucun profil trouvé sur cette page. Fin de campagne.")
                    session.is_active = False
                    session.save()
                    break

                for i in range(position, len(profiles)):
                    profile = profiles[i]
                    profile_id = profile.get("id")
                    name = profile.get("name") or (
                            profile.get("first_name", "Inconnu") + " " + profile.get("last_name", "")
                    )

                    # Vérifie si déjà envoyé
                    if ProspectionTarget.objects.filter(session=session, profile_id=profile_id).exists():
                        print(f"⏭️ Déjà traité : {name}")
                        continue

                    # Prépare le message
                    message = session.note_template.replace("{{first_name}}", name.split(" ")[0])
                    success, error_msg = send_invitation(account.account_id, profile_id, message)

                    # Détection de blocage temporaire
                    if "cannot_resend_yet" in error_msg:
                        print("🚫 LinkedIn bloque temporairement les invitations. Arrêt de la campagne du jour.")
                        session.current_page = current_page
                        session.position_in_page = i  # on ne passe pas au suivant
                        session.last_sent_at = now()
                        session.save()
                        return  # on sort proprement

                    # Enregistrement du résultat
                    target = ProspectionTarget.objects.create(
                        session=session,
                        profile_id=profile_id,
                        full_name=name.strip(),
                        status="sent" if success else "error",
                        error_message=error_msg if not success else "",
                        sent_at=now() if success else None,
                    )

                    if success:
                        print(f"✅ Invitation envoyée à {name}")
                        sent_today += 1
                    else:
                        print(f"❌ Échec pour {name}: {error_msg}")

                    position = i + 1

                    if sent_today >= daily_limit:
                        print("🎯 Objectif journalier atteint.")
                        break

                    delay = random.randint(9, 29)
                    print(f"⏱️ Pause de {delay}s...")
                    time.sleep(delay)

                # Si on a fini tous les profils de cette page, on passe à la suivante
                if position >= len(profiles):
                    current_page += 1
                    position = 0
                else:
                    break  # on n'a pas fini la page mais on a atteint la limite

            # Sauvegarde de la progression
            session.current_page = current_page
            session.position_in_page = position
            session.last_sent_at = now()
            session.save()
            print(f"💾 Session mise à jour : page={current_page}, position={position}")


def _set_page_in_url(url: str, page_number: int) -> str:
    import re
    pattern = r"([?&])page=\d+"
    new_param = f"\\1page={page_number}"

    if re.search(pattern, url):
        return re.sub(pattern, new_param, url)
    else:
        if "?" in url:
            return url + f"&page={page_number}"
        else:
            return url + f"?page={page_number}"
