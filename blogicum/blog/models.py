from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from core.constants import (
    MAX_CAT_TITLE_LENGTH,
    MAX_COMMENT_LENGTH,
    MAX_TEXT_LENGTH
)
from core.models import CreatedAtModel, PublishedModel


User = get_user_model()


class PublishedPostsAndRelatedTablesMangager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        ).select_related(
            'author', 'location', 'category'
        )


class Post(PublishedModel, CreatedAtModel):
    title = models.CharField(
        max_length=MAX_TEXT_LENGTH,
        blank=False,
        verbose_name='Заголовок'
    )
    text = models.TextField(blank=False, verbose_name='Текст')
    pub_date = models.DateTimeField(
        blank=False,
        verbose_name='Дата и время публикации',
        help_text='Если установить дату и время в будущем '
        '— можно делать отложенные публикации.'
    )
    author = models.ForeignKey(
        User,
        blank=False,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор публикации'
    )
    image = models.ImageField(
        blank=True,
        verbose_name='Фото',
        upload_to='post_images'
    )
    location = models.ForeignKey(
        'Location',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        'Category',
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Категория'
    )
    objects = models.Manager()
    public_posts = PublishedPostsAndRelatedTablesMangager()

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.title


class Category(PublishedModel, CreatedAtModel):
    title = models.CharField(
        max_length=MAX_TEXT_LENGTH,
        blank=False,
        verbose_name='Заголовок'
    )
    description = models.TextField(
        blank=False,
        verbose_name='Описание'
    )
    slug = models.SlugField(
        unique=True,
        blank=False,
        verbose_name='Идентификатор',
        help_text='Идентификатор страницы для URL; '
        'разрешены символы латиницы, цифры, дефис и подчёркивание.'
    )

    class Meta(CreatedAtModel.Meta):
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title[:MAX_CAT_TITLE_LENGTH]


class Location(PublishedModel, CreatedAtModel):
    name = models.CharField(
        max_length=MAX_TEXT_LENGTH,
        blank=False,
        verbose_name='Название места'
    )

    class Meta(CreatedAtModel.Meta):
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Comment(CreatedAtModel):
    text = models.TextField(verbose_name='Текст комментария')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено'
    )

    class Meta(CreatedAtModel.Meta):
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return (
            f'Комментарий пользователя {self.author} '
            f'к посту "{self.post}": {self.text:.{MAX_COMMENT_LENGTH}}...'
        )
