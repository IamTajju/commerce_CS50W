from django.db import models
from django.contrib.auth.models import AbstractUser
import urllib.request
from django.core.files.base import ContentFile
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator, MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ValidationError
from django.utils import timezone

# Create your models here.


class User(AbstractUser):
    email = models.EmailField(unique=True)
    watchlist = models.ManyToManyField(
        'auctions.Listing', null=True, blank=True)
    is_oauth_registered = models.BooleanField(default=False)
    display_picture = models.ImageField(
        upload_to='display-pictures/', max_length=250, default='display-pictures/default-dp.png')

    email_verification_token = models.CharField(
        max_length=200, null=True, blank=True)
    forget_password_token = models.CharField(
        max_length=200, null=True, blank=True)

    previous_email = models.EmailField(null=True, default=None)

    def __str__(self):
        return f"{self.username}"

    def save_image_from_url(self, url):
        picture_path = f'{self.username}_profile_picture.jpg'
        picture_content = urllib.request.urlopen(url).read()
        picture_content_file = ContentFile(picture_content)
        self.display_picture.save(picture_path, picture_content_file)
        self.save()


class Address(models.Model):
    class City(models.TextChoices):
        DHAKA = 'D', _('Dhaka')
        CHITTAGONG = 'C', _('Chittagong')
        RAJSHAHI = 'R', _('Rajshahi')
        KHULNA = 'K', _('Khulna')
        BARISAL = 'B', _('Barisal')
        SYLHET = 'S', _('Sylhet')
        RANGPUR = 'RG', _('Rangpur')
        MYMENSING = 'M', _('Mymensing')

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address_line_1 = models.CharField(max_length=500)
    address_line_2 = models.CharField(max_length=500)
    city = models.CharField(
        max_length=256, choices=City.choices, default=City.DHAKA)

    def __str__(self):
        return f"{self.get_city_display()} - {self.address_line_1}, {self.address_line_2}"


class PaymentMethod(models.Model):
    class PaymentOption(models.TextChoices):
        BKASH = 'B', _('Bkash')
        CREDIT_CARD = 'CC', _('Credit Card')
        DEBIT_CARD = 'DC', _('Debit Card')
        COD = 'COD', _('Cash On Delivery')

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_option = models.CharField(
        max_length=256, choices=PaymentOption.choices)

    def __str__(self):
        if self.payment_option == self.PaymentOption.BKASH:
            return f"{self.get_payment_option_display()}-{self.bkashpayment.phone_number}"
        elif self.payment_option == self.PaymentOption.CREDIT_CARD or self.payment_option == self.PaymentOption.DEBIT_CARD:
            return f"{self.get_payment_option_display()}-{self.cardpayment.card_number}-{self.cardpayment.card_name}"

        else:
            return self.get_payment_option_display()


class CardPayment(models.Model):
    payment_method = models.OneToOneField(
        PaymentMethod, on_delete=models.CASCADE, primary_key=True)

    card_name = models.CharField(
        max_length=256, blank=False, null=False)

    card_number = models.CharField(max_length=16)

    cvc_code = models.CharField(max_length=3)

    expiration_date = models.CharField(max_length=7)

    @staticmethod
    def is_not_expired(expiration_date):
        if expiration_date:
            current_date = timezone.now()
            expiration_date = timezone.make_aware(
                timezone.datetime.strptime(expiration_date, '%m/%Y')
            )
            return expiration_date > current_date
        return False

    @staticmethod
    def is_luhn_valid(card_number):
        digits = [int(digit) for digit in card_number[::-1]]
        checksum = sum(digits[0::2]) + sum(sum(divmod(d * 2, 10))
                                           for d in digits[1::2])
        return checksum % 10 == 0


class BkashPayment(models.Model):
    payment_method = models.OneToOneField(
        PaymentMethod, on_delete=models.CASCADE, primary_key=True)

    phone_number = models.CharField(max_length=15)
