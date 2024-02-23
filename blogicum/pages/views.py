from django.shortcuts import render
from django.views.generic import TemplateView


class AboutTemplateView(TemplateView):
    """Отображение страницы О проекте"""

    template_name = 'pages/about.html'


class RulesTemplateView(TemplateView):
    """Отображение страницы Правила"""

    template_name = 'pages/rules.html'


def page_not_found(request, exception):
    """Функция для отрисовки страницы 404 ошибки"""
    return render(request, 'pages/404.html', status=404)


def csrf_failure(request, reason=''):
    """Функция для отрисовки страницы 403 ошибки"""
    return render(request, 'pages/403csrf.html', status=403)


def server_error(request):
    """Функция для отрисовки страницы 500 ошибки"""
    return render(request, 'pages/500.html', status=500)
