from django.urls import path
from . import views
from django.urls import path
from . import views

app_name = "articles"

urlpatterns = [
    path("", views.ArticleListView.as_view(), name="list"),
    path("new/", views.ArticleCreateView.as_view(), name="create"),
    path("upload-media/", views.upload_media, name="upload-media"),
    path("<slug:slug>/", views.ArticleDetailView.as_view(), name="detail"),
    path("<slug:slug>/edit/", views.ArticleUpdateView.as_view(), name="edit"),
    path("<slug:slug>/delete/", views.ArticleDeleteView.as_view(), name="delete"),
]
