from urllib import request

from django.contrib import messages
from django.db import models
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from notifications.models import ReadingHistory, Notification, UserFollowing
from .models import Article
from .forms import ArticleForm

from django.db.models import Exists, OuterRef  # Bularni import qilishni unutmang


class ArticleListView(ListView):
    model = Article
    template_name = "articles/article_list.html"
    paginate_by = 10

    def get_queryset(self):
        # 1. Asosiy queryset
        qs = Article.objects.filter(status="published").select_related("author").prefetch_related("tags")

        # 2. Qidiruv qismi
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(title__icontains=q) | qs.filter(body__icontains=q)

        # 3. Bookmark tekshirish (To'g'rilangan qism)
        user = self.request.user
        if user.is_authenticated:
            # Diqqat: Bu yerda Article.objects emas, Bookmark.objects bo'lishi shart!
            user_bookmarks = Bookmark.objects.filter(
                article=OuterRef('pk'),
                user=user
            )
            qs = qs.annotate(user_has_bookmarked=Exists(user_bookmarks))

        return qs



from django.views.generic import DetailView
from django.db.models import Exists, OuterRef
from .models import Article
from interactions.models import ArticleLike, Bookmark

from django.views.generic import DetailView
from django.db.models import Exists, OuterRef


# Bookmark modelini import qiling (agar alohida model bo'lsa)

class ArticleDetailView(DetailView):
    model = Article
    template_name = "articles/article_detail.html"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)

        # Check if user can view this article
        if not obj.can_view(self.request.user):
            raise Http404("This article is for members only.")

        return obj

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if user.is_authenticated:
            # 1. Like status
            user_likes = ArticleLike.objects.filter(article=OuterRef('pk'), user=user)

            # 2. Bookmark status
            user_bookmarks = Bookmark.objects.filter(article=OuterRef('pk'), user=user)

            # 3. Follow status (Muallifga obuna bo'lganmi?)
            # Bu yerda Follow modelini ishlatamiz. Model nomi sizda boshqacha bo'lishi mumkin.
            user_follows = UserFollowing.objects.filter(
                following=OuterRef('author'),  # Maqola muallifiga obuna bo'lganmi?
                follower=user  # Hozirgi foydalanuvchi obunachimi?
            )

            return queryset.annotate(
                user_has_liked=Exists(user_likes),
                user_has_bookmarked=Exists(user_bookmarks),
                user_follows_author = Exists(user_follows)
            )

        return queryset

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        # Track reading history if user is authenticated
        if request.user.is_authenticated:
            article = self.get_object()
            ReadingHistory.objects.get_or_create(user=request.user, article=article)
            # Increment views count
            article = get_object_or_404(Article, slug=article.slug)
            session = f"viewed_article{article.id}"
            if not request.session.get(session):
                article.views_count += 1
                article.save()
                request.session[session] = True

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            context['is_following'] = self.object.author.followers.filter(
                follower=self.request.user
            ).exists()
        else:
            context['is_following'] = False

        return context


class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = "articles/article_form.html"

    def form_valid(self, form):
        article = form.save(author=self.request.user)

        # If publishing, notify followers
        if article.status == "published":
            followers = self.request.user.followers.values_list("follower", flat=True)
            notifications = [
                Notification(
                    recipient_id=follower_id,
                    sender=self.request.user,
                    notification_type="new_article",
                    article=article,
                    title=f"{self.request.user.username} published a new article",
                    description=f"'{article.title}'"
                )
                for follower_id in followers
            ]
            Notification.objects.bulk_create(notifications)

        return super().form_valid(form)

class AuthorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user


class ArticleUpdateView(LoginRequiredMixin, AuthorRequiredMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = "articles/article_form.html"

    def get_initial(self):
        initial = super().get_initial()
        initial["tags"] = ", ".join([t.name for t in self.get_object().tags.all()])
        return initial

    def form_valid(self, form):
        # form.instance allaqachon mavjud ob'ektga bog'liq
        # author ni o'zgartirmaslik kerak
        article = form.save(commit=False)
        article.save()
        form.save_m2m()  # agar tags M2M bo'lsa
        return redirect(article.get_absolute_url())

class ArticleDeleteView(LoginRequiredMixin, AuthorRequiredMixin, DeleteView):
    model = Article
    success_url = reverse_lazy("articles:list")
    template_name = "articles/article_confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Article deleted successfully!")
        return super().delete(request, *args, **kwargs)


