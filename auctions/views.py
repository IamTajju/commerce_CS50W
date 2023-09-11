from typing import List
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import *
from .forms import *
from .utils import *
from datetime import date


# Homepage
def index(request, category=None):
    bidForm = BidForm()
    
    if category:
        listings = Listing.objects.filter(category=category).filter(active=True)
    else:
        listings = Listing.objects.filter(active=True)

    return render(request, "auctions/index.html", {
        "listings": listings,
        "bidForm": bidForm,
        "user": request.user,
        "categories": getAllCategories(),
        "categoryName": dict(Listing.Category.choices).get(category, '')
    }
    )


# Listing details page
def viewListingDetails(request, title):
    listing = Listing.objects.get(title=title)
    bidForm = BidForm()
    commentForm = CommentForm()

    # Get all other listings in same category to display in Similar Products section
    category = listing.category
    similarListings = Listing.objects.filter(category=category)

    # For checks in template
    lister = False
    winningBidder = False
    watchlistAdded = False

    # Checks if the lister is viewing listing page
    if (request.user == listing.listedBy):
        lister = True

    # Checks if the current user is the winner of the closed Listing
    if ((listing.active == False) and (request.user == listing.getWinner())):
        winningBidder = True

    # Checking for watchlist added
    query = User.objects.filter(watchlist=title)
    if query:
        watchlistAdded = True

    # Sets alert messages to empty string when page loads
    if request.method == "GET":
        request.session['failMessage'] = ""
        request.session['successMessage'] = ""

    # Get user prompts from bidding on listing
    try:
        successMessage = request.session['successMessage']
        failMessage = request.session['failMessage']
    except:
        successMessage = ""
        failMessage = ""

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "similarListings": similarListings,
        "bidForm": bidForm,
        "commentForm": commentForm,
        "failMessage": failMessage,
        "successMessage": successMessage,
        "lister": lister,
        "winningBidder": winningBidder,
        "watchlistAdded": watchlistAdded,
        "categories": getAllCategories(),
        "Comments": getComments(listing),
    }
    )

# Adds Listing to Watchlist and returns to Listing Details Page
@login_required(login_url="/login")
def addToWatchlist(request, title):
    user = User.objects.get(username=request.user)
    item = Listing.objects.get(title=title)
    user.watchlist.add(item)
    user.save()
    return viewListingDetails(request, title)


# User's Watchlist Listings Page
@login_required(login_url="/login")
def getWatchlist(request):
    bidForm = BidForm()
    user = User.objects.get(username=request.user)
    listings = user.watchlist.all()
    return render(request, "auctions/watchlist.html", {
        "listings": listings,
        "bidForm": bidForm,
        "categories": getAllCategories()
    })


# Form Page to Create New Listing Item
@login_required(login_url="/login")
def createListing(request):
    form = ListingForm()
    failMessage = ""
    successMessage = ""

    if request.method == "POST":
        form = ListingForm(request.POST)

        if form.is_valid():
            listing = form.cleaned_data
            newListing = Listing(title=listing['title'], description=listing['description'], startBid=listing['startBid'],
                                 image=listing['image'], listedBy=User.objects.get(username=request.user), category=listing['category'])
            newListing.save()
            successMessage = "New Listing Posted!"
        else:
            failMessage = "Please try again"

    return render(request, "auctions/createListing.html", {
        "form": form,
        "successMessage": successMessage,
        "failMessage": failMessage,
        "categories": getAllCategories()
    }
    )


# Places bid on listing details page
@login_required(login_url="/login")
def bids(request, title):
    if request.method == "POST":
        form = BidForm(request.POST)

        if form.is_valid():
            bid = form.cleaned_data

            currentBid = Listing.objects.get(title=title).getCurrentPrice()
            noOfBids = len(Listing.objects.get(title=title).getBids())

            # Checks if bid placed is higher than current winning bid or if its the valid first bid.
            if ((bid['price'] > currentBid) or (bid['price'] == currentBid) and (noOfBids == 0)):
                newBid = Bid(price=bid['price'], listing=Listing.objects.get(
                    title=title), bidBy=User.objects.get(username=request.user))
                newBid.save()
                # Stores the user prompts in sessions to let viewListingDetails view to access it.
                request.session['successMessage'] = "Bid Successfully Placed!"
                request.session['failMessage'] = ""

            else:
                request.session['failMessage'] = "Please place a higher bid."
                request.session['successMessage'] = ""

        else:
            request.session['failMessage'] = "Please try again"
            request.session['successMessage'] = ""

    return viewListingDetails(request, title)


# Closes a Listing
@login_required(login_url="/login")
def closeListing(request, title):
    item = Listing.objects.get(title=title)
    item.active = False
    item.save()
    return viewListingDetails(request, title)


# Summary page of all the user's bids
@login_required(login_url="/login")
def userBids(request):
    bids = Bid.objects.filter(bidBy=request.user)

    activeBids = []
    closedBids = []
    for bid in bids:
        if (bid.listing.active == True):
            activeBids.append(bid)
        else:
            closedBids.append(bid)

    return render(request, "auctions/bids.html", {
        "activeBids": activeBids,
        "closedBids": closedBids,
        "categories": getAllCategories()
    })


# Login Page
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


# Searches keyword to find matching Listings
def search(request):
    if request.method == "POST":
        title = request.POST.get('title', '')
        listings = Listing.objects.filter(
            title__contains=title)

        # If only one Listing matches redirects to that Listings page
        if len(listings) == 1:
            return viewListingDetails(request, listings[0].title)

        # Else renders a page with Listings that contain search keyword
        else:
            return render(request, "auctions/searchResult.html", {
                "listings": listings,
                "categories": getAllCategories()
            })

    # If there's an issue redirect to Home
    return HttpResponseRedirect(reverse("index"))


# Logs out
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


# Register Page
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

# Place comment on Listing Details page


@login_required(login_url="/login")
def comment(request, title):
    if request.method == "POST":
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.cleaned_data
            newComment = Comment(user=User.objects.get(username=request.user), listing=Listing.objects.get(
                title=title), comment=comment['comment'], date=date.today())
            newComment.save()

    return viewListingDetails(request, title)
