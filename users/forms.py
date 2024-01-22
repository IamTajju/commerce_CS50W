from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, UserChangeForm
from django.contrib.auth import get_user_model
from django.utils.functional import cached_property
from django.forms import FileInput
from .models import *
from .validators import *
from django.core.validators import EmailValidator


User = get_user_model()


class FormErrorClassMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields[field_name]
            field.widget.attrs['placeholder'] = field.label
            field.widget.attrs['class'] = 'form-control'
            if field_name in self.errors:
                field.widget.attrs['class'] += ' is-invalid'


class UserRegistrationForm(FormErrorClassMixin, UserCreationForm):
    display_picture = forms.ImageField(
        required=False, help_text='Optional. Upload a display picture.')

    class Meta:
        model = User
        fields = ['username', 'email',
                  'display_picture', 'password1', 'password2']


class UserPasswordChangeForm(FormErrorClassMixin, UserCreationForm):
    class Meta:
        model = User
        fields = ['password1', 'password2']


class UserUpdateForm(FormErrorClassMixin, UserChangeForm):
    display_picture = forms.ImageField(
        required=False, help_text='Optional. Upload a display picture.')

    class Meta:
        model = User
        fields = ['username', 'email', 'display_picture']

    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields[field_name]

            if self.initial.get('username', None):
                field.help_text = ""
                field.widget.attrs['placeholder'] = self.initial.get(
                    'username')

            elif self.initial.get('email', None):
                field.widget.attrs['placeholder'] = self.initial.get(
                    'email')

            if field_name == 'email':
                field.help_text = "Email change will temporarily deactivate your account."
                field.widget.attrs['aria-label'] = "Email"
                field.widget.attrs['aria-describedby'] = "basic-addon1"

            if field_name == 'username':
                field.help_text = "Username must be unique."
                field.widget.attrs['aria-label'] = "Username"
                field.widget.attrs['aria-describedby'] = "basic-addon1"

            if field_name == 'display_picture':
                field.help_text = "Upload JPG, GIF or PNG image. 300 x 300 required."
                field.widget.attrs['class'] = field.widget.attrs['class'] + \
                    " form-control-sm"

            if field_name == 'password':
                field.help_text = 'Requires email verification.'
                field.widget.attrs['class'] = 'form-control-plaintext'


class AddressForm(FormErrorClassMixin, forms.ModelForm):
    class Meta:
        model = Address
        fields = ['address_line_1', 'address_line_2', 'city']
        widgets = {
            'city': forms.Select(attrs={'class': 'form-select form-select-lg'}),
        }


class PaymentMethodForm(FormErrorClassMixin, forms.ModelForm):
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


class CardPaymentForm(FormErrorClassMixin, forms.ModelForm):

    card_number = forms.CharField(
        max_length=16, min_length=16, validators=[card_number_validator], help_text='Enter the 16-digit Card number', label='Card Number')

    cvc_code = forms.CharField(
        max_length=3, min_length=3, validators=[cvc_validator], help_text='Enter the 3-digit code from the back of your card.', label='CVC Code')

    expiration_date = forms.CharField(max_length=7, min_length=7, validators=[
                                      expiration_date_validator], help_text='Format MM/YYYY e.g. 09/2028', label='Expiration Date')

    class Meta:
        model = CardPayment
        fields = ['card_name', 'card_number', 'cvc_code', 'expiration_date']

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


class BkashPaymentForm(FormErrorClassMixin, forms.ModelForm):
    phone_number = forms.CharField(max_length=15, min_length=11, validators=[
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
