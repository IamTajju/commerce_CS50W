from django.contrib import admin
from .models import *


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'startBid', 'currentPrice', 'category', 'buying_format',
                    'condition', 'location', 'free_shipping', 'local_pickup', 'active']
    list_filter = ['category', 'buying_format', 'condition',
                   'location', 'free_shipping', 'local_pickup', 'active']
    search_fields = ['title', 'description', 'listedBy__username']

    def currentPrice(self, obj):
        return obj.get_current_price


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ['listing', 'bid_by', 'amount']
    list_filter = ['listing__title', 'bid_by__username']
    search_fields = ['listing__title', 'bid_by__username']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['listing', 'user', 'comment', 'date']
    list_filter = ['listing__title', 'user__username', 'date']
    search_fields = ['listing__title', 'user__username']
