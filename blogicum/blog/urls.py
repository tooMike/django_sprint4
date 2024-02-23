from django.urls import path

from . import views

app_name = "blog"

urlpatterns = [
    path("", views.PostListView.as_view(), name="index"),
    path(
        "posts/<int:pk>/comment",
        views.CommentCreateView.as_view(),
        name="add_comment",
    ),
    path(
        "posts/<int:pk>/edit_comment/<int:comment_id>",
        views.CommentUpdateView.as_view(),
        name="edit_comment",
    ),
    path(
        "posts/<int:pk>/delete_comment/<int:comment_id>",
        views.CommentDeleteView.as_view(),
        name="delete_comment",
    ),
    path(
        "posts/<int:pk>/",
        views.PostDetailView.as_view(),
        name="post_detail"
    ),
    path("posts/create/", views.PostCreateView.as_view(), name="create_post"),
    path(
        "posts/<int:pk>/edit/",
        views.PostUpdateView.as_view(),
        name="edit_post"
    ),
    path(
        "posts/<int:pk>/delete/",
        views.PostDeleteView.as_view(),
        name="delete_post"
    ),
    path(
        "category/<slug:slug>/",
        views.CategoryListView.as_view(),
        name="category_posts"
    ),
    path(
        "profile/<slug:slug>/edit",
        views.UserUpdateView.as_view(),
        name="edit_profile"
    ),
    path(
        "profile/<slug:slug>/",
        views.UserDetailView.as_view(),
        name="profile"
    ),
]
