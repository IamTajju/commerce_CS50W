from .models import Listing, Comment, Bid, Category, PurchaseTransaction
from users.models import User
from distutils.util import strtobool
from django.db.models import Q, F, Max, Case, When, Value, IntegerField
from django.db.models.functions import Coalesce
from functools import reduce
from operator import and_, or_
import math
from .forms import BidForm, OfferForm, BuyItNowForm
from django.contrib.auth.models import AnonymousUser
# Gets the list of active categories


def format_price(price):
    suffixes = ['k', 'M', 'B', 'T']
    magnitude = 0
    while price >= 1000 and magnitude < len(suffixes) - 1:
        magnitude += 1
        price /= 1000

    return price if magnitude == 0 else f"{price:.0f}{suffixes[magnitude-1]}"


def is_anonymous_user(user):
    if isinstance(user, AnonymousUser):
        return True


def get_field_name_display(field_name):
    # Remove underscores and capitalize each word
    formatted_data = ' '.join(word.capitalize()
                              for word in field_name.split('_'))
    return formatted_data


class PurchaseFormManager:
    def __init__(self, user, listing, error_data, post_data):
        self.form_mapping = {
            Listing.BuyingFormat.AUCTION: BidForm,
            Listing.BuyingFormat.ACCEPT_OFFERS: OfferForm,
            Listing.BuyingFormat.BUT_IT_NOW: BuyItNowForm,
        }
        self.form_class = self.form_mapping.get(listing.buying_format)
        self.user = user
        self.listing = listing
        self.attempted_purchase = self.has_transaction()
        self.form = self.get_purchase_form(error_data, post_data)

    def is_seller(self):
        if self.listing.listed_by == self.user:
            return True
        return False

    def has_transaction(self):
        transaction_exists = self.form_class.Meta.model.objects.filter(
            buyer=self.user, listing=self.listing).exists()
        print(transaction_exists)
        return transaction_exists

    def get_previous_bid_if_outbid(self):
        if self.listing.buying_format == Listing.BuyingFormat.AUCTION and self.attempted_purchase:
            bid = self.user.bid_buyer.filter(listing=self.listing).first()
            return bid if bid.amount < self.listing.auction.highest_bid_amount else None
        return None

    def get_purchase_form(self, error_data, post_data):
        if self.is_seller() or is_anonymous_user(self.user):
            return None

        if error_data:
            return self.form_class(data=error_data, listing=self.listing, user=self.user)

        previous_bid = self.get_previous_bid_if_outbid()

        # For passing form user input from request.POST
        if post_data:
            return self.form_class(post_data, instance=previous_bid, listing=self.listing, user=self.user)

        # If user is making first purchase attempt for listing send new fresh form to create purchase
        if not self.attempted_purchase:
            return self.form_class(listing=self.listing, user=self.user)

        # If user has been outbid let user edit previous bid
        if previous_bid:
            return self.form_class(instance=previous_bid, listing=self.listing, user=self.user)

        # If there's no appropriate form class found, return None
        return None


def apply_filter(queryset, filters, max_price):
    q_objects = Q()
    for param, value in filters.items():
        if param == 'price_range':
            threshold = ((float(value[0])/100.0)*max_price)
            queryset_beyond_price = [
                query.pk for query in queryset if query.get_price > threshold]
            queryset = queryset.exclude(pk__in=queryset_beyond_price)
        elif param == 'local_pickup':
            value = bool(strtobool(value[0]))
            queryset = queryset.filter(local_pickup=value)
        elif param == 'free_shipping':
            value = bool(strtobool(value[0]))
            queryset = queryset.filter(free_shipping=value)
        elif param == 'buying_format':
            q_objects &= Q(**{f"{param}__in": value})
        else:
            q_objects &= Q(**{f"{param}__name__in": value})
    return queryset.filter(q_objects)


class Paginator:
    def __init__(self, current_page, listings, sort_option):
        self.num_of_items = 20
        self.listings = listings
        self.sort_option = sort_option
        self.num_of_pages = max(math.ceil(len(listings)/self.num_of_items), 1)
        if current_page > self.num_of_pages:
            self.current_page = self.num_of_pages
        else:
            self.current_page = current_page

    def has_listings(self):
        if not self.listings:
            return False
        return True

    def get_listings(self):
        starting_index = max((self.current_page-1), 0)*self.num_of_items
        ending_index = self.current_page*self.num_of_items
        if self.sort_option == 'high-to-low':
            return Listing.annotate_price(self.listings).order_by('-price')[starting_index:ending_index]
        elif self.sort_option == 'low-to-high':
            return Listing.annotate_price(self.listings).order_by('price')[starting_index:ending_index]
        return self.listings[starting_index:ending_index]

    def has_previous(self):
        if self.current_page > 1:
            return True
        return False

    def has_next(self):
        if self.current_page < self.num_of_pages:
            return True
        return False

    def get_page_numbers(self):
        if self.current_page == 1:
            return [i for i in range(self.current_page, min(self.current_page+3, self.num_of_pages+1))]
        elif self.current_page > 1 and self.current_page < self.num_of_pages:
            return [i for i in range(self.current_page-1, self.current_page+2)]
        elif self.current_page == self.num_of_pages:
            return [i for i in range(max(1, self.current_page-3), self.current_page+1)]
        else:
            return [i for i in range(self.current_page, self.num_of_pages+1)]
