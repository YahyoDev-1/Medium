from django.contrib import admin
from django.utils.html import format_html
from .models import Article, Tag


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "status", "published_at", "cover_preview", "views_count")
    list_filter = ("status", "tags", "published_at")
    search_fields = ("title", "body")
    prepopulated_fields = {"slug": ("title",)}

    fieldsets = (
        ("Basic Info", {
            "fields": ("title", "slug", "excerpt", "author", "status")
        }),
        ("Content", {
            "fields": ("body",),
            "classes": ("wide",)
        }),
        ("Media", {
            "fields": ("cover_image",)
        }),
        ("Metadata", {
            "fields": ("tags", "views_count", "created_at", "updated_at", "published_at"),
            "classes": ("collapse",)
        })
    )

    readonly_fields = ("created_at", "updated_at", "views_count")

    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" width="80" height="80" style="border-radius:4px;object-fit:cover">',
                obj.cover_image.url
            )
        return "—"

    cover_preview.short_description = "Cover"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}