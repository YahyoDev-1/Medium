from django.urls import path
from . import views

app_name = "comments"

urlpatterns = [
    path("add/", views.add_comment, name="add"),
]