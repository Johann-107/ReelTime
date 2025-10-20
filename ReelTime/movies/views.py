from django.shortcuts import render, redirect
from .forms import MovieForm
from .models import Movie, MovieAdminDetails
from accounts.decorators import admin_required
from datetime import datetime
from zoneinfo import ZoneInfo


@admin_required
def add_movie(request):
    if request.method == 'POST':
        form = MovieForm(request.POST, request.FILES, admin=request.user)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')  # Redirect back to admin home
    else:
        form = MovieForm(admin=request.user)

    return render(request, 'movies/add_movie.html', {'form': form})


# Movie List view
def movie_list_view(request):
    manila_tz = ZoneInfo("Asia/Manila")
    today = datetime.now(manila_tz).date()

    # You can filter by admin=request.user if needed
    admin_details_qs = MovieAdminDetails.objects.select_related('movie').all()

    movies = []

    for detail in admin_details_qs:
        release_date = detail.release_date
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
            showing_times_display = ", ".join(detail.showing_times)
        else:
            showing_times_display = str(detail.showing_times)

        movies.append({
            'detail': detail,  # this is a MovieAdminDetails instance
            'release_label': release_label,
            'showing_times_display': showing_times_display,
            'days_diff': days_diff,
        })

    # Sort: Today (0) → Upcoming (>0) → Past (<0)
    movies.sort(key=lambda x: (x['days_diff'] != 0, x['days_diff'] > 0, abs(x['days_diff'])))

    return render(request, 'movies/movie_list.html', {'movies': movies})