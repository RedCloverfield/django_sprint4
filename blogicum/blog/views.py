from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.generic import ListView

from .constants import MAX_NUM_OF_POSTS
from .models import Post, Category


User = get_user_model()


def post_related_tables():
    return Post.objects.select_related('author', 'category', 'location')


def index(request):
    post_list = post_related_tables().filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    )[:MAX_NUM_OF_POSTS]
    context = {'post_list': post_list}
    return render(request, 'blog/index.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(
        post_related_tables().filter(pk=post_id),
        Q(pub_date__lte=timezone.now())
        & Q(is_published=True)
        & Q(category__is_published=True)
    )
    context = {'post': post}
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category.objects.values('title', 'description'),
        slug=category_slug,
        is_published=True
    )
    post_list = Category.objects.get(slug=category_slug).posts.filter(
        is_published=True,
        pub_date__lte=timezone.now()
    )
    context = {
        'category': category,
        'post_list': post_list,
    }
    return render(request, 'blog/category.html', context)


class UserProfileListView(ListView):
    model = User
    ordering = ''
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = User.objects.all()
        return context
