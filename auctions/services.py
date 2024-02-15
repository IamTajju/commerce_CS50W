from .models import *
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from datetime import timedelta


class PurchaseServices:
    @staticmethod  # ALWAYS CALL WITHIN AN ATOMIC TRANSACTION
    def close_listing(listing, is_purchased):
        listing.active = False
        listing.purchased = is_purchased
        listing.save()

    @staticmethod
    def process_any_listing_close(listing):
        if listing.buying_format == Listing.BuyingFormat.AUCTION:
            AuctionServices.process_auction_close(listing)
        elif listing.buying_format == Listing.BuyingFormat.ACCEPT_OFFERS:
            OfferServices.process_offer_listing_close(listing)
        else:
            PurchaseServices.close_listing(listing=listing, is_purchased=False)


class AuctionServices(PurchaseServices):
    @classmethod
    def process_auction_close(cls, listing):
        with transaction.atomic():
            auction = listing.auction
            if auction.highest_bid_amount > listing.base_price:
                cls.close_all_losing_bids(auction)
                auction.auction_status = Auction.AuctionStatus.SOLD
                auction.save()
                cls.close_listing(listing=listing, is_purchased=True)
            else:
                auction.auction_status = Auction.AuctionStatus.CLOSED_WITHOUT_SALE
                auction.save()
                cls.close_listing(listing=listing, is_purchased=False)

    @staticmethod
    def close_all_losing_bids(auction):
        winning_bid = Bid.objects.get(
            auction=auction, amount=auction.highest_bid_amount)
        winning_bid.bid_status = Bid.BidStatus.WON
        winning_bid.save()
        losing_bids = Bid.objects.filter(
            auction=auction).exclude(id=winning_bid.id)
        losing_bids.update(bid_status=Bid.BidStatus.LOST)

    @staticmethod
    def create_auction_on_listing_creation(listing):
        # Calculate end date for the auction (1 week from listing timestamp)
        end_date = listing.timestamp + timedelta(weeks=1)

        Auction.objects.create(
            listing=listing,
            end_date=end_date,
            highest_bid_amount=listing.base_price,
            auction_status=Auction.AuctionStatus.ONGOING
        )


class OfferServices(PurchaseServices):
    # Primary Action Methods
    @classmethod
    def process_offer_listing_sale(cls, offer=None, counter_offer=None):
        with transaction.atomic():
            if counter_offer:
                # Update the status of the counter offer
                counter_offer.counter_offer_status = CounterOffer.CounterOfferStatus.ACCEPTED
                counter_offer.save()

                # Update the associated offer's offer status
                offer = counter_offer.offer
                offer.offer_status = Offer.OfferStatus.COUNTER_ACCEPTED
                offer.save()

            elif offer:
                # Update the status of the offer
                offer.offer_status = Offer.OfferStatus.ACCEPTED
                offer.save()

            else:
                raise Exception(
                    "Incorrect use of Offer Service's process listing sale method.")

            cls.find_and_close_all_losing_offers(winning_offer=offer)

            # Update listing status
            cls.close_listing(listing=offer.listing, is_purchased=True)

    @classmethod
    def process_offer_listing_close(cls, listing):
        with transaction.atomic():
            cls.close_all_losing_offers(listing=listing)
            cls.close_listing(listing=listing, is_purchased=False)

    @classmethod
    def process_offer_reject(cls, offer):
        offer.offer_status = Offer.OfferStatus.REJECTED
        offer.save()

    @classmethod
    def process_counter_offer_creation(cls, counter_offer):
        offer = counter_offer.offer
        offer.offer_status = Offer.OfferStatus.COUNTER
        offer.save()

    # Auxilary Methods
    @staticmethod  # ALWAYS CALL WITHIN AN ATOMIC TRANSACTION
    def close_all_losing_offers(winning_offer=None, listing=None):

        offers = Offer.objects.exclude(Q(offer_status=Offer.OfferStatus.REJECTED) |
                                       Q(offer_status=Offer.OfferStatus.COUNTER_REJECTED))
        # Fetch losing offers associated with the same listing
        if listing:
            losing_offers = offers.filter(listing=listing)
        elif winning_offer:
            losing_offers = offers.filter(
                listing=winning_offer.listing).exclude(id=winning_offer.id)

        else:
            raise ValueError(
                "Incorrect use of method. Need to pass either the winning offer or a Listing")

        # Update the status of losing offers to "rejected"
        for losing_offer in losing_offers:
            losing_offer.offer_status = Offer.OfferStatus.REJECTED
            losing_offer.save()

            # If a counter offer exists, mark it as rejected
            if hasattr(losing_offer, 'c') and losing_offer.c:
                losing_offer.c.counter_offer_status = CounterOffer.CounterOfferStatus.REJECTED
                losing_offer.c.save()
