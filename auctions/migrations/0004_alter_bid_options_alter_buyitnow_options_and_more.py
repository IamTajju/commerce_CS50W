# Generated by Django 5.0 on 2024-02-18 11:56

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_alter_auction_auction_status_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bid',
            options={'ordering': ['-timestamp']},
        ),
        migrations.AlterModelOptions(
            name='buyitnow',
            options={'ordering': ['-timestamp']},
        ),
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['-date']},
        ),
        migrations.AlterModelOptions(
            name='listing',
            options={'ordering': ['-timestamp']},
        ),
        migrations.AlterModelOptions(
            name='offer',
            options={'ordering': ['-timestamp']},
        ),
        migrations.AddField(
            model_name='listing',
            name='buyer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='purchased_listing', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='bid',
            name='listing',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s', to='auctions.listing'),
        ),
        migrations.AlterField(
            model_name='buyitnow',
            name='listing',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s', to='auctions.listing'),
        ),
        migrations.AlterField(
            model_name='offer',
            name='listing',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s', to='auctions.listing'),
        ),
    ]