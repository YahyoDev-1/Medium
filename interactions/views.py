from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, render, redirect
from articles.models import Article
from .models import ArticleLike, Bookmark, ReadingList, ReadingListItem
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.utils.text import slugify

# Add this import at top
from notifications.models import Notification

# Update toggle_bookmark to add notification
@require_POST
@login_required
def toggle_bookmark(request, article_id):
    article = get_object_or_404(Article, pk=article_id, status="published")
    try:
        bookmark, created = Bookmark.objects.get_or_create(user=request.user, article=article)
    except IntegrityError:
        created = False

    if not created:
        Bookmark.objects.filter(user=request.user, article=article).delete()
        saved = False
    else:
        saved = True
        # Notify article author
        if article.author != request.user:
            Notification.objects.create(
                recipient=article.author,
                sender=request.user,
                notification_type="like",
                article=article,
                title=f"{request.user.username} saved your article",
                description=f"'{article.title}'"
            )

    count = article.bookmarked_by.count()
    return JsonResponse({"saved": saved, "count": count})

# Similarly update toggle_like
@require_POST
@login_required
def toggle_like(request, article_id):
    article = get_object_or_404(Article, pk=article_id, status="published")
    like, created = ArticleLike.objects.get_or_create(user=request.user, article=article)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
        # Notify article author
        if article.author != request.user:
            Notification.objects.create(
                recipient=article.author,
                sender=request.user,
                notification_type="like",
                article=article,
                title=f"{request.user.username} liked your article",
                description=f"'{article.title}'"
            )

    count = article.likes.count()
    return JsonResponse({"liked": liked, "count": count})

@login_required
def library_view(request):
    """
    Show user's library (bookmarked articles, lists, and notifications).
    """
    # 1. Bookmarks va Lists (Mavjud kod)
    bookmarks = request.user.bookmarks.select_related("article__author", "article").all()
    lists = request.user.reading_lists.all()

    # 2. Notifications (Xatoni to'g'irlash uchun qo'shilgan qism)
    # Bildirishnomalarni view ichida filtrlaymiz
    comment_notifications = request.user.notifications.filter(
        notification_type__in=['comment', 'reply']
    ).select_related('sender', 'article')

    context = {
        "bookmarks": bookmarks,
        "lists": lists,
        "comment_notifications": comment_notifications  # Shablonda shu nomdan foydalanamiz
    }

    return render(request, "interactions/library.html", context)


@login_required
def stats_view(request):
    user = request.user
    articles_count = user.articles.count()
    likes_received = sum(a.likes.count() for a in user.articles.all())
    saved_count = user.bookmarks.count()
    return render(request, "interactions/stats.html", {
        "articles_count": articles_count,
        "likes_received": likes_received,
        "saved_count": saved_count,
    })

# ----- Reading list management -----
@login_required
@require_POST
def add_to_list(request):
    """
    POST params:
      - article_id (required)
      - list_id (optional) OR list_name (optional): if list_id provided, add to it; otherwise use or create list with list_name.
    Returns JSON: { success, list_id, list_name, added }
    """
    article_id = request.POST.get("article_id")
    list_id = request.POST.get("list_id")
    list_name = request.POST.get("list_name", "").strip()

    if not article_id:
        return JsonResponse({"error": "article_id required"}, status=400)

    article = get_object_or_404(Article, pk=article_id, status="published")

    reading_list = None
    if list_id:
        reading_list = get_object_or_404(ReadingList, pk=list_id, user=request.user)
    else:
        if not list_name:
            return JsonResponse({"error": "Provide list_id or list_name"}, status=400)
        # create or get by name for this user
        reading_list, created = ReadingList.objects.get_or_create(user=request.user, name=list_name)

    # add item
    try:
        item, created_item = ReadingListItem.objects.get_or_create(reading_list=reading_list, article=article)
    except IntegrityError:
        created_item = False

    added = bool(created_item)
    return JsonResponse({
        "success": True,
        "list_id": reading_list.id,
        "list_name": reading_list.name,
        "added": added,
        "items_count": reading_list.items.count()
    })

@login_required
@require_POST
def remove_from_list(request):
    """
    POST: article_id, list_id
    """
    article_id = request.POST.get("article_id")
    list_id = request.POST.get("list_id")
    if not article_id or not list_id:
        return JsonResponse({"error": "article_id and list_id required"}, status=400)

    reading_list = get_object_or_404(ReadingList, pk=list_id, user=request.user)
    ArticleObj = get_object_or_404(Article, pk=article_id)
    ReadingListItem.objects.filter(reading_list=reading_list, article=ArticleObj).delete()
    return JsonResponse({"success": True, "items_count": reading_list.items.count()})

@login_required
def lists_view(request):
    """
    Show user's lists with items.
    """
    lists = request.user.reading_lists.prefetch_related("items__article__author").all()
    return render(request, "interactions/lists.html", {"lists": lists})

@login_required
def reading_list_detail(request, list_id):
    reading_list = get_object_or_404(ReadingList, pk=list_id, user=request.user)
    items = reading_list.items.select_related("article__author").all()
    return render(request, "interactions/reading_list_detail.html", {"list": reading_list, "items": items})