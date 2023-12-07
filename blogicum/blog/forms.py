from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Post, Comment


User = get_user_model()


class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('title', 'text', 'pub_date', 'category', 'location', 'image')
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'})
            # , format='%d.%m.%Y %H:%M')
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
