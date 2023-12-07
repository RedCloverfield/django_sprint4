from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import models
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, UpdateView, CreateView, DeleteView, DetailView

from .constants import MAX_NUM_OF_POSTS
from .forms import PostForm, CommentForm
from .models import Post, Category, Comment

from blog.forms import CustomUserCreationForm

User = get_user_model()


def post_related_tables():
    return Post.objects.select_related('author', 'category', 'location')


class Index(ListView): # главная страница
    model = Post
    paginate_by = 10
    template_name = 'blog/index.html'

    queryset = Post.objects.annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date').filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    ).select_related(
            'author', 'location', 'category'
    )


class PostDetail(DetailView): # страница поста
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if Post.objects.get(pk=self.kwargs['post_id']).author == self.request.user:
            context['post'] = post_related_tables().get(pk=self.kwargs['post_id'])
        else:
            context['post'] = get_object_or_404(
            post_related_tables().filter(pk=self.kwargs['post_id']),
            Q(pub_date__lte=timezone.now())
            & Q(is_published=True)
            & Q(category__is_published=True)
        )
        context['form'] = CommentForm()
        context['comments'] = Post.objects.get(id=self.kwargs['post_id']).comments.select_related('author')
        return context


class CategoryPosts(ListView): # страница категории
    model = Category
    paginate_by = 10
    template_name = 'blog/category.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = Category.objects.get(slug=self.kwargs['category_slug'])
        return context

    def get_queryset(self):
        q = get_object_or_404(Category, slug=self.kwargs['category_slug'], is_published=True) #super().get_queryset().get(slug=self.kwargs['category_slug'])
        queryset = q.posts.annotate(
            comment_count=Count('comments')
        ).order_by(
            '-pub_date'
        ).filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        )
        return queryset


class UserProfile(ListView): # страница пользователя
    model = get_user_model()
    paginate_by = 10
    template_name = 'blog/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        get_object_or_404(User, username=self.kwargs['username'])
        context['profile'] = User.objects.get(username=self.kwargs['username'])
        return context

    def get_queryset(self):
        q = get_object_or_404(User, username=self.kwargs['username'])
        if self.request.user.username == self.kwargs['username']:
            queryset = q.posts.annotate(
                comment_count=Count('comments')
            ).order_by('-pub_date')
        else:
            queryset = q.posts.annotate(comment_count=Count('comments')).order_by(
                '-pub_date'
            ).filter(
                pub_date__lte=timezone.now(),
                is_published=True,
                category__is_published=True
            )
        return queryset


class UserProfileUpdate(LoginRequiredMixin, UpdateView): # страница редактирования данных пользователя
    model = User
    form_class = CustomUserCreationForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        obj = queryset.get(username=self.request.user.username)
        return obj

    def get_success_url(self):
        return reverse_lazy('blog:index')


class PostCreate(LoginRequiredMixin, CreateView): # страница создания поста
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'


    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={'username': self.request.user.username})


class PostUpdate(UpdateView): # страница редактирования поста
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'
    success_url = '/posts/{id}/' # перепроверить, дописать или заменить на get_absolute_url в models

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['post_id'])
        if instance.author != request.user:
            return redirect('blog:post_detail', post_id=instance.pk)
        return super().dispatch(request, *args, **kwargs)


class PostDelete(DeleteView): # страница удаления публикации
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=Post.objects.get(pk=self.kwargs['post_id']))
        return context

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['post_id'])
        if instance.author != request.user:
            return redirect('blog:post_detail', post_id=instance.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={'username': self.request.user.username})


class CommentCreate(LoginRequiredMixin, CreateView): # страница создания коммента, сразу после получения формы перенаправляет назад на страницу поста
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'post_id'
    template_name = 'blog/comments.html'

    def dispatch(self, request, *args, **kwargs):
        get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post_id = self.kwargs['post_id']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.kwargs['post_id']})


class CommentUpdate(LoginRequiredMixin, UpdateView): # страница редактирования коммента
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Comment, pk=kwargs['comment_id'])
        if instance.author != request.user: # не срабатывает эта строка
            return redirect('blog:post_detail', post_id=instance.post_id)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'post_id': self.kwargs['post_id']})


class CommentDelete(LoginRequiredMixin, DeleteView): # страница удаления коммента
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment'] = Comment.objects.get(pk=self.kwargs['comment_id'])
        return context

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Comment, pk=kwargs['comment_id'])
        if instance.author != request.user: # и эта
            return redirect('blog:post_detail', post_id=instance.post_id)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'post_id': self.kwargs['post_id']})
