import requests
import json
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from .models import LinkedAccount, CustomUser
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decouple import config
from datetime import datetime, timedelta


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

    if linked_account:
        account_is_valid = is_linkedin_account_still_valid(linked_account.account_id)
        if not account_is_valid:
            linked_account.delete()
            linked_account = None  # On l’efface localement
    else:
        account_is_valid = False  # rien en base, donc pas valide

    return render(request, "accounts/dashboard.html", {
        "user": request.user,
        "linked_account": linked_account,
    })


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def connect_linkedin(request):
    expires_on = (datetime.utcnow() + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S.999Z")

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
        "notify_url": "https://bf09-2a01-e0a-1a4-6a40-1de2-d8cf-a2b0-8165.ngrok-free.app/unipile-callback/",
        "name": str(request.user.id),
        "success_redirect_url": "https://bf09-2a01-e0a-1a4-6a40-1de2-d8cf-a2b0-8165.ngrok-free.app/dashboard/",
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

            LinkedAccount.objects.update_or_create(
                user=user,
                defaults={"account_id": account_id, "provider": provider}
            )

            return HttpResponse(status=200)

        except Exception as e:
            print("Erreur callback Unipile :", e)
            return HttpResponse("Erreur interne", status=500)

    return HttpResponse("Méthode non autorisée", status=405)