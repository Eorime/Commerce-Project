from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

CATEGORY_CHOICES = [
    ("Electronics", "Electronics"),
    ("Books", "Books"),
    ("Household", "Household"),
    ("Furniture", "Furniture"),
    ("Clothing", "Clothing"),
    ("Other", "Other")
]

class User(AbstractUser):
    name = models.CharField(max_length=64)
    email = models.EmailField(max_length=64)
    password = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name}"

class Listing(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField()
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="listings",
    )
    bid = models.DecimalField(max_digits=10, decimal_places=2)
    comment = models.TextField()
    category = models.CharField(max_length=64, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to='listing_images/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    winner = models.ForeignKey(settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="won_auctions")

    def __str__(self):
        return f"{self.name}, {self.id}, seller: {self.seller}"
        
    def close_auction(self):
        highest_bid = self.bids.order_by('-bidStarterAmount').first()
        if highest_bid:
            self.winner = highest_bid.bidder
            self.bid = highest_bid.bidStarterAmount 
            self.is_active = False
            self.save()
            return True
        return False

class Bid(models.Model):
    bidder = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bids",
    )
    bidStarterAmount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")

    def save(self, *args, **kwargs):
        if not self.bidStarterAmount:
            self.bidStarterAmount = self.listing.bid 
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.bidStarterAmount} for {self.listing}"

class Watchlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="watchlist")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="watchlist")
    
    def __str__(self):
        return f"{self.user}- {self.listing.name}"

class Comment(models.Model):
    commenter = models.ForeignKey(settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="comments",
    )
    commentContent = models.TextField()
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")

    def save(self, *args, **kwargs):
        if not self.commentContent:
            self.commentContent = self.listing.comment
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Comment by {self.commenter} on {self.listing}"

# class Category(models.Model):
#     name = models.CharField()