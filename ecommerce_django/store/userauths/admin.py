from django.contrib import admin
from userauths.models import User, UserProfile



@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "username", "is_staff", "is_active")

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "mobile_number", "user_type", "created_at")


