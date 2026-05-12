from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# Create your models here.


class CustomUser(AbstractUser):
    # Extend later if needed; we use a profile model for richer fields
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    website = models.URLField(blank=True)

    def __str__(self):
        return self.get_username()
