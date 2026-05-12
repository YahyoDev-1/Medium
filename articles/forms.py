from django import forms
from django.utils.text import slugify
from .models import Article, Tag
from django.conf import settings
import bleach

# Allowed tags/attributes for incoming HTML (adjust for your needs)
ALLOWED_TAGS = ["p", "br", "strong", "em", "a", "ul", "ol", "li", "blockquote", "h2", "h3"]
ALLOWED_ATTRS = {"a": ["href", "rel", "target"]}

class ArticleForm(forms.ModelForm):
    tags = forms.CharField(required=False, help_text="Comma-separated tags", label="Tags")
    # hidden field to receive HTML from the contenteditable editor
    body_html = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Article
        fields = ["title", "excerpt", "status", "tags"]

    def clean_tags(self):
        raw = self.cleaned_data.get("tags", "")
        names = [t.strip() for t in raw.split(",") if t.strip()]
        return names

    def clean(self):
        cleaned = super().clean()
        # If body_html provided, sanitize it; otherwise error:
        body_html = cleaned.get("body_html") or self.data.get("body_html") or self.data.get("body", "")
        if not body_html:
            self.add_error(None, "Article body cannot be empty.")
        else:
            # sanitize using bleach (if installed); fall back to plain text
            try:
                cleaned_body = bleach.clean(body_html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, strip=True)
            except Exception:
                cleaned_body = body_html
            cleaned["body"] = cleaned_body
        return cleaned

    def save(self, commit=True, author=None):
        names = self.cleaned_data.pop("tags", [])
        body = self.cleaned_data.pop("body", "")
        article = super().save(commit=False)
        article.body = body
        if author and not article.author_id:
            article.author = author
        if commit:
            article.save()
            # attach tags
            article.tags.clear()
            for name in names:
                tag, _ = Tag.objects.get_or_create(name=name, defaults={"slug": slugify(name)})
                article.tags.add(tag)
        return article