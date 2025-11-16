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
        # Your existing reservation creation logic
        try:
            # Assuming you have form processing here
            reservation = Reservation(
                user=request.user,
                movie_detail=request.POST.get('movie_detail'),  # Adjust based on your actual form
                cinema_name=request.POST.get('cinema_name'),
                selected_date=request.POST.get('selected_date'),
                selected_showtime=request.POST.get('selected_showtime'),
                number_of_seats=request.POST.get('number_of_seats'),
                selected_seats=request.POST.get('selected_seats', []),
                status='confirmed'
            )
            
            # Save the reservation (this will trigger the confirmation email from model save)
            reservation.save()
            
            messages.success(request, "Reservation created successfully! Confirmation email sent.")
            return redirect('user_reservations')
            
        except Exception as e:
            messages.error(request, f"Error creating reservation: {str(e)}")
            return redirect('create_reservation')
    
    # Your existing GET request handling
    return render(request, 'reservations/create_reservation.html')

# --------------------------
# Send Reservation Confirmation Email
# --------------------------
def send_reservation_confirmation_email(reservation):
    """Send reservation confirmation email - same pattern as admin registration"""
    user = reservation.user
    subject = f"🎬 Reservation Confirmed - {reservation.movie_detail.movie.title}"
    
    message = (
        f"Hello {user.first_name or user.username},\n\n"
        f"Your movie reservation has been confirmed!\n\n"
        f"📋 Reservation Details:\n"
        f"Movie: {reservation.movie_detail.movie.title}\n"
        f"Cinema: {reservation.cinema_name}\n"
        f"Date: {reservation.selected_date}\n"
        f"Showtime: {reservation.selected_showtime}\n"
        f"Number of Seats: {reservation.number_of_seats}\n"
        f"Seats: {', '.join(reservation.selected_seats)}\n"
        f"Reservation ID: {reservation.id}\n\n"
        f"We look forward to seeing you at the cinema!\n\n"
        f"Thank you for choosing ReelTime!"
    )
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )

# --------------------------
# Send Reservation Reminder Email
# --------------------------
def send_reservation_reminder_email(reservation):
    """Send reservation reminder email for tomorrow's reservation"""
    user = reservation.user
    subject = f"⏰ Movie Reminder - {reservation.movie_detail.movie.title} tomorrow!"
    
    message = (
        f"Hello {user.first_name or user.username},\n\n"
        f"This is a friendly reminder about your movie reservation tomorrow!\n\n"
        f"🎟️ Your Reservation:\n"
        f"Movie: {reservation.movie_detail.movie.title}\n"
        f"Cinema: {reservation.cinema_name}\n"
        f"Date: {reservation.selected_date}\n"
        f"Showtime: {reservation.selected_showtime}\n"
        f"Seats: {', '.join(reservation.selected_seats)}\n\n"
        f"Please arrive at least 15 minutes before the showtime.\n\n"
        f"Enjoy your movie experience! 🍿"
    )
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )