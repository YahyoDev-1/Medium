from django.db.models.signals import post_save
from django.dispatch import receiver
from notifications.models import ReadingHistory
from .models import DailyStats
from datetime import date

@receiver(post_save, sender=ReadingHistory)
def track_article_view(sender, instance, created, **kwargs):
    """
    When an article is viewed (ReadingHistory created/updated), track it.
    """
    if created:
        daily_stat, _ = DailyStats.objects.get_or_create(
            user=instance.article.author,
            article=instance.article,
            date=date.today(),
        )
        daily_stat.views += 1
        daily_stat.save(update_fields=['views'])