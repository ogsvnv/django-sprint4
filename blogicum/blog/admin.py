from django.contrib import admin

from .models import Category, Location, Post


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
        'location', 'is_published', 'created_at'
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
                ),
                'description': (
                    'Если установить дату и время в будущем — '
                    'можно делать отложенные публикации. '
                    'Снимите галочку "Опубликовано", чтобы скрыть публикацию.'
                ),
            }),
        ]
