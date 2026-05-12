from urllib import request

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Article
from .forms import ArticleForm


class ArticleListView(ListView):
    model = Article
    template_name = "articles/article_list.html"
    paginate_by = 10

    def get_queryset(self):
        qs = Article.objects.filter(status="published").select_related("author").prefetch_related("tags")
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(title__icontains=q) | qs.filter(body__icontains=q)
        return qs


from django.views.generic import DetailView
from django.db.models import Exists, OuterRef
from .models import Article
from interactions.models import ArticleLike


class ArticleDetailView(DetailView):
    model = Article
    template_name = "articles/article_detail.html"

    def get_queryset(self):
        # Asosiy querysetni olamiz
        queryset = super().get_queryset()

        # Agar foydalanuvchi tizimga kirgan bo'lsa
        if self.request.user.is_authenticated:
            # Subquery: Like modelidan hozirgi maqola va userga mosini qidirish
            user_likes = ArticleLike.objects.filter(
                article=OuterRef('pk'),
                user=self.request.user
            )
            # Maqolaga user_has_liked (True/False) maydonini qo'shish
            return queryset.annotate(user_has_liked=Exists(user_likes))

        return queryset


class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = "articles/article_form.html"

    def form_valid(self, form):
        # form.save will set body and author
        form.save(author=self.request.user)
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
        # prepare tags line
        initial["tags"] = ", ".join([t.name for t in self.get_object().tags.all()])
        initial["body_html"] = self.get_object().body
        return initial

    def form_valid(self, form):
        form.instance = self.get_object()
        form.save(author=self.request.user)
        return super().form_valid(form)


class ArticleDeleteView(LoginRequiredMixin, AuthorRequiredMixin, DeleteView):
    model = Article
    success_url = reverse_lazy("articles:list")
    template_name = "articles/article_confirm_delete.html"


# Keep existing imports and view classes above; add the following to the bottom

import os
import uuid
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.conf import settings

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
