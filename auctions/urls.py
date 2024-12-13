from django.urls import path
from django.conf import settings
from django.conf.urls.static import static



from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("categories", views.categories, name="categories"),
    path('category/<str:category_name>/', views.category_listings, name='category_listings'),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("bid/<int:listing_id>", views.bid, name="bid"),
    path("comment/<int:listing_id>", views.comment, name="comment"),
    # watchlist paths
    path("watchlist/", views.view_watchlist, name="watchlist"),
    path("watchlist/add/<int:listing_id>/", views.add_to_watchlist, name="add_to_watchlist"),
    path("watchlist/remove/<int:listing_id>/", views.remove_from_watchlist, name="remove_from_watchlist"),
    # close the auction
    path('close_auction/<int:listing_id>', views.close_auction, name='close_auction'),
]

if settings.DEBUG:  # Serve media files in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)