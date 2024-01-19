from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.utils.functional import cached_property
from django.forms import FileInput
from .models import *
from .validators import *


User = get_user_model()


class UserRegistrationForm(UserCreationForm):
    display_picture = forms.ImageField(
        required=False, help_text='Optional. Upload a display picture.')

    class Meta:
        model = User
        fields = ['username', 'email',
                  'display_picture', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields[field_name]
            field.widget.attrs['placeholder'] = field.label
            field.widget.attrs['class'] = 'form-control'

            if field_name in self.errors:
                field.widget.attrs['class'] += ' is-invalid'


class UserPasswordChangeForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(UserPasswordChangeForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields[field_name]
            field.widget.attrs['placeholder'] = field.label
            field.widget.attrs['class'] = 'form-control'

            if field_name in self.errors:
                field.widget.attrs['class'] += ' is-invalid'


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'display_picture']

    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields[field_name]
            field.widget.attrs['class'] = 'form-control'
            field.help_text = None
            field.label = None

            if self.initial.get('username', None):
                field.widget.attrs['placeholder'] = self.initial.get(
                    'username')

            elif self.initial.get('email', None):
                field.widget.attrs['placeholder'] = self.initial.get(
                    'email')

            if field_name == 'email':
                field.help_text = "Please enter a valid email address, email change process will deactivate your account till you've verified it"
                field.widget.attrs['aria-label'] = "Email"
                field.widget.attrs['aria-describedby'] = "basic-addon1"

            if field_name == 'username':
                field.widget.attrs['aria-label'] = "Username"
                field.widget.attrs['aria-describedby'] = "basic-addon1"

            if field_name in self.errors:
                field.widget.attrs['class'] += ' is-invalid'


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['address_line_1', 'address_line_2', 'city']
        widgets = {
            'address_line_1': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line_2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.Select(attrs={'class': 'form-select form-select-lg'}),
        }

    def __init__(self, *args, **kwargs):
        super(AddressForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields[field_name]
            if field_name in self.errors:
                field.widget.attrs['class'] += ' is-invalid'


class PaymentMethodForm(forms.ModelForm):
    class Meta:
        model = PaymentMethod
        fields = ['payment_option']
        widgets = {
            'payment_option': forms.Select(attrs={'class': 'form-select form-select-lg'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Exclude 'Cash On Delivery' from choices
        excluded_option = PaymentMethod.PaymentOption.COD
        self.fields['payment_option'].choices = [
            option for option in self.fields['payment_option'].choices if option[0] != excluded_option
        ]


class CardPaymentForm(forms.ModelForm):

    card_number = forms.CharField(
        max_length=16, min_length=16, validators=[card_number_validator], help_text='Enter the 16-digit Card number', label='Card Number')

    cvc_code = forms.CharField(
        max_length=3, min_length=3, validators=[cvc_validator], help_text='Enter the 3-digit code from the back of your card.', label='CVC Code')

    expiration_date = forms.CharField(max_length=7, min_length=7, validators=[
                                      expiration_date_validator], help_text='Format MM/YYYY e.g. 09/2028', label='Expiration Date')

    class Meta:
        model = CardPayment
        fields = ['card_name', 'card_number', 'cvc_code', 'expiration_date']

    def __init__(self, *args, **kwargs):
        super(CardPaymentForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields[field_name]
            field.widget.attrs['placeholder'] = field.label
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['aria-describedby'] = field.label

            if field_name in self.errors:
                field.widget.attrs['class'] += ' is-invalid'

    def clean_card_number(self):
        card_number = self.cleaned_data['card_number']
        if card_number and not CardPayment.is_luhn_valid(card_number):
            raise ValidationError('Invalid credit card number.')

        return card_number

    def clean_expiration_date(self):
        cleaned_data = super().clean()
        expiration_date = cleaned_data['expiration_date']
        if not CardPayment.is_not_expired(expiration_date):
            raise ValidationError('Card has expired.')

        return expiration_date


class BkashPaymentForm(forms.ModelForm):
    phone_number = forms.CharField(max_length=15, min_length=12, validators=[
        phone_number_validator],
        help_text='Enter a valid Bangladeshi phone number. (e.g., 017XXXXXXXX)',
        label='Bkash Number',
        widget=forms.TextInput(attrs={
            'class': 'form-control rounded-start',
            'placeholder': 'Enter your Bkash number',
            'aria-label': 'Bkash Number',
        }),)

    class Meta:
        model = BkashPayment
        fields = ['phone_number']

    def __init__(self, *args, **kwargs):
        super(BkashPaymentForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields[field_name]
            if field_name in self.errors:
                field.widget.attrs['class'] += ' is-invalid'
