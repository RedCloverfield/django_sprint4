from django import forms
from django.contrib.auth.forms import UserCreationForm

from .constants import USER
from .models import Post, Comment


class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = USER
        fields = ('username', 'first_name', 'last_name', 'email')


class CustomUserChangeForm(forms.ModelForm):

    class Meta:
        model = USER
        fields = ('username', 'first_name', 'last_name', 'email')


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('title', 'text', 'pub_date', 'category', 'location', 'image')
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
