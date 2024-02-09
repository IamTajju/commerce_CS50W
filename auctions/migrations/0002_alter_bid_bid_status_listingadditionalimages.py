# Generated by Django 5.0 on 2024-02-09 13:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bid',
            name='bid_status',
            field=models.CharField(choices=[('W', 'Won'), ('L', 'Lost'), ('O', 'Ongoing')], default='O', max_length=2),
        ),
        migrations.CreateModel(
            name='ListingAdditionalImages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(max_length=250, upload_to='listings/')),
                ('listing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='auctions.listing')),
            ],
            options={
                'verbose_name_plural': 'Listing Additional Images',
            },
        ),
    ]