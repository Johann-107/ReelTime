from django.shortcuts import render, redirect, get_object_or_404
from .forms import MovieForm
from .models import Movie, MovieAdminDetails, Reservation
from accounts.decorators import admin_required
from datetime import datetime
from zoneinfo import ZoneInfo
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages
from .forms import MovieAdminDetailsForm
from django.db.models import Q
import json

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

        # ✅ Include end date (formatted)
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
    # Fetch the MovieAdminDetails entry
    detail = get_object_or_404(MovieAdminDetails.objects.select_related('movie'), pk=pk)

    # Only admins who own the movie can edit/delete
    can_manage = request.user.is_admin and detail.admin == request.user

    manila_tz = ZoneInfo("Asia/Manila")
    today = datetime.now(manila_tz).date()

    release_label = detail.release_date.strftime("%B %d, %Y").replace(" 0", " ")
    end_date_label = detail.end_date.strftime("%B %d, %Y").replace(" 0", " ")
    if isinstance(detail.showing_times, (list, tuple)):
        showing_times_display = ", ".join(
            s['time'] for s in detail.showing_times if 'time' in s
        )
    else:
        showing_times_display = str(detail.showing_times)
    context = {
        'detail': detail,
        'release_label': release_label,
        'end_date_label': end_date_label,
        'showing_times_display': showing_times_display,
        'can_manage': can_manage,
    }

    return render(request, 'movies/movie_detail.html', context)


@login_required
def reserve_movie_view(request, movie_id):
    """
    Show all registered cinemas with their details for this movie
    """
    from django.contrib.auth import get_user_model
    from django.db.models import Sum

    User = get_user_model()

    # Get the movie
    movie = get_object_or_404(Movie, id=movie_id)

    # Get all cinema admins
    cinema_admins = User.objects.filter(is_admin=True).order_by('cinema_name')

    movie_details_dict = {}
    for detail in MovieAdminDetails.objects.filter(movie=movie).select_related('admin'):
        movie_details_dict[detail.admin_id] = detail

    # Prepare cinema data
    cinemas = []
    for admin in cinema_admins:
        movie_detail = movie_details_dict.get(admin.id)

        if movie_detail:
            # Cinema has this movie - build showtimes with remaining seats
            showtimes_data = []
            for s in movie_detail.showing_times:  # this is already a Python list of dicts
                # Expect each item to be a dict with 'time' and 'max_seats'
                if isinstance(s, dict):
                    time = s.get("time")
                    max_seats = s.get("max_seats", 0)
                else:
                    # If legacy string format, assume a default max_seats (e.g., 100)
                    time = s
                    max_seats = 100  # arbitrary fallback

                # Calculate reserved seats
                reserved = Reservation.objects.filter(
                    movie_detail=movie_detail,
                    selected_showtime=time
                ).aggregate(total_reserved=Sum('number_of_seats'))['total_reserved'] or 0

                remaining = max_seats - reserved
                showtimes_data.append({
                    "time": time,
                    "max_seats": max_seats,
                    "remaining": remaining,
                })

            cinemas.append({
                'detail_id': movie_detail.id,
                'cinema_name': admin.cinema_name,
                'showing_times': json.dumps(showtimes_data),
                'poster': movie_detail.poster,
                'has_movie': True,
            })
        else:
            # Cinema doesn't have this movie yet
            cinemas.append({
                'detail_id': None,
                'cinema_name': admin.cinema_name,
                'showing_times': json.dumps([]),
                'poster': None,
                'has_movie': False,
            })

    context = {
        'movie': movie,
        'cinemas': cinemas,
    }

    return render(request, 'movies/reserve_movie.html', context)


@login_required
def confirm_reservation_view(request, detail_id):
    """
    Confirm the reservation for a specific cinema and showtime.
    """
    detail = get_object_or_404(MovieAdminDetails, id=detail_id)

    if request.method == 'POST':
        # Match your form field names from the modal
        selected_date = request.POST.get('selected_date')
        selected_showtime = request.POST.get('selected_showtime')
        number_of_seats = request.POST.get('number_of_seats', 1)

        # Create the reservation record
        reservation = Reservation.objects.create(
            user=request.user,
            movie_detail=detail,
            cinema_name=detail.admin.cinema_name,
            selected_date=selected_date,
            selected_showtime=selected_showtime,
            number_of_seats=int(number_of_seats),
            status='confirmed',
        )

        messages.success(
            request,
            f"Reservation confirmed for {detail.movie.title} at {detail.admin.cinema_name} "
            f"on {selected_date} ({selected_showtime})!"
        )
        return redirect('user_dashboard')

    context = {
        'detail': detail,
    }

    return render(request, 'movies/confirm_reservation.html', context)


@login_required
def user_reservations_view(request):
    reservations = Reservation.objects.filter(user=request.user)
    return render(request, 'movies/reservations.html', {'reservations': reservations})