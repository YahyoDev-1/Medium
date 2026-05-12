# Create your models here.

from django.db import models
from django.conf import settings
from articles.models import Article


class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    body = models.TextField()
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="children")
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=True)  # in prod, set to False for moderation if desired

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.author} on {self.article}"
