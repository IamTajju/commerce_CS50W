from django import forms
from django.forms import ModelForm, widgets
from django.forms.forms import Form
from .models import Comment, Listing, Bid, Offer, BuyItNow, Auction, ListingAdditionalImages
from users.models import PaymentMethod, Address
from users.forms import FormErrorClassMixin
from django.forms import inlineformset_factory, BaseInlineFormSet

class ListingForm(FormErrorClassMixin, ModelForm):
    hero_image = forms.ImageField(
        help_text='Upload a hero image for the main display.')

    class Meta:
        model = Listing
        fields = ['title', 'description', 'base_price',
                  'hero_image', 'category', 'buying_format', 'condition', 'location', 'free_shipping', 'local_pickup']

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'base_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.Select(attrs={'class': 'form-select'}),
            'condition': forms.Select(attrs={'class': 'form-select'}),
            'buying_format': forms.Select(attrs={'class': 'form-select'}),
            'free_shipping': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'local_pickup': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ListingForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        listing = super(ListingForm, self).save(commit=False)
        listing.listed_by = self.user
        if commit:
            listing.save()
        return listing


class ListingAdditionalImagesForm(FormErrorClassMixin, ModelForm):
    image = forms.ImageField(
        help_text='Upload additional images of your listing.')

    class Meta:
        model = ListingAdditionalImages
        fields = ['image']

class CustomInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        for form in self.forms:
            if form.cleaned_data.get('image') is None:
                self.forms.remove(form)

ListingAdditionalImagesFormSet = forms.inlineformset_factory(
    Listing, ListingAdditionalImages, form=ListingAdditionalImagesForm, extra=4, min_num=0, formset=CustomInlineFormSet)


class PurchaseForm(ModelForm):
    class Meta:
        fields = ['amount', 'payment_method', 'shipping_address']

        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control rounded-start', 'aria-label': 'amount'}),
            'payment_method': forms.Select(attrs={'class': 'form-select rounded-start', 'aria-label': 'payment'}),
            'shipping_address': forms.Select(attrs={'class': 'form-select rounded-start', 'aria-label': 'address'})
        }

    def __init__(self, *args, **kwargs):
        self.listing = kwargs.pop('listing', None)
        self.user = kwargs.pop('user', None)
        super(PurchaseForm, self).__init__(*args, **kwargs)

        # Filter payment methods based on the current user
        self.fields['payment_method'].queryset = PaymentMethod.objects.filter(
            user=self.user)
        self.fields['shipping_address'].queryset = Address.objects.filter(
            user=self.user)

    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get('amount')
        if amount is not None:
            if amount <= 0:
                self.add_error(
                    'amount', 'Bid/Offer amount must be greater than 0.')
        return cleaned_data

    def save(self, commit=True):
        purchase = super(PurchaseForm, self).save(commit=False)
        purchase.listing = self.listing
        purchase.bid_by = self.user
        if commit:
            purchase.save()

        return purchase


class BidForm(FormErrorClassMixin, PurchaseForm):
    class Meta(PurchaseForm.Meta):
        model = Bid

    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get('amount')
        if amount <= self.listing.auction.highest_bid_amount:
            self.add_error(
                'amount', 'Bid amount must be greater than the current price.')

        return cleaned_data

    def save(self, commit=True):
        bid = super(BidForm, self).save(commit=False)
        bid.auction = Auction.objects.get(listing=self.listing)
        if commit:
            bid.save()
        return bid


class OfferForm(FormErrorClassMixin, PurchaseForm):
    class Meta(PurchaseForm.Meta):
        model = Offer

    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get('amount')
        if amount <= self.listing.base_price:
            self.add_error(
                'amount', 'You Offer must be greater than the starting price.')

        return cleaned_data


class BuyItNowForm(FormErrorClassMixin, PurchaseForm):
    class Meta(PurchaseForm.Meta):
        model = BuyItNow

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        del self.fields['amount']

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data['amount'] = self.listing.base_price
        return cleaned_data


class CommentForm(FormErrorClassMixin, ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']

        widgets = {
            'comment': forms.TextInput(attrs={'class': 'form-control'})
        }
