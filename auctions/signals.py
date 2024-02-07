from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Bid, Listing, CounterOffer, BidStatus, CounterOfferStatus, BuyingFormat


@receiver(post_save, sender=Listing)
def mark_other_bids_on_listing_purchased(sender, instance, **kwargs):
    if instance.purchased:
        other_bids = Bid.objects.filter(
            listing=instance).exclude(bid_status='Won')
        other_bids.update(
            bid_status=BidStatus.objects.get_or_create(name='Lost')[0])
        instance.active = False


@receiver(post_save, sender=Bid)
def mark_listing_as_purchased_on_bid_won(sender, instance, **kwargs):
    if instance.bid_status == 'Won':
        instance.listing.purchased = True
        instance.listing.save()


@receiver(post_save, sender=Bid)
def mark_counter_offers_as_rejected_on_bid_lost(sender, instance, **kwargs):
    if instance.bid_status == 'Lost':
        other_counter_offers = CounterOffer.objects.filter(
            bid__listing=instance.listing)
        other_counter_offers.update(
            status=CounterOfferStatus.objects.get_or_create(name='Rejected')[0])


@receiver(post_save, sender=CounterOffer)
def mark_bids_on_counter_offer(sender, instance, **kwargs):
    bid = instance.bid
    if instance.status == 'Accepted':
        bid.bid_status = BidStatus.objects.get_or_create(name='Won')[0]
        bid.save()

    elif instance.status == 'Rejected':
        bid.bid_status = BidStatus.objects.get_or_create(name='Lost')[0]
        bid.save()

