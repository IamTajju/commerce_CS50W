# Generated by Django 5.0 on 2024-01-12 07:39

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0011_alter_bid_bid_by_delete_address'),
        ('users', '0006_alter_user_email'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_option', models.CharField(choices=[('B', 'Bkash'), ('CC', 'Credit Card'), ('DC', 'Debit Card'), ('COD', 'Cash On Delivery')], max_length=256)),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='watchlist',
            field=models.ManyToManyField(blank=True, null=True, to='auctions.listing'),
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address_line_1', models.CharField(max_length=500)),
                ('address_line_2', models.CharField(max_length=500)),
                ('city', models.CharField(choices=[('D', 'Dhaka'), ('C', 'Chittagong'), ('R', 'Rajshahi'), ('K', 'Khulna'), ('B', 'Barisal'), ('S', 'Sylhet'), ('RG', 'Rangpur'), ('M', 'Mymensing')], default='D', max_length=256)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='BkashPayment',
            fields=[
                ('payment_method', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='users.paymentmethod')),
                ('phone_number', models.CharField(help_text='Enter a valid Bangladeshi phone number. (e.g., 017XXXXXXXX)', max_length=15, validators=[django.core.validators.RegexValidator(message='Enter a valid Bangladeshi phone number.', regex='^01[3-9]\\d{8}$')])),
            ],
        ),
        migrations.CreateModel(
            name='CardPayment',
            fields=[
                ('payment_method', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='users.paymentmethod')),
                ('card_number', models.CharField(help_text='Enter a valid 16-digit card number.', max_length=16, validators=[django.core.validators.RegexValidator(message='Enter a valid 16-digit card number.', regex='^\\d{16}$')])),
                ('cvc_code', models.CharField(help_text='Enter a valid 3-digit CVC.', max_length=3, validators=[django.core.validators.RegexValidator(message='Enter a valid 3-digit CVC.', regex='^\\d{3}$')])),
                ('expiration_date', models.CharField(help_text='Enter a valid expiration date in the format MM/YYYY.', max_length=7, validators=[django.core.validators.RegexValidator(message='Enter a valid expiration date in the format MM/YYYY.', regex='^(0[1-9]|1[0-2])\\/\\d{4}$')])),
            ],
        ),
        migrations.AddField(
            model_name='paymentmethod',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
