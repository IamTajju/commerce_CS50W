# Generated by Django 5.0 on 2024-02-06 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0029_rename_bidstatus_counterofferstatus_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='BidStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
