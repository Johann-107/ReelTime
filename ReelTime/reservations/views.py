from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Reservation
from django.core.mail import send_mail
from django.conf import settings

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

# --------------------------
# Create Reservation with Email Notification
# --------------------------
@login_required
def create_reservation(request):
    if request.method == "POST":
        try:
            print("🟡 Starting reservation creation...")

            reservation = Reservation(
                user=request.user,
                movie_detail=request.POST.get('movie_detail'),
                cinema_name=request.POST.get('cinema_name'),
                selected_date=request.POST.get('selected_date'),
                selected_showtime=request.POST.get('selected_showtime'),
                number_of_seats=request.POST.get('number_of_seats'),
                selected_seats=request.POST.get('selected_seats', []),
                status='confirmed'
            )
            
            print(f"🟡 About to save reservation for user: {request.user.email}")
            reservation.save()  # This will trigger the email automatically
            print("🟢 Reservation saved, email should be sent")
            
            messages.success(request, "Reservation created successfully! Confirmation email sent.")
            return redirect('user_reservations')
            
        except Exception as e:
            print(f"🔴 Error: {e}")
            messages.error(request, f"Error creating reservation: {str(e)}")
    
    return render(request, 'reservations/create_reservation.html')