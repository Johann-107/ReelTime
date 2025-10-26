from django.shortcuts import render, redirect, get_object_or_404
from .forms import MovieForm
from .models import Movie, MovieAdminDetails
from accounts.decorators import admin_required
from datetime import datetime
from zoneinfo import ZoneInfo
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages
from .forms import MovieAdminDetailsForm

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


@login_required
def edit_movie_view(request, pk):
    detail = get_object_or_404(MovieAdminDetails, pk=pk)

    # ✅ Only the admin who added the movie can edit it
    if not (request.user.is_admin and detail.admin == request.user):
        messages.error(request, "You do not have permission to edit this movie.")
        return redirect('movie_detail', pk=pk)

    movie_form = MovieForm(instance=detail.movie)
    detail_form = MovieAdminDetailsForm(instance=detail)

    if request.method == 'POST':
        movie_form = MovieForm(request.POST, instance=detail.movie)
        detail_form = MovieAdminDetailsForm(request.POST, request.FILES, instance=detail)

        if movie_form.is_valid() and detail_form.is_valid():
            movie_form.save()
            detail_form.save()
            messages.success(request, "Movie details updated successfully!")
            return redirect('movie_detail', pk=pk)

    context = {
        'movie_form': movie_form,
        'detail_form': detail_form,
        'detail': detail,
    }
    return render(request, 'movies/edit_movie.html', context)


@login_required
def delete_movie_view(request, pk):
    detail = get_object_or_404(MovieAdminDetails, pk=pk)

    # ✅ Only the admin who added the movie can delete it
    if not (request.user.is_admin and detail.admin == request.user):
        messages.error(request, "You do not have permission to delete this movie.")
        return redirect('movie_detail', pk=pk)

    if request.method == 'POST':
        detail.movie.delete()  # deletes movie and all related admin details
        messages.success(request, "Movie deleted successfully!")
        return redirect('movie_list')

    return render(request, 'movies/delete_movie.html', {'detail': detail})


# Movie List view
def movie_list_view(request):
    manila_tz = ZoneInfo("Asia/Manila")
    today = datetime.now(manila_tz).date()

    user = request.user

    # ✅ Filter: only show movies added by the current admin
    if user.is_authenticated and user.is_admin:
        admin_details_qs = MovieAdminDetails.objects.select_related('movie').filter(admin=user)
    else:
        # 👥 Non-admin: only now showing and coming soon
        admin_details_qs = MovieAdminDetails.objects.select_related('movie').filter(
            end_date__gte=today  # excludes already ended movies
        )

    movies = []

    for detail in admin_details_qs:
        release_date = detail.release_date
        end_date = detail.end_date
        days_diff = (release_date - today).days

        if days_diff == 0:
            release_label = "Today"
        elif days_diff == 1:
            release_label = "Tomorrow"
        elif days_diff < 0 and detail.end_date < today:
            release_label = "Ended"
        else:
            release_label = release_date.strftime("%B %d, %Y").replace(" 0", " ")

        if isinstance(detail.showing_times, (list, tuple)):
            showing_times_display = ", ".join(detail.showing_times)
        else:
            showing_times_display = str(detail.showing_times)

        end_date_label = end_date.strftime("%B %d, %Y").replace(" 0", " ") if end_date else "N/A"

        movies.append({
            'detail': detail,  # this is a MovieAdminDetails instance
            'release_label': release_label,
            'end_date': end_date_label,
            'showing_times_display': showing_times_display,
            'days_diff': days_diff,
        })

    # Sort: Today (0) → Upcoming (>0) → Past (<0)
    movies.sort(key=lambda x: (x['days_diff'] != 0, x['days_diff'] > 0, abs(x['days_diff'])))

    return render(request, 'movies/movie_list.html', {'movies': movies})


@login_required
def movie_detail_view(request, pk):
    detail = get_object_or_404(MovieAdminDetails.objects.select_related('movie'), pk=pk)

    can_manage = request.user.is_admin and detail.admin == request.user

    manila_tz = ZoneInfo("Asia/Manila")
    today = datetime.now(manila_tz).date()

    release_label = detail.release_date.strftime("%B %d, %Y").replace(" 0", " ")
    end_date_label = detail.end_date.strftime("%B %d, %Y").replace(" 0", " ")
    showing_times_display = ", ".join(detail.showing_times) if isinstance(detail.showing_times, (list, tuple)) else str(detail.showing_times)

    context = {
        'detail': detail,
        'release_label': release_label,
        'end_date_label': end_date_label,
        'showing_times_display': showing_times_display,
        'can_manage': can_manage,
    }

    return render(request, 'movies/movie_detail.html', context)