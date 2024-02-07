from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import User, Address, PaymentMethod
from django.db.models import Max
from django.core.exceptions import ValidationError
import logging


class EnumBase(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class BuyingFormat(EnumBase):
    action_name = models.CharField(max_length=50)


class Condition(EnumBase):
    pass


class Location(EnumBase):
    pass


class Category(EnumBase):
    pass


class Listing(models.Model):
    title = models.CharField(max_length=64, primary_key=True)
    description = models.CharField(max_length=300)
    starting_price = models.IntegerField()
    image = models.ImageField(
        upload_to='listings/', max_length=250, default='listings/placeholder-image.png')
    listed_by = models.ForeignKey(
        User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    category = models.ForeignKey(Category, on_delete=models.PROTECT)

    buying_format = models.ForeignKey(BuyingFormat, on_delete=models.PROTECT)

    condition = models.ForeignKey(Condition, on_delete=models.PROTECT)

    location = models.ForeignKey(Location, on_delete=models.PROTECT)

    free_shipping = models.BooleanField(default=False)

    local_pickup = models.BooleanField(default=False)

    active = models.BooleanField(default=True)

    purchased = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title}"

    def get_bids(self):
        all_bids = Bid.objects.filter(listing=self)
        return all_bids

    @property
    def get_current_price(self):
        max_bid = self.get_bids().aggregate(max_bid=Max('amount'))['max_bid']
        return max(self.starting_price, max_bid) if max_bid is not None else self.starting_price

    @staticmethod
    def get_highest_current_price():
        all_listings = Listing.objects.filter(active=True)
        highest_price = max(
            listing.get_current_price for listing in all_listings) if all_listings else 0
        return highest_price


class AuctionListing(Listing):
    end_time = models.DateTimeField()


class StatusBase(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class BidStatus(StatusBase):
    @classmethod
    def get_default_bid_status(cls):
        ongoing_status, created = cls.objects.get_or_create(
            name="Ongoing")
        return ongoing_status.id


class Bid(models.Model):
    amount = models.IntegerField()
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="bid")
    bid_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='bid')
    shipping_address = models.ForeignKey(
        Address, on_delete=models.PROTECT, related_name="bid")
    payment_method = models.ForeignKey(
        PaymentMethod, on_delete=models.PROTECT, related_name='bid')

    bid_status = models.ForeignKey(
        BidStatus, on_delete=models.SET_NULL, null=True, default=BidStatus.get_default_bid_status)

    def __str__(self):
        return f"Bid by:{self.bid_by} | Bid: {self.amount} | On: {self.listing}"

    def is_valid_bid(self):
        if self.amount > self.listing.get_current_price or self.listing.buying_format.name == 'Buy It Now':
            return True
        return False


    def save(self, *args, **kwargs):
        if self.listing.buying_format == BuyingFormat.objects.get(name='Buy It Now'):
            self.bid_status = BidStatus.objects.get_or_create(name='Won')[0]
        super().save(*args, **kwargs)


class CounterOfferStatus(StatusBase):
    @classmethod
    def get_default_counter_offer_status(cls):
        pending_response, created = cls.objects.get_or_create(
            name="Pending Counter Offer Response")
        return pending_response.id


class CounterOffer(models.Model):
    bid = models.OneToOneField(
        'Bid', on_delete=models.CASCADE, related_name='counter_offer')
    amount = models.IntegerField()
    status = models.ForeignKey(
        CounterOfferStatus, on_delete=models.SET_NULL, null=True, default=CounterOfferStatus.get_default_counter_offer_status)

    def __str__(self):
        return f"Counter Offer for Bid: {self.bid}"


class Comment(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE)
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE)

    comment = models.CharField(max_length=300, null=True)
    date = models.DateField(null=True)

    def __str__(self):
        return f"By: {self.user} | On: {self.listing}"
