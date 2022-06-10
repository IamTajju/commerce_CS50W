from django import forms
from django.forms import ModelForm, widgets
from django.forms.forms import Form
from .models import Comment, Listing, Bid


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
        fields = ['price']

        widgets = {
            'price': forms.NumberInput(attrs={'class': 'form-control'})
        }


class SearchForm(forms.Form):
    title = forms.CharField()


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']

        widgets = {
            'comment': forms.TextInput(attrs={'class': 'form-control'})
        }
