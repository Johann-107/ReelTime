from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Home view
def home(request):
    return render(request, 'reel_time/index.html')

# Movie List view
def movie_list_view(request):
    return render(request, 'reel_time/movies.html')

@login_required
def user_dashboard_view(request):
    return render(request, 'user-dashboard.html')