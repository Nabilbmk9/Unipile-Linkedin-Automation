import requests
import json
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST

from .forms import NewProspectionForm
from .models import LinkedAccount, CustomUser, ProspectionSession, ProspectionTarget
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decouple import config
from datetime import datetime, timedelta, timezone
import time

from .services.unipile_api import get_profiles_from_search


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Identifiants incorrects.")

    return render(request, 'accounts/login.html')


def is_linkedin_account_still_valid(account_id):
    headers = {
        "X-API-KEY": config("UNIPILE_API_KEY"),
        "accept": "application/json",
    }

    response = requests.get("https://api9.unipile.com:13973/api/v1/accounts", headers=headers)

    if response.status_code == 200:
        accounts = response.json().get("items", [])
        for acc in accounts:
            if acc.get("id") == account_id:
                return True  # Le compte est encore valide
    return False  # Compte non trouvé => plus valide


@login_required
def dashboard_view(request):
    linked_account = LinkedAccount.objects.filter(user=request.user).first()

    if linked_account and not is_linkedin_account_still_valid(linked_account.account_id):
        linked_account.delete()
        linked_account = None

    prospections = ProspectionSession.objects.filter(user=request.user)

    # Statistiques calculées ici pour chaque campagne
    prospection_stats = []
    for p in prospections:
        stats = {
            "session": p,
            "pending": p.targets.filter(status="pending").count(),
            "sent": p.targets.filter(status="sent").count(),
            "error": p.targets.filter(status="error").count(),
        }
        prospection_stats.append(stats)

    return render(request, "accounts/dashboard.html", {
        "user": request.user,
        "linked_account": linked_account,
        "prospection_stats": prospection_stats,
    })



def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def connect_linkedin(request):
    expires_on = (datetime.now(timezone.utc) + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S.999Z")

    headers = {
        "X-API-KEY": config("UNIPILE_API_KEY"),
        "accept": "application/json",
        "content-type": "application/json"
    }

    payload = {
        "type": "create",
        "providers": ["LINKEDIN"],
        "api_url": "https://api9.unipile.com:13973",
        "expiresOn": expires_on,
        "notify_url": "https://web-production-f81a1.up.railway.app/unipile_callback/",
        "name": str(request.user.id),
        "success_redirect_url": "https://web-production-f81a1.up.railway.app/dashboard/",
        "bypass_success_screen": True,
    }

    response = requests.post(
        "https://api9.unipile.com:13973/api/v1/hosted/accounts/link",
        json=payload,
        headers=headers
    )

    try:
        data = response.json()
        # Unipile encapsule sa réponse dans le champ "error", qui est en fait un JSON stringifié 🤯
        if "url" in data:
            return redirect(data["url"])
        elif "error" in data:
            inner = json.loads(data["error"])
            return redirect(inner["url"])
        else:
            return redirect("dashboard")  # sécurité : au cas où il n'y a rien
    except Exception as e:
        print("Erreur de parsing Unipile :", e)
        return redirect("dashboard")


@csrf_exempt
def unipile_callback(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_id = int(data.get("name"))  # name = user.id envoyé à l'étape de création
            account_id = data.get("account_id")
            provider = data.get("provider", "LINKEDIN")

            user = CustomUser.objects.get(id=user_id)

            if not account_id or not user_id:
                return JsonResponse({"error": "Missing account_id or user_id"}, status=400)

            LinkedAccount.objects.update_or_create(
                user=user,
                defaults={"account_id": account_id, "provider": provider}
            )

            return HttpResponse(status=200)

        except Exception as e:
            print("Erreur callback Unipile :", e)
            return HttpResponse("Erreur interne", status=500)

    return HttpResponse("Méthode non autorisée", status=405)


@login_required
def new_prospection_view(request):
    if request.method == "POST":
        form = NewProspectionForm(request.POST)
        if form.is_valid():
            prospection = form.save(commit=False)
            prospection.user = request.user
            prospection.is_active = False  # on attend la confirmation
            prospection.save()
            return redirect("confirm_prospection", pk=prospection.pk)
    else:
        form = NewProspectionForm()

    return render(request, "accounts/new_prospection.html", {"form": form})


@login_required
def toggle_prospection(request, pk):
    prospection = get_object_or_404(ProspectionSession, pk=pk, user=request.user)

    if request.method == "POST":
        prospection.is_active = not prospection.is_active
        prospection.save()

    return redirect("dashboard")


@login_required
def confirm_prospection_view(request, pk):
    prospection = get_object_or_404(ProspectionSession, pk=pk, user=request.user)
    return render(request, "accounts/confirm_prospection.html", {
        "prospection": prospection
    })


@login_required
@require_POST
def launch_prospection_view(request, pk):
    """
    Active simplement la campagne sans importer les profils.
    La logique d'envoi sera gérée par la commande automatisée.
    """
    prospection = get_object_or_404(ProspectionSession, pk=pk, user=request.user)

    prospection.is_active = True
    prospection.current_page = 1
    prospection.position_in_page = 0
    prospection.save()

    messages.success(request, "La campagne a été activée. Les invitations commenceront à être envoyées automatiquement.")
    return redirect("dashboard")


@login_required
def prospection_detail_view(request, pk):
    prospection = get_object_or_404(ProspectionSession, pk=pk, user=request.user)
    targets = prospection.targets.all()

    return render(request, "accounts/prospection_detail.html", {
        "prospection": prospection,
        "targets": targets
    })


@login_required
@require_POST
def delete_prospection_view(request, pk):
    """
    Supprime une campagne et toutes ses cibles associées.
    """
    prospection = get_object_or_404(ProspectionSession, pk=pk, user=request.user)
    prospection.delete()
    messages.success(request, "Campagne supprimée avec succès.")
    return redirect("dashboard")
