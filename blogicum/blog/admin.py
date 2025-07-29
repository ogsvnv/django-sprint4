from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Category, Location, Post, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'created_at')
    list_filter = ('is_published',)
    search_fields = ('title', 'description')
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'description', 'is_published'),
        }),
    )

    def get_fieldsets(self, request, obj=None):
        return [
            (None, {
                'fields': ('title', 'slug', 'description', 'is_published'),
                'description': (
                    'Идентификатор страницы для URL: разрешены '
                    'символы латиницы, цифры, дефис и подчёркивание. '
                    'Снимите галочку "Опубликовано", чтобы скрыть публикацию.'
                ),
            }),
        ]


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published', 'created_at')
    list_filter = ('is_published',)
    search_fields = ('name',)
    fieldsets = (
        (None, {
            'fields': ('name', 'is_published'),
        }),
    )

    def get_fieldsets(self, request, obj=None):
        return [
            (None, {
                'fields': ('name', 'is_published'),
                'description': 'Снимите галочку "Опубликовано", чтобы'
                ' скрыть публикацию.',
            }),
        ]


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'pub_date', 'author', 'category',
        'location', 'is_published', 'created_at', 'get_image'
    )
    list_filter = ('is_published', 'category', 'location', 'author')
    search_fields = ('title', 'text')
    date_hierarchy = 'pub_date'
    fieldsets = (
        (
            None,
            {
                'fields': (
                    'title',
                    'text',
                    'pub_date',
                    'author',
                    'category',
                    'location',
                    'is_published',
                    'image',
                ),
            },
        ),
    )

    def get_fieldsets(self, request, obj=None):
        return [
            (None, {
                'fields': (
                    'title',
                    'text',
                    'pub_date',
                    'author',
                    'category',
                    'location',
                    'is_published',
                    'image',
                ),
                'description': (
                    'Если установить дату и время в будущем — '
                    'можно делать отложенные публикации. '
                    'Снимите галочку "Опубликовано", чтобы скрыть публикацию.'
                ),
            }),
        ]

    @admin.display(description='Изображение')
    def get_image(self, obj):
        return (
            mark_safe(
                f'<img src={obj.image.url} width="80" height="60">'
            ) if obj.image else ''
        )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'created_at')
    list_filter = ('author', 'post', 'created_at')
    search_fields = ('text',)
    date_hierarchy = 'created_at'
    fieldsets = (
        (None, {
            'fields': ('text', 'post', 'author'),
        }),
    )

    def get_fieldsets(self, request, obj=None):
        return [
            (None, {
                'fields': ('text', 'post', 'author'),
                'description': 'Комментарий к публикации.',
            }),
        ]
