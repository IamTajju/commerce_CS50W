from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("listing/<str:title>", views.viewListingDetails, name="listing"),
    path("register", views.register, name="register"),
    path("categories/<category>", views.viewCategoryListings, name="categories"),
    path("addToWatchlist/<str:title>",
         views.addToWatchlist, name="addToWatchlist"),
    path("watchlist", views.getWatchlist, name="watchlist"),
    path("createListing", views.createListing, name="createListing"),
    path("bid/<str:title>", views.bids, name="bid"),
    path("closeListing/<str:title>", views.closeListing, name="close"),
    path("userBids", views.userBids, name="userBids"),
    path("search", views.search, name="search"),
    path("comment/<str:title>", views.comment, name="comment")
]
