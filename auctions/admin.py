from django.contrib import admin
from .models import *


@admin.register(Condition)
@admin.register(Category)
@admin.register(Location)
class EnumAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_editable = ('name',)


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Listing._meta.fields]
    list_filter = ['category', 'buying_format', 'condition',
                   'location', 'free_shipping', 'local_pickup', 'active']
    search_fields = ['title', 'description', 'listed_by__username']


@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Auction._meta.fields]
    list_filter = ['listing', 'auction_status']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['listing', 'user', 'comment', 'date']
    list_filter = ['listing__title', 'user__username', 'date']
    search_fields = ['listing__title', 'user__username']
