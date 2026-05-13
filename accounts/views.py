# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from .forms import CustomUserCreationForm, ProfileForm
from .models import CustomUser
from django.contrib import messages


def signup_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Welcome! Your account was created.")
            return redirect("core:home")
    else:
        form = CustomUserCreationForm()
    return render(request, "accounts/signup.html", {"form": form})


def profile_view(request, username):
    user_obj = get_object_or_404(CustomUser, username=username)

    # Faqat "published" holatidagi maqolalarni ajratib olamiz
    published_articles = user_obj.articles.filter(status='published')

    stats = {
        "articles_count": published_articles.count(),  # Faqat chop etilganlarini sanash uchun
        "followers_count": 0,
        "bookmarks_count": user_obj.bookmarks.count() if hasattr(user_obj, "bookmarks") else 0,
    }

    return render(request, "accounts/profile.html", {
        "profile_user": user_obj,
        "articles": published_articles,  # Yangi o'zgaruvchi
        "stats": stats
    })

@login_required
def profile_edit(request, username): # 'username' argumentini qo'shdik
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("accounts:profile", username=request.user.username)
    else:
        form = ProfileForm(instance=request.user)
    return render(request, "accounts/profile_edit.html", {"form": form})



@require_http_methods(["GET", "POST"])
@login_required
def logout_confirm(request):
    """
    Show confirmation page (GET). On POST, log the user out and redirect home.
    """
    if request.method == "POST":
        logout(request)
        return redirect("core:home")
    # GET: render confirmation
    return render(request, "accounts/logout_confirm.html")
