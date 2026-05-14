# Create your models here.
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.conf import settings
from django.utils import timezone

from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from django_quill.fields import QuillField


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Article(models.Model):
    STATUS_CHOICES = (("draft", "Draft"), ("published", "Published"))

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="articles")
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=300, unique=True, blank=True)

    # Changed from TextField to QuillField for rich text editing
    body = models.TextField()

    excerpt = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="draft")
    tags = models.ManyToManyField(Tag, blank=True, related_name="articles")

    # Member-only flag
    is_member_only = models.BooleanField(
        default=False,
        help_text="Only followers can read this article"
    )

    # Cover image (optional)
    cover_image = models.ImageField(upload_to="article_covers/", blank=True, null=True)

    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]
        indexes = [models.Index(fields=["-published_at", "status"])]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:200]
            slug = base
            counter = 1
            while Article.objects.filter(slug=slug).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        if self.status == "published" and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("articles:detail", kwargs={"slug": self.slug})

    def can_view(self, user):
        """Check if a user can view this article."""
        if not self.is_member_only:
            return True
        if not user or not user.is_authenticated :
            return False
        if user == self.author:
            return True
        return self.author.followers.filter(follower=user).exists()

    def get_root_comments(self):
        return self.comments.filter(parent__isnull=True)\
    .select_related("author")\
    .prefetch_related("children")
