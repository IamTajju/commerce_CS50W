from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("filter/", views.index, name='filter'),
    path("listing/<str:title>", views.view_listing, name="view-listing"),
    path("listing/<str:title>/bid/", views.view_listing,
         name="view-listing-with-bid-form"),
    path("place-bid/<str:title>", views.place_bid, name="place-bid"),
    path("add-to-watchlist/<str:title>",
         views.add_to_watch_list, name="add-to-watchlist"),
    path("watchlist", views.getWatchlist, name="watchlist"),
    path("createListing", views.createListing, name="createListing"),
    path("bid/<str:title>", views.bids, name="bid"),
    path("closeListing/<str:title>", views.closeListing, name="close"),
    path("bids", views.user_bids, name="user_bids"),
    path("search", views.search, name="search"),
    path("comment/<str:title>", views.comment, name="comment"),
]
