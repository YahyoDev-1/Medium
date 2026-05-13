from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from notifications.models import UserFollowing
from interactions.models import Bookmark
from articles.models import Article
from .models import DailyStats
from datetime import timedelta, date
import json


@login_required
def stats_view(request):
    """
    Comprehensive stats dashboard with charts and analytics.
    """
    user = request.user

    # Ensure UserStats exists (or create it)
    from .models import UserStats
    user_stats, _ = UserStats.objects.get_or_create(user=user)

    # Get all published articles
    articles = user.articles.filter(status="published")

    # Calculate metrics
    total_views = sum(a.views_count for a in articles)
    total_likes = sum(a.likes.count() for a in articles)
    total_followers = user.followers.count()
    total_subscribers = user.followers.count()  # In future, distinguish subscribers

    # Get last 30 days of data
    end_date = date.today()
    start_date = end_date - timedelta(days=29)

    daily_stats = []
    for i in range(30):
        current_date = start_date + timedelta(days=i)
        stats = DailyStats.objects.filter(user=user, date=current_date).aggregate(
            views=Sum('views'),
            reads=Sum('reads')
        )
        daily_stats.append({
            'date': current_date.strftime('%m-%d'),
            'views': stats['views'] or 0,
            'reads': stats['reads'] or 0,
        })

    # Get followers list
    followers = user.followers.select_related('follower').all()[:10]

    # Get following list
    following = user.following.select_related('following').all()[:10]

    # Prepare chart data (JSON)
    chart_data = {
        'labels': [d['date'] for d in daily_stats],
        'views': [d['views'] for d in daily_stats],
        'reads': [d['reads'] for d in daily_stats],
    }

    context = {
        'total_views': total_views,
        'total_likes': total_likes,
        'total_followers': total_followers,
        'total_subscribers': total_subscribers,
        'articles_count': articles.count(),
        'chart_data': json.dumps(chart_data),
        'followers': followers,
        'following': following,
    }

    return render(request, 'stats/stats.html', context)


@login_required
def audience_view(request):
    """
    Audience/followers detailed view.
    """
    user = request.user
    followers = user.followers.select_related('follower').order_by('-created_at')
    following = user.following.select_related('following').order_by('-created_at')

    context = {
        'followers': followers,
        'following': following,
        'followers_count': followers.count(),
        'following_count': following.count(),
    }

    return render(request, 'stats/audience.html', context)