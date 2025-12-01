from django.contrib.auth.decorators import login_required
from accounts.decorators import admin_required
from django.shortcuts import render
from movies.models import MovieAdminDetails
from reservations.models import Reservation
from datetime import datetime
from zoneinfo import ZoneInfo

@login_required
def user_dashboard(request):
    manila_tz = ZoneInfo("Asia/Manila")
    today = datetime.now(manila_tz).date()

    user = request.user

    # Get movies based on user type
    if user.is_authenticated and user.is_admin:
        admin_details_qs = MovieAdminDetails.objects.select_related('movie').filter(admin=user)
        movies_list = admin_details_qs
    else:
        # Non-admin: only now showing and coming soon, get unique movies by title
        admin_details_qs = MovieAdminDetails.objects.select_related('movie').filter(
            end_date__gte=today  # excludes already ended movies
        )
        
        # Get unique movie titles (case-insensitive)
        seen_titles = set()
        movies_list = []
        for detail in admin_details_qs:
            title_lower = detail.movie.title.lower().strip()
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                movies_list.append(detail)

    movies = []

    for detail in movies_list:
        release_date = detail.release_date
        end_date = detail.end_date
        days_diff = (release_date - today).days

        # Human-readable release label
        if days_diff == 0:
            release_label = "Today"
        elif days_diff == 1:
            release_label = "Tomorrow"
        elif days_diff < 0 and detail.end_date < today:
            release_label = "Ended"
        else:
            release_label = release_date.strftime("%B %d, %Y").replace(" 0", " ")

        # Handle showing_times list
        if isinstance(detail.showing_times, (list, tuple)):
            showing_times_display = ", ".join(
                s['time'] for s in detail.showing_times if 'time' in s
            )
        else:
            showing_times_display = str(detail.showing_times)

        # Format end date
        end_date_label = end_date.strftime("%B %d, %Y").replace(" 0", " ") if end_date else "N/A"

        movies.append({
            'detail': detail,
            'release_label': release_label,
            'end_date': end_date_label,
            'showing_times_display': showing_times_display,
            'days_diff': days_diff,
        })

    # Sort: Today (0) → Upcoming (>0) → Past (<0)
    movies.sort(key=lambda x: (x['days_diff'] != 0, x['days_diff'] > 0, abs(x['days_diff'])))

    return render(request, 'dashboards/user_dashboard.html', {
        'username': request.user.username,
        'movies': movies
    })

@admin_required
def admin_dashboard(request):
    movies_count = MovieAdminDetails.objects.filter(admin=request.user).count()
    reservations_count = Reservation.objects.filter(movie_detail__admin=request.user).count()
    
    # Get movies for this admin
    admin_movies = MovieAdminDetails.objects.filter(
        admin=request.user
    ).select_related('movie').order_by('-created_at')
    
    # Get all reservations for this admin's movies (limit to 5 most recent)
    reservations = Reservation.objects.filter(
        movie_detail__admin=request.user
    ).select_related('user', 'movie_detail__movie').order_by('-reservation_date')[:5]
    
    return render(request, 'dashboards/admin_dashboard.html', {
        'movies_count': movies_count,
        'reservations_count': reservations_count,
        'admin_movies': admin_movies,
        'recent_reservations': reservations,
    })
