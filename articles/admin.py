# Register your models here.

from django.contrib import admin
from .models import Article, Tag

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "status", "published_at")
    list_filter = ("status", "tags")
    search_fields = ("title", "body")
    prepopulated_fields = {"slug": ("title",)}

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}