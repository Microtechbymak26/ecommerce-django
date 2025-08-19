from django.contrib import admin
from .models import Wishlist, Address, Notification
# Register your models here.

class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'address_line1', 'city', 'state', 'zip_code', 'country', 'created_at')
    search_fields = ('user__username', 'full_name', 'city', 'state')
    list_filter = ('country',)

class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    search_fields = ('user__username', 'product__name')
    list_filter = ('created_at',)

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'type', 'seen', 'created_at')
    search_fields = ('user__username', 'message', 'type')
    list_filter = ('type', 'seen')

admin.site.register(Wishlist, WishlistAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Notification, NotificationAdmin)
