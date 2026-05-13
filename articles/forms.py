from django import forms
from django.utils.text import slugify
from .models import Article, Tag
from django_quill.fields import QuillFormField


class ArticleForm(forms.ModelForm):
    tags = forms.CharField(
        required=False,
        help_text="Comma-separated tags",
        label="Tags",
        widget=forms.TextInput(attrs={'placeholder': 'e.g. technology, django, web'})
    )

    # Use QuillFormField for the body
    body = forms.CharField(
        required=True,
        widget=forms.HiddenInput()
    )

    cover_image = forms.ImageField(required=False, widget=forms.FileInput(attrs={
        'accept': 'image/*',
        'class': 'file-input'
    }))

    class Meta:
        model = Article
        fields = ["title", "excerpt", "body", "cover_image", "status", "tags"]
        widgets = {
            "title": forms.TextInput(attrs={
                "placeholder": "Article title",
                "class": "editor-title",
                "required": True
            }),
            "excerpt": forms.Textarea(attrs={
                "placeholder": "Brief description of your article (optional)",
                "rows": 3,
                "class": "editor-excerpt"
            }),
            "status": forms.Select(attrs={"class": "status-select"}),
        }

    def clean_tags(self):
        raw = self.cleaned_data.get("tags", "")
        names = [t.strip() for t in raw.split(",") if t.strip()]
        return names

    def clean(self):
        cleaned = super().clean()
        body = cleaned.get("body")

        if not body:
            self.add_error("body", "Article body cannot be empty.")

        return cleaned

    def save(self, commit=True, author=None):
        names = self.cleaned_data.pop("tags", [])
        article = super().save(commit=False)

        if author and not article.author_id:
            article.author = author

        if commit:
            article.save()
            # Attach tags
            article.tags.clear()
            for name in names:
                tag, _ = Tag.objects.get_or_create(name=name, defaults={"slug": slugify(name)})
                article.tags.add(tag)

        return article