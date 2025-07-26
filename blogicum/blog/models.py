from django.db import models
from django.contrib.auth import get_user_model

from .constants import MAX_CHARFIELD_LENGTH, STR_TRUNCATE_LENGTH

User = get_user_model()


class BaseModel(models.Model):
    is_published = models.BooleanField(
        default=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        abstract = True


class BaseTitle(models.Model):
    title = models.CharField(
        max_length=MAX_CHARFIELD_LENGTH,
    )

    class Meta:
        abstract = True


class Location(BaseModel):
    name = models.CharField(
        max_length=MAX_CHARFIELD_LENGTH,
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'
        ordering = ('name',)

    def __str__(self):
        return self.name[:STR_TRUNCATE_LENGTH]


class Category(BaseModel, BaseTitle):
    description = models.TextField()
    slug = models.SlugField(
        unique=True,
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'
        ordering = ('title',)

    def __str__(self):
        return self.title[:STR_TRUNCATE_LENGTH]


class Post(BaseModel, BaseTitle):
    text = models.TextField()
    pub_date = models.DateTimeField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
    )
    image = models.ImageField(
        upload_to='images',
        blank=True,
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        default_related_name = 'posts'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.title[:STR_TRUNCATE_LENGTH]


class Comment(models.Model):
    text = models.TextField()
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('created_at',)

    def __str__(self):
        return f'Комментарий пользователя {self.author}'
