# Create your views here.

# create core/views.py
from django.shortcuts import render
from articles.models import Article

from django.shortcuts import render
from articles.models import Article

def home(request):
    qs = Article.objects.filter(status="published").select_related("author")[:10]
    return render(request, "core/home.html", {"articles": qs})

def intro(request):
    return render(request, "core/intro.html")
