# reservations/utils.py
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_reservation_confirmation_email(reservation):
    """Send reservation confirmation email"""
    user = reservation.user
    subject = f"🎬 Reservation Confirmed - {reservation.movie_detail.movie.title}"
    
    # Create plain text message
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