from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import *
from datetime import timedelta
import logging
from .services import OfferServices, AuctionServices


@receiver(post_save, sender=Listing)
def create_auction(sender, instance, created, **kwargs):
    if created and instance.buying_format == Listing.BuyingFormat.AUCTION:
        AuctionServices.create_auction_on_listing_creation(instance)


@receiver(post_save, sender=Bid)
def update_auction_highest_bid(sender, instance, **kwargs):
    auction_instance = instance.auction 
    auction_instance.highest_bid_amount = instance.amount
    auction_instance.save()


@receiver(post_save, sender=CounterOffer)
def update_offer_status_on_counter_create(sender, instance, created, **kwargs):
    if created:
        OfferServices.process_counter_offer_creation(instance)


        
