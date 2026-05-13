from django.db import models
from django.conf import settings
from articles.models import Article
from django.utils.text import slugify

class ArticleLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="likes")
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "article")

class Bookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookmarks")
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="bookmarked_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "article")
        ordering = ["-created_at"]

class ReadingList(models.Model):
    """
    A user-owned collection (list) of articles. Example: 'Reading list', 'Favorites'.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reading_lists")
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=180, blank=True)
    description = models.TextField(blank=True)
    is_private = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "name")
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:170]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.user})"

class ReadingListItem(models.Model):
    reading_list = models.ForeignKey(ReadingList, on_delete=models.CASCADE, related_name="items")
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="in_reading_lists")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("reading_list", "article")
        ordering = ["-created_at"]