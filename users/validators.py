from django.core.validators import RegexValidator

card_number_validator = RegexValidator(
    regex=r'^\d{16}$',
    message='Enter a valid 16-digit card number.'
)

cvc_validator = RegexValidator(
    regex=r'^\d{3}$',
    message='Enter a valid 3-digit CVC.'
)

expiration_date_validator = RegexValidator(
    regex=r'^(0[1-9]|1[0-2])\/\d{4}$',
    message='Enter a valid expiration date in the format MM/YYYY.'
)

phone_number_validator = RegexValidator(
    regex=r'^(?:\+88)?01[3-9]\d{8}$',
    message='Enter a valid Bangladeshi phone number.'
)