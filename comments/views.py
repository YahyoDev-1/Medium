# Create your views here.

from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template.defaultfilters import truncatewords
from django.urls import reverse
from django.views.decorators.http import require_POST
from articles.models import Article
from .models import Comment

from notifications.models import Notification

@require_POST
@login_required
def add_comment(request):
    body = request.POST.get("body", "").strip()
    article_id = request.POST.get("article_id")
    parent_id = request.POST.get("parent_id")
    article = get_object_or_404(Article, pk=article_id)
    if body:
        parent = None
        if parent_id:
            try:
                parent = Comment.objects.get(pk=parent_id, article=article)
            except Comment.DoesNotExist:
                parent = None
        comment = Comment.objects.create(article=article, author=request.user, body=body, parent=parent)

        # Notify article author
        if article.author != request.user:
            Notification.objects.create(
                recipient=article.author,
                sender=request.user,
                notification_type="comment",
                article=article,
                comment=comment,
                title=f"{request.user.username} commented on your article",
                description=truncatewords(body, 15)
            )

        # Notify parent comment author if this is a reply
        if parent and parent.author != request.user:
            Notification.objects.create(
                recipient=parent.author,
                sender=request.user,
                notification_type="reply",
                article=article,
                comment=comment,
                title=f"{request.user.username} replied to your comment",
                description=truncatewords(body, 15)
            )

    url = article.get_absolute_url() + "#comments"
    return redirect(url)