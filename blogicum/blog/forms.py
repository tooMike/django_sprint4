from django import forms

from .models import Post, Comments


class PostForm(forms.ModelForm):
    """Форма для создания поста"""

    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }


class CommentForm(forms.ModelForm):
    """Форма для создания комментариев"""

    class Meta:
        model = Comments
        fields = ('text',)
