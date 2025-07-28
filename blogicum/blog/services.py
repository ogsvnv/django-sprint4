from django.db.models import Count
from django.utils import timezone


def annotate_posts_with_comment_count(queryset):
    return queryset \
        .select_related('category', 'location', 'author') \
        .annotate(comment_count=Count('comments')) \
        .order_by('-pub_date')


def filter_published_posts(queryset):
    return queryset.filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    )