# Keep existing imports and view classes above; add the following to the bottom


from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

ALLOWED_IMAGE_TYPES = ("image/jpeg", "image/png", "image/gif", "image/webp")
ALLOWED_VIDEO_TYPES = ("video/mp4", "video/webm", "video/ogg")
ALLOWED_FILE_TYPES = ("application/pdf", "text/plain", "application/msword",
                      "application/vnd.openxmlformats-officedocument.wordprocessingml.document")


@login_required
@require_POST
def upload_media(request):
    """
    Accepts a file via POST (field 'file') and stores it under MEDIA_ROOT/article_media/.
    Returns JSON: { url: <media_url>, name: <filename>, type: <type> }
    """
    the_file = request.FILES.get("file")
    if not the_file:
        return JsonResponse({"error": "No file provided."}, status=400)

    content_type = the_file.content_type
    kind = "file"
    if content_type in ALLOWED_IMAGE_TYPES:
        kind = "image"
    elif content_type in ALLOWED_VIDEO_TYPES:
        kind = "video"
    else:
        kind = "file"

    # Create filename with uuid to avoid collisions
    ext = os.path.splitext(the_file.name)[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    subdir = "article_media"
    full_path = os.path.join(subdir, filename)

    saved_path = default_storage.save(full_path, ContentFile(the_file.read()))
    media_url = default_storage.url(saved_path)

    return JsonResponse({"url": media_url, "name": the_file.name, "type": kind})


# keep existing imports and classes, then add or replace the upload_media view with the following

import os
import uuid
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import JsonResponse, Http404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.conf import settings


@login_required
@require_POST
def upload_media(request):
    """
    Accepts a file via POST (field 'file') and stores it under MEDIA_ROOT/article_media/.
    Enforces strict upload limits and allowed MIME types configured in settings.
    Returns JSON: { url: <media_url>, name: <filename>, type: <type> }
    """
    the_file = request.FILES.get("file")
    if not the_file:
        return JsonResponse({"error": "No file provided."}, status=400)

    content_type = the_file.content_type or ""
    size = the_file.size

    # categorize and enforce limits
    if content_type in getattr(settings, "ALLOWED_IMAGE_TYPES", []):
        kind = "image"
        if size > getattr(settings, "IMAGE_MAX_UPLOAD_SIZE", 5 * 1024 * 1024):
            return JsonResponse({"error": "Image too large. Max size is {} bytes.".format(
                getattr(settings, "IMAGE_MAX_UPLOAD_SIZE", 5 * 1024 * 1024))}, status=400)
    elif content_type in getattr(settings, "ALLOWED_VIDEO_TYPES", []):
        kind = "video"
        if size > getattr(settings, "VIDEO_MAX_UPLOAD_SIZE", 25 * 1024 * 1024):
            return JsonResponse({"error": "Video too large. Max size is {} bytes.".format(
                getattr(settings, "VIDEO_MAX_UPLOAD_SIZE", 25 * 1024 * 1024))}, status=400)
    elif content_type in getattr(settings, "ALLOWED_FILE_TYPES", []):
        kind = "file"
        if size > getattr(settings, "FILE_MAX_UPLOAD_SIZE", 10 * 1024 * 1024):
            return JsonResponse({"error": "File too large. Max size is {} bytes.".format(
                getattr(settings, "FILE_MAX_UPLOAD_SIZE", 10 * 1024 * 1024))}, status=400)
    else:
        return JsonResponse({"error": f"Unsupported file type: {content_type}."}, status=400)

    # create safe filename
    ext = os.path.splitext(the_file.name)[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    subdir = "article_media"
    full_path = os.path.join(subdir, filename)

    saved_path = default_storage.save(full_path, ContentFile(the_file.read()))
    media_url = default_storage.url(saved_path)

    return JsonResponse({"url": media_url, "name": the_file.name, "type": kind})
