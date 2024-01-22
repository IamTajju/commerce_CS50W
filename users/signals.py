
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import User, PaymentMethod
from .utils import send_token
import uuid


@receiver(pre_save, sender=User)
def send_email_token(sender, instance, **kwargs):
    if instance.id is None:
        if not instance.is_oauth_registered:
            instance.is_active = False
            token = str(uuid.uuid4())
            instance.email_verification_token = token
            send_token(instance, token, 'email')

    else:
        previous_email = User.objects.get(id=instance.id).email
        if (instance.email != previous_email):
            instance.previous_email = previous_email
            instance.is_active = False
            token = str(uuid.uuid4())
            instance.email_verification_token = token
            send_token(instance, token, 'email')


@receiver(post_save, sender=User)
def create_payment_method(sender, instance, created, **kwargs):
    if created:
        PaymentMethod.objects.create(
            user=instance, payment_option=PaymentMethod.PaymentOption.COD)
