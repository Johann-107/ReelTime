from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from movies.models import MovieAdminDetails  # Import from your movies app
from datetime import date

# Home view
def home(request):
    today = date.today()
    
    # Get MovieAdminDetails that are currently showing
    available_movies = MovieAdminDetails.objects.filter(
        release_date__lte=today,
        end_date__gte=today
    )[:6]  # Limit to 6
    
    # Get coming soon movies
    coming_soon_movies = MovieAdminDetails.objects.filter(
        release_date__gt=today
    ).order_by('release_date')[:3]  # Get next 3
    
    context = {
        'available_movies': available_movies,
        'coming_soon_movies': coming_soon_movies,
    }
    return render(request, 'reel_time/index.html', context)

@login_required
def user_dashboard_view(request):
    return render(request, 'user-dashboard.html')