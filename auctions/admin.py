from django.contrib import admin
from .models import *


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'starting_price', 'get_current_price', 'category', 'buying_format',
                    'condition', 'location', 'free_shipping', 'local_pickup', 'active']
    list_filter = ['category', 'buying_format', 'condition',
                   'location', 'free_shipping', 'local_pickup', 'active']
    search_fields = ['title', 'description', 'listedBy__username']

    list_editable = ['starting_price', 'category', 'buying_format',
                     'condition', 'location', 'free_shipping', 'local_pickup', 'active']



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


@admin.register(BuyingFormat)
class BuyingFormatAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'action_name')


@admin.register(Condition)
class ConditionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
