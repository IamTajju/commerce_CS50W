from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.base import Model
from django.db.models.deletion import CASCADE, SET_NULL
from django.db.models.fields import URLField


class User(AbstractUser):
    watchlist = models.ManyToManyField('Listing', null=True, blank=True)

    def __str__(self):
        return f"{self.username}"


class Listing(models.Model):
    title = models.CharField(max_length=64, primary_key=True)
    description = models.CharField(max_length=300)
    startBid = models.IntegerField()
    image = models.URLField(blank=True)
    listedBy = models.ForeignKey(
        User, on_delete=models.CASCADE)
    categories = (
        ('F', 'Fashion'),
        ('T', 'Toys'),
        ('E', 'Electronics'),
        ('H', 'Home')
    )
    category = models.CharField(
        max_length=1, choices=categories, null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title}"

    def getBids(self):
        allBids = Bid.objects.filter(listing=self)
        return allBids

    def getCurrentPrice(self):
        allBids = Bid.objects.filter(listing=self)
        maxBid = self.startBid
        for bid in allBids:
            if (bid.price > maxBid):
                maxBid = bid.price

        return maxBid

    def getWinner(self):
        allBids = Bid.objects.filter(listing=self)
        maxBid = self.startBid
        winner = ""
        for bid in allBids:
            if (bid.price > maxBid):
                maxBid = bid.price
                winner = bid.bidBy

        return winner

    def isValidBid(self, Bid):
        if (Bid.price < self.getCurrentPrice()):
            return False
        else:
            return True


class Bid(models.Model):
    price = models.IntegerField()
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="AllBids")
    bidBy = models.ForeignKey(
        User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Bid by:{self.bidBy} | Bid: {self.price} | On: {self.listing}"


class Comment(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE)
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE)

    comment = models.CharField(max_length=300, null=True)
    date = models.DateField(null=True)

    def __str__(self):
        return f"By: {self.user} | On: {self.listing}"
