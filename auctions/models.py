from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import User, Address, PaymentMethod
from django.db.models import Max, F, IntegerField, Q
from django.db.models.functions import Coalesce
from django.core.exceptions import ValidationError
import logging
from django.utils.translation import gettext_lazy as _


class EnumBase(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class Condition(EnumBase):
    pass


class Location(EnumBase):
    pass


class Category(EnumBase):
    pass


class Listing(models.Model):
    class BuyingFormat(models.TextChoices):
        BUT_IT_NOW = 'BIN', _('Buy It Now')
        AUCTION = 'A', _('Auction')
        ACCEPT_OFFERS = 'AO', _('Accept Offers')
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=400, blank=False)
    base_price = models.PositiveIntegerField()
    hero_image = models.ImageField(
        upload_to='listings/', max_length=250, default='listings/placeholder-image.png')
    listed_by = models.ForeignKey(
        User, on_delete=models.CASCADE)

    timestamp = models.DateTimeField(auto_now_add=True)

    category = models.ForeignKey(Category, on_delete=models.PROTECT)

    buying_format = models.CharField(
        max_length=3, choices=BuyingFormat.choices, default=BuyingFormat.AUCTION)

    condition = models.ForeignKey(Condition, on_delete=models.PROTECT)

    location = models.ForeignKey(Location, on_delete=models.PROTECT)

    free_shipping = models.BooleanField(default=False)

    local_pickup = models.BooleanField(default=False)

    active = models.BooleanField(default=True)

    purchased = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} - {self.buying_format}"

    def get_buying_format_action_name(self):
        action_names = {
            self.BuyingFormat.BUT_IT_NOW: 'Buy',
            self.BuyingFormat.AUCTION: 'Place Bid',
            self.BuyingFormat.ACCEPT_OFFERS: 'Make Offer',
        }
        return action_names.get(self.buying_format, None)

    @property
    def get_price(self):
        return self.auction.highest_bid_amount if self.buying_format == self.BuyingFormat.AUCTION else self.base_price

    @staticmethod
    def annotate_price(listings):
        return listings.annotate(
            price=Coalesce(
                Max('auction__highest_bid_amount', filter=~Q(bid=None)),
                F('base_price'),
                output_field=IntegerField()
            )
        )

    @classmethod
    def get_highest_price(cls):
        # Annotated listing with its maximum price
        listings_with_prices = cls.annotate_price(cls.objects.all())
        # Get the maximum price across all listings
        highest_price = listings_with_prices.aggregate(Max('price'))
        # Return 0 if there are no listings
        return highest_price['price__max'] or 0


class ListingAdditionalImages(models.Model):
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(
        upload_to='listings/', max_length=250)

    class Meta:
        verbose_name_plural = "Listing Additional Images"


class Auction(models.Model):
    class AuctionStatus(models.TextChoices):
        SOLD = 'S', _('Sold')
        ONGOING = 'O', _('Ongoing')
        CLOSED_WITHOUT_SALE = 'CWS', _('Closed Without Sale')

    listing = models.OneToOneField(
        Listing, on_delete=models.CASCADE, primary_key=True)
    end_date = models.DateTimeField()
    highest_bid_amount = models.PositiveIntegerField()
    auction_status = models.CharField(
        max_length=3, choices=AuctionStatus.choices, default=AuctionStatus.ONGOING)


class PurchaseTransaction(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()
    buyer = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='%(class)s_buyer')
    shipping_address = models.ForeignKey(
        Address, on_delete=models.PROTECT)
    payment_method = models.ForeignKey(
        PaymentMethod, on_delete=models.PROTECT)

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.buyer.get_full_name()} | {self.listing.title} | BDT {self.amount}"

    class Meta:
        abstract = True


class Bid(PurchaseTransaction):
    class BidStatus(models.TextChoices):
        WON = 'W', _("Won")
        LOST = 'L', _("Lost")
        ONGOING = 'O', _("Ongoing")

    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    bid_status = models.CharField(
        max_length=2, choices=BidStatus.choices, default=BidStatus.ONGOING)


class Offer(PurchaseTransaction):
    class OfferStatus(models.TextChoices):
        ACCEPTED = 'A', _('Accepted')
        REJECTED = 'R', _('Rejected')
        COUNTER = 'C', _('Counter')
        COUNTER_ACCEPTED = 'CA', _('Counter Accepted')
        COUNTER_REJECTED = 'CR', _('Counter Rejected')
        PENDING = 'P', _('Pending')

    offer_status = models.CharField(
        max_length=2, choices=OfferStatus.choices, default=OfferStatus.PENDING)


class CounterOffer(models.Model):
    class CounterOfferStatus(models.TextChoices):
        ACCEPTED = 'A', _('Accepted')
        REJECTED = 'R', _('Rejected')
        PENDING = 'P', _('Pending')

    offer = models.OneToOneField(
        Offer, on_delete=models.CASCADE, related_name='c')
    counter_offer_amount = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    counter_offer_status = models.CharField(
        max_length=2, choices=CounterOfferStatus.choices, default=CounterOfferStatus.PENDING)


class BuyItNow(PurchaseTransaction):
    pass


class Comment(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE)
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE)

    comment = models.CharField(max_length=300, null=True)
    date = models.DateField(null=True)

    def __str__(self):
        return f"By: {self.user} | On: {self.listing}"
