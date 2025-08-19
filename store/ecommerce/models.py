from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.utils import timezone
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
from django.utils.timezone import now

# Importing the custom User model and UserProfile
from userauths.models import User, UserProfile


import shortuuid

STATUS = (
    ("Published","Published"),
    ("Draft","Draft"),
    ("Disabled","Disabled"),
)

RATING = (
     ("⭐","⭐")
    ,("⭐⭐","⭐⭐")
    ,("⭐⭐⭐","⭐⭐⭐")
    ,("⭐⭐⭐⭐","⭐⭐⭐⭐")
    ,("⭐⭐⭐⭐⭐","⭐⭐⭐⭐⭐")
)

# Create your models here.

class Category(models.Model):
    title = models.CharField(max_length=225)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['title']

class Product(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    description = CKEditor5Field('Text',config_name='extends',blank=True, null=True)

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    prize = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True, verbose_name='Sale Price')
    regular_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True, verbose_name='Regular Price')

    stock = models.PositiveIntegerField(default=0, null=True, blank=True)
    shipping = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True,verbose_name='Shipping Amount')

    status = models.CharField(max_length=20, choices=STATUS, default='Draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    featured = models.BooleanField(default=False, verbose_name='Marketplace Featured')

    vendor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    sku = ShortUUIDField(
        length=5,
        max_length=50,
        prefix='SKU-',
        unique=True,
        alphabet="1234567890"
    )

    slug = models.SlugField (null=True, blank=True)

    date = models.DateTimeField(default=timezone.now) 


    class Meta:
        ordering = ['-id']
        verbose_name_plural = "Products"


    def __str__(self):
        return self.name
    
    def average_rating(self):
        return Review.objects.filter(product=self).aggregate(avg_rating=models.Avg('rating'))['rating__avg'] 
    
    def review(self):
        return Review.objects.filter(product=self)
    
    def gallery(self):
        return Gallery.objects.filter(product=self)
    
    def variants(self):
        return Variant.objects.filter(product=self)
    

    def vendor_orders(self):
        return OrderItem.objects.filter(product=self,vendors=self.vendor)
    

    def average_rating(self):
        """
        Calculate numeric average rating from emoji-based ratings.
        """
        ratings = self.reviews.all().values_list('rating', flat=True)
        if not ratings:
            return None
        
        total = sum(len(r) for r in ratings)
        return total / len(ratings)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name) + "-" + str (shortuuid.uuid().lower()[:2])
        super(Product, self).save(*args, **kwargs)

    def discount_percent(self):
        if self.regular_price and self.prize < self.regular_price:
            return int((self.regular_price - self.prize) / self.regular_price * 100)
        return 0






class Variant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,null=True,related_name="variants" )  # related_name="variants" add kara hai
    name = models.CharField(max_length=1000, verbose_name="Variant Name", null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def items(self):
        return VariantItem.objects.filter(variant=self)
    
    def __str__(self):
        return self.name

class VariantItem(models.Model):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name='variant_items')
    title = models.CharField(max_length=1000, verbose_name="Item Title", null=True ,blank=True)
    content = models.CharField(max_length=1000, verbose_name="Item Content", null=True ,blank=True)


    def __str__(self):
        return self.variant.name



class Gallery(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    image = models.ImageField(upload_to='images')
    gallery_id = ShortUUIDField(length=6,max_length=10,alphabet="1234567890")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Gallery for {self.product.name} - image"
    
    class Meta:
        verbose_name_plural = " Gallery"
        # ordering = ['-created_at']



class Cart(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variants = models.TextField(null=True, blank=True)  # To store variant selections add kara hai
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=0,null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    prize = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    sub_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)  
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    size = models.CharField(max_length=100, null=True, blank=True)
    color = models.CharField(max_length=100, null=True, blank=True)
    shipping = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    cart_id = models.CharField(max_length=1000, null=True, blank=True)

    def __str__(self):
        return f'{self.cart_id} - {self.product.name}'
    

class Order(models.Model):
    vendors = models.ManyToManyField(User, blank=True)
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='customer', blank=True)
    sub_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    shipping = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    service_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Completed', 'Completed'), ('Failed', 'Failed')], default='Pending') 
    payment_method = models.CharField(max_length=50, choices=[('Credit Card', 'Credit Card'), ('PayPal', 'PayPal'), ('Bank Transfer', 'Bank Transfer')], default='Credit Card')
    order_status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Processing', 'Processing'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')], default='Pending')
    initial_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    address = models.ForeignKey("customer.Address", on_delete=models.SET_NULL, null=True, blank=True)
    order_id = ShortUUIDField(length=6, max_length=10, alphabet="1234567890", unique=True)
    payment_id = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Order"
        ordering = ['-created_at']

    def __str__(self):
        # Admin me readable string return kare
        items = OrderItem.objects.filter(order=self)
        products = ", ".join([str(item.product.name) for item in items])
        vendors = ", ".join([str(vendor.username) for vendor in self.vendors.all()])

        summary = f"Order {self.order_id}"
        if products:
            summary += f" | Products: {products}"
        if vendors:
            summary += f" | Vendors: {vendors}"
        
        return summary




class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    order_status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Processing', 'Processing'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')], default='Pending')
    shipping_service = models.CharField(max_length=100, choices=[('Standard', 'Standard'), ('Express', 'Express'), ('Overnight', 'Overnight')], default='Standard', null=True, blank=True)
    tracking_id = models.CharField(max_length=100, null=True, blank=True, default=None)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.IntegerField(default=0)
    variants = models.TextField(null=True, blank=True)  # To store variant selections add kara hai
    prize = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    sub_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    shipping = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    initial_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    saved = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    item_id = ShortUUIDField(length=6, max_length=10, alphabet="1234567890", unique=True)
    vendor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    date = models.DateTimeField(auto_now_add=True)

    def order_id(self):
        return f'{self.order.order_id} - {self.product.name}'
    
    def __str__(self):
        return self.item_id
    
    class Meta:
        ordering = ['-date']

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews')
    review = models.TextField(blank=True, null=True)
    reply = models.TextField(blank=True, null=True)
    rating = models.IntegerField(default=0)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    rating = models.CharField(max_length=10, choices=RATING, default="🧡🧡🧡🧡🧡")


    def __str__(self):
        return f"{self.user.username} - {self.product.name} Review"
    
    
