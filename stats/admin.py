from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import DailyStats, UserStats

@admin.register(DailyStats)
class DailyStatsAdmin(admin.ModelAdmin):
    list_display = ("user", "article", "date", "views", "reads")
    list_filter = ("date", "user")
    search_fields = ("user__username", "article__title")
    readonly_fields = ("date",)

@admin.register(UserStats)
class UserStatsAdmin(admin.ModelAdmin):
    list_display = ("user", "total_views", "total_reads", "total_followers", "updated_at")
    readonly_fields = ("updated_at",)