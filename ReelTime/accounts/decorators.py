from django.shortcuts import redirect
from functools import wraps
from .models import User


def login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('login')
        user = User.objects.get(id=user_id)
        if not user.is_admin:
            return redirect('user_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper
