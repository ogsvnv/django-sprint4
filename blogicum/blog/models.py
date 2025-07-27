from django.db import models
from django.contrib.auth import get_user_model

from .constants import MAX_CHARFIELD_LENGTH, STR_TRUNCATE_LENGTH

User = get_user_model()


class CreatedAt(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        abstract = True
        ordering = ('created_at',)


class IsPublishedCreatedAt(CreatedAt):
    is_published = models.BooleanField(
        default=True,
    )

    class Meta:
        abstract = True


class TitleAbstract(models.Model):
    title = models.CharField(
        max_length=MAX_CHARFIELD_LENGTH,
    )

    class Meta:
        abstract = True


class Location(IsPublishedCreatedAt):
    name = models.CharField(
        max_length=MAX_CHARFIELD_LENGTH,
    )

    class Meta(CreatedAt.Meta):
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'
        ordering = ('name',)

    def __str__(self):
        return self.name[:STR_TRUNCATE_LENGTH]


class Category(IsPublishedCreatedAt, TitleAbstract):
    description = models.TextField(verbose_name='описание')
    slug = models.SlugField(
        unique=True,
        verbose_name='слаг',
    )

    class Meta(CreatedAt.Meta):
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'
        ordering = ('title',)

    def __str__(self):
        return self.title[:STR_TRUNCATE_LENGTH]


class Post(IsPublishedCreatedAt, TitleAbstract):
    text = models.TextField(verbose_name='текст')
    pub_date = models.DateTimeField(verbose_name='дата публикации')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='автор',
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='местоположение',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        null=True,
        verbose_name='категория',
    )
    image = models.ImageField(
        upload_to='images',
        blank=True,
        null=True,
        verbose_name='изображение',
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        default_related_name = 'posts'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.title[:STR_TRUNCATE_LENGTH]


class Comment(CreatedAt):
    text = models.TextField(verbose_name='текст')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='публикация',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='автор',
    )

    class Meta(CreatedAt.Meta):
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'Комментарий пользователя {self.author}'
