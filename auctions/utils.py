from .models import Listing, Comment, Bid
from users.models import User
from faker import Faker
import random
from django.db.models import Q, F, Max, Case, When, Value, IntegerField
from django.db.models.functions import Coalesce
from functools import reduce
from operator import and_, or_
import math
# Gets the list of active categories

def get_field_name_display(field_name):
    # Remove underscores and capitalize each word
    formatted_data = ' '.join(word.capitalize() for word in field_name.split('_'))
    return formatted_data


def user_has_bid(user, listing):
    if Bid.objects.filter(listing=listing, bid_by=user).exists():
        return True
    return False


def getAllCategories():
    return list(Listing.Category.choices)


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
        else:
            q_objects &= Q(**{f"{param}__in": value})
    return queryset.filter(q_objects)


fake = Faker()

# Create users for listing ownership
users = User.objects.all()

# Function to create a Listing instance


def create_listing():
    title = fake.text(max_nb_chars=20)
    description = fake.text(max_nb_chars=150)
    start_bid = random.randint(10, 1000)
    image = fake.image_url()
    listed_by = random.choice(users)
    category = random.choice([choice[0]
                             for choice in Listing.Category.choices])
    buying_format = random.choice([choice[0]
                                  for choice in Listing.BuyingFormat.choices])
    condition = random.choice([choice[0]
                              for choice in Listing.Condition.choices])
    location = random.choice([choice[0]
                             for choice in Listing.Location.choices])
    free_shipping = fake.boolean()
    local_pickup = fake.boolean()
    active = fake.boolean()

    listing = Listing.objects.create(
        title=title,
        description=description,
        startBid=start_bid,
        image=image,
        listedBy=listed_by,
        category=category,
        buying_format=buying_format,
        condition=condition,
        location=location,
        free_shipping=free_shipping,
        local_pickup=local_pickup,
        active=active,
    )

    # Create bids for the listing
    num_bids = random.randint(0, 10)
    for _ in range(num_bids):
        bid_price = random.randint(start_bid, start_bid + 100)
        bid_by = random.choice(users)
        Bid.objects.create(listing=listing, price=bid_price, bidBy=bid_by)


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
                    Max('bid__price', filter=~Q(bid=None)),
                    F('startBid'),
                    output_field=IntegerField()
                )
            ).order_by('-current_price')[starting_index:ending_index]
        elif self.sort_option == 'low-to-high':
            return self.listings.annotate(
                current_price=Coalesce(
                    Max('bid__price', filter=~Q(bid=None)),
                    F('startBid'),
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
