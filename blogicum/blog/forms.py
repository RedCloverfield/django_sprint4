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
        # добавил format, но при редактировании поста
        # дата и время не подгружаются
        widgets = {
            'pub_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%d.%m.%Y %H:%M'
            )
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
