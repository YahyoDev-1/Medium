from django.urls import path
from . import views

app_name = "interactions"

urlpatterns = [
    path("like-toggle/<int:article_id>/", views.toggle_like, name="like-toggle"),
    path("bookmark-toggle/<int:article_id>/", views.toggle_bookmark, name="bookmark-toggle"),
    path("library/", views.library_view, name="library"),
    path("stats/", views.stats_view, name="stats"),
]