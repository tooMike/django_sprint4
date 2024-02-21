from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms.widgets import DateInput
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic import CreateView, DetailView, ListView

from blog.models import Category, Post

now = timezone.now()

User = get_user_model()


class PostMixin:
    model = Post


class PostDetailView(PostMixin, DetailView):
    pass


class PostCreateView(PostMixin, LoginRequiredMixin, CreateView):
    fields = '__all__'

    def get_form(self, form_class=None):
        """Настроить виджеты формы внутри представления."""
        form = super().get_form(form_class)
        form.fields['pub_date'].widget = DateInput(attrs={'type': 'date'})
        return form



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
            pub_date__lte=now,
            is_published=True,
            category__is_published=True
        )


class PostListView(PostListMixin, ListView):
    pass


class CategoryListView(PostListMixin, ListView):
    template_name = 'blog/category_list.html'

    def get_queryset(self):
        """Фильтруем посты по категории."""
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['slug'],
            is_published=True,
        )

        return super().get_queryset().filter(category=self.category)

    def get_context_data(self, **kwargs):
        """Добавляем категории в контекст."""
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class UserDetailView(PostListMixin, ListView):
    template_name = 'blog/profile.html'

    def get_queryset(self):
        self.author = get_object_or_404(
            User,
            username=self.kwargs['slug'],
        )
        return super().get_queryset().filter(author=self.author)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.author
        return context
