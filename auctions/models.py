from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import User, Address, PaymentMethod
from django.db.models import Max
from django.core.exceptions import ValidationError


class Listing(models.Model):
    title = models.CharField(max_length=64, primary_key=True)
    description = models.CharField(max_length=300)
    startBid = models.IntegerField()
    image = models.ImageField(
        upload_to='listings/', max_length=250, default='listings/placeholder-image.png')
    listedBy = models.ForeignKey(
        User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    class Category(models.TextChoices):
        FASHION = 'F', _('Fashion')
        TOYS = 'T', _('Toys')
        ELECTRONICS = 'E', _('Electronics')
        HOME = 'H', _('Home')
        OTHERS = 'O', _('Others')

    class BuyingFormat(models.TextChoices):
        AUCTION = 'A', _('Auction')
        BUY_IT_NOW = 'BIN', _('Buy It Now')
        ACCEPT_OFFER = 'AO', _('Accept Offer')

    class Condition(models.TextChoices):
        NEW = 'N', _('New')
        GOOD_R = 'G_R', ('Good - Refurbished')
        USED = 'U', ('Used')

    class Location(models.TextChoices):
        DHAKA = 'D', _('Dhaka')
        CHITTAGONG = 'C', _('Chittagong')
        RAJSHAHI = 'R', _('Rajshahi')
        KHULNA = 'K', _('Khulna')
        BARISAL = 'B', _('Barisal')
        SYLHET = 'S', _('Sylhet')
        RANGPUR = 'RG', _('Rangpur')
        MYMENSING = 'M', _('Mymensing')

    category = models.CharField(
        max_length=250, choices=Category.choices, default=Category.OTHERS)

    buying_format = models.CharField(
        max_length=250, choices=BuyingFormat.choices, default=BuyingFormat.AUCTION)

    condition = models.CharField(
        max_length=250, choices=Condition.choices, default=Condition.GOOD_R)

    location = models.CharField(
        max_length=250, choices=Location.choices, default=Location.DHAKA)

    free_shipping = models.BooleanField(default=False)

    local_pickup = models.BooleanField(default=False)

    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title}"

    def get_bids(self):
        all_bids = Bid.objects.filter(listing=self)
        return all_bids

    @property
    def get_current_price(self):
        max_bid = self.get_bids().aggregate(max_bid=Max('amount'))['max_bid']
        return max(self.startBid, max_bid) if max_bid is not None else self.startBid

    @staticmethod
    def get_highest_current_price():
        all_listings = Listing.objects.filter(active=True)
        highest_price = max(
            listing.get_current_price for listing in all_listings) if all_listings else 0
        return highest_price


class Bid(models.Model):
    amount = models.IntegerField()
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="bid")
    bid_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='bid')
    shipping_address = models.ForeignKey(
        Address, on_delete=models.CASCADE, related_name="bid")
    payment_method = models.ForeignKey(
        PaymentMethod, on_delete=models.CASCADE, related_name='bid')

    def __str__(self):
        return f"Bid by:{self.bid_by} | Bid: {self.amount} | On: {self.listing}"

    def is_valid_bid(self):
        if self.amount > self.listing.get_current_price or self.listing.buying_format == Listing.BuyingFormat.BUY_IT_NOW:
            return True
        return False


class Comment(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE)
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE)

    comment = models.CharField(max_length=300, null=True)
    date = models.DateField(null=True)

    def __str__(self):
        return f"By: {self.user} | On: {self.listing}"
