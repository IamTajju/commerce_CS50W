from .models import Listing


class PurchaseValidator():
    def __init__(self, listing, user, cleaned_data):
        self.listing = listing
        self.user = user
        self.cleaned_data = cleaned_data
        self.field_name = None

    def validate(self):
        self.validate_amount()
        self.validate_user()

    def validate_amount(self):
        if self.listing.buying_format == Listing.BuyingFormat.BUT_IT_NOW:
            return True

        amount = self.cleaned_data.get('amount')
        self.field_name = 'amount'
        if amount <= 0:
            raise ValueError("Bid/Offer amount must be greater than 0.")

        if self.listing.buying_format == Listing.BuyingFormat.AUCTION and amount <= self.listing.auction.highest_bid_amount:
            raise ValueError("Bid must be greater than current price")

        if self.listing.buying_format == Listing.BuyingFormat.ACCEPT_OFFERS and amount < self.listing.base_price:
            raise ValueError(
                "Offer must be greater or equal to the stated base price.")

        return True

    def validate_user(self):
        self.field_name = 'buyer'
        if self.user == self.listing.listed_by:
            raise ValueError("Seller cannot make purchase on own listing.")

        return True
