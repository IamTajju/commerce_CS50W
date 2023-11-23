from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    # watchlist = models.ManyToManyField('Listing', null=True, blank=True)

    def __str__(self):
        return f"{self.username}"
