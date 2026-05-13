from django.urls import path
from . import views

app_name = "notifications"

urlpatterns = [
    path("", views.notifications_list, name="list"),
    path("mark-as-read/<int:notification_id>/", views.mark_as_read, name="mark-as-read"),
    path("mark-all-as-read/", views.mark_all_as_read, name="mark-all-as-read"),
    path("unread-count/", views.unread_count, name="unread-count"),
    path("follow/<int:user_id>/", views.follow_user, name="follow"),
    path("reading-history/", views.reading_history, name="reading-history"),
]