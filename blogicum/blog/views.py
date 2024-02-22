from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.forms.widgets import DateInput
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from blog.models import Category, Post, Comments

from .forms import PostForm, CommentForm

now = timezone.now()

User = get_user_model()


class OnlyAuthorMixin(UserPassesTestMixin):
    """
    Проверяем является ли пользователь автором поста
    или хозяином аккаунта
    """
    def test_func(self):
        object = self.get_object()
        username = getattr(object, 'username', None)
        author = getattr(object, 'author', None)
        user = self.request.user
        return user.username == username or (author is not None and user == author)


class UserUpdateView(OnlyAuthorMixin, UpdateView):
    """Изменение данных пользователя"""
    model = User
    template_name = 'blog/user.html'
    slug_field = 'username'
    fields = ['first_name', 'last_name', 'username', 'email']

    def get_success_url(self):
        # Возвращаем пользователя на страницу редактирования после успешного обновления
        return reverse_lazy('blog:profile', kwargs={'slug': self.object.username})


class PostMixin:
    model = Post


class PostDetailView(PostMixin, DetailView):
    """Просмотр поста"""
    
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
    """"Создание новой публикации"""
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'slug': self.request.user.username}
        )


class PostUpdateView(PostMixin, OnlyAuthorMixin, UpdateView):
    """Изменение существующей публикации """
    form_class = PostForm

    def dispatch(self, request, *args, **kwargs):
        # Проверяем, имеет ли пользователь право на редактирование
        self.object = self.get_object()
        if not self.object.author == request.user:
            # Если пользователь не автор, выполняем редирект на страницу публикации
            post_url = reverse('blog:post_detail', kwargs={'pk': self.object.pk})
            return redirect(post_url)
        # Если проверка пройдена, продолжаем обычный поток выполнения
        return super(PostUpdateView, self).dispatch(request, *args, **kwargs)


class PostListMixin(PostMixin):
    """Добавляем в миксине фильтры и связанные модели"""
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related(
            "category",
            "location",
            "author",
        ).filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=now,
        )


class PostListView(PostListMixin, ListView):
    pass


class CommentCreateView(LoginRequiredMixin, CreateView):
    post_my = None
    model = Comments
    form_class = CommentForm
    template_name = 'blog/comments.html'

    # Переопределяем dispatch()
    def dispatch(self, request, *args, **kwargs):
        self.post_my = get_object_or_404(Post, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    # Переопределяем form_valid()
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post_my = self.post_my
        return super().form_valid(form)

    # Переопределяем get_success_url()
    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.post_my.pk})


class CategoryListView(PostListMixin, ListView):
    template_name = 'blog/category_list.html'

    def get_queryset(self):
        """Фильтруем посты по категории."""
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['slug'],
        )

        return super().get_queryset().filter(
            category=self.category,
        )

    def get_context_data(self, **kwargs):
        """Добавляем категории в контекст."""
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class UserDetailView(PostListMixin, ListView):
    template_name = 'blog/profile.html'
    paginate_by = 10

    def get_queryset(self):
        self.author = get_object_or_404(
            User,
            username=self.kwargs['slug'],
        )
        # Если пользователь является автором
        # то показываем ему все посты без фильтров
        if self.request.user == self.author:
            queryset = Post.objects.select_related(
                "category",
                "location",
                "author",
            ).filter(
                author=self.author,
            )
        # Если пользователь не является автором
        # то показываем ему только опубликованные посты
        else:
            queryset = super().get_queryset().filter(
                author=self.author
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.author
        return context


