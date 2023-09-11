from .models import Listing, Comment

# Gets the list of active categories


def getAllCategories():
    return list(Listing.Category.choices)


def getComments(Listing):
    Comments = Comment.objects.filter(listing=Listing)
    return list(Comments)
