# Generated by Django 5.0 on 2024-02-02 13:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0024_alter_listing_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buyingformat',
            name='action_name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='listing',
            name='category',
            field=models.CharField(choices=[('F', 'Fashion'), ('T', 'Toys'), ('E', 'Electronics'), ('H', 'Home'), ('O', 'Others')], default='O', max_length=250),
        ),
    ]
