from django.contrib import admin
from ecommerce.models import Category, Product, Gallery, Order, OrderItem, Cart, Variant, VariantItem, Review

# Register your models here.

class GalleryInline(admin.TabularInline):
    model = Gallery

class VariantInline(admin.TabularInline):  
    model = Variant

class VariantItemInline(admin.TabularInline):
    model = VariantItem

class categoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug')  
    prepopulated_fields = {'slug': ('title',)}  

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'prize', 'category', 'stock', 'regular_price', 'featured', 'vendor', 'date', 'status', 'created_at', 'updated_at')
    search_fields = ('name', 'category__title')
    list_filter = ('category', 'status', 'vendor')
    inlines = [GalleryInline,VariantInline]  
    list_editable = ('prize', 'stock', 'status')
    prepopulated_fields = {'slug': ('name',)}

class VariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'name', 'price', 'stock', 'created_at', 'updated_at')
    search_fields = ('product__name', 'name')
    inlines = [VariantItemInline]  


class VariantItemAdmin(admin.ModelAdmin):
    list_display = ('variant', 'title', 'content')  
    search_fields = ('variant__name', 'title')

class GalleryAdmin(admin.ModelAdmin):
    list_display = ('product', 'image', 'gallery_id', 'created_at')
    search_fields = ('product__name',)

class cartAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'quantity', 'created_at', 'updated_at', 'prize', 'sub_total', 'tax', 'total', 'size', 'color', 'cart_id')
    search_fields = ('product__name', 'user__username', 'cart_id')
    list_filter = ('created_at', 'product')  
    list_editable = ('quantity', 'prize', 'sub_total', 'tax', 'total')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'customer', 'initial_total', 'payment_method', 'order_status', 'created_at', 'updated_at')
    list_editable = ('order_status', 'payment_method')
    search_fields = ('order_id', 'customer__username')
    list_filter = ('order_status', 'payment_method')

class OrderItemAdmin(admin.ModelAdmin):
    
    list_display = ('item_id', 'order', 'product', 'qty', 'prize', 'created_at', 'updated_at')
    search_fields = ('item_id', 'order__order_id', 'product__name')
    list_filter = ('created_at',)  

class ReviewAdmin(admin.ModelAdmin):
   
    list_display = ('user', 'rating', 'product', 'created_at', 'updated_at')
    search_fields = ('product__name', 'user__username')
    list_filter = ('active', 'rating')


admin.site.register(Category, categoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Gallery, GalleryAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Cart, cartAdmin)
admin.site.register(Variant, VariantAdmin)
admin.site.register(VariantItem, VariantItemAdmin)
admin.site.register(Review, ReviewAdmin)
