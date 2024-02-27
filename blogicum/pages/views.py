from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render
from django.views.generic import CreateView, TemplateView
from django.urls import reverse_lazy


class AboutTemplateView(TemplateView):
    """Отображение страницы О проекте"""

    template_name = 'pages/about.html'


class RulesTemplateView(TemplateView):
    """Отображение страницы Правила"""

    template_name = 'pages/rules.html'


class AuthCreateView(CreateView):
    """Форма регистрации"""

    template_name = 'registration/registration_form.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('blog:index')


def page_not_found(request, exception):
    """Функция для отрисовки страницы 404 ошибки"""
    return render(request, 'pages/404.html', status=404)


def csrf_failure(request, reason=''):
    """Функция для отрисовки страницы 403 ошибки"""
    return render(request, 'pages/403csrf.html', status=403)


def server_error(request):
    """Функция для отрисовки страницы 500 ошибки"""
    return render(request, 'pages/500.html', status=500)
