from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse
from .models import *
from .forms import *
from .utils import *
from datetime import date
from django.db.models import Max, Count
from django.shortcuts import get_object_or_404
from django.conf import settings

# Homepage


def index(request):
    listings = Listing.objects.filter(active=True)
    categories = Listing.Category.choices
    buying_formats = Listing.BuyingFormat.choices
    conditions = Listing.Condition.choices
    locations = Listing.Location.choices
    max_price = Listing.get_highest_current_price()

    filters = {key.replace("[]", ""): value for key, value in dict(request.GET).items(
    ) if key != "page" and key != "sort"}
    filter_labels = [(label, label.replace("_", " "))
                     for label in filters if label != 'price_range']
    current_page_number = int(request.GET.get("page", 1))
    sort_option = request.GET.get("sort", "best-match")

    if filters:
        listings = apply_filter(listings, filters, max_price)

    paginator = Paginator(current_page_number, listings, sort_option)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'auctions/listings.html', {'paginator': paginator, 'filter_labels': filter_labels})

    return render(request, "auctions/index.html", {
        "paginator": paginator,
        "user": request.user,
        "categories": categories,
        'buying_formats': buying_formats,
        'conditions': conditions,
        'locations': locations,
        'max_price': max_price,
    }
    )


# Listing details page
def view_listing(request, title):
    listing = get_object_or_404(Listing, title=title)
    comment_form = CommentForm()
    comments = Comment.objects.filter(listing=listing)
    similar_listings = Listing.objects.filter(
        category=listing.category, location=listing.location).exclude(title=title)[:8]
    watchers = User.objects.filter(watchlist=listing).annotate(
        watchlist_count=Count('id')).count()
    total_bids = Bid.objects.filter(listing=listing).count()

    open_modal = False

    redirect = request.session.pop('listing_title', None)
    success_data = messages.get_messages(request)
    if redirect or success_data:
        open_modal = True

    # Create a new BidForm instance and set its errors
    bid_form = BidForm(listing=listing, user=request.user)

    # Retrieve bid form errors from the session
    error_data = request.session.pop('data', None)

    # If there are errors, update the form's errors dictionary
    if error_data:
        bid_form = BidForm(data=error_data, listing=listing, user=request.user)
        open_modal = True

    return render(request, "auctions/listing-details.html", {
        "listing": listing,
        'bid_form': bid_form,
        'comment_form': comment_form,
        'comments': comments,
        'similar_listings': similar_listings,
        'open_modal': open_modal,
        'user_has_bid': user_has_bid(request.user, listing),
        'watchers': watchers,
        'total_bids': total_bids
    }
    )


@login_required(login_url=settings.LOGIN_URL)
def place_bid(request, title):
    if request.method == "POST":
        listing = Listing.objects.get(title=title)
        form = BidForm(request.POST, listing=listing,
                       user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Bid/Offer placed successfully")
        else:
            print(form.errors)
            # Store form data in session and redirect to the view_listing view
            request.session['data'] = form.data

    return HttpResponseRedirect(reverse('view-listing', args=[title]))

# Place comment on Listing Details page


@login_required(login_url=settings.LOGIN_URL)
def comment(request, title):
    if request.method == "POST":
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.cleaned_data
            new_comment = Comment(user=User.objects.get(username=request.user), listing=Listing.objects.get(
                title=title), comment=comment['comment'], date=date.today())
            new_comment.save()

    return HttpResponseRedirect(reverse('view-listing', args=[title]))

# Adds Listing to Watchlist and returns to Listing Details Page


@login_required(login_url=settings.LOGIN_URL)
def add_to_watch_list(request, title):
    user = User.objects.get(username=request.user)
    item = Listing.objects.get(title=title)
    user.watchlist.add(item)
    user.save()
    return HttpResponseRedirect(reverse('view-listing', args=[title]))


# User's Watchlist Listings Page
@login_required(login_url=settings.LOGIN_URL)
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
@login_required(login_url=settings.LOGIN_URL)
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
@login_required(login_url=settings.LOGIN_URL)
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

    return view_listing(request, title)


# Closes a Listing
@login_required(login_url=settings.LOGIN_URL)
def closeListing(request, title):
    item = Listing.objects.get(title=title)
    item.active = False
    item.save()
    return view_listing(request, title)


# Summary page of all the user's bids
@login_required(login_url=settings.LOGIN_URL)
def user_bids(request):
    bids = Bid.objects.filter(bid_by=request.user)

    active_ao_bids = bids.filter(
        listing__active=True, listing__buying_format=Listing.BuyingFormat.ACCEPT_OFFER)
    closed_bids = bids.filter(listing__active=True)

    return render(request, "auctions/bids-table.html", {
        "active_ao_bids": active_ao_bids,
        "closed_bids": closed_bids,
    })


def search(request):
    if request.method == "POST":
        title = request.POST.get('title', '')
        listings = Listing.objects.filter(title__contains=title)

        # If only one Listing matches, redirect to that Listing's page
        if listings.count() == 1:
            listing = listings.first()
            return HttpResponseRedirect(reverse('listing', args=[listing.title]))

        # Otherwise, render a page with Listings that contain the search keyword
        else:
            return render(request, "auctions/searchResult.html", {
                "listings": listings,
                "categories": getAllCategories()
            })

    # If there's an issue, redirect to the Home page
    return HttpResponseRedirect(reverse("index"))
