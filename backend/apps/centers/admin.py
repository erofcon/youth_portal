from django.contrib import admin
from .models import District, YouthCenter, UserProfile


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ["name"]


@admin.register(YouthCenter)
class YouthCenterAdmin(admin.ModelAdmin):
    list_display = ["name", "district", "phone", "responsible_name"]
    list_filter = ["district"]
    search_fields = ["name", "address", "responsible_name"]


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "role", "center", "phone", "telegram_chat_id"]
    list_filter = ["role", "center"]
    search_fields = ["user__username", "phone", "telegram_chat_id"]
