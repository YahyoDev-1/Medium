# Create your views here.

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, render
from articles.models import Article
from .models import ArticleLike, Bookmark
from django.db import IntegrityError

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
    count = article.likes.count()
    return JsonResponse({"liked": liked, "count": count})

@require_POST
@login_required
def toggle_bookmark(request, article_id):
    article = get_object_or_404(Article, pk=article_id, status="published")
    try:
        bookmark, created = Bookmark.objects.get_or_create(user=request.user, article=article)
    except IntegrityError:
        created = False
        bookmark = Bookmark.objects.filter(user=request.user, article=article).first()

    if not created:
        # remove
        Bookmark.objects.filter(user=request.user, article=article).delete()
        saved = False
    else:
        saved = True
    count = article.bookmarked_by.count()
    return JsonResponse({"saved": saved, "count": count})

@login_required
def library_view(request):
    """
    Show user's library (bookmarked articles). Page replicates Medium library layout.
    """
    bookmarks = request.user.bookmarks.select_related("article__author", "article").all()
    return render(request, "interactions/library.html", {"bookmarks": bookmarks})

@login_required
def stats_view(request):
    """
    Simple stats dashboard: counts for user's articles, likes received, saved articles.
    """
    user = request.user
    articles_count = user.articles.count()
    likes_received = sum(a.likes.count() for a in user.articles.all())
    saved_count = user.bookmarks.count()
    return render(request, "interactions/stats.html", {
        "articles_count": articles_count,
        "likes_received": likes_received,
        "saved_count": saved_count,
    })
