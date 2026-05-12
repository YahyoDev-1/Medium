from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ("username", "email", "password1", "password2")


class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ("username", "email", "bio", "website", "avatar")
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4, "placeholder": "Tell readers a little about yourself..."}),
            "website": forms.URLInput(attrs={"placeholder": "https://your-site.example"}),
            "username": forms.TextInput(attrs={"placeholder": "Display name"}),
            "email": forms.EmailInput(attrs={"placeholder": "you@example.com"}),
        }
