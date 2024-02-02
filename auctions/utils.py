from .models import Listing, Comment, Bid, Category
from users.models import User
from distutils.util import strtobool
from django.db.models import Q, F, Max, Case, When, Value, IntegerField
from django.db.models.functions import Coalesce
from functools import reduce
from operator import and_, or_
import math
from django.contrib.auth.models import AnonymousUser
# Gets the list of active categories


def is_anonymous_user(user):
    if isinstance(user, AnonymousUser):
        return True


def get_field_name_display(field_name):
    # Remove underscores and capitalize each word
    formatted_data = ' '.join(word.capitalize()
                              for word in field_name.split('_'))
    return formatted_data


def user_has_bid(user, listing):
    if is_anonymous_user(user):
        return False
    if Bid.objects.filter(listing=listing, bid_by=user).exists():
        return True
    return False


def has_been_outbid(user, listing):
    if is_anonymous_user(user):
        return False

    auction_bid = Bid.objects.filter(
        listing=listing,
        bid_by=user,
        listing__buying_format__name='Auction'
    ).first()

    if auction_bid is not None and auction_bid.amount < listing.get_current_price:
        return auction_bid

    return False


def getAllCategories():
    return Category.objects.all()


def getComments(Listing):
    Comments = Comment.objects.filter(listing=Listing)
    return list(Comments)


def apply_filter(queryset, filters, max_price):
    q_objects = Q()
    for param, value in filters.items():
        if param == 'price_range':
            threshold = ((float(value[0])/100.0)*max_price)
            queryset_beyond_price = [
                query for query in queryset if query.get_current_price > threshold]
            queryset = queryset.exclude(pk__in=queryset_beyond_price)
        elif param == 'local_pickup':
            value = bool(strtobool(value[0]))
            queryset = queryset.filter(local_pickup=value)
        elif param == 'free_shipping':
            value = bool(strtobool(value[0]))
            queryset = queryset.filter(free_shipping=value)
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
            return self.listings.annotate(
                current_price=Coalesce(
                    Max('bid__amount', filter=~Q(bid=None)),
                    F('starting_price'),
                    output_field=IntegerField()
                )
            ).order_by('-current_price')[starting_index:ending_index]
        elif self.sort_option == 'low-to-high':
            return self.listings.annotate(
                current_price=Coalesce(
                    Max('bid__amount', filter=~Q(bid=None)),
                    F('starting_price'),
                    output_field=IntegerField()
                )
            ).order_by('current_price')[starting_index:ending_index]
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
