from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone

from django.views.generic import (CreateView, DeleteView,
                                  DetailView, ListView, UpdateView)

from blog.models import Category, Post
from .forms import CommentForm, PostForm
from .query_utils import get_model_queryset
from .views_mixins import (CommentMixin, OnlyAuthorMixin,
                           OnlyAuthorCommentMixin,
                           PostMixin, PostListMixin)


# Импортируем число постов на странице из настроек проекта
paginate_by = getattr(settings, 'PAGINATE_BY', 10)
User = get_user_model()


class PostDetailView(PostMixin, DetailView):
    """Просмотр поста"""

    # Автору показываем все его посты
    # другим пользователям только опубликованные
    def get_object(self):
        queryset = super().get_object()
        post = get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        # Если пользователь – автор поста, то показываем ему пост
        # в любом случае
        # Если пользователь не автор, то фильтруем посты и
        # проверяем опубликован ли пост и категория
        if (
            self.request.user != post.author and (
                not post.is_published
                or post.pub_date > timezone.now()
                or not post.category.is_published
            )
        ):
            raise Http404
        return queryset

    # Добавляем комментарии к посту
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            # Дополнительно подгружаем авторов комментариев,
            # чтобы избежать множества запросов к БД.
            self.object.comments.select_related('author')
        )
        return context


class PostCreateView(PostMixin, LoginRequiredMixin, CreateView):
    """Создание новой публикации"""

    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostListView(PostListMixin, ListView):
    """Список постов"""


class PostUpdateView(PostMixin, UpdateView):
    """Изменение существующей публикации"""

    form_class = PostForm

    def dispatch(self, request, *args, **kwargs):
        # Проверяем, имеет ли пользователь право на редактирование
        post_object = self.get_object()
        if post_object.author != request.user:
            # Если пользователь не автор,
            # выполняем редирект на страницу публикации
            post_url = reverse(
                'blog:post_detail',
                kwargs={'post_id': post_object.pk}
            )
            return redirect(post_url)
        # Если проверка пройдена, продолжаем обычный поток выполнения
        return super().dispatch(request, *args, **kwargs)


class PostDeleteView(PostMixin, OnlyAuthorMixin, DeleteView):
    """Удаление публикации"""

    form_class = PostForm
    template_name = 'blog/post_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context

    def get_success_url(self):
        return reverse('blog:index',)


class CommentCreateView(CommentMixin, LoginRequiredMixin, CreateView):
    """Создание комментариев"""

    template_name = 'blog/comments.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)


class CommentDeleteView(CommentMixin, OnlyAuthorCommentMixin, DeleteView):
    """Удаление комментария"""


class CommentUpdateView(CommentMixin, OnlyAuthorCommentMixin, UpdateView):
    """Изменение комментария"""


class CategoryListView(PostListMixin, ListView):
    """Просмотр категории постов"""

    slug_url_kwarg = 'category_slug'
    template_name = 'blog/category_list.html'

    def get_category(self):
        """Получаем категорию"""
        category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True,
        )
        return category

    def get_queryset(self):
        """Фильтруем посты по категории."""
        category = self.get_category()
        return get_model_queryset(model_manager=category.posts)

    def get_context_data(self, **kwargs):
        """Добавляем категорию в контекст"""
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_category()
        return context


class UserDetailView(PostListMixin, ListView):
    """Просмотр информации о пользователе"""

    template_name = 'blog/profile.html'
    paginate_by = paginate_by
    slug_url_kwarg = 'username'

    def get_author(self):
        """Получаем автора"""
        author = get_object_or_404(
            User,
            username=self.kwargs['username'],
        )
        return author

    def get_queryset(self):
        """
        Меняем логику отображения постов в зависимости от того
        является ли пользователем автором или нет
        """
        author = self.get_author()
        # Если пользователь является автором
        # то показываем ему все посты без фильтров
        if self.request.user == author:
            queryset = get_model_queryset(
                model_manager=author.posts,
                add_filters=False,
                add_annotation=True,
            )
        # Если пользователь не является автором
        # то показываем ему только опубликованные посты
        else:
            queryset = get_model_queryset(
                model_manager=author.posts,
                add_filters=True,
                add_annotation=True,
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_author()
        return context


class UserUpdateView(LoginRequiredMixin, UpdateView):
    """Изменение данных пользователя"""

    model = User
    template_name = 'blog/user.html'
    fields = ['first_name', 'last_name', 'username', 'email']

    def get_object(self):
        """Возвращаем объект пользователя из request.user"""
        return self.request.user

    def get_success_url(self):
        # Возвращаем пользователя на страницу редактирования
        # после успешного обновления
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.object.username}
        )
