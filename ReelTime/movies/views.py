from django.shortcuts import render, redirect, get_object_or_404
from .forms import MovieForm
from .models import Movie, MovieAdminDetails
from reservations.models import Reservation
from accounts.decorators import admin_required
from datetime import datetime
from zoneinfo import ZoneInfo
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import MovieAdminDetailsForm
from django.http import JsonResponse
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

    # Edited here: Restructured to handle POST with FILES properly
    if request.method == 'POST':
        # Edited here: Added request.FILES to movie_form to handle poster uploads
        movie_form = MovieForm(request.POST, request.FILES, instance=detail.movie)
        detail_form = MovieAdminDetailsForm(request.POST, request.FILES, instance=detail)

        # Check if user wants to clear the poster
        # Edited here: Added check if poster exists before deletion
        if request.POST.get('clear_poster') == 'true':
            if detail.poster:
                detail.poster.delete(save=False)
                detail.poster = None
                detail.save()

        if movie_form.is_valid() and detail_form.is_valid():
            movie_form.save()
            detail_form.save()
            messages.success(request, "Movie details updated successfully!")
            return redirect('movie_detail', pk=pk)
        else:
            # Edited here: Added detailed error notifications
            if not movie_form.is_valid():
                for field, errors in movie_form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
            if not detail_form.is_valid():
                for field, errors in detail_form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
    else:
        # Edited here: Initialize forms in else block for GET requests
        movie_form = MovieForm(instance=detail.movie)
        detail_form = MovieAdminDetailsForm(instance=detail)

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

            # Get the poster URL safely
            poster_url = None
            if movie_detail.poster:
                try:
                    # Use the model's poster_url property if available
                    if hasattr(movie_detail, 'poster_url'):
                        poster_url = movie_detail.poster_url
                    else:
                        # Fallback: build URL manually
                        poster_url = movie_detail.poster.build_url(
                            width=400,
                            height=600,
                            crop="fill",
                            quality="auto"
                        )
                except (AttributeError, Exception):
                    # If anything fails, use the direct URL
                    poster_url = movie_detail.poster.url

            cinemas.append({
                'detail_id': movie_detail.id,
                'cinema_name': admin.cinema_name,
                'showing_times': json.dumps(showtimes_data),
                'poster': movie_detail.poster,
                'poster_url': poster_url,  # Add this line
                'has_movie': True,
                'price': movie_detail.price,
                'end_date': movie_detail.end_date.isoformat(),
            })
        else:
            # Cinema doesn't have this movie yet
            cinemas.append({
                'detail_id': None,
                'cinema_name': admin.cinema_name,
                'showing_times': json.dumps([]),
                'poster': None,
                'poster_url': None,  # Add this line
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
    Confirm the reservation for a specific cinema, date, showtime, and selected seats.
    """
    detail = get_object_or_404(MovieAdminDetails, id=detail_id)

    if request.method == 'POST':
        selected_date = request.POST.get('selected_date')
        selected_showtime = request.POST.get('selected_showtime')
        number_of_seats = int(request.POST.get('number_of_seats', 1))
        selected_seats_json = request.POST.get('selected_seats', '[]')

        try:
            selected_seats = json.loads(selected_seats_json)
        except json.JSONDecodeError:
            messages.error(request, "Invalid seat selection.")
            return redirect('reserve_movie', movie_id=detail.movie.id)

        # Validate number of seats matches selected seats
        if len(selected_seats) != number_of_seats:
            messages.error(request, "Number of selected seats does not match your input.")
            return redirect('reserve_movie', movie_id=detail.movie.id)

        # Check that seats are not already reserved
        existing_reservations = Reservation.objects.filter(
            movie_detail=detail,
            selected_date=selected_date,
            selected_showtime=selected_showtime
        ).values_list('selected_seats', flat=True)

        already_reserved = []
        for seats in existing_reservations:
            if isinstance(seats, str):
                seats = json.loads(seats)
            already_reserved.extend(seats)

        if any(seat in already_reserved for seat in selected_seats):
            messages.error(request, "One or more of your selected seats have already been reserved.")
            return redirect('reserve_movie', movie_id=detail.movie.id)

        # Calculate total cost
        total_cost = detail.price * number_of_seats

        # Create the reservation
        reservation = Reservation.objects.create(
            user=request.user,
            movie_detail=detail,
            cinema_name=detail.admin.cinema_name,
            selected_date=selected_date,
            selected_showtime=selected_showtime,
            number_of_seats=number_of_seats,
            selected_seats=selected_seats,
            total_cost=total_cost,  # Add total cost
            status='confirmed',
        )

        messages.success(
            request,
            f"Reservation confirmed for {detail.movie.title} at {detail.admin.cinema_name} "
            f"on {selected_date} ({selected_showtime})! Seats: {', '.join(selected_seats)} - "
            f"Total Cost: ${total_cost:.2f}"
        )
        return redirect('user_dashboard')

    context = {
        'detail': detail,
    }
    return render(request, 'movies/confirm_reservation.html', context)


@login_required
def hall_seat_layout_view(request, detail_id, selected_date, selected_showtime):
    """
    Return the seat layout and already reserved seats for a given movie detail, date, and showtime.
    """
    detail = get_object_or_404(MovieAdminDetails, id=detail_id)

    # Hall layout: default to empty dict if not set
    hall_layout = detail.hall.layout or {}

    # Get reserved seats for this showtime and date
    reserved_qs = Reservation.objects.filter(
        movie_detail=detail,
        selected_date=selected_date,
        selected_showtime=selected_showtime
    ).values_list('selected_seats', flat=True)

    reserved_seats = []
    for seats in reserved_qs:
        if seats:
            try:
                if isinstance(seats, str):
                    seat_list = json.loads(seats)
                else:
                    seat_list = seats
                reserved_seats.extend(seat_list)
            except (json.JSONDecodeError, TypeError):
                # Handle case where selected_seats might be stored differently
                continue

    return JsonResponse({
        "seat_map": hall_layout,
        "reserved": reserved_seats,
    })