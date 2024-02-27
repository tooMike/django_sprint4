"""Функция для получения постов"""

from django.db.models import Count

from django.utils import timezone

from blog.models import Post


def get_model_queryset(
        model_manager=Post.objects,
        add_filters=True,
        add_annotation=False):
    """Функция для получения нужных постов"""
    queryset = model_manager.select_related(
        'category',
        'location',
        'author',
    ).order_by('-pub_date')
    if add_filters:
        queryset = queryset.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now(),
        )
    if add_annotation:
        queryset = queryset.annotate(
            comment_count=Count('comments')
        )
    return queryset
