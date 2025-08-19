from django.db import models
from ecommerce.models import Product
from userauths.models import User
# Create your models here.


TYPE = (
    ("New Order" ,  "New Order"),
    ("Item Shipped" ,  "Item Shipped"),
    ("Item Delivered" ,  "Item Delivered"),
)

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlist')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Wishlist"

    def __str__(self):
        if self.product.name:
            return self.product.name
        else:
            return "Wishlist"
        
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    full_name = models.CharField(max_length=255, null=True, blank=True, default=None)
    address_line1 = models.CharField(max_length=255, blank=True, null=True, default=None)
    address_line2 = models.CharField(max_length=255, blank=True, null=True, default=None)
    phone = models.CharField(max_length=20, blank=True, null=True, default=None)
    city = models.CharField(max_length=100, blank=True, null=True, default=None)
    state = models.CharField(max_length=100 , blank=True, null=True, default=None)
    zip_code = models.CharField(max_length=20, blank=True, null=True, default=None)
    country = models.CharField(max_length=100, blank=True, null=True, default=None)
    email = models.EmailField(max_length=254, blank=True, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        verbose_name_plural = "Customer Address"
        
    def __str__(self):
        return self.full_name
    
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)     
    message = models.TextField()
    type = models.CharField(max_length=50, choices=TYPE, default=None)
    seen= models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Notifications"

    def __str__(self):
        return f"Notification for {self.user.username} - {self.type}"