from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse
from .models import *
from .forms import *
from .utils import *
from datetime import date
from django.db.models import Count, Sum
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, redirect
from django.conf import settings
from django.forms import inlineformset_factory
from .services import OfferServices, PurchaseServices
import logging
from itertools import zip_longest

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
def view_listing(request, id):
    # Listing details
    listing = get_object_or_404(Listing, id=id)
    additional_listing_images = ListingAdditionalImages.objects.filter(
        listing=listing)

    total_bids_offers = Bid.objects.filter(listing=listing).count(
    ) if listing.buying_format == Listing.BuyingFormat.AUCTION else Offer.objects.filter(listing=listing).count()
    response_context = {
        "listing": listing,
        "additional_listing_images": additional_listing_images,
        'comments': Comment.objects.filter(listing=listing),
        'similar_listings': Listing.objects.filter(
            category=listing.category, location=listing.location, active=True, purchased=False).exclude(id=id)[:8],
        'open_modal': False,
        # Set to True if the user is not anonymous
        'user_logged_in': not is_anonymous_user(request.user),
        'watchers': User.objects.filter(watchlist=listing).annotate(
            watchlist_count=Count('id')).count(),
        'total_bids_offers': total_bids_offers
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


# Make Purchase Transaction
@login_required(login_url=settings.LOGIN_URL)
def make_purchase(request, id):
    if request.method == "POST":
        listing = Listing.objects.get(id=id)

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

    return redirect('view-listing', id)


# Place comment on Listing Details page
@login_required(login_url=settings.LOGIN_URL)
def comment(request, id):
    if request.method == "POST":
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.cleaned_data
            new_comment = Comment(user=User.objects.get(username=request.user), listing=Listing.objects.get(
                id=id), comment=comment['comment'], date=date.today())
            new_comment.save()

    return redirect('view-listing', id)


# Adds Listing to Watchlist and returns to Listing Details Page
@login_required(login_url=settings.LOGIN_URL)
def add_to_watch_list(request, id):
    user = User.objects.get(username=request.user)
    item = Listing.objects.get(id=id)
    user.watchlist.add(item)
    user.save()
    return redirect('view-listing', id)


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
            return redirect('view-listing', listing.id)
    else:
        listing_form = ListingForm(user=request.user)
        images_formset = ListingAdditionalImagesFormSet(instance=Listing())

    return render(request, 'auctions/listing-form.html', {'listing_form': listing_form, 'images_formset': images_formset, 'header': header, 'action': 'create'})


# Form Page to Edit Listing Item
@login_required(login_url=settings.LOGIN_URL)
def edit_listing(request, id):
    listing = get_object_or_404(Listing, id=id, listed_by=request.user)
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
            return redirect('view-listing', listing.id)

        else:
            print(images_formset.error_class)
            print(images_formset.errors)
    else:
        listing_form = ListingForm(instance=listing, user=request.user)
        images_formset = formset(instance=listing)

    return render(request, 'auctions/listing-form.html', {'listing_form': listing_form, 'images_formset': images_formset, 'header': header, 'action': 'edit', 'id': id})


# View all active listings on sale
@login_required(login_url=settings.LOGIN_URL)
def view_seller_dashboard(request):
    listings = Listing.objects.filter(listed_by=request.user, purchased=False, active=True).annotate(
        watchlist_count=Count('user')
    )

    if not listings:
        return render(request, 'auctions/seller-dashboard.html', {"empty_message": "No Active Listings for Sale.", "sell": True})

    summary_stats = listings.aggregate(Sum('base_price'), Count('id'))
    total_listings = summary_stats['id__count']
    expected_revenue = format_price(summary_stats['base_price__sum'])
    return render(request, 'auctions/seller-dashboard.html', {'total_listings': total_listings, 'expected_revenue': expected_revenue, 'listings': listings})


# Close a listing
@login_required(login_url=settings.LOGIN_URL)
def close_listing(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id, listed_by=request.user)
    try:
        PurchaseServices.process_any_listing_close(listing)
        if listing.purchased:
            messages.success(
                request, "Congratulations your Listing has been sold!")
            return redirect("listing-history")
        else:
            messages.info(request, "Listing Closed Successfuly")
            return redirect("seller-dashboard")
    except Exception as e:
        logging.critical(e)
        messages.error(
            request, "There was an issue with the process. Please contact the service admistrator")
        return redirect("seller-dashboard")


# View all offers on any listing
@login_required(login_url=settings.LOGIN_URL)
def sellers_offers_list(request, listing_id):
    try:
        listing = Listing.objects.get(
            id=listing_id, listed_by=request.user, purchased=False, active=True)

        offers = Offer.objects.filter(listing=listing).order_by('-timestamp')
        counter_offer_forms = [CounterOfferForm(
            offer=offer) if offer.offer_status == Offer.OfferStatus.PENDING else None for offer in offers]

        offers_forms = zip(offers, counter_offer_forms)
        return render(request, "auctions/seller-offers-received.html", {'offers_forms': offers_forms, 'listing': listing})

    except ObjectDoesNotExist:
        return redirect("seller-dashboard")


@login_required(login_url=settings.LOGIN_URL)
def accept_offer(request, offer_id):
    offer = get_object_or_404(
        Offer, id=offer_id, listing__listed_by=request.user)

    try:
        OfferServices().process_offer_listing_sale(offer=offer)
        messages.success(
            request, f"Offer Accepted, Congratulations your Listing has been sold to {offer.buyer.username}")
        return redirect("listing-history")

    except ValidationError as v:
        print(v)
        messages.error(
            request, v)
        return redirect("seller-dashboard")

    except Exception as e:
        print(e)
        messages.error(
            request, "There was an issue with the purchase. Please contact the service admistrator")
        return redirect("seller-offers-received", offer.listing.id)


@login_required(login_url=settings.LOGIN_URL)
def reject_offer(request, offer_id):
    offer = get_object_or_404(
        Offer, id=offer_id, listing__listed_by=request.user)

    try:
        OfferServices().process_offer_reject(offer=offer)
        messages.info(request, f"Offer Rejected.")
        return redirect("seller-offers-received", offer.listing.id)

    except:
        messages.error(
            request, "There was an issue with transaction. Please contact the service admistrator")
        return redirect("seller-offers-received", offer.listing.id)


@login_required(login_url=settings.LOGIN_URL)
def accept_counter_offer(request, counter_offer_id):
    counter_offer = get_object_or_404(
        CounterOffer, id=counter_offer_id, offer__buyer=request.user)

    try:
        OfferServices().process_offer_listing_sale(counter_offer=counter_offer)
        messages.success(
            request, f"Counter offer Accepted, Congratulations you've purchased the listing!")
        return redirect('purchase-history')

    except ValidationError as v:
        print(v)
        messages.error(
            request, v)
        return redirect("buyer-dashboard")

    except Exception as e:
        print(e)
        messages.error(
            request, "There was an issue with the purchase. Please contact the service admistrator")
        return redirect("buyer-dashboard")


@login_required(login_url=settings.LOGIN_URL)
def reject_counter_offer(request, counter_offer_id):
    counter_offer = get_object_or_404(
        CounterOffer, id=counter_offer_id, offer__buyer=request.user)

    try:
        OfferServices().process_counter_offer_reject(counter_offer=counter_offer)
        messages.info(request, f"Counter Offer Rejected.")
        return redirect("buyer-dashboard")

    except Exception as e:
        print(e)
        messages.error(
            request, "There was an issue with transaction. Please contact the service admistrator")
        return redirect("buyer-dashboard")


@login_required(login_url=settings.LOGIN_URL)
def make_counter_offer(request, offer_id):
    if request.method == 'POST':
        offer = get_object_or_404(
            Offer, id=offer_id, listing__listed_by=request.user)
        counter_offer_form = CounterOfferForm(request.POST, offer=offer)

        if counter_offer_form.is_valid():
            counter_offer_form.save()
            messages.success(
                request, "Counter Offer sent to buyer successfully")
        else:
            messages.error(
                request, "Couldn't be counter please try again after some time.")

        return redirect("seller-offers-received", offer.listing.id)


@login_required(login_url=settings.LOGIN_URL)
def view_buyer_dashboard(request):
    offers = Offer.objects.filter(
        buyer=request.user, listing__active=True).order_by('-timestamp')
    bids = Bid.objects.filter(
        buyer=request.user, listing__active=True).order_by('-timestamp')

    return render(request, "auctions/buyer-dashboard.html", {
        "offers": offers,
        "bids": bids,
    })


@login_required(login_url=settings.LOGIN_URL)
def view_purchase_history(request):
    offers = Offer.objects.filter(
        buyer=request.user, listing__active=False).order_by('offer_status').order_by('-timestamp')
    bids = Bid.objects.filter(
        buyer=request.user, listing__active=False).order_by('bid_status').order_by('-timestamp')
    bins = BuyItNow.objects.filter(
        buyer=request.user, listing__active=False).order_by('-timestamp')
    purchases = zip_longest(offers, bids, bins, fillvalue=None)
    return render(request, "auctions/purchase-history.html", {
        "purchases": purchases
    })


@login_required(login_url=settings.LOGIN_URL)
def view_listing_history(request):
    listings = Listing.objects.filter(listed_by=request.user, active=False).annotate(
        watchlist_count=Count('user')
    ).order_by('-timestamp')
    if not listings:
        return render(request, 'auctions/listing-history.html', {"empty_message": "No Listing History.", "sell": True})

    summary_stats = listings.filter(purchased=True).aggregate(
        Sum('base_price'), Count('id'))
    total_listings_sold = summary_stats['id__count']
    total_revenue = format_price(summary_stats['base_price__sum'])
    return render(request, "auctions/listing-history.html", {"listings": listings, "total_sold": total_listings_sold, "total_revenue": total_revenue})


@login_required(login_url=settings.LOGIN_URL)
def view_watchlist(request):
    listings = request.user.watchlist.all().order_by('-timestamp')

    return render(request, "auctions/watchlist.html", {"listings": listings})


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
                "categories": Category.objects.all()
            })

    # If there's an issue, redirect to the Home page
    return HttpResponseRedirect(reverse("index"))
