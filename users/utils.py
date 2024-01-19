import base64
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponseBadRequest
from google.oauth2 import id_token
from google.auth.transport import requests
import string
import random


def send_token(instance, token, type):
    current_site = settings.CURRENT_SERVER_URL
    message = f'Welcome to Auctions! Click on the following link to verify your email address {current_site}/users/verify-email/{token}/{instance.username}/{type}'
    subject = "Auction Email Verification"
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [instance.email]
    try:
        send_mail(subject, message, email_from, recipient_list)
    except Exception as e:
        print(e)


def get_user_data_from_google(request):
    csrf_token_cookie = request.COOKIES.get('g_csrf_token')
    if not csrf_token_cookie:
        return HttpResponseBadRequest('No CSRF token in Cookie.')
    csrf_token_body = request.POST.get('g_csrf_token')
    if not csrf_token_body:
        return HttpResponseBadRequest('No CSRF token in post body.')
    if csrf_token_cookie != csrf_token_body:
        return HttpResponseBadRequest('Failed to verify double submit cookie.')

    token = request.POST.get('credential')
    google_request = requests.Request()
    id_info = id_token.verify_oauth2_token(
        token, google_request, '100295696058-7iois28fokoq4u65v5jc1mhmk0feual0.apps.googleusercontent.com')

    id_info['username'] = id_info['email'].replace('@gmail.com', '') + str(''.join(random.choices(string.ascii_uppercase +
                                                                                                  string.digits, k=3)))
    return id_info
