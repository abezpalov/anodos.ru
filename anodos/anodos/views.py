import json

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout


def view_index(request):
    context = {}
    return render(request, 'main.html', context)


def view_login(request):
    context = {}
    return render(request, 'login.html', context)


def ajax_login(request):
    """AJAX-представление: Log-in."""

    if not request.is_ajax() or request.method != 'POST':
        return HttpResponse(status=400)

    username = request.POST.get('username')
    password = request.POST.get('password')

    user = authenticate(username=username, password=password)

    if user is None:
        result = {
            'status': 'error',
            'message': 'Имя пользователя или пароль не корректны.'}
    elif user.is_active:
        login(request, user)
        result = {'status': 'success'}
    else:
        result = {
            'status': 'error',
            'message': 'Пользователь заблокирован.'}

    return HttpResponse(json.dumps(result), 'application/javascript')


def ajax_logout(request):
    """AJAX-представление: Log-out"""

    import json

    if not request.is_ajax() or request.method != 'POST':
        return HttpResponse(status=400)

    logout(request)

    result = {'status': 'success'}

    return HttpResponse(json.dumps(result), 'application/javascript')
