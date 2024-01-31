# Generated by Django 5.0 on 2024-01-15 16:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0012_bid_payment_method'),
        ('users', '0009_cardpayment_card_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='bid',
            name='shipping_address',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bid', to='users.address'),
        ),
        migrations.AlterField(
            model_name='bid',
            name='payment_method',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bid', to='users.paymentmethod'),
        ),
    ]