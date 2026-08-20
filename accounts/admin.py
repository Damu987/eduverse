from django.contrib import admin
from .models import UserProfile

# Register your models here.
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):

    list_display=(
        'user',
        'role',
        'phone_number',
        'created_at',
    )

    list_filter = (
        'role',
        'created_at',
    )
    search_fields = (
        'user_username',
        'user_email',
        'phone_number',
    )

    ordering = (
        '-created_at',
    )
