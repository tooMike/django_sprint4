from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Count

from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone


from blog.models import Post, Comments
from .forms import CommentForm


class OnlyAuthorMixin(UserPassesTestMixin):
    """Проверяем является ли пользователь автором поста"""

    def test_func(self):
        post = get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        return self.request.user == post.author


class OnlyAuthorCommentMixin(UserPassesTestMixin):
    """Проверяем является ли пользователь автором комментария"""

    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def test_func(self):
        comment = get_object_or_404(Comments, pk=self.kwargs.get('comment_id'))
        return self.request.user == comment.author


class PostMixin:
    """Миксин для поста"""

    model = Post
    pk_url_kwarg = 'post_id'


class PostListMixin(PostMixin):
    """Добавляем в миксине фильтры и связанные модели"""

    paginate_by = 10

    def get_queryset(self):
        return get_model_queryset(
            add_filters=True,
            add_annotation=True,
        )


class CommentMixin():
    """Миксин для комментариев"""

    model = Comments
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.object.post.pk}
        )


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
