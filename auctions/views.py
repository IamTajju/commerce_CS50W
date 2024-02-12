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
from django.forms import inlineformset_factory


# Homepage
def index(request):
    listings = Listing.objects.filter(active=True)
    categories = Category.objects.all()
    buying_formats = Listing.BuyingFormat.choices
    conditions = Condition.objects.all()
    locations = Location.objects.all()
    max_price = Listing.get_highest_price()

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
        return render(request, 'auctions/filtered-listings.html', {'paginator': paginator, 'filter_labels': filter_labels})

    return render(request, "auctions/index.html", {
        "paginator": paginator,
        "user": request.user,
        "categories": categories,
        'buying_formats': buying_formats,
        'conditions': conditions,
        'locations': locations,
        'max_price': max_price,
        'max_price_view': format_price(max_price),
    }
    )


# Listing details page
def view_listing(request, title):
    # Listing details
    listing = get_object_or_404(Listing, title=title)
    additional_listing_images = ListingAdditionalImages.objects.filter(
        listing=listing)

    response_context = {
        "listing": listing,
        "additional_listing_images": additional_listing_images,
        'comments': Comment.objects.filter(listing=listing),
        'similar_listings': Listing.objects.filter(
            category=listing.category, location=listing.location).exclude(title=title)[:8],
        'open_modal': False,
        # Set to True if the user is not anonymous
        'user_logged_in': not is_anonymous_user(request.user),
        'watchers': User.objects.filter(watchlist=listing).annotate(
            watchlist_count=Count('id')).count(),
        'total_bids': Bid.objects.filter(listing=listing).count()
    }

    # Logged In User action
    if response_context['user_logged_in']:

        # Retrieve bid form errors from the session
        error_data = request.session.pop('data', None)

        purchase_manager = PurchaseFormManager(
            listing=listing, user=request.user, error_data=error_data, post_data=None)
        response_context['comment_form'] = CommentForm()

        # Open modal bc redirected from payment/shipping form
        if "/open-modal/" in request.path or error_data:
            response_context['open_modal'] = True

        response_context['purchase_manager'] = purchase_manager

    return render(request, "auctions/listing-details.html", response_context)


@login_required(login_url=settings.LOGIN_URL)
def make_purchase(request, title):
    if request.method == "POST":
        listing = Listing.objects.get(title=title)

        purchase_manager = PurchaseFormManager(
            listing=listing, user=request.user, error_data=None, post_data=request.POST)
        form = purchase_manager.form

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


# Form Page to Create New Listing Item
@login_required(login_url=settings.LOGIN_URL)
def create_listing(request):
    header = 'Create New Listing'
    if request.method == 'POST':
        listing_form = ListingForm(
            request.POST, request.FILES, user=request.user)
        images_formset = ListingAdditionalImagesFormSet(
            request.POST, request.FILES, instance=Listing())
        if listing_form.is_valid() and images_formset.is_valid():
            listing = listing_form.save()
            images_formset.instance = listing
            images_formset.save()
            messages.success(request, "Listing Created Successfuly")
            return HttpResponseRedirect(reverse('view-listing', args=[listing.title]))
            # Redirect to success page or another view
    else:
        listing_form = ListingForm(user=request.user)
        images_formset = ListingAdditionalImagesFormSet(instance=Listing())

    return render(request, 'auctions/listing-form.html', {'listing_form': listing_form, 'images_formset': images_formset, 'header': header, 'action': 'create'})


# Form Page to Edit Listing Item
@login_required(login_url=settings.LOGIN_URL)
def edit_listing(request, title):
    listing = get_object_or_404(Listing, title=title, listed_by=request.user)
    header = f'Edit Listing Item'
    formset = inlineformset_factory(
        Listing, ListingAdditionalImages, form=ListingAdditionalImagesForm, extra=0, min_num=0, formset=CustomInlineFormSet)

    if request.method == 'POST':
        listing_form = ListingForm(
            request.POST, request.FILES, user=request.user, instance=listing)

        images_formset = formset(
            request.POST, request.FILES, instance=listing)

        if listing_form.is_valid() and images_formset.is_valid():
            listing = listing_form.save()
            images_formset.instance = listing
            images_formset.save()
            messages.success(request, "Listing Edited Successfuly")
            return HttpResponseRedirect(reverse('view-listing', args=[listing.title]))

        else:
            print(images_formset.error_class)
            print(images_formset.errors)
    else:
        listing_form = ListingForm(instance=listing, user=request.user)
        images_formset = formset(instance=listing)

    return render(request, 'auctions/listing-form.html', {'listing_form': listing_form, 'images_formset': images_formset, 'header': header, 'action': 'edit', 'title': title})

# Summary page of all the user's bids


@login_required(login_url=settings.LOGIN_URL)
def counter_offers(request):
    bids = Bid.objects.filter(buyer=request.user)

    counter_offers = bids.filter(
        listing__active=True, listing__buying_format=Listing.BuyingFormat.ACCEPT_OFFERS)

    return render(request, "auctions/counter-offers.html", {
        "counter_offers": counter_offers,
    })


@login_required(login_url=settings.LOGIN_URL)
def ongoing_bids(request):
    bids = Bid.objects.filter(buyer=request.user)

    ongoing_bids = bids.filter(
        listing__active=True, listing__buying_format=Listing.BuyingFormat.AUCTION)

    return render(request, "auctions/ongoing-bids.html", {
        "ongoing_bids": ongoing_bids,
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
