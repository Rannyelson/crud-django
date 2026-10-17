from functools import wraps
from urllib.parse import urlencode

from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(
                f"{reverse('login')}?{urlencode({'next': request.path})}"
            )
        if not request.user.is_admin:
            messages.error(request, 'Acesso negado: área restrita ao administrador.')
            return redirect('home')
        return view_func(request, *args, **kwargs)

    return wrapper
