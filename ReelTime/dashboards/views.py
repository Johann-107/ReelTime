from django.contrib.auth.decorators import login_required
from accounts.decorators import admin_required
from django.shortcuts import render

@login_required
def user_dashboard(request):
    return render(request, 'dashboards/user_dashboard.html', {
        'username': request.user.username
    })

@admin_required
def admin_dashboard(request):
    return render(request, 'dashboards/admin_dashboard.html')
