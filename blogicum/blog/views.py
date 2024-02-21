from typing import Any
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
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


class PostCreateView(PostMixin, CreateView):
    fields = "__all__"


class PostListMixin(PostMixin):
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related(
            "category",
            "location",
            "author",
        ).filter(pub_date__lte=now, is_published=True, category__is_published=True)


class PostListView(PostListMixin, ListView):
    pass


class CategoryListView(PostListMixin, ListView):

    def get_queryset(self, **kwargs):
        """Фильтруем посты по категории."""
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs["slug"],
            is_published=True,
        )
        return super().get_queryset().filter(category=self.category)

    def get_context_data(self, **kwargs):
        """Добавляем категории в контекст."""
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        return context


class UserDetailView(DetailView):
    model = User
    slug_field = "username"
    template_name = "blog/profile.html"
    context_object_name = "profile"

    def get_context_data(self, **kwargs):
        """Добавляем посты нужного автора в контекст."""
        context = super().get_context_data(**kwargs)
        post_list = Post.objects.select_related(
            "author",
        ).filter(
            author__username=self.kwargs["slug"],
        )
        paginator = Paginator(post_list, 10)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        context["page_obj"] = page_obj
        return context
