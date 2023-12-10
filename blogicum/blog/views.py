from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from core.constants import POSTS_PER_PAGE, USER

from .forms import CommentForm, CustomUserChangeForm, PostForm
from .mixins import (
    CommentUpdateDeleteMixin,
    PostUpdateDeleteMixin,
    ReverseToPostPageMixin,
    ReverseToProfilePageMixin
)
from .models import Category, Comment, Post
from .utils import public_posts_with_comment_count


class Index(ListView):
    model = Post
    paginate_by = POSTS_PER_PAGE
    template_name = 'blog/index.html'
    queryset = public_posts_with_comment_count()


class PostDetail(DetailView):
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/detail.html'

    def get_object(self):
        obj = get_object_or_404(self.model.objects, pk=self.kwargs['post_id'])
        if obj.author == self.request.user:
            return obj
        return get_object_or_404(
            self.model.public_posts, pk=self.kwargs['post_id']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.get_object()
        context['form'] = CommentForm()
        context['comments'] = Post.objects.get(
            id=self.kwargs['post_id']
        ).comments.select_related('author')
        return context


class CategoryPosts(ListView):
    model = Category
    paginate_by = POSTS_PER_PAGE
    template_name = 'blog/category.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = Category.objects.get(
            slug=self.kwargs['category_slug']
        )
        return context

    def get_queryset(self):
        if get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        ):
            return public_posts_with_comment_count().filter(
                category__slug=self.kwargs['category_slug'],
                category__is_published=True
            )


class UserProfile(ListView):
    model = USER
    paginate_by = POSTS_PER_PAGE
    template_name = 'blog/profile.html'

    def get_object(self):
        return get_object_or_404(self.model, username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_object()
        return context

    def get_queryset(self):
        if self.request.user.username == self.kwargs['username']:
            return self.get_object().posts.annotate(
                comment_count=Count('comments')
            ).order_by('-pub_date')
        return public_posts_with_comment_count().filter(
            author__username=self.get_object().username
        )


class UserProfileUpdate(LoginRequiredMixin,
                        ReverseToProfilePageMixin,
                        UpdateView):
    model = USER
    form_class = CustomUserChangeForm
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user


class PostCreate(LoginRequiredMixin,
                 ReverseToProfilePageMixin,
                 CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdate(PostUpdateDeleteMixin,
                 ReverseToPostPageMixin,
                 ReverseToProfilePageMixin,
                 UpdateView):
    form_class = PostForm


class PostDelete(PostUpdateDeleteMixin, DeleteView):

    def get_object(self):
        return get_object_or_404(self.model, pk=self.kwargs['post_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.get_object())
        return context


class CommentCreate(LoginRequiredMixin, ReverseToPostPageMixin, CreateView):
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


class CommentUpdate(CommentUpdateDeleteMixin,
                    ReverseToPostPageMixin,
                    LoginRequiredMixin,
                    UpdateView):
    form_class = CommentForm


class CommentDelete(CommentUpdateDeleteMixin,
                    ReverseToPostPageMixin,
                    LoginRequiredMixin,
                    DeleteView):

    def get_object(self):
        return get_object_or_404(self.model, pk=self.kwargs['comment_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment'] = self.get_object()
        return context
