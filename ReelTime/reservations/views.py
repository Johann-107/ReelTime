from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Reservation

# Create your views here.
@login_required
def user_reservations_view(request):
    # If admin, show all customer reservations for their cinema's movies
    # If regular user, show only their own reservations
    if request.user.is_admin:
        reservations = Reservation.objects.filter(
            movie_detail__admin=request.user
        ).select_related('user', 'movie_detail__movie').order_by('-reservation_date')
    else:
        reservations = Reservation.objects.filter(user=request.user).order_by('-reservation_date')
    
    return render(request, 'reservations/reservations.html', {'reservations': reservations})