from django import forms
from django.core.exceptions import ValidationError
from django.core.mail import send_mail

from .models import Post


class PostForm(forms.ModelForm):
    
    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'})
        } 

    