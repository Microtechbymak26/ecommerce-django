from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone 

# Create your models here.
class User(AbstractUser):

    username = models.CharField(max_length=150,null=True ,unique=True)
    email = models.EmailField(max_length=254,unique=True)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        email_username, _= self.email.split('@')
        if not self.username:
            self.username = email_username
        super(User,self).save(*args, **kwargs)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    user_type = models.CharField(max_length=50, choices=[('customer', 'Customer'), ('vendor', 'Vendor')], default='customer')
    shipping_address = models.TextField(blank=False, null=False)   # ✅ yahan add kiya
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    
    def save(self, *args, **kwargs):
        if not self.full_name:
            self.full_name = self.user.username
        super(UserProfile,self).save(*args, **kwargs)