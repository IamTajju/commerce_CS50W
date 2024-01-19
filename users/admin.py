from django.contrib import admin
from .models import *

admin.site.register(User)
admin.site.register(PaymentMethod)
admin.site.register(CardPayment)
admin.site.register(BkashPayment)
# Register your models here.
