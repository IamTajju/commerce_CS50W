from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("verify-email/<uuid:token>/<str:username>/<str:type>",
         views.verify_email, name='verify-user'),
    path("profile", views.user_profile, name='profile'),
    path("google-auth-receiver", views.google_auth_receiver, name='google-auth'),
    path("change-password/<uuid:token>/<str:username>",
         views.change_or_create_password, name='change-password'),
    path("forgot-password", views.forgot_password, name='forgot-password'),
    path('add-payment-method', views.payment_method_form_view,
         name='add_payment_method'),
    path('add-payment-method/<str:redirect>', views.payment_method_form_view,
         name='add_payment_method_redirect'),
    path('add-shipping-address', views.shipping_address_form_view,
         name='add_shipping_address'),
    path('add-shipping-address/<str:redirect>', views.shipping_address_form_view,
         name='add_shipping_address_redirect'),

]
