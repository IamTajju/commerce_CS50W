from .models import Listing, Comment

# Gets the list of active categories


def getAllCategories():
    return list(Listing.objects.first().categories)


def getComments(Listing):
    Comments = Comment.objects.filter(listing=Listing)
    return list(Comments)
