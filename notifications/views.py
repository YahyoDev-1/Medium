from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Notification, ReadingHistory, UserFollowing
from django.db.models import Q

@login_required
def notifications_list(request):
    """
    Show all notifications for the logged-in user.
    """
    notifications = request.user.notifications.all()
    unread_count = notifications.filter(is_read=False).count()
    return render(request, "notifications/notifications_list.html", {
        "notifications": notifications,
        "unread_count": unread_count
    })

@login_required
@require_POST
def mark_as_read(request, notification_id):
    """
    Mark a single notification as read.
    """
    notification = get_object_or_404(Notification, pk=notification_id, recipient=request.user)
    notification.mark_as_read()
    return JsonResponse({"success": True, "is_read": notification.is_read})

@login_required
@require_POST
def mark_all_as_read(request):
    """
    Mark all notifications as read.
    """
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return JsonResponse({"success": True})

@login_required
def unread_count(request):
    """
    AJAX endpoint: return count of unread notifications for badge.
    """
    count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({"unread_count": count})

@login_required
@require_POST
def follow_user(request, user_id):
    """
    Follow or unfollow a user. Toggle.
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user_to_follow = get_object_or_404(User, pk=user_id)

    if user_to_follow == request.user:
        return JsonResponse({"error": "Cannot follow yourself."}, status=400)

    following, created = UserFollowing.objects.get_or_create(
        follower=request.user,
        following=user_to_follow
    )

    if not created:
        following.delete()
        is_following = False
    else:
        is_following = True
        # Create a notification for the followed user
        Notification.objects.create(
            recipient=user_to_follow,
            sender=request.user,
            notification_type="follow",
            title=f"{request.user.username} followed you",
            description=""
        )

    followers_count = user_to_follow.followers.count()
    return JsonResponse({"is_following": is_following, "followers_count": followers_count})

@login_required
def reading_history(request):
    """
    Show user's reading history (articles they viewed).
    """
    history = request.user.reading_history.select_related("article__author").all()
    return render(request, "notifications/reading_history.html", {"history": history})