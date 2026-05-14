from django.contrib import admin
from django.utils.html import format_html
from .models import Article, Tag


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "status", "member_only_badge", "published_at", "cover_preview", "views_count")
    list_filter = ("status", "is_member_only", "tags", "published_at")
    search_fields = ("title", "body")
    prepopulated_fields = {"slug": ("title",)}

    fieldsets = (
        ("Basic Info", {
            "fields": ("title", "slug", "excerpt", "author", "status", "is_member_only")
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

    def member_only_badge(self, obj):
        if obj.is_member_only:
            return format_html(
                '<span style="background:#fef3c7;color:#92400e;padding:.35rem .6rem;border-radius:999px;font-size:.8rem;font-weight:600">⭐ Member-only</span>')
        return "—"

    member_only_badge.short_description = "Type"

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