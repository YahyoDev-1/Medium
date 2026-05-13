from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Bookmark, ReadingList, ReadingListItem, ArticleLike

@admin.register(ArticleLike)
class ArticleLikeAdmin(admin.ModelAdmin):
    list_display = ("user", "article", "created_at")
    search_fields = ("user__username", "article__title")

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ("user", "article", "created_at")
    search_fields = ("user__username", "article__title")

@admin.register(ReadingList)
class ReadingListAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "items_count", "is_private", "created_at")
    list_filter = ("is_private", "created_at")
    search_fields = ("name", "user__username")

    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = "Items"

@admin.register(ReadingListItem)
class ReadingListItemAdmin(admin.ModelAdmin):
    list_display = ("reading_list", "article", "created_at")
    search_fields = ("reading_list__name", "article__title")