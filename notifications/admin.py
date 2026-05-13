from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Notification, ReadingHistory, UserFollowing

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("recipient", "notification_type", "title", "is_read", "created_at")
    list_filter = ("notification_type", "is_read", "created_at")
    search_fields = ("title", "recipient__username", "sender__username")
    readonly_fields = ("created_at",)

@admin.register(ReadingHistory)
class ReadingHistoryAdmin(admin.ModelAdmin):
    list_display = ("user", "article", "viewed_at")
    list_filter = ("viewed_at",)
    search_fields = ("user__username", "article__title")

@admin.register(UserFollowing)
class UserFollowingAdmin(admin.ModelAdmin):
    list_display = ("follower", "following", "created_at")
    list_filter = ("created_at",)
    search_fields = ("follower__username", "following__username")