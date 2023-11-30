from django.shortcuts import render


def csrf_failure(request, reason=''):
    return render(request, 'pages/403csrf.tmml', status=403)


def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)


def server_error(request):
    return (request, 'pages/500.html')
