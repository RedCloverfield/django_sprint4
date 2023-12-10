from django import forms
from django.contrib.auth.forms import UserCreationForm

from core.constants import USER

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
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%d %H:%M'
            )
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
