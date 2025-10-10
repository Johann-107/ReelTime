from accounts.decorators import login_required, admin_required
from django.shortcuts import render

# Create your views here.
@login_required
def user_dashboard(request):
    username = request.session.get('username')
    return render(request, 'dashboards/user_dashboard.html', {'username': username})


@admin_required
def admin_dashboard(request):
    return render(request, 'dashboards/admin_dashboard.html')