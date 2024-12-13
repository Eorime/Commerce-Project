from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from decimal import Decimal

from .models import User, Listing, Bid, Comment, Watchlist, CATEGORY_CHOICES

def index(request):
    listings = Listing.objects.all()
    return render(request, "auctions/index.html", {
        "listings": listings,
    })

def listing(request, listing_id):
    listing = Listing.objects.get(id=listing_id)

    current_bid = None
    if request.user.is_authenticated:
        current_bid = Bid.objects.filter(
            listing=listing, 
            bidder=request.user
        ).order_by('-bidStarterAmount').first()
    
    
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "comments": listing.comments.all(),
        "bids": listing.bids.all()  
    })

@login_required(login_url="/login", redirect_field_name=None)
def close_auction(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    
    if request.user != listing.seller:
        messages.error(request, "Only the seller can close this auction.")
        return redirect('listing', listing_id=listing_id)
    
    if not listing.is_active:
        messages.warning(request, "This auction is already closed.")
        return redirect('listing', listing_id=listing_id)
    
    if listing.close_auction():
        messages.success(request, "Auction closed successfully!")
    else:
        messages.warning(request, "No bids found. Unable to close auction.")
    
    return redirect('listing', listing_id=listing_id)

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
    
    
@login_required(login_url="/login", redirect_field_name=None)
def create(request):
    if request.method == "POST":
        listingName = request.POST.get("name")
        listingDescription = request.POST.get("description")
        listingBid = request.POST.get("bid")
        listingImage = request.FILES.get("image")
        listingCategory = request.POST.get("category")
        errorMessage = "Please fill all fields."

        if request.user.is_authenticated:
            seller = request.user
        else:
            seller = None


        if listingName and listingDescription and listingBid:
            try:
                listing = Listing.objects.create(
                    name = listingName,
                    seller = seller,
                    description = listingDescription,
                    bid = listingBid,
                    category = listingCategory,
                    image = listingImage
                )
                return redirect("index")
                
            except Exception as e: 
                errorMessage = f"Error saving the listing, {e}"
                return render(request, "auctions/create.html", {
                    "error": errorMessage
                })
        else: 
           return render(request, "auctions/create.html", {
               "error": errorMessage,
                "categories": CATEGORY_CHOICES
           })
    else: 
        return render(request, "auctions/create.html", {
            "categories": CATEGORY_CHOICES
        })
    

def categories(response):
    return render(response, "auctions/categories.html",{
        "categories": CATEGORY_CHOICES
    })

def category_listings(request, category_name):
        valid_categories = [choice[0] for choice in CATEGORY_CHOICES]

        if category_name not in valid_categories:
            return render(request, "auctions/categories.html", {
                "error": "Category not found."
            })
        
        listings = Listing.objects.filter(category = category_name)

        return render(request, "auctions/categories.html", {
            "category_name": category_name,
            "listings": listings,
        })

@login_required(login_url="/login")
def bid(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    
    if request.method == "POST":
        try:
            bid_amount = Decimal(request.POST.get('bid_amount', '0'))
        except (TypeError, ValueError):
            messages.error(request, "Invalid bid amount.")
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "error": "Invalid bid amount."
            })
        
        # check if the bid meets minimum requirements
        if bid_amount < listing.bid:
            messages.error(request, f"Bid must be at least ${listing.bid}.")
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "error": f"Bid must be at least ${listing.bid}."
            })
        
        # checks if bid is higher than the existing ones
        existing_bids = Bid.objects.filter(listing=listing).order_by('-bidStarterAmount')
        if existing_bids.exists():
            highest_bid = existing_bids.first().bidStarterAmount
            if bid_amount <= highest_bid:
                messages.error(request, f"Bid must be higher than the current highest bid of ${highest_bid}.")
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "error": f"Bid must be higher than the current highest bid of ${highest_bid}."
                })
        
        bid = Bid.objects.create(
            bidder=request.user,
            listing=listing,
            bidStarterAmount=bid_amount
        )
        
        listing.bid = bid_amount
        listing.save()
        
        messages.success(request, "Bid placed successfully!")
        return HttpResponseRedirect(reverse('listing', args=[listing_id]))
    
    # if get request
    return render(request, "auctions/listing.html", {
        "listing": listing
    })

@login_required(login_url="/login")
def comment(request, listing_id):
    listing = Listing.objects.get(id=listing_id)

    if request.method == "POST":
        comment_content = request.POST.get('comment_content')

        if comment_content is not "":
            comment = Comment.objects.create(
            commenter = request.user,
            listing = listing,
            commentContent = comment_content  
        )

        return HttpResponseRedirect(reverse('listing', args=[listing_id]))
    
    return render(request, "auctions/listing.html", {
        "listing": listing
    })

#watchlist views 

@login_required(login_url="/login", redirect_field_name=None)
def add_to_watchlist(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    user = request.user

    # check if already in watchlist to avoid duplicates
    watchlist_item, created = Watchlist.objects.get_or_create(
        user=user, 
        listing=listing
    )
    
    if created:
        messages.success(request, f"{listing.name} added to your watchlist!")
    else:
        messages.info(request, f"{listing.name} is already in your watchlist.")

    return redirect('watchlist')

@login_required(login_url="/login", redirect_field_name=None)
def remove_from_watchlist(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    user = request.user

    deleted_count, _ = Watchlist.objects.filter(user=user, listing=listing).delete()
    
    if deleted_count:
        messages.success(request, f"{listing.name} removed from your watchlist.")
    else:
        messages.warning(request, f"{listing.name} was not in your watchlist.")

    return redirect('/watchlist/')

@login_required(login_url="/login", redirect_field_name=None)
def view_watchlist(request):
    # get the listings in the user's watchlist
    watchlistItems = Listing.objects.filter(watchlist__user=request.user)
    
    return render(request, "auctions/watchlist.html", {
        "watchlistItems": watchlistItems
    })