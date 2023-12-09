from django.db.models import Count

from .models import Post


def public_posts_with_comment_count():
    return Post.public_posts.annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')
