from django.contrib import admin
from .models import User, Listing, Bid, Comment  

class BidAdmin(admin.ModelAdmin):
    list_display = ('bidder', 'bidStarterAmount', 'listing')
    list_editable = ('bidStarterAmount',)
    search_fields = ('bidder__username', 'listing__name')

class CommentAdmin(admin.ModelAdmin):
    list_display = ('commenter', 'listing', 'commentContent')
    list_editable = ('commentContent',)
    search_fields = ('commenter__username', 'listing__name')

admin.site.register(User)
admin.site.register(Listing)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)