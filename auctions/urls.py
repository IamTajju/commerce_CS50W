from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("filter/", views.index, name='filter'),
    path("listing/<int:id>", views.view_listing, name="view-listing"),
    path("listing/<int:id>/open-modal/", views.view_listing,
         name="view-listing-with-open-modal"),
    path("make-purchase/<int:id>", views.make_purchase, name="make-purchase"),
    path("add-to-watchlist/<int:id>",
         views.add_to_watch_list, name="add-to-watchlist"),
    path("create-listing", views.create_listing, name="create-listing"),
    path("edit-listing/<int:id>", views.edit_listing, name="edit-listing"),
    path("seller-dashboard", views.view_seller_dashboard, name='seller-dashboard'),
    path("close-listing/<int:listing_id>", views.close_listing, name='close-listing'),
    path("seller-offers-received/<int:listing_id>", views.sellers_offers_list, name="seller-offers-received"),
    path("accept-offer/<int:offer_id>", views.accept_offer, name='accept-offer'),
    path("reject-offer/<int:offer_id>", views.reject_offer, name='reject-offer'),
    path("make-counter-offer/<int:offer_id>", views.make_counter_offer, name="make-counter-offer"),
    path("bids", views.index, name="user_bids"),
    path("counter-offers", views.counter_offers, name="counter-offers"),
    path("ongoing-bids", views.ongoing_bids, name="ongoing-bids"),
    path("search", views.search, name="search"),
    path("comment/<int:id>", views.comment, name="comment"),
]
