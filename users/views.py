from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt
import jwt
from jwt.algorithms import get_default_algorithms
from google.oauth2 import id_token
from google.auth.transport import requests
from .models import *

# Create your views here.


def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "users/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "users/login.html")


# Logs out
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


# Register Page
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "users/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "users/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "users/register.html")


@csrf_exempt
def google_auth_receiver(request):
    csrf_token_cookie = request.COOKIES.get('g_csrf_token')
    if not csrf_token_cookie:
        return HttpResponseBadRequest('No CSRF token in Cookie.')
    csrf_token_body = request.POST.get('g_csrf_token')
    if not csrf_token_body:
        return HttpResponseBadRequest('No CSRF token in post body.')
    if csrf_token_cookie != csrf_token_body:
        return HttpResponseBadRequest('Failed to verify double submit cookie.')

    token = request.POST.get('credential')
    request = requests.Request()
    id_info = id_token.verify_oauth2_token(
        token, request, '100295696058-7iois28fokoq4u65v5jc1mhmk0feual0.apps.googleusercontent.com')

    print(id_info)
    return HttpResponse("ok")
