from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("listing/<str:title>", views.view_listing, name="view-listing"),
    path("place-bid/<str:title>", views.place_bid, name="place-bid"),
    path("comment/<str:title>", views.comment, name="comment"),
    path("addToWatchlist/<str:title>",
         views.addToWatchlist, name="addToWatchlist"),
    path("watchlist", views.getWatchlist, name="watchlist"),
    path("createListing", views.createListing, name="createListing"),
    path("bid/<str:title>", views.bids, name="bid"),
    path("closeListing/<str:title>", views.closeListing, name="close"),
    path("userBids", views.userBids, name="userBids"),
    path("search", views.search, name="search"),
    path("filter/", views.index, name="filter"),
]
