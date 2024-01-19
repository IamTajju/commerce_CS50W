from auctions.models import Listing
from django.core.files import File
from django.core.files.images import ImageFile
from django.core.management import BaseCommand
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Set default image for all listings'

    def handle(self, *args, **options):
        # Define the default image path
        default_image_path = 'listings/placeholder-image.png'

        # Get all listings
        listings = Listing.objects.all()

        for listing in listings:
            # Construct the default image file path
            default_image_full_path = os.path.join(
                settings.MEDIA_ROOT, default_image_path)

            # Open the default image file and set it for the listing
            with open(default_image_full_path, 'rb') as default_image_file:
                listing.image.save(os.path.basename(
                    default_image_path), File(default_image_file), save=True)

            self.stdout.write(self.style.SUCCESS(
                f'Successfully set default image for listing: {listing.title}'))
