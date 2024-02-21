from django.shortcuts import render


def about(request):
    """Функция для отрисовки страницы О проекте"""
    template = 'pages/about.html'
    return render(request, template)


def rules(request):
    """Функция для отрисовки страницы правил"""
    template = 'pages/rules.html'
    return render(request, template)


def page_not_found(request, exception):
    """Функция для отрисовки страницы 404 ошибки"""
    return render(request, 'pages/404.html', status=404)


def csrf_failure(request, reason=''):
    """Функция для отрисовки страницы 403 ошибки"""
    return render(request, 'pages/403csrf.html', status=403)


def server_error(request):
    """Функция для отрисовки страницы 500 ошибки"""
    return render(request, 'pages/500.html', status=500)
