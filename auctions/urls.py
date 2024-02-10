from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("filter/", views.index, name='filter'),
    path("listing/<str:title>", views.view_listing, name="view-listing"),
    path("listing/<str:title>/bid/", views.view_listing,
         name="view-listing-with-bid-form"),
    path("make-purchase/<str:title>", views.make_purchase, name="make-purchase"),
    path("add-to-watchlist/<str:title>",
         views.add_to_watch_list, name="add-to-watchlist"),
    path("create-listing", views.create_listing, name="create-listing"),
    path("bids", views.index, name="user_bids"),
    path("counter-offers", views.counter_offers, name="counter-offers"),
    path("ongoing-bids", views.ongoing_bids, name="ongoing-bids"),
    path("search", views.search, name="search"),
    path("comment/<str:title>", views.comment, name="comment"),
]
