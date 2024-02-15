from django import forms
from django.forms import ModelForm, widgets
from django.forms.forms import Form
from .models import Comment, Listing, Bid, Offer, BuyItNow, Auction, ListingAdditionalImages, CounterOffer
from users.models import PaymentMethod, Address
from users.forms import FormErrorClassMixin
from django.forms import inlineformset_factory, BaseInlineFormSet
from .validators import PurchaseValidator
from django.db import transaction


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
        self.instance = kwargs.get('instance')

        super(ListingForm, self).__init__(*args, **kwargs)

        # If editing an existing instance, remove buying_format field from the form
        if self.instance.id:
            self.fields.pop('buying_format')

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
        validator = PurchaseValidator(
            listing=self.listing, user=self.user, cleaned_data=cleaned_data)
        try:
            validator.validate()
        except ValueError as error:
            self.add_error(validator.field_name, error)

        return cleaned_data

    def save(self, commit=True):
        purchase = super(PurchaseForm, self).save(commit=False)
        purchase.listing = self.listing
        purchase.buyer = self.user
        if commit:
            purchase.save()
        return purchase


class BidForm(FormErrorClassMixin, PurchaseForm):
    class Meta(PurchaseForm.Meta):
        model = Bid

    def save(self, commit=True):
        bid = super().save(commit=False)
        bid.auction = Auction.objects.get(listing=self.listing)
        if commit:
            bid.save()
        return bid


class OfferForm(FormErrorClassMixin, PurchaseForm):
    class Meta(PurchaseForm.Meta):
        model = Offer

    def clean(self):
        cleaned_data = super().clean()
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


class CounterOfferForm(ModelForm):
    class Meta:
        model = CounterOffer
        fields = ['counter_offer_amount']

        widgets = {
            'counter_offer_amount': forms.NumberInput(attrs={'class': 'form-control rounded-start', 'aria-label': 'amount', 'placeholder': '৳'}),
        }

    def __init__(self, *args, **kwargs):
        self.offer = kwargs.pop('offer', None)
        super(CounterOfferForm, self).__init__(*args, **kwargs)

    
    def save(self, commit=True):
        counter_offer = super(CounterOfferForm, self).save(commit=False)
        counter_offer.offer = self.offer
        if commit:
            counter_offer.save()
        return counter_offer
