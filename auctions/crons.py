from django.utils import timezone
from auctions.models import AuctionListing

# def mark_expired_listings_as_won():
#     current_time = timezone.now()
#     expired_listings = AuctionListing.objects.filter(end_time__lte=current_time)

#     for listing in expired_listings:
#         winning_bid = listing.bid_set.filter(bid_status='Won').first()
#         if winning_bid:
#             # Already marked as won, skip
#             continue
        
#         highest_bid = listing.bid_set.order_by('-amount').first()
#         if highest_bid:
#             highest_bid.bid_status = 'Won'
#             highest_bid.save()