# Create your models here.
from django.db import models
from django.conf import settings
from articles.models import Article

class ArticleLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="likes")
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "article")

class Bookmark(models.Model):
    """
    A saved article (Library). A user can bookmark many articles.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookmarks")
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="bookmarked_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "article")
        ordering = ["-created_at"]