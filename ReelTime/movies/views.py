from django.shortcuts import render, redirect
from .forms import MovieForm
from .models import Movie
from accounts.decorators import admin_required
from datetime import datetime
from zoneinfo import ZoneInfo


@admin_required
def add_movie(request):
    if request.method == 'POST':
        form = MovieForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')  # Redirect back to admin home
    else:
        form = MovieForm()

    return render(request, 'movies/add_movie.html', {'form': form})


# Movie List view
def movie_list_view(request):
    # Use modern zoneinfo for Philippine timezone
    manila_tz = ZoneInfo("Asia/Manila")
    today = datetime.now(manila_tz).date()

    movies_qs = Movie.objects.all()
    movies = []

    for m in movies_qs:
        rd = m.release_date
        days_diff = (rd - today).days

        # Determine how to display release date
        if days_diff == 0:
            release_label = "Today"
        elif days_diff == 1:
            release_label = "Tomorrow"
        else:
            release_label = rd.strftime("%B %d, %Y").replace(" 0", " ")

        # Handle showing_times gracefully
        showing_times_display = ""
        try:
            if isinstance(m.showing_times, (list, tuple)):
                showing_times_display = ", ".join(m.showing_times)
            else:
                showing_times_display = str(m.showing_times)
        except Exception:
            showing_times_display = str(m.showing_times)

        movies.append({
            'obj': m,
            'release_label': release_label,
            'showing_times_display': showing_times_display,
            'days_diff': days_diff,
        })

    # Today (0) → Upcoming (>0) → Past (<0)
    movies.sort(key=lambda x: (x['days_diff'] != 0, x['days_diff'] > 0, abs(x['days_diff'])))

    return render(request, 'movies/movie_list.html', {'movies': movies})
