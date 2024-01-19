from django import forms
from django.forms import ModelForm, widgets
from django.forms.forms import Form
from .models import Comment, Listing, Bid
from users.models import PaymentMethod, Address


class ListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'startBid',
                  'image', 'category']

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'startBid': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.URLInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'custom-select'})

        }


class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['amount', 'payment_method', 'shipping_address']

        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control rounded-start', 'aria-label': 'amount'}),
            'payment_method': forms.Select(attrs={'class': 'form-select rounded-start', 'aria-label': 'payment'}),
            'shipping_address': forms.Select(attrs={'class': 'form-select rounded-start', 'aria-label': 'address'})
        }

    def __init__(self, *args, **kwargs):
        self.listing = kwargs.pop('listing', None)
        self.user = kwargs.pop('user', None)
        super(BidForm, self).__init__(*args, **kwargs)

        # Filter payment methods based on the current user
        self.fields['payment_method'].queryset = PaymentMethod.objects.filter(
            user=self.user)
        self.fields['shipping_address'].queryset = Address.objects.filter(
            user=self.user)

        if self.listing.buying_format == Listing.BuyingFormat.BUY_IT_NOW:
            # If it's a Buy It Now listing, exclude the 'amount' field
            del self.fields['amount']

        if self.errors:
            self.fields['amount'].widget.attrs['class'] += ' is-invalid'

    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get('amount')

        if self.listing.buying_format == Listing.BuyingFormat.BUY_IT_NOW:
            # If it's a Buy It Now listing, use the startBid as the amount
            cleaned_data['amount'] = self.listing.startBid
        else:
            # Otherwise, perform the validation checks
            if amount is not None:
                if amount <= 0:
                    self.add_error(
                        'amount', 'Bid/Offer amount must be greater than 0.')

                if amount <= self.listing.get_current_price and self.listing.buying_format != Listing.BuyingFormat.BUY_IT_NOW:
                    self.add_error(
                        'amount', 'Bid/Offer amount must be greater than the current price.')

        return cleaned_data

    def save(self, commit=True):
        bid = super(BidForm, self).save(commit=False)
        bid.listing = self.listing
        bid.bid_by = self.user
        if commit:
            bid.save()

        return bid


class CommentForm(ModelForm): 
    class Meta:
        model = Comment
        fields = ['comment']

        widgets = {
            'comment': forms.TextInput(attrs={'class': 'form-control'})
        }
