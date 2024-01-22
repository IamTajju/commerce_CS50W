from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from .models import *
from .forms import *
from .utils import get_user_data_from_google, send_token
from auctions.utils import get_field_name_display
import uuid
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import time


def login_view(request):
    logout(request)
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


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    logout(request)
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            # user.is_active = False
            user.save()
            # Redirect to verification pending page
            return render(request, 'users/check-email-page.html', {"title": 'Verify Your Email', "message": "Click on the link sent to your email address to verify your account."})
    else:
        form = UserRegistrationForm()

    return render(request, 'users/register.html', {'form': form})


def change_or_create_password(request, token, username):
    logout(request)
    user = User.objects.get(username=username)
    if request.method == 'GET':
        form = UserPasswordChangeForm()
        if str(user.forget_password_token) != str(token):
            return render(request, 'users/success-fail-page.html', {'success': False, 'title': 'Password Change Failed', 'message': 'Account has been locked for suspicious activity, contact site administrator for details.'})

    if request.method == 'POST':
        form = UserPasswordChangeForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save()
            user.is_active = True
            user.is_oauth_registered = False
            user.forget_password_token = None
            user.save()
            login(request, user)
            return render(request, 'users/success-fail-page.html', {'success': True, 'title': 'Password Change Process Completed', 'message': 'Your password has been changed successfully!'})

    return render(request, 'users/change-password.html', {'form': form, 'token': token, 'username': username})


def verify_email(request, token, username, type):
    logout(request)
    user = User.objects.get(username=username)

    if type == 'password':
        if str(user.forget_password_token) == str(token):
            return HttpResponseRedirect(reverse('change-password', args=[token, username]))

    if str(user.email_verification_token) == str(token):
        user.email_verification_token = None

        if user.is_oauth_registered:
            password_token = str(uuid.uuid4())
            user.forget_password_token = password_token
            user.save()
            return HttpResponseRedirect(reverse('change-password', args=[password_token, username]))

        user.is_active = True
        user.save()
        login(request, user)
        return render(request, 'users/success-fail-page.html', {'success': True, 'title': 'Email Verification Successful', 'message': 'Email verification process was successful, your account is active.'})
    else:
        return render(request, 'users/success-fail-page.html', {'success': False, 'title': 'Email Verification Failed', 'message': 'Email verification process failed, please register again.'})


def forgot_password(request):
    try:
        user = request.user
        password_token = str(uuid.uuid4())
        user.forget_password_token = password_token
        user.save()
        send_token(user, password_token, 'password')
        return render(request, 'users/check-email-page.html', {"title": 'Verify Your Email', "message": "Click on the link sent to your email address to change your password"})

    except Exception as e:
        return render(request, 'users/success-fail-page.html', {'success': False, 'title': 'Failed', 'message': 'Password change process failed, please register again.'})


@login_required(login_url=settings.LOGIN_URL)
def user_profile(request):
    user = request.user
    user_dict = {'username': user.username, 'email': user.email}
    form = UserUpdateForm(initial=user_dict)

    if request.method == 'POST':
        user_dict.update({item: value for item, value in request.POST.items()})
        if not request.FILES:
            form = UserUpdateForm(
                user_dict, instance=user)
        else:
            form = UserUpdateForm(
                user_dict, request.FILES, instance=user)

        if form.is_valid():
            form.save()
            if 'email' in form.changed_data:
                return HttpResponse(render(request, 'users/check-email-page.html', {"title": 'Verify Your Email', "message": "Click on the link sent to your new email address to verify your new email address and reactivate your account."}))
            if form.changed_data:
                messages.success(
                    request, f'{get_field_name_display(("_".join(field for field in form.changed_data)))} changed successfully!')
            return HttpResponseRedirect(reverse('profile'))

    elif request.method == 'GET' and 'remove_picture' in request.GET:
        # Remove the display picture and set the default image
        user.display_picture.delete()
        user.display_picture = 'display-pictures/default-dp.png'
        user.save()
        return redirect('profile')

    return render(request, 'users/profile-details.html', {'user': user, 'form': form, })


@csrf_exempt
def google_auth_receiver(request):
    user_info = get_user_data_from_google(request)
    try:
        user = User.objects.get(
            email=user_info['email'])
        if not user.is_active:
            return HttpResponse(render(request, 'users/check-email-page.html', {"title": 'Verify Your Email', "message": "Click on the link sent to your email address to verify your new email address and reactivate your account."}))
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    except User.DoesNotExist:
        # Create the user instance
        if User.objects.filter(previous_email=user_info['email']):
            return HttpResponse(render(request, 'users/check-email-page.html', {"title": 'Verify Your Email', "message": "Click on the link sent to your email address to verify your new email address and reactivate your account."}))

        user_instance = User.objects.create(
            username=user_info['username'],
            email=user_info['email'],
            first_name=user_info['given_name'],
            last_name=user_info['family_name'],
            is_oauth_registered=True
        )

        # Save Display picture
        user_instance.save_image_from_url(user_info['picture'])
        login(request, user_instance)
        return HttpResponseRedirect(reverse("index"))


@login_required(login_url=settings.LOGIN_URL)
def payment_method_form_view(request, redirect=None):
    payment_method_form = PaymentMethodForm()
    card_payment_form = CardPaymentForm()
    bkash_payment_form = BkashPaymentForm()
    if redirect:
        request.session['listing_title'] = redirect

    if request.method == 'POST':
        payment_method_form = PaymentMethodForm(request.POST)

        if payment_method_form.is_valid():
            payment_option = payment_method_form.cleaned_data['payment_option']
            user = request.user  # Assuming the user is authenticated

            # Save the PaymentMethod
            payment_method = payment_method_form.save(commit=False)
            payment_method.user = user
            payment_method.save()
            # Save the specific payment method based on the user's choice
            if payment_option == PaymentMethod.PaymentOption.CREDIT_CARD or payment_option == PaymentMethod.PaymentOption.DEBIT_CARD:
                card_payment_form = CardPaymentForm(request.POST)
                if card_payment_form.is_valid():
                    card_payment = card_payment_form.save(commit=False)
                    card_payment.payment_method = payment_method
                    card_payment.save()
                    messages.success(
                        request, 'Payment method added successfully.')

                else:
                    payment_method.delete()

            elif payment_option == PaymentMethod.PaymentOption.BKASH:
                bkash_payment_form = BkashPaymentForm(request.POST)
                if bkash_payment_form.is_valid():
                    bkash_payment = bkash_payment_form.save(commit=False)
                    bkash_payment.payment_method = payment_method
                    bkash_payment.save()
                    messages.success(
                        request, 'Payment method added successfully.')

                else:
                    payment_method.delete()

            # return redirect('bid_form')

    return render(request, 'users/payment-method-form.html', {
        'payment_method_form': payment_method_form,
        'card_payment_form': card_payment_form,
        'bkash_payment_form': bkash_payment_form,
    })


@login_required(login_url=settings.LOGIN_URL)
def shipping_address_form_view(request, redirect=None):
    form = AddressForm
    if redirect:
        request.session['listing_title'] = redirect

    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(
                request, 'Shipping Address was added successfully.')

    return render(request, 'users/shipping-address-form.html', {'form': form})
